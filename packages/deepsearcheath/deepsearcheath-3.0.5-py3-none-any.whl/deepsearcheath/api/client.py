import os
import aiohttp
import pandas as pd
from typing import Optional, Dict, Any, List, Union

class DeepSearchClient:
    """
    DeepSearch API Async Client
    """
    BASE_URL = "https://api-v2.deepsearch.com"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DeepSearch client.
        :param api_key: DeepSearch API Key. If not provided, it looks for DEEPSEARCH_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("DEEPSEARCH_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEARCH_API_KEY environment variable is not set")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """
        Context manager entry. Creates a persistent session.
        """
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit. Closes the session.
        """
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Internal request helper.
        Uses existing session if available, otherwise creates a temporary one.
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # Use existing session if in context manager
        if self.session:
            async with self.session.request(method, url, **kwargs) as response:
                if not response.ok:
                    error_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=f"{response.reason}, body={error_text}",
                        headers=response.headers
                    )
                return await response.json()
        
        # Create temporary session if not in context manager
        async with aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        ) as session:
            async with session.request(method, url, **kwargs) as response:
                if not response.ok:
                    error_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=f"{response.reason}, body={error_text}",
                        headers=response.headers
                    )
                return await response.json()

    async def get_articles(
        self,
        keyword: Optional[str] = None,
        company_name: Optional[str] = None,
        symbols: Optional[Union[str, List[str]]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        highlight: Optional[str] = None,
        clustering: Optional[bool] = None,
        uniquify: Optional[bool] = True,
        order: Optional[str] = None,
        research_insight: Optional[bool] = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        국내 뉴스 검색 (GET /v1/articles)
        
        :param keyword: 검색 키워드 (예: '전기차', 'title:(삼성전자 AND 구글)')
        :param company_name: 회사 이름 (예: '삼성전자')
        :param symbols: 기업/ETF 종목코드 (문자열 또는 리스트, 예: 'KRX:005930')
        :param date_from: 시작일 (YYYY-MM-DD)
        :param date_to: 종료일 (YYYY-MM-DD)
        :param page: 페이지 번호 (기본값: 1)
        :param page_size: 페이지 당 아이템 수 (기본값: 10)
        :param highlight: 하이라이트 타입 ('plain', 'unified', 'unified_non_tags')
        :param clustering: 클러스터링 여부
        :param uniquify: 중복 제거 여부 (기본값: True)
        :param order: 정렬 기준 ('score', 'published_at')
        :param research_insight: 증권사 리포트 인사이트 포함 여부
        :return: 뉴스 검색 결과 JSON
        """
        params = {
            "page": page,
            "page_size": page_size,
            **kwargs
        }

        # 모든 파라미터 값을 문자열로 변환 (aiohttp 호환성 확보)
        for k, v in params.items():
            if isinstance(v, bool):
                params[k] = str(v).lower()

        if keyword:
            params["keyword"] = keyword
            
        if company_name:
            params["company_name"] = company_name

        if symbols:
            if isinstance(symbols, list):
                params["symbols"] = ",".join(symbols)
            else:
                params["symbols"] = symbols

        if date_from:
            params["date_from"] = date_from
            
        if date_to:
            params["date_to"] = date_to

        if highlight:
            params["highlight"] = highlight

        if clustering is not None:
            params["clustering"] = str(clustering).lower()

        if uniquify is not None:
            params["uniquify"] = str(uniquify).lower()
            
        if order:
            params["order"] = order

        if research_insight is not None:
            params["research_insight"] = str(research_insight).lower()

        return await self._request("GET", "/v1/articles", params=params)

    async def aggregate_articles(
        self,
        keyword: str = "*",
        company_name: Optional[str] = None,
        symbols: Optional[Union[str, List[str]]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        groupby: Optional[str] = None,
        size: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        국내 뉴스 집계 (GET /v1/articles/aggregation)

        :param keyword: 검색 키워드 (기본값: "*")
        :param company_name: 회사 이름
        :param symbols: 종목코드 (문자열 또는 리스트)
        :param date_from: 시작 날짜 (YYYY-MM-DD)
        :param date_to: 종료 날짜 (YYYY-MM-DD)
        :param groupby: 그룹화 기준 (예: 'companies.name', 'publisher')
        :param size: 가져올 데이터 수 (기본값: 100, 최대 10000)
        :return: 뉴스 집계 결과 JSON
        """
        params = {
            "keyword": keyword,
            "size": size,
            **kwargs
        }
        
        # 모든 파라미터 값을 문자열로 변환 (aiohttp 호환성 확보)
        for k, v in params.items():
            if isinstance(v, bool):
                params[k] = str(v).lower()
        
        if company_name:
            params["company_name"] = company_name

        if symbols:
            if isinstance(symbols, list):
                params["symbols"] = ",".join(symbols)
            else:
                params["symbols"] = symbols

        if date_from:
            params["date_from"] = date_from
            
        if date_to:
            params["date_to"] = date_to

        if groupby:
            params["groupby"] = groupby

        return await self._request("GET", "/v1/articles/aggregation", params=params)

    async def get_companies(
        self,
        country_code: str = "us",
        page: int = 1,
        page_size: int = 10000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        회사 목록 조회 (국내, 미국) (GET /v2/companies)

        :param country_code: 국가 코드 ('kr', 'us')
        :param page: 페이지 번호
        :param page_size: 페이지 당 아이템 수 (최대 10000)
        :return: 회사 목록 JSON
        """
        params = {
            "country_code": country_code,
            "page": page,
            "page_size": page_size,
            **kwargs
        }
        
        # 모든 파라미터 값을 문자열로 변환 (aiohttp 호환성 확보)
        for k, v in params.items():
            if isinstance(v, bool):
                params[k] = str(v).lower()
                
        return await self._request("GET", "/v2/companies", params=params)

    async def get_stock_price(
        self,
        symbol: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1,
        page_size: int = 10000,
        period: Optional[str] = None,
        delay: bool = False,
        include_trading_halted: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        단일 주식 조회 (국내, 미국) (GET /v2/companies/{symbol}/stock)

        :param symbol: 종목 코드 (예: 'NASDAQ:AAPL', '005930')
        :param date_from: 시작 날짜 (YYYY-MM-DD)
        :param date_to: 종료 날짜 (YYYY-MM-DD)
        :param page: 페이지 번호
        :param page_size: 페이지 당 아이템 수 (최대 10000)
        :param period: 기간
        :param delay: 요청 딜레이 시간 (기본값: False)
        :param include_trading_halted: 거래정지 포함 여부 (기본값: False)
        :return: 주식 데이터 JSON
        """
        params = {
            "page": page,
            "page_size": page_size,
            "delay": str(delay).lower(),
            "include_trading_halted": str(include_trading_halted).lower(),
            **kwargs
        }
        
        # 모든 파라미터 값을 문자열로 변환 (aiohttp 호환성 확보)
        for k, v in params.items():
            if isinstance(v, bool):
                params[k] = str(v).lower()
        
        if date_from:
            params["date_from"] = date_from
        
        if date_to:
            params["date_to"] = date_to
            
        if period:
            params["period"] = period

        # symbol에 특수문자나 공백이 있을 수 있으므로 URL 인코딩은 aiohttp가 처리하지만,
        # path parameter로 들어가는 symbol은 직접 처리해주는 것이 안전할 수 있음.
        # 여기서는 aiohttp에 맡기되, endpoint 문자열 포맷팅 사용.
        return await self._request("GET", f"/v2/companies/{symbol}/stock", params=params)


class KRXClient:
    """
    KRX Open API Async Client
    """
    BASE_URL = "https://data-dbg.krx.co.kr"
    # BASE_URL = "https://data.krx.co.kr" 


    def __init__(self, auth_key: Optional[str] = None):
        """
        Initialize the KRX client.
        :param auth_key: KRX API Key. If not provided, it looks for KRX_API_KEY env var.
        """
        self.auth_key = auth_key or os.getenv("KRX_API_KEY")
        if not self.auth_key:
            raise ValueError("KRX_API_KEY environment variable is not set")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """
        Context manager entry. Creates a persistent session.
        """
        self.session = aiohttp.ClientSession(
            headers={
                "AUTH_KEY": self.auth_key,
                "Content-Type": "application/json"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit. Closes the session.
        """
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Internal request helper.
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        if self.session:
            async with self.session.request(method, url, **kwargs) as response:
                if not response.ok:
                    error_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=f"{response.reason}, body={error_text}",
                        headers=response.headers
                    )
                return await response.json()
        
        async with aiohttp.ClientSession(
            headers={
                "AUTH_KEY": self.auth_key,
                "Content-Type": "application/json"
            }
        ) as session:
            async with session.request(method, url, **kwargs) as response:
                if not response.ok:
                    error_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=f"{response.reason}, body={error_text}",
                        headers=response.headers
                    )
                return await response.json()

    async def get_stock_daily_trade_info(self, bas_dd: str) -> Dict[str, Any]:
        """
        유가증권 일별매매정보 (stk_bydd_trd)
        
        :param bas_dd: 기준일자 (YYYYMMDD, 8자리 문자열)
        :return: 유가증권 일별매매정보 JSON (OutBlock_1 포함)
        """
        params = {
            "basDd": bas_dd
        }
        return await self._request("GET", "/svc/apis/sto/stk_bydd_trd", params=params)

    async def get_kosdaq_daily_trade_info(self, bas_dd: str) -> Dict[str, Any]:
        """
        코스닥 일별매매정보 (ksq_bydd_trd)
        
        :param bas_dd: 기준일자 (YYYYMMDD, 8자리 문자열)
        :return: 코스닥 일별매매정보 JSON (OutBlock_1 포함)
        """
        params = {
            "basDd": bas_dd
        }
        return await self._request("GET", "/svc/apis/sto/ksq_bydd_trd", params=params)

