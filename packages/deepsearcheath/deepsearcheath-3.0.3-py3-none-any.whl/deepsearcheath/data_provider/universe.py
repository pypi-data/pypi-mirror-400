import pandas as pd
from pathlib import Path
import datetime
import logging
from ..api.client import DeepSearchClient

logger = logging.getLogger(__name__)

class UniverseManager:
    """미국 주식 유니버스(티커) 관리"""
    def __init__(self, cache_dir: Path):
        self.universe_dir = cache_dir / "universe"
        self.universe_dir.mkdir(parents=True, exist_ok=True)
        self.nasdaq_url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
        self.nyse_url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"

    def _get_nasdaq_tickers(self):
        cache_file_dir = self.universe_dir / "nasdaq_tickers.csv"
        
        # 캐시된 데이터가 있고 당일 데이터면 사용
        if cache_file_dir.exists() and (datetime.datetime.now() - datetime.datetime.fromtimestamp(cache_file_dir.stat().st_mtime)).days < 1:
            try:
                return pd.read_csv(cache_file_dir)
            except Exception:
                pass
            
        try:
            logger.info("Downloading NASDAQ data...")
            df = pd.read_csv(self.nasdaq_url, sep='|', dtype=str, index_col=False)
            df = df.iloc[:-1]  # 마지막 행 제거
            df['Exchange'] = 'NASDAQ'
            
            # 캐시 저장
            df.to_csv(cache_file_dir, index=False)
            return df
        except Exception as e:
            logger.error(f"[_get_nasdaq_tickers] Error fetching NASDAQ data: {e}")
            # 캐시된 데이터라도 있으면 사용
            if cache_file_dir.exists():
                return pd.read_csv(cache_file_dir)
            return pd.DataFrame()
            
    def _get_nyse_tickers(self):
        cache_file_dir = self.universe_dir / "nyse_tickers.csv"
        
        if cache_file_dir.exists() and (datetime.datetime.now() - datetime.datetime.fromtimestamp(cache_file_dir.stat().st_mtime)).days < 1:
            try:
                return pd.read_csv(cache_file_dir)
            except Exception:
                pass
            
        try:
            logger.info("Downloading NYSE data...")
            df = pd.read_csv(self.nyse_url, sep='|', dtype=str, index_col=False)
            df = df.iloc[:-1]
            df['Exchange'] = df.get('Exchange', 'NYSE')
            
            df.to_csv(cache_file_dir, index=False)
            return df
        except Exception as e:
            logger.error(f"[_get_nyse_tickers] Error fetching NYSE data: {e}")
            if cache_file_dir.exists():
                return pd.read_csv(cache_file_dir)
            return pd.DataFrame()

    async def _get_kr_tickers_from_api(self):
        """API를 통해 한국 티커 목록을 가져옴"""
        cache_file_dir = self.universe_dir / "kr_tickers.csv"
        
        # 캐시 확인 (1일)
        if cache_file_dir.exists() and (datetime.datetime.now() - datetime.datetime.fromtimestamp(cache_file_dir.stat().st_mtime)).days < 1:
            try:
                return pd.read_csv(cache_file_dir)
            except Exception:
                pass
                
        try:
            logger.info("Fetching KR tickers from API...")
            
            client = DeepSearchClient()
            async with client:
                response = await client.get_companies(country_code='kr', page_size=10000)
                data = response.get('data', {})
                if isinstance(data, dict) and 'companies' in data:
                    raw_data = data['companies']
                elif isinstance(data, list):
                    raw_data = data
                else:
                    raw_data = []
            
            if not raw_data:
                return pd.DataFrame()
                
            # 데이터 가공
            # API 응답 구조: [{'symbol': '005930', 'name_ko': '삼성전자', 'exchange_code': 'KOSPI', ...}, ...]
            df = pd.DataFrame(raw_data)
            
            # 컬럼 매핑
            if 'symbol' in df.columns:
                df = df.rename(columns={'symbol': 'Symbol', 'name_ko': 'Name', 'exchange_code': 'Exchange'})
                
            # 필요한 컬럼만 선택
            cols = ['Symbol', 'Exchange', 'Name']
            df = df[[c for c in cols if c in df.columns]]
            
            # 캐시 저장
            df.to_csv(cache_file_dir, index=False)
            return df
            
        except Exception as e:
            logger.error(f"[_get_kr_tickers_from_api] Error: {e}")
            if cache_file_dir.exists():
                return pd.read_csv(cache_file_dir)
            return pd.DataFrame()

    async def get_all_tickers(self, region: str = "US"):
        """
        모든 거래소의 티커 데이터를 가져와서 통합
        
        Args:
            region: "US" (미국), "KR" (한국), "ALL" (전체)
        """
        all_data = []
        
        if region.upper() in ["US", "ALL"]:
            # NASDAQ과 NYSE 데이터 가져오기 (동기 함수)
            nasdaq_df = self._get_nasdaq_tickers()
            nyse_df = self._get_nyse_tickers()
            
            # NYSE/Other의 경우 ACT Symbol 컬럼을 Symbol로 복사
            if not nyse_df.empty and 'ACT Symbol' in nyse_df.columns:
                nyse_df['Symbol'] = nyse_df['ACT Symbol']
                
            if not nasdaq_df.empty:
                all_data.append(nasdaq_df)
            if not nyse_df.empty:
                all_data.append(nyse_df)
        
        if region.upper() in ["KR", "ALL"]:
            # 한국 티커 가져오기 (비동기 함수)
            kr_df = await self._get_kr_tickers_from_api()
            if not kr_df.empty:
                all_data.append(kr_df)
            
        if not all_data:
            return pd.DataFrame()
            
        combined_df = pd.concat(all_data, ignore_index=True)
        return self._clean_tickers(combined_df)
    
    def _clean_tickers(self, df):
        """티커 데이터 정제"""
        try:
            # Symbol 컬럼 찾기
            symbol_col = None
            for col in ['Symbol', 'ACT Symbol']:
                if col in df.columns:
                    symbol_col = col
                    break
            
            if not symbol_col:
                raise ValueError("Symbol column not found")
                
            # 기본 필터링
            df = df[df[symbol_col].notna()].copy()
            df[symbol_col] = df[symbol_col].str.strip().str.upper()
            
            # 필터링 조건
            mask = (
                (~df[symbol_col].str.contains(r'[\$\^]', regex=True)) &  # 특수문자 제외
                (~df[symbol_col].str.contains('TEST')) &                  # 테스트 종목 제외
                ((df[symbol_col].str.len() <= 5) | (df[symbol_col].str.len() == 6)) # 미국(<=5) + 한국(6자리)
            )
            
            # ETF 필터링 (ETF 컬럼이 있는 경우, 'Y'이면 제외 -> 주식만)
            if 'ETF' in df.columns:
                mask = mask & (df['ETF'] != 'Y')
            
            filtered_df = df[mask].copy()
            
            # 컬럼 이름 통일
            if 'Security Name' in filtered_df.columns:
                filtered_df = filtered_df.rename(columns={'Security Name': 'Name'})
            elif 'Company Name' in filtered_df.columns:
                filtered_df = filtered_df.rename(columns={'Company Name': 'Name'})
            
            # 필요한 컬럼만 선택
            required_columns = ['Symbol', 'Exchange']
            if 'Name' in filtered_df.columns:
                required_columns.append('Name')
                
            filtered_df = filtered_df[required_columns].copy()
            filtered_df = filtered_df.rename(columns={symbol_col: 'Symbol'})
            
            # 중복 제거
            filtered_df = filtered_df.drop_duplicates(subset=['Symbol'])
            
            return filtered_df
            
        except Exception as e:
            logger.error(f"[_clean_tickers] Error in _clean_tickers: {e}")
            return pd.DataFrame()

