import pandas as pd
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Union
import datetime
from .constants import MAINSTREAM_NEWS_VENDORS

logger = logging.getLogger(__name__)

@dataclass
class MarketDataCache:
    """
    시장 데이터 캐시 관리 클래스 (V2 API 대응)
    
    Attributes:
        cache_dir (Path): 캐시 디렉토리 경로
        price_data (pd.DataFrame): 시계열 가격 데이터 (columns: date, symbol, open, high, low, close, volume, ...)
        news_data (pd.DataFrame): 뉴스 데이터 (columns: date, symbol, title, url, provider, sentiment, ...)
        metadata (pd.DataFrame): 종목 메타데이터 (columns: symbol, company_name, ...)
    """
    cache_dir: Path
    price_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    news_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    metadata: pd.DataFrame = field(default_factory=pd.DataFrame)
    
    def __post_init__(self):
        self.cache_dir = Path(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self):
        """캐시 로드"""
        price_path = self.cache_dir / "price_data.parquet"
        news_path = self.cache_dir / "news_data.parquet"
        metadata_path = self.cache_dir / "metadata.parquet"

        if price_path.exists():
            try:
                self.price_data = pd.read_parquet(price_path)
                # 날짜 타입 변환 보장
                if 'date' in self.price_data.columns:
                    self.price_data['date'] = pd.to_datetime(self.price_data['date'])
            except Exception as e:
                logger.error(f"Failed to load price cache: {e}")
                self.price_data = pd.DataFrame()
        
        if news_path.exists():
            try:
                self.news_data = pd.read_parquet(news_path)
                if 'date' in self.news_data.columns:
                    self.news_data['date'] = pd.to_datetime(self.news_data['date'])
            except Exception as e:
                logger.error(f"Failed to load news cache: {e}")
                self.news_data = pd.DataFrame()

        if metadata_path.exists():
            try:
                self.metadata = pd.read_parquet(metadata_path)
            except Exception as e:
                logger.error(f"Failed to load metadata cache: {e}")
                self.metadata = pd.DataFrame()

    def save(self):
        """캐시 저장"""
        if not self.price_data.empty:
            # 저장 전 정렬: symbol, date 순
            save_df = self.price_data.sort_values(['symbol', 'date'])
            save_df.to_parquet(self.cache_dir / "price_data.parquet", index=False)
        
        if not self.news_data.empty:
            # symbol이 list 타입일 경우 정렬 시 에러 발생 (unhashable) 방지
            df_to_save = self.news_data
            sort_cols = ['date']
            
            is_symbol_list = False
            if 'symbol' in df_to_save.columns and len(df_to_save) > 0:
                # 첫 번째 유효한 값으로 타입 확인
                first_valid_idx = df_to_save['symbol'].first_valid_index()
                if first_valid_idx is not None:
                    first_val = df_to_save['symbol'].loc[first_valid_idx]
                    if isinstance(first_val, list):
                        is_symbol_list = True
            
            if is_symbol_list:
                # 리스트를 문자열로 변환하여 정렬 기준으로 사용
                # 원본 데이터프레임을 건드리지 않기 위해 복사
                df_to_save = df_to_save.copy()
                df_to_save['_symbol_str'] = df_to_save['symbol'].astype(str)
                sort_cols = ['_symbol_str', 'date']
            elif 'symbol' in df_to_save.columns:
                sort_cols = ['symbol', 'date']
                
            save_news_df = df_to_save.sort_values(sort_cols)
            
            if is_symbol_list:
                save_news_df = save_news_df.drop(columns=['_symbol_str'])
                
            save_news_df.to_parquet(self.cache_dir / "news_data.parquet", index=False)

        if not self.metadata.empty:
            # symbol 기준 정렬
            meta_save_df = self.metadata.sort_values(['symbol'])
            meta_save_df.to_parquet(self.cache_dir / "metadata.parquet", index=False)
            
    def get_last_date(self, symbol: str) -> Optional[datetime.date]:
        """특정 심볼의 마지막 데이터 날짜 반환 (가격 데이터 기준)"""
        if self.price_data.empty:
            return None
        
        # 벡터화된 연산이 빠르지만, 특정 심볼만 필터링 필요
        if symbol not in self.price_data['symbol'].values:
            return None
            
        symbol_data = self.price_data[self.price_data['symbol'] == symbol]
        return symbol_data['date'].max().date()

    def get_last_news_date(self, symbol: Optional[str] = None, keyword: Optional[str] = None) -> Optional[datetime.date]:
        """특정 심볼 또는 키워드의 마지막 뉴스 날짜 반환"""
        if self.news_data.empty:
            return None
        
        mask = None
        if symbol:
            # symbol 컬럼이 리스트인지 확인
            is_list = False
            if not self.news_data.empty and 'symbol' in self.news_data.columns:
                first_val = self.news_data['symbol'].iloc[0]
                if isinstance(first_val, list):
                    is_list = True
            
            if is_list:
                # 리스트 안에 symbol이 포함되어 있는지 확인
                mask = self.news_data['symbol'].apply(lambda x: symbol in x if isinstance(x, list) else False)
            else:
                mask = self.news_data['symbol'] == symbol
        elif keyword and 'keyword' in self.news_data.columns:
            mask = self.news_data['keyword'] == keyword
            
        if mask is None or not mask.any():
            return None
            
        symbol_data = self.news_data[mask]
        return symbol_data['date'].max().date()

    def update_data(self, new_data: List[Dict]):
        """새로운 가격 데이터 병합"""
        if not new_data:
            return

        new_df = pd.DataFrame(new_data)
        
        # 필수 컬럼 확인
        if 'date' not in new_df.columns or 'symbol' not in new_df.columns:
            logger.warning("New data missing required columns (date, symbol). Skipping update.")
            return

        new_df['date'] = pd.to_datetime(new_df['date'])
        
        # 1. 메타데이터 추출 및 업데이트
        # 메타데이터로 쓸만한 컬럼들 후보
        meta_cols = ['symbol', 'company_name', 'stock_type', 'market_cap', 'shares_outstanding'] 
        available_meta_cols = [c for c in meta_cols if c in new_df.columns]
        
        if available_meta_cols:
            new_meta = new_df[available_meta_cols].drop_duplicates(subset=['symbol'], keep='last')
            if self.metadata.empty:
                self.metadata = new_meta
            else:
                # 기존 메타데이터와 병합 (새로운 정보로 덮어쓰기)
                self.metadata = pd.concat([self.metadata, new_meta])
                self.metadata = self.metadata.drop_duplicates(subset=['symbol'], keep='last')

        # 2. 가격 데이터 업데이트
        if self.price_data.empty:
            self.price_data = new_df
        else:
            self.price_data = pd.concat([self.price_data, new_df])
            # 중복 제거 (symbol, date 기준, 최신 데이터 우선)
            self.price_data = self.price_data.drop_duplicates(subset=['date', 'symbol'], keep='last')

    def update_news_data(self, new_news: List[Dict]):
        """새로운 뉴스 데이터 병합"""
        if not new_news:
            return

        new_df = pd.DataFrame(new_news)
        
        if 'date' not in new_df.columns or 'symbol' not in new_df.columns:
            logger.warning("New news data missing required columns. Skipping update.")
            return

        new_df['date'] = pd.to_datetime(new_df['date'])

        if self.news_data.empty:
            self.news_data = new_df
        else:
            self.news_data = pd.concat([self.news_data, new_df])
            
            # symbol이 리스트 타입인 경우 처리
            is_symbol_list = False
            if 'symbol' in self.news_data.columns and not self.news_data.empty:
                first_val = self.news_data['symbol'].iloc[0]
                if isinstance(first_val, list):
                    is_symbol_list = True

            # 중복 제거 (symbol, keyword, date, title 기준)
            # symbol이 None인 경우도 처리됨 (NaN으로 취급)
            subset_cols = ['date']
            
            # symbol 컬럼 처리
            if 'symbol' in self.news_data.columns:
                if is_symbol_list:
                    # 리스트는 unhashable 하므로 문자열로 변환하여 임시 컬럼 생성
                    self.news_data['_symbol_hash'] = self.news_data['symbol'].astype(str)
                    subset_cols.append('_symbol_hash')
                else:
                    subset_cols.append('symbol')
            
            # keyword 컬럼이 있으면 포함
            if 'keyword' in new_df.columns:
                subset_cols.append('keyword')
                
            if 'title' in new_df.columns:
                subset_cols.append('title')
            elif 'id' in new_df.columns:
                subset_cols.append('id')
                
            self.news_data = self.news_data.drop_duplicates(subset=subset_cols, keep='last')
            
            if is_symbol_list and '_symbol_hash' in self.news_data.columns:
                self.news_data = self.news_data.drop(columns=['_symbol_hash'])

    def get_price(self, symbols: Union[str, List[str]], date_from: str, date_to: str) -> pd.DataFrame:
        """데이터 조회"""
        if self.price_data.empty:
            return pd.DataFrame()
            
        if isinstance(symbols, str):
            symbols = [symbols]
            
        date_from_dt = pd.to_datetime(date_from)
        date_to_dt = pd.to_datetime(date_to)
        
        mask = (
            (self.price_data['symbol'].isin(symbols)) & 
            (self.price_data['date'] >= date_from_dt) & 
            (self.price_data['date'] <= date_to_dt)
        )
        return self.price_data.loc[mask].copy()

    def get_news(
        self, 
        symbols: Optional[Union[str, List[str]]] = None, 
        date_from: str = None, 
        date_to: str = None,
        mainstream_only: bool = False
    ) -> pd.DataFrame:
        """뉴스 데이터 조회 (심볼 또는 키워드)"""
        if self.news_data.empty:
            return pd.DataFrame()
            
        if symbols and isinstance(symbols, str):
            symbols = [symbols]
            
        mask = pd.Series(True, index=self.news_data.index)
        
        # 날짜 필터링
        if date_from:
            mask = mask & (self.news_data['date'] >= pd.to_datetime(date_from))
        if date_to:
            mask = mask & (self.news_data['date'] <= pd.to_datetime(date_to))
            
        # 심볼/키워드 필터링
        # symbols 인자에 키워드가 들어올 수도 있다고 가정 (기존 호환성)
        # 하지만 명확히 구분하는게 좋음. 여기서는 symbols 인자가 주어지면
        # symbol 컬럼과 keyword 컬럼 모두에서 찾도록 유연하게 처리
        if symbols:
            # symbol 컬럼이 리스트인지 확인
            is_list = False
            if not self.news_data.empty and 'symbol' in self.news_data.columns:
                first_val = self.news_data['symbol'].iloc[0]
                if isinstance(first_val, list):
                    is_list = True
            
            if is_list:
                # 리스트 요소 중 하나라도 symbols에 포함되는지 확인
                symbol_set = set(symbols)
                symbol_mask = self.news_data['symbol'].apply(
                    lambda x: any(s in symbol_set for s in x) if isinstance(x, list) else False
                )
            else:
                symbol_mask = self.news_data['symbol'].isin(symbols)
            
            keyword_mask = pd.Series(False, index=self.news_data.index)
            if 'keyword' in self.news_data.columns:
                keyword_mask = self.news_data['keyword'].isin(symbols)
                
            mask = mask & (symbol_mask | keyword_mask)
        
        if mainstream_only:
            if 'provider' in self.news_data.columns:
                mask = mask & (self.news_data['provider'].isin(MAINSTREAM_NEWS_VENDORS))
        
        return self.news_data.loc[mask].copy()

    def get_market_matrices(
        self,
        symbols: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        캐시된 데이터를 기반으로 분석용 행렬(Matrix) 데이터셋을 반환합니다.
        
        Args:
            symbols: 대상 심볼 리스트 (None일 경우 캐시된 전체 심볼)
            date_from: 시작 날짜 (YYYY-MM-DD)
            date_to: 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            Dict containing:
                - price: 종가 행렬 (date x symbol)
                - market_cap: 시가총액 행렬 (date x symbol)
                - volume: 거래량 행렬 (date x symbol)
        """
        # 1. 데이터 조회 (Long Format)
        if self.price_data.empty:
            return {
                'price': pd.DataFrame(),
                'market_cap': pd.DataFrame(),
                'volume': pd.DataFrame()
            }

        if symbols is None:
            # 전체 심볼 사용
            symbols = self.price_data['symbol'].unique().tolist()
            
        # date_from/to가 없으면 전체 기간 사용
        if date_from is None:
            date_from = self.price_data['date'].min().strftime('%Y-%m-%d')
        if date_to is None:
            date_to = self.price_data['date'].max().strftime('%Y-%m-%d')
            
        df = self.get_price(symbols, date_from, date_to)
        
        if df.empty:
            return {
                'price': pd.DataFrame(),
                'market_cap': pd.DataFrame(),
                'volume': pd.DataFrame()
            }
            
        # 2. Pivot 변환
        result = {}
        
        # 컬럼 이름 정제 함수 (거래소 접두어 제거)
        def clean_columns(df):
            if df.empty:
                return df
            # 컬럼명이 'NASDAQ:AAPL' 형태라면 'AAPL'만 남김
            df.columns = [col.split(':')[-1] if ':' in col else col for col in df.columns]
            return df
        
        # 종가 (close)
        if 'close' in df.columns:
            result['price'] = clean_columns(df.pivot(index='date', columns='symbol', values='close'))
        else:
            result['price'] = pd.DataFrame()
        
        # 시가총액 (market_cap)
        if 'market_cap' in df.columns:
            result['market_cap'] = clean_columns(df.pivot(index='date', columns='symbol', values='market_cap'))
        else:
            # logger.warning("'market_cap' column not found in data.")
            result['market_cap'] = pd.DataFrame()
            
        # 거래량 (volume)
        if 'volume' in df.columns:
            result['volume'] = clean_columns(df.pivot(index='date', columns='symbol', values='volume'))
        else:
            result['volume'] = pd.DataFrame()
            
        # 수익률 (return) - pct_change 사용
        if not result['price'].empty:
            result['return'] = result['price'].pct_change(fill_method=None)
        else:
            result['return'] = pd.DataFrame()
            
        return result

