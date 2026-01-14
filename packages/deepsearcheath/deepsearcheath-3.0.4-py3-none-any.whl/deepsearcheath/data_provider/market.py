import asyncio
import logging
import datetime
import os
from tqdm.asyncio import tqdm
import shutil
from pathlib import Path
from typing import List, Dict, Union
import pandas as pd
from ..api.client import DeepSearchClient, KRXClient
from .store import MarketDataCache
from .universe import UniverseManager

logger = logging.getLogger(__name__)

async def fetch_symbol_data(
    client: DeepSearchClient,
    symbol: str,
    date_from: str,
    date_to: str,
    semaphore: asyncio.Semaphore,
    max_retries: int = 3,
    verbose: bool = True
) -> List[Dict]:
    """단일 심볼 데이터 비동기 요청 (Retry 로직 포함)"""
    async with semaphore:
        for attempt in range(max_retries):
            try:
                # API 호출
                response = await client.get_stock_price(
                    symbol=symbol,
                    date_from=date_from,
                    date_to=date_to,
                    page_size=10000,
                    include_trading_halted=True
                )
                
                data = response.get('data', [])
                if not data:
                    return []

                # 데이터 가공
                processed_data = []
                for item in data:
                    item['symbol'] = symbol
                    processed_data.append(item)
                    
                return processed_data
                
            except Exception as e:
                # 마지막 시도에서 에러 발생 시 로그 출력 및 빈 리스트 반환
                if attempt == max_retries - 1:
                    if verbose:
                        logger.error(f"Error fetching {symbol} after {max_retries} attempts: {e}")
                    return []
                
                # 지수 백오프 대기 (1s, 2s, 4s...)
                wait_time = 2 ** attempt
                if verbose:
                    logger.warning(f"Retry {attempt + 1}/{max_retries} for {symbol} due to error: {e}. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
        return []

def chunk_date_range(start_date: datetime.date, end_date: datetime.date, years: int = 1):
    """주어진 날짜 범위를 n년 단위로 분할"""
    current = start_date
    while current <= end_date:
        next_date = current + datetime.timedelta(days=365 * years)
        # 종료일보다 넘어가면 종료일로 맞춤. 단, next_date가 end_date보다 하루라도 크면 end_date 사용
        chunk_end = min(next_date - datetime.timedelta(days=1), end_date)
        
        # 시작일이 종료일보다 늦으면 종료
        if current > chunk_end:
            break
            
        yield current, chunk_end
        current = chunk_end + datetime.timedelta(days=1)

async def prepare_market_data(
    symbols: List[str],
    date_from: str,
    date_to: str,
    cache_dir: str = ".cache/market_data_v2",
    concurrency: int = 10,
    force_refresh: bool = False,
    flush: bool = False,
    verbose: bool = True
) -> MarketDataCache:
    """
    시장 데이터 준비 메인 함수 (캐싱 파이프라인)
    
    Args:
        symbols: 조회할 티커 리스트. "ALL_US" 입력 시 미국 전체 주식 대상.
        date_from: 시작 날짜 (YYYY-MM-DD)
        date_to: 종료 날짜 (YYYY-MM-DD)
        cache_dir: 캐시 디렉토리
        concurrency: 동시 요청 수
        force_refresh: 캐시 무시하고 새로 요청 여부 (기존 캐시는 유지하되 기간만 새로 요청)
        flush: 기존 캐시 파일을 삭제하고 처음부터 다시 시작할지 여부
        verbose: 상세 로그 출력 여부 (기본값: True)
    """
    # Flush 처리: 캐시 디렉토리 내 데이터 파일 삭제
    if flush:
        cache_path = Path(cache_dir)
        if cache_path.exists():
            logger.warning(f"Flush requested. Deleting cache directory: {cache_dir}")
            try:
                shutil.rmtree(cache_path)
            except Exception as e:
                logger.error(f"Failed to delete cache directory: {e}")

    cache = MarketDataCache(cache_dir)
    
    # "ALL_US" 등 키워드 처리
    target_region = None
    if isinstance(symbols, str):
        if symbols == "ALL_US": target_region = "US"
        elif symbols == "ALL_KO": target_region = "KR"
        elif symbols == "ALL": target_region = "ALL"
        else: symbols = [symbols] # 단일 티커인 경우 리스트로 변환
        
    if isinstance(symbols, list) and len(symbols) == 1:
        if symbols[0] == "ALL_US": target_region = "US"
        elif symbols[0] == "ALL_KO": target_region = "KR"
        elif symbols[0] == "ALL": target_region = "ALL"

    if target_region:
        logger.info(f"Target: ALL {target_region} Stocks. Fetching ticker list...")
        um = UniverseManager(Path(cache_dir))
        universe_df = await um.get_all_tickers(region=target_region)
        
        if universe_df.empty:
            logger.error(f"Failed to fetch {target_region} ticker list.")
            return cache
            
        target_symbols = []
        for _, row in universe_df.iterrows():
            sym = str(row['Symbol'])
            exch = str(row.get('Exchange', '')).upper()
            
            # API 호출용 심볼 생성
            # [수정] 티커가 6자리 숫자인 경우도 한국 주식으로 포함하도록 조건 강화
            is_korean_stock = (
                (target_region == "KR") or 
                (exch in ['KOSPI', 'KOSDAQ']) or #, 'KONEX']) or 
                (sym.isdigit() and len(sym) == 6)
            )
            
            if is_korean_stock:
                # 한국 주식: 심볼 그대로 사용 (API가 005930 형태 인식)
                target_symbols.append(sym)
            else:
                # 미국 주식: 접두어 추가
                if exch == 'NASDAQ':
                    target_symbols.append(f"NASDAQ:{sym}")
                else:
                    target_symbols.append(f"NYSE:{sym}")
        
        symbols = target_symbols
        logger.info(f"Resolved {len(symbols)} tickers for {target_region}.")

    client = DeepSearchClient() # API Key from env
    semaphore = asyncio.Semaphore(concurrency)
    
    date_to_dt = pd.to_datetime(date_to).date()
    date_from_dt = pd.to_datetime(date_from).date()
    
    symbols_to_fetch = []
    
    logger.info(f"Checking cache for {len(symbols)} symbols...")
    
    for symbol in symbols:
        fetch_start = date_from_dt
        
        if not force_refresh:
            last_date = cache.get_last_date(symbol)
            if last_date:
                if last_date >= date_to_dt:
                    # 이미 최신 데이터까지 있음 -> 스킵
                    continue
                # 마지막 날짜 다음날부터 요청
                fetch_start = max(date_from_dt, last_date + datetime.timedelta(days=1))
        
        if fetch_start > date_to_dt:
            continue
            
        symbols_to_fetch.append((symbol, fetch_start.strftime("%Y-%m-%d")))

    if not symbols_to_fetch:
        logger.info("All data is up to date in cache.")
        return cache

    logger.info(f"Need to fetch data for {len(symbols_to_fetch)} symbols from API...")
    
    async with client:
        fetch_tasks = []
        for symbol, start_date in symbols_to_fetch:
            # 1년 단위 청킹 적용
            task_start_dt = pd.to_datetime(start_date).date()
            task_end_dt = date_to_dt
            
            for chunk_start, chunk_end in chunk_date_range(task_start_dt, task_end_dt):
                fetch_tasks.append(
                    fetch_symbol_data(
                        client, 
                        symbol, 
                        chunk_start.strftime("%Y-%m-%d"), 
                        chunk_end.strftime("%Y-%m-%d"), 
                        semaphore, 
                        verbose=verbose
                    )
                )
        
        # 진행 상황 표시를 위해 chunk로 나누거나 tqdm 등을 쓸 수 있지만 여기선 단순 gather
        # results = await asyncio.gather(*fetch_tasks)
        results = []
        for f in tqdm.as_completed(fetch_tasks, total=len(fetch_tasks), desc="Fetching Market Data"):
            res = await f
            results.append(res)
        
        # 결과 병합
        all_new_data = []
        for res in results:
            all_new_data.extend(res)
            
        if all_new_data:
            logger.info(f"Fetched {len(all_new_data)} records. Updating cache...")
            cache.update_data(all_new_data)
            cache.save()
            logger.info("Cache saved successfully.")
        else:
            logger.info("No new data fetched.")
            
    return cache

async def get_krx_market_price(date: str, market: str = "ALL", auth_key: str = None) -> pd.DataFrame:
    """
    KRX 일별 시세 데이터를 조회합니다.
    
    :param date: 조회 일자 (YYYYMMDD)
    :param market: 시장 구분 ("STK": 유가증권, "KSQ": 코스닥, "ALL": 전체)
    :param auth_key: KRX API Key (없으면 환경변수 KRX_API_KEY 사용)
    :return: 통합된 시세 데이터 DataFrame
    """
    auth_key = auth_key or os.getenv("KRX_API_KEY")
    
    # 날짜 포맷 변경: YYYY-MM-DD -> YYYYMMDD
    date = date.replace("-", "")
    
    async with KRXClient(auth_key=auth_key) as client:
        dfs = []
        
        # 타입 변환을 위한 컬럼 목록
        numeric_cols = [
            'TDD_CLSPRC', 'CMPPREVDD_PRC', 'FLUC_RT', 'TDD_OPNPRC', 
            'TDD_HGPRC', 'TDD_LWPRC', 'ACC_TRDVOL', 'ACC_TRDVAL', 
            'MKTCAP', 'LIST_SHRS'
        ]

        # 유가증권(STK)
        if market in ["STK", "ALL"]:
            try:
                data_stk = await client.get_stock_daily_trade_info(bas_dd=date)
                if "OutBlock_1" in data_stk:
                    df_stk = pd.DataFrame(data_stk["OutBlock_1"])
                    
                    # 타입 변환
                    if not df_stk.empty:
                        # 날짜 변환
                        if 'BAS_DD' in df_stk.columns:
                            df_stk['BAS_DD'] = pd.to_datetime(df_stk['BAS_DD'], format='%Y%m%d')
                            df_stk['BAS_DD'] = df_stk['BAS_DD'].apply(lambda x: x.strftime('%Y-%m-%d'))
                            df_stk['BAS_DD'] = pd.to_datetime(df_stk['BAS_DD'])

                        
                        # 숫자 변환 (쉼표 제거 후 float)
                        for col in numeric_cols:
                            if col in df_stk.columns:
                                df_stk[col] = df_stk[col].astype(str).str.replace(',', '').astype(float)

                    df_stk['MARKET'] = 'STK'
                    dfs.append(df_stk)
            except Exception as e:
                logger.error(f"Failed to fetch KRX STK data for {date}: {e}")
        
        # 코스닥(KSQ)
        if market in ["KSQ", "ALL"]:
            try:
                data_ksq = await client.get_kosdaq_daily_trade_info(bas_dd=date)
                if "OutBlock_1" in data_ksq:
                    df_ksq = pd.DataFrame(data_ksq["OutBlock_1"])
                    
                    # 타입 변환
                    if not df_ksq.empty:
                        # 날짜 변환
                        if 'BAS_DD' in df_ksq.columns:
                            df_ksq['BAS_DD'] = pd.to_datetime(df_ksq['BAS_DD'], format='%Y%m%d')
                            df_ksq['BAS_DD'] = df_ksq['BAS_DD'].apply(lambda x: x.strftime('%Y-%m-%d'))
                            df_ksq['BAS_DD'] = pd.to_datetime(df_ksq['BAS_DD'])

                        # 숫자 변환 (쉼표 제거 후 float)
                        for col in numeric_cols:
                            if col in df_ksq.columns:
                                df_ksq[col] = df_ksq[col].astype(str).str.replace(',', '').astype(float)

                    df_ksq['MARKET'] = 'KSQ'
                    dfs.append(df_ksq)
            except Exception as e:
                logger.error(f"Failed to fetch KRX KSQ data for {date}: {e}")
        
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        
        return pd.DataFrame()

async def get_krx_market_price_period(
    date_from: str, 
    date_to: str, 
    market: str = "ALL", 
    auth_key: str = None,
    concurrency: int = 10,
    delay: float = 0.3
) -> pd.DataFrame:
    """
    기간별 KRX 시장 데이터를 조회하여 통합 DataFrame을 반환합니다.
    (속도 제한 기능 포함)
    
    :param date_from: 시작일 (YYYY-MM-DD)
    :param date_to: 종료일 (YYYY-MM-DD)
    :param market: 시장 구분
    :param concurrency: 동시 요청 수 제한 (기본값: 5)
    :param delay: 요청 간 딜레이(초) (기본값: 0.5초)
    :return: 통합 DataFrame
    """
    dates = pd.date_range(start=date_from, end=date_to)
    
    # 동시 실행 제한을 위한 세마포어
    semaphore = asyncio.Semaphore(concurrency)
    
    async def _fetch_with_limit(date_val):
        async with semaphore:
            # 딜레이 추가 (너무 빠른 호출 방지)
            await asyncio.sleep(delay)
            date_str = date_val.strftime("%Y%m%d")
            df = await get_krx_market_price(date=date_str, market=market, auth_key=auth_key)
            if not df.empty:
                df['BAS_DD'] = date_str # 날짜 컬럼 보장
            return df
            
    tasks = [_fetch_with_limit(d) for d in dates]
    
    results = []
    # tqdm으로 진행률 표시
    for f in tqdm.as_completed(tasks, total=len(tasks), desc="Fetching Period Data"):
        res = await f
        results.append(res)
        
    valid_dfs = [df for df in results if not df.empty]
    
    if valid_dfs:
        return_df = pd.concat(valid_dfs, ignore_index=True)
        return_df['BAS_DD'] = pd.to_datetime(return_df['BAS_DD']).apply(lambda x: x.strftime('%Y-%m-%d'))
        return_df['BAS_DD'] = pd.to_datetime(return_df['BAS_DD'])
        
        # --- 갭 수익률 계산 추가 ---
        return_df = return_df.sort_values(by=['ISU_CD', 'BAS_DD'])
        return_df['PREV_CLSPRC'] = return_df.groupby('ISU_CD')['TDD_CLSPRC'].shift(1)
        return_df['GAP_RT'] = (return_df['TDD_OPNPRC'] - return_df['PREV_CLSPRC']) / return_df['PREV_CLSPRC']
        # (보정) 시가가 0인 경우(거래정지/휴장 등) GAP_RT를 0으로 강제 할당
        return_df.loc[return_df['TDD_OPNPRC'] == 0, 'GAP_RT'] = 0.0
        # ------------------------
        
        # 다시 date 객체로 변환이 필요하다면
        # return_df['BAS_DD'] = return_df['BAS_DD'].dt.date
        
        
        return return_df
        
    return pd.DataFrame()
