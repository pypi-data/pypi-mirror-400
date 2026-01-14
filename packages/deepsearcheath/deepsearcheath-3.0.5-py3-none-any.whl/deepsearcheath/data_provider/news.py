import asyncio
import logging
import datetime
import json
from typing import List, Dict, Optional
from tqdm.asyncio import tqdm
import pandas as pd
from pathlib import Path
import gc
from ..api.client import DeepSearchClient
from .store import MarketDataCache

logger = logging.getLogger(__name__)

async def fetch_symbol_news(
    client: DeepSearchClient,
    symbol: Optional[str],
    date_from: str,
    date_to: str,
    semaphore: asyncio.Semaphore,
    max_retries: int = 3,
    save_raw_response: bool = False,
    raw_response_dir: Optional[str] = None,
    **kwargs
) -> List[Dict]:
    """
    단일 심볼 또는 키워드 뉴스 데이터 비동기 요청 (페이징 포함)
    
    Args:
        client: API 클라이언트
        symbol: 종목 코드 (Optional)
        date_from: 시작일
        date_to: 종료일
        semaphore: 동시성 제어 세마포어
        max_retries: 재시도 횟수
        save_raw_response: 원본 응답 저장 여부
        raw_response_dir: 원본 응답 저장 경로
        **kwargs: 추가 검색 파라미터 (keyword, company_name, highlight, clustering, uniquify, order, research_insight)
    """
    async with semaphore:
        for attempt in range(max_retries):
            try:
                # API 호출 파라미터 설정
                query_symbol = None
                if symbol:
                    query_symbol = symbol
                    if symbol.isdigit() and len(symbol) == 6: # 한국 티커
                        query_symbol = f"KRX:{symbol}"
                
                # 수집된 데이터에 할당할 keyword 값 추출
                target_keyword = kwargs.get('keyword')

                all_processed_data = []
                page = 1
                max_pages = 1000  # 무한 루프 방지용 최대 페이지 제한
                
                while page <= max_pages:
                    response = await client.get_articles(
                        symbols=query_symbol,  # None이면 전체 검색
                        date_from=date_from,
                        date_to=date_to,
                        page=page,
                        page_size=100,  # 뉴스 API 최대 페이지 사이즈
                        **kwargs  # 추가 파라미터 전달
                    )
                    
                    # 원본 응답 저장 (요구사항 3)
                    if save_raw_response and raw_response_dir:
                        try:
                            # 저장 경로 생성
                            save_dir = Path(raw_response_dir) / date_from[:4]  # 연도별 폴더
                            save_dir.mkdir(parents=True, exist_ok=True)
                            
                            # 파일명 식별자: symbol이 있으면 symbol, 없으면 keyword, 둘 다 없으면 'ALL'
                            file_ident = symbol if symbol else (target_keyword if target_keyword else 'ALL')
                            
                            # 파일명: {identifier}_{date_from}_{date_to}_{page}.json
                            filename = f"{file_ident}_{date_from}_{date_to}_p{page}.json"
                            file_path = save_dir / filename
                            
                            with open(file_path, "w", encoding="utf-8") as f:
                                json.dump(response, f, ensure_ascii=False, indent=2)
                        except Exception as e:
                            logger.error(f"Failed to save raw response: {e}")

                    data = response.get('data', [])
                    if not data:
                        break

                    # 데이터 가공
                    for item in data:
                        # 요구사항 2: 모든 데이터 저장 (item 복사)
                        processed_item = item.copy()
                        
                        # [추가] keyword 컬럼 할당
                        processed_item['keyword'] = target_keyword
                        
                        # 필수/편의 필드 보장 및 포맷팅
                        # store.py의 update_news_data에서 'symbol' 컬럼 유무를 검사하므로 반드시 추가해야 함
                        
                        # [수정] symbol 할당 로직: API 응답의 companies 첫 번째 심볼 사용 (없으면 요청 심볼 유지)
                        # symbol_req: 요청한 심볼 (검색 기준) -> 원래 symbol 변수 사용
                        processed_item['symbol_req'] = symbol
                        
                        resp_companies = item.get('companies', [])
                        
                        extracted_symbols = []
                        extracted_names = []
                        
                        # companies 리스트에서 모든 심볼과 이름 추출
                        if resp_companies and isinstance(resp_companies, list):
                            for comp in resp_companies:
                                if isinstance(comp, dict):
                                    comp_symbol = comp.get('symbol')
                                    comp_name = comp.get('name')
                                    if comp_symbol:
                                        extracted_symbols.append(comp_symbol)
                                    if comp_name:
                                        extracted_names.append(comp_name)
                        
                        # 응답에 없으면 요청했던 심볼(fallback) 사용, 그것도 없으면 빈 리스트 (키워드 검색인 경우)
                        if not extracted_symbols:
                            if symbol:
                                extracted_symbols = [symbol]
                            
                        processed_item['symbol'] = extracted_symbols
                        processed_item['symbol_name'] = extracted_names
                        
                        # 요구사항 1: date 의 시분초 데이터를 남겨라
                        # published_at이 없으면 빈 문자열
                        processed_item['date'] = item.get('published_at', '')
                        # 기존 호환성을 위해 필요한 필드 매핑 (없으면 생성)
                        if 'provider' not in processed_item:
                            processed_item['provider'] = item.get('publisher', '')
                        if 'url' not in processed_item:
                            processed_item['url'] = item.get('content_url', '')
                        if 'sentiment' not in processed_item:
                             processed_item['sentiment'] = item.get('sentiment_score')
                        
                        # entities와 named_entities 구분 저장
                        if 'named_entities' not in processed_item:
                             processed_item['named_entities'] = []
                        if 'entities' not in processed_item:
                             processed_item['entities'] = []

                        all_processed_data.append(processed_item)
                    
                    # 다음 페이지 확인
                    total_pages = response.get('total_pages', 0)
                    if page >= total_pages:
                        break
                    
                    page += 1
                    
                return all_processed_data
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Error fetching news for {symbol}: {e}")
                    return []
                await asyncio.sleep(2 ** attempt)
        return []

def chunk_date_range(start_date: datetime.date, end_date: datetime.date, years: int = 1):
    """주어진 날짜 범위를 n년 단위로 분할"""
    current = start_date
    while current <= end_date:
        next_date = current + datetime.timedelta(days=365 * years)
        chunk_end = min(next_date - datetime.timedelta(days=1), end_date)
        if current > chunk_end:
            break
        yield current, chunk_end
        current = chunk_end + datetime.timedelta(days=1)

async def prepare_news_data(
    symbols: Optional[List[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    cache_dir: str = ".cache/market_data_v2",
    concurrency: int = 10,
    force_refresh: bool = False,
    flush: bool = False,
    verbose: bool = True,
    save_raw_response: bool = False,
    raw_response_dir: Optional[str] = None,
    **kwargs
) -> MarketDataCache:
    """
    뉴스 데이터 준비 메인 함수
    
    Args:
        symbols: 조회할 티커 리스트 (Optional)
        date_from: 시작 날짜 (YYYY-MM-DD)
        date_to: 종료 날짜 (YYYY-MM-DD)
        cache_dir: 캐시 디렉토리
        concurrency: 동시 요청 수
        force_refresh: 캐시 무시하고 새로 요청 여부
        flush: 기존 캐시 파일을 삭제하고 처음부터 다시 시작할지 여부
        verbose: 상세 로그 출력 여부 (기본값: True)
        save_raw_response: 원본 JSON 응답 저장 여부
        raw_response_dir: 원본 저장 경로
        **kwargs: 추가 검색 파라미터 (keyword, company_name, highlight, clustering, uniquify, order, research_insight)
    """
    if date_from is None or date_to is None:
        raise ValueError("date_from and date_to must be provided")

    # Flush 처리: 캐시 디렉토리 내 데이터 파일 삭제
    if flush:
        import shutil
        cache_path = Path(cache_dir)
        if cache_path.exists():
            if verbose:
                logger.warning(f"Flush requested. Deleting cache directory: {cache_dir}")
            try:
                shutil.rmtree(cache_path)
            except Exception as e:
                logger.error(f"Failed to delete cache directory: {e}")

    cache = MarketDataCache(cache_dir)
    
    client = DeepSearchClient()
    semaphore = asyncio.Semaphore(concurrency)
    
    date_to_dt = pd.to_datetime(date_to).date()
    date_from_dt = pd.to_datetime(date_from).date()
    
    symbols_to_fetch = []
    
    # [변경] 심볼 리스트가 없으면 None을 포함한 리스트 생성 (1회 실행용)
    if not symbols:
        target_iterator = [None]
        # 캐시 키로 사용할 식별자 (키워드)
        identifier = kwargs.get('keyword')
        if verbose:
            logger.info(f"Checking news cache for keyword: '{identifier}'...")
    else:
        target_iterator = symbols
        if verbose:
            logger.info(f"Checking news cache for {len(symbols)} symbols...")
    
    for symbol in target_iterator:
        fetch_start = date_from_dt
        
        # 캐시 체크: 심볼이 있으면 심볼 기준, 없으면 키워드 기준
        # Store API 변경에 맞춰 호출 (symbol 또는 keyword)
        cache_key_keyword = kwargs.get('keyword')
        
        if not force_refresh:
            if symbol:
                last_date = cache.get_last_news_date(symbol=symbol)
            elif cache_key_keyword:
                last_date = cache.get_last_news_date(keyword=cache_key_keyword)
            else:
                last_date = None
            
            if last_date:
                if last_date >= date_to_dt:
                    continue
                fetch_start = max(date_from_dt, last_date + datetime.timedelta(days=1))
        
        if fetch_start > date_to_dt:
            continue
            
        symbols_to_fetch.append((symbol, fetch_start.strftime("%Y-%m-%d")))
    
    if not symbols_to_fetch:
        if verbose:
            logger.info("All news data is up to date.")
        return cache
    
    if verbose:
        logger.info(f"Fetching news for {len(symbols_to_fetch)} items...")
    
    async with client:
        fetch_tasks = []
        for symbol, start_date in symbols_to_fetch:
            # 1년 단위 청킹 적용
            task_start_dt = pd.to_datetime(start_date).date()
            task_end_dt = date_to_dt
            
            for chunk_start, chunk_end in chunk_date_range(task_start_dt, task_end_dt):
                fetch_tasks.append(
                    fetch_symbol_news(
                        client, 
                        symbol, 
                        chunk_start.strftime("%Y-%m-%d"), 
                        chunk_end.strftime("%Y-%m-%d"), 
                        semaphore, 
                        save_raw_response=save_raw_response,
                        raw_response_dir=raw_response_dir,
                        **kwargs
                    )
                )
            
        # results = await asyncio.gather(*fetch_tasks)
        results = []
        
        # tqdm 설정: verbose가 True일 때만 표시
        iterator = tqdm.as_completed(fetch_tasks, total=len(fetch_tasks), desc="Fetching News") if verbose else asyncio.as_completed(fetch_tasks)
        
        for f in iterator:
            res = await f
            results.append(res)
        
        all_new_data = []
        for res in results:
            all_new_data.extend(res)
            
        if all_new_data:
            if verbose:
                logger.info(f"Fetched {len(all_new_data)} news items. Updating cache...")
            cache.update_news_data(all_new_data)
            cache.save()
            if verbose:
                logger.info("News cache saved.")
        else:
            if verbose:
                logger.info("No new news fetched.")
            
    return cache

async def collect_news_frozen(
    target_symbols: list, 
    start_date: str, 
    end_date: str, 
    base_cache_dir: str = ".cache/news_data_kr_batches",
    batch_size: int = 50,
    concurrency: int = 10,
    verbose: bool = True,
    save_raw_response: bool = False,
    raw_response_dir: Optional[str] = None,
    # 요구사항 4: 파라미터 추가
    keyword: Optional[str] = None,
    company_name: Optional[str] = None,
    highlight: Optional[str] = None,
    clustering: Optional[bool] = None,
    uniquify: Optional[bool] = True,
    order: Optional[str] = None,
    research_insight: Optional[bool] = False,
    **kwargs
):
    """
    대용량 뉴스 데이터 고정 수집 함수 (기존 파일이 있으면 건너뜀)
    이전 이름: collect_news_safe
    
    Args:
        target_symbols: 수집할 종목 코드 리스트
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        base_cache_dir: 데이터를 저장할 기본 디렉토리
        batch_size: 한 번에 처리할 종목 수 (기본값: 50)
        concurrency: 동시 요청 수 (기본값: 10)
        verbose: 진행 상황 출력 여부
        save_raw_response: 원본 응답 저장 여부
        raw_response_dir: 원본 저장 경로
        keyword: 검색 키워드
        company_name: 회사 이름
        highlight: 하이라이트 타입
        clustering: 클러스터링 여부
        uniquify: 중복 제거 여부
        order: 정렬 기준
        research_insight: 증권사 리포트 인사이트 포함 여부
    """
    if verbose:
        print("=== Frozen News Data Collection Start ===")
        print(f"Total Targets: {len(target_symbols)} symbols")
        print(f"Period: {start_date} ~ {end_date}")
        print(f"Batch Size: {batch_size}")
    
    BASE_DIR = Path(base_cache_dir)
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 임시 작업 폴더 (각 배치마다 비우고 다시 씀)
    TEMP_DIR = BASE_DIR / "temp_worker"
    
    total_batches = (len(target_symbols) + batch_size - 1) // batch_size
    
    iterator = range(0, len(target_symbols), batch_size)
    if verbose:
        iterator = tqdm(
            iterator, 
            total=total_batches, 
            desc="Overall Progress",
            unit="batch"
        )
    
    # API 파라미터 묶음
    api_params = {
        "keyword": keyword,
        "company_name": company_name,
        "highlight": highlight,
        "clustering": clustering,
        "uniquify": uniquify,
        "order": order,
        "research_insight": research_insight,
        **kwargs
    }

    for i in iterator:
        batch_symbols = target_symbols[i : i + batch_size]
        batch_num = (i // batch_size) + 1
        
        # 배치 결과 파일명 (0001, 0002... 형태로 정렬 용이하게)
        batch_file = BASE_DIR / f"news_batch_{batch_num:04d}.parquet"
        
        if batch_file.exists():
            if verbose:
                # tqdm 환경에서 print 대신 write 사용
                tqdm.write(f"Batch {batch_num}/{total_batches} already exists. Skipping...")
            continue
            
        if verbose:
            tqdm.write(f"\nProcessing Batch {batch_num}/{total_batches} ({len(batch_symbols)} symbols)...")
        
        try:
            # 1. 해당 배치만 수집 (flush=True로 매번 깨끗한 상태에서 시작)
            # 이렇게 하면 이전 배치의 데이터가 메모리에 남지 않음
            temp_cache = await prepare_news_data(
                batch_symbols, 
                start_date, 
                end_date, 
                cache_dir=str(TEMP_DIR),
                concurrency=concurrency,
                force_refresh=True,  # 배치 내에서는 새로 받음
                flush=True,          # 임시 폴더 초기화 (메모리/디스크 절약 핵심)
                verbose=False,       # 내부 로그는 끄기
                save_raw_response=save_raw_response,
                raw_response_dir=raw_response_dir,
                **api_params
            )
            
            # 2. 결과 저장 (데이터가 있을 경우에만)
            if not temp_cache.news_data.empty:
                # 필요한 컬럼만 선택하여 용량 최적화 (선택 사항)
                # temp_cache.news_data = temp_cache.news_data[['date', 'symbol', 'title', ...]]
                temp_cache.news_data.to_parquet(batch_file, index=False)
                if verbose:
                    tqdm.write(f"Saved: {batch_file} ({len(temp_cache.news_data)} rows)")
            else:
                # 데이터가 없어도 빈 파일 생성하여 재시도 방지 (필요 시 주석 처리)
                # 빈 데이터프레임 생성 (컬럼 구조 유지)
                # 모든 필드를 저장하므로 컬럼 정의를 유연하게 하거나, 대표 컬럼만 지정
                empty_df = pd.DataFrame(columns=['date', 'symbol', 'title', 'provider', 'url', 'sentiment', 'summary', 'entities'])
                empty_df.to_parquet(batch_file, index=False)
                if verbose:
                    tqdm.write(f"Saved empty batch: {batch_file}")
            
            # 3. 메모리 명시적 해제
            del temp_cache
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error in Batch {batch_num}: {e}")
            if verbose:
                tqdm.write(f"Error in Batch {batch_num}: {e}")
            # 에러 발생 시 해당 배치는 건너뛰고 다음으로 진행
            continue
            
    if verbose:
        print("\n=== Collection Completed ===")
        print(f"All batches saved in: {BASE_DIR}")
        print("To load all data: pd.concat([pd.read_parquet(f) for f in Path(BASE_DIR).glob('*.parquet')])")


def load_and_preprocess_news(base_dir, sections=None, vendors=None, date_from=None, date_to=None):
    """
    저장된 뉴스 데이터(parquet)를 로드하고 필터링합니다. (Progress bar 추가)
    """
    import glob
    from tqdm import tqdm
    
    # 기본 섹션 설정
    if sections is None:
        sections = ['economy']
        
    # glob을 사용하여 파일 목록 가져오기
    files = glob.glob(f"{base_dir}/*.parquet")

    dfs = []
    # [수정] tqdm을 사용하여 파일 로딩 진행률 표시
    for f in tqdm(files, desc="Loading News Parquet Files", unit="file"):
        sub_df = pd.read_parquet(f)
        
        # 섹션 필터링
        if sections:
            mask_sections = sub_df['sections'].apply(lambda x: list(x) == sections if x is not None else False)
            sub_df = sub_df[mask_sections]
            
        # 언론사 필터링
        if vendors is not None:
            sub_df = sub_df[sub_df['publisher'].isin(vendors)]
            
        # 날짜 필터링
        if date_from is not None:
            date_from_dt = pd.to_datetime(date_from)
            sub_df = sub_df[sub_df['date'] >= date_from_dt]
        if date_to is not None:
            date_to_dt = pd.to_datetime(date_to)
            sub_df = sub_df[sub_df['date'] <= date_to_dt]
            
        dfs.append(sub_df)

    if not dfs:
        return pd.DataFrame()

    # [수정된 부분]
    final_df = pd.concat(dfs, ignore_index=True)
    if 'date' in final_df.columns:
        final_df['date'] = pd.to_datetime(final_df['date']).apply(lambda x: x.strftime('%Y-%m-%d'))
        final_df['date'] = pd.to_datetime(final_df['date'])
    return final_df

def filter_news_by_symbol(df, target_tickers):
    """
    뉴스 데이터프레임에서 특정 심볼이 포함된 뉴스만 필터링합니다.
    """
    import numpy as np
    
    target_set = set(target_tickers)
    
    def has_target_symbol(companies_list):
        if not isinstance(companies_list, list) and not isinstance(companies_list, np.ndarray):
            return False
        # company dict 내 'symbol' 키 확인
        return any(company.get('symbol') in target_set for company in companies_list)
        
    return df[df['companies'].apply(has_target_symbol)]

def split_news_by_session(df: pd.DataFrame, date_col: str = 'published_at'):
    """
    뉴스 데이터프레임을 시간대에 따라 Intraday, Aftermarket, Overnight으로 분리합니다.
    
    Args:
        df (pd.DataFrame): 뉴스 데이터프레임
        date_col (str): 날짜/시간 정보가 담긴 컬럼명 (기본값: 'published_at')
        
    Returns:
        tuple: (df_intraday, df_aftermarket, df_overnight)
    """
    if df.empty:
        return df, df, df

    # 원본 데이터 보존을 위해 복사
    temp_df = df.copy()
    
    # datetime 형식으로 변환
    if not pd.api.types.is_datetime64_any_dtype(temp_df[date_col]):
        temp_df[date_col] = pd.to_datetime(temp_df[date_col], errors='coerce')
    
    # 시간 비교를 위한 기준 시간 설정
    t_start = datetime.time(9, 0, 0)
    t_close = datetime.time(15, 30, 0)
    t_night = datetime.time(20, 30, 0)
    
    def get_session_label(dt):
        if pd.isna(dt):
            return 'unknown'
        t = dt.time()
        # 09:00 <= t < 15:30 -> Intraday
        if t_start <= t < t_close:
            return 'intraday'
        # 15:30 <= t < 20:30 -> Aftermarket
        elif t_close <= t < t_night:
            return 'aftermarket'
        # 나머지 -> Overnight
        else:
            return 'overnight'
            
    # 세션 라벨링
    temp_df['session'] = temp_df[date_col].apply(get_session_label)
    # temp_df = temp_df[['id', 'sections', 'title', 'publisher', 'summary','companies','entities','named_entities','published_at','date', 'symbol']]
    temp_df['date'] = pd.to_datetime(temp_df['date']).apply(lambda x: x.strftime('%Y-%m-%d'))
    temp_df['date'] = pd.to_datetime(temp_df['date'])
    
    # 데이터프레임 분리
    df_intraday = temp_df[temp_df['session'] == 'intraday'].drop(columns=['session'])
    df_aftermarket = temp_df[temp_df['session'] == 'aftermarket'].drop(columns=['session'])
    df_overnight = temp_df[temp_df['session'] == 'overnight'].drop(columns=['session'])
    

    return df_intraday, df_aftermarket, df_overnight

async def collect_news_liquid(
    target_symbols: list, 
    start_date: str, 
    end_date: Optional[str] = None, 
    base_cache_dir: str = ".cache/news_data_kr_batches",
    batch_size: int = 50,
    concurrency: int = 10,
    verbose: bool = True,
    save_raw_response: bool = False,
    raw_response_dir: Optional[str] = None,
    # 요구사항 4: 파라미터 추가
    keyword: Optional[str] = None,
    company_name: Optional[str] = None,
    highlight: Optional[str] = None,
    clustering: Optional[bool] = None,
    uniquify: Optional[bool] = True,
    order: Optional[str] = None,
    research_insight: Optional[bool] = False,
    **kwargs
):
    """
    대용량 뉴스 데이터 유동 수집 함수 (증분 업데이트 지원)
    기존 데이터가 있으면 마지막 날짜부터 이어서 수집합니다.
    주의: 마지막 날짜(Last Date)에 해당하는 데이터는 중복 방지를 위해 기존 파일에서 삭제하고 재수집합니다.
    
    Args:
        target_symbols: 수집할 종목 코드 리스트
        start_date: (기존 파일이 없을 경우) 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD). None 입력 시 오늘 날짜 사용.
        base_cache_dir: 데이터를 저장할 기본 디렉토리
        batch_size: 한 번에 처리할 종목 수 (기본값: 50)
        concurrency: 동시 요청 수 (기본값: 10)
        verbose: 진행 상황 출력 여부
        save_raw_response: 원본 응답 저장 여부
        raw_response_dir: 원본 저장 경로
        keyword: 검색 키워드
        company_name: 회사 이름
        highlight: 하이라이트 타입
        clustering: 클러스터링 여부
        uniquify: 중복 제거 여부
        order: 정렬 기준
        research_insight: 증권사 리포트 인사이트 포함 여부
    """
    if end_date is None:
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")

    if verbose:
        print("=== Liquid News Data Collection Start (Incremental Update) ===")
        print(f"Total Targets: {len(target_symbols)} symbols")
        print(f"Period: ~ {end_date}")
        print(f"Batch Size: {batch_size}")
    
    BASE_DIR = Path(base_cache_dir)
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 임시 작업 폴더
    TEMP_DIR = BASE_DIR / "temp_worker_liquid"
    
    total_batches = (len(target_symbols) + batch_size - 1) // batch_size
    
    iterator = range(0, len(target_symbols), batch_size)
    if verbose:
        iterator = tqdm(
            iterator, 
            total=total_batches, 
            desc="Overall Progress",
            unit="batch"
        )
    
    # API 파라미터 묶음
    api_params = {
        "keyword": keyword,
        "company_name": company_name,
        "highlight": highlight,
        "clustering": clustering,
        "uniquify": uniquify,
        "order": order,
        "research_insight": research_insight,
        **kwargs
    }

    for i in iterator:
        batch_symbols = target_symbols[i : i + batch_size]
        batch_num = (i // batch_size) + 1
        
        batch_file = BASE_DIR / f"news_batch_{batch_num:04d}.parquet"
        
        existing_df = pd.DataFrame()
        current_start_date = start_date
        
        # 1. 기존 파일 확인 및 로드
        if batch_file.exists():
            try:
                existing_df = pd.read_parquet(batch_file)
                if not existing_df.empty:
                    # 마지막 날짜 확인
                    # date 컬럼은 보통 문자열 YYYY-MM-DD (하지만 이제는 시분초 포함됨)
                    if 'date' in existing_df.columns:
                        last_date_val = existing_df['date'].max()
                        
                        # Timestamp를 문자열로 변환 (시분초 포함)
                        if isinstance(last_date_val, pd.Timestamp):
                            last_date_full_str = last_date_val.strftime('%Y-%m-%d %H:%M:%S')
                            last_date_day_str = last_date_val.strftime('%Y-%m-%d')
                        else:
                            last_date_full_str = str(last_date_val)
                            # 문자열이 YYYY-MM-DDTHH:MM:SS 형식이면 앞 10자리만
                            last_date_day_str = last_date_full_str[:10]
                        
                        # 마지막 날짜의 데이터 삭제 (시간 이슈 커버를 위해 재수집)
                        # 여기서는 시분초를 포함한 전체 문자열 비교가 아닌, '날짜(Day)' 기준으로 삭제해야 함
                        # 왜냐하면 그 날의 나머지 데이터가 추가되었을 수 있으므로 그 날 전체를 다시 받는 게 안전함.
                        
                        # 날짜 부분만 추출하여 비교
                        # pandas 벡터화 연산 사용
                        existing_df['temp_date_str'] = existing_df['date'].astype(str).str[:10]
                        existing_df = existing_df[existing_df['temp_date_str'] != last_date_day_str]
                        existing_df = existing_df.drop(columns=['temp_date_str'])
                        
                        # 수집 시작일을 마지막 날짜로 설정
                        current_start_date = last_date_day_str
                        
                        if verbose:
                            tqdm.write(f"Batch {batch_num}: Resuming from {current_start_date} (Overwrite last date)")
                    else:
                        # date 컬럼 없으면 처음부터
                        current_start_date = start_date
            except Exception as e:
                tqdm.write(f"Error reading batch {batch_num}: {e}. Starting fresh.")
                existing_df = pd.DataFrame()
                current_start_date = start_date
        
        # 수집 기간 유효성 체크
        if current_start_date > end_date:
            if verbose:
                tqdm.write(f"Batch {batch_num} is already up to date ({current_start_date} > {end_date}). Skipping...")
            continue
            
        if verbose:
            tqdm.write(f"\nProcessing Batch {batch_num}/{total_batches} ({len(batch_symbols)} symbols) | {current_start_date} ~ {end_date}")
        
        try:
            # 2. 부족한 기간 수집 (flush=True로 임시 폴더 초기화)
            temp_cache = await prepare_news_data(
                batch_symbols, 
                current_start_date, 
                end_date, 
                cache_dir=str(TEMP_DIR),
                concurrency=concurrency,
                force_refresh=True,  
                flush=True,          
                verbose=False,
                save_raw_response=save_raw_response,
                raw_response_dir=raw_response_dir,
                **api_params
            )
            
            new_data = temp_cache.news_data
            
            # 3. 병합 및 저장
            final_df = existing_df
            if not new_data.empty:
                if not existing_df.empty:
                    # 컬럼 순서 맞추기 (혹시 다를 수 있으므로)
                    final_df = pd.concat([existing_df, new_data], ignore_index=True)
                else:
                    final_df = new_data
                    
                # 중복 제거 (혹시 모를 안전장치: 종목+날짜+제목+언론사)
                # final_df = final_df.drop_duplicates(subset=['symbol', 'date', 'title', 'provider'])
                
                final_df.to_parquet(batch_file, index=False)
                
                if verbose:
                    tqdm.write(f"Saved: {batch_file} (Total {len(final_df)} rows, Added {len(new_data)} rows)")
            else:
                # 새로운 데이터가 없을 때
                if existing_df.empty:
                     # 아예 데이터가 없으면 빈 파일 생성
                    empty_df = pd.DataFrame(columns=['date', 'symbol', 'title', 'provider', 'url', 'sentiment', 'summary', 'entities'])
                    empty_df.to_parquet(batch_file, index=False)
                    if verbose:
                        tqdm.write(f"Saved empty batch: {batch_file}")
                else:
                    # 기존 데이터는 있지만 새 데이터가 없는 경우 (재수집한 마지막 날짜 데이터가 없을 수도 있음)
                    # 삭제했던 마지막 날짜 데이터를 복구할 방법은 없으므로 (이미 삭제됨), 
                    # 만약 API가 데이터를 안 주면 그 날짜 데이터는 비게 됨.
                    # 하지만 API가 정상이면 줘야 함. 
                    # 그냥 저장.
                    existing_df.to_parquet(batch_file, index=False)
                    if verbose:
                        tqdm.write(f"Updated: {batch_file} (Total {len(existing_df)} rows, No new data)")

            # 4. 메모리 정리
            del temp_cache, existing_df, new_data, final_df
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error in Batch {batch_num}: {e}")
            if verbose:
                tqdm.write(f"Error in Batch {batch_num}: {e}")
            continue
            
    if verbose:
        print("\n=== Collection Completed ===")
        print(f"All batches saved in: {BASE_DIR}")
