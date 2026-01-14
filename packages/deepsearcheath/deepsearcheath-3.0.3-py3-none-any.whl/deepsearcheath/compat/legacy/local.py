import requests
from datetime import datetime
import time
import os
import asyncio
import aiohttp
import FinanceDataReader as fdr
from pandas_datareader import data as pdr

import pandas as pd
import numpy as np

from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

from dateutil.relativedelta import relativedelta

load_dotenv(verbose=True)


class asyncDeepSearchAPI(object):
    _COMPUTE_API = "{}/v1/compute".format('https://api.deepsearch.com')
    _AUTH_ID = os.getenv('_AUTH_ID')
    _AUTH_PW = os.getenv('_AUTH_PW')
    _AUTH = HTTPBasicAuth(_AUTH_ID, _AUTH_PW)
    
    @classmethod
    async def compute(cls, query, locale='ko_KR'):
        params = {
            'input': query,
            'locale': locale
        } 
        _count = 0
        while True:
            try:
                async with aiohttp.ClientSession() as sess:

                    async with sess.post( url=cls._COMPUTE_API, auth=aiohttp.BasicAuth(cls._AUTH_ID, cls._AUTH_PW), data=params, timeout=120 ) as co_resp:
                        response_json = await co_resp.json()
                        if (co_resp.status != 200) or (not response_json['success']):
                            try:
                                print("Response code, Success status:", co_resp.status, response_json['success'])
                            except:
                                print(response_json)
                            print("Exception query log:", query)
                            print(response_json)
                            return None

                        pods = response_json['data']['pods']  # pods[0]: input

                        if pods[1]['class'] == 'Result:DataFrame':
                            data    =    pods[1]['content']['data']
                            index   =   pods[1]['content']['index']
                            dtypes  =  pods[1]['content']['dtypes']
                            columns = pods[1]['content']['columns']

                            results = []

                            no_obs = len(data[columns[0]])
                            for i in range(no_obs):
                                item = dict()
                                for col in columns:
                                    item[col] = data[col][i]
                                results.append(item)

                            df_results = pd.DataFrame(results)

                            if df_results.empty:
                                return None

                            for col in dtypes.keys():  # pyarrow converting
                                # df_results[col] = df_results[col].astype(dtypes[col])
                                
                                if dtypes[col] == 'datetime64':
                                    df_results[col] = pd.to_datetime(df_results[col], errors='coerce')
                                else:
                                    df_results[col] = df_results[col].astype(dtypes[col])  # pandas 1.5.3 

                            df_results = df_results.set_index(index)  # 'symbol'
                            df_results = df_results.sort_index()

                            return df_results

                        elif pods[1]['class'] == 'Result:DocumentTrendsResult':
                            data    =    pods[1]['content']['data']
                            trends  =   pods[1]['content']['data']['trends']
                            total_matches = trends[0]['total_matches']
                            buckets = trends[0]['buckets']

                            df_results = pd.DataFrame(buckets)
                            
                            return df_results

                        else:
                            return pods[1]['content']
            
            except Exception as e:
                print("Exception query log:", query)
                print(e)
                _count += 1
                if _count > 5:
                    return [None]
                time.sleep(5)
                continue



class asyncDeepSearchAPI_mk2(object):
    _COMPUTE_API = "{}/v1/compute".format('https://api.deepsearch.com')
    _AUTH_ID = os.getenv('_AUTH_ID')
    _AUTH_PW = os.getenv('_AUTH_PW')
    _AUTH = HTTPBasicAuth(_AUTH_ID, _AUTH_PW)
    
    @classmethod
    async def compute(cls, query, locale='ko_KR', timeout=120, max_count=5, sentiment=False, verbose=False):
        """
        queries = [
            deepsearch_async.compute(f"{ticker} 시가총액 2000-2025") 
            for ticker in all_df["티커"].unique()
        ]

        async def main(queries):
            results = []
            for coro in tqdm.tqdm(asyncio.as_completed(queries), total=len(queries)):
                result = await coro
                results.append(result)
            return results

        import asyncio
        asyncio.run(main(queries))
        """
        params = {
            'input': query,
            'locale': locale
        } 
        _count = 0
        retry = False
        while True:
            try:
                async with aiohttp.ClientSession() as sess:

                    async with sess.post( url=cls._COMPUTE_API, auth=aiohttp.BasicAuth(cls._AUTH_ID, cls._AUTH_PW), data=params, timeout=timeout ) as co_resp:
                        response_json = await co_resp.json()
                        if (co_resp.status != 200) or (not response_json['success']):
                            if verbose:
                                print("Response code, Success status:", co_resp.status, response_json['success'])
                            if sentiment:
                                raise Exception("Response code, Success status:", co_resp.status, response_json['success'])
                            
                            raise Exception("Exception query log:", query)
                            return None, query
                            return None

                        pods = response_json['data']['pods']  # pods[0]: input

                        if pods[1]['class'] == 'Result:DataFrame':
                            data    =    pods[1]['content']['data']
                            index   =   pods[1]['content']['index']
                            dtypes  =  pods[1]['content']['dtypes']
                            columns = pods[1]['content']['columns']

                            results = []

                            no_obs = len(data[columns[0]])
                            for i in range(no_obs):
                                item = dict()
                                for col in columns:
                                    item[col] = data[col][i]
                                results.append(item)

                            df_results = pd.DataFrame(results)

                            if df_results.empty:
                                if verbose:
                                    print("Empty DataFrame:", query)
                                return None, query
                                return None

                            for col in dtypes.keys():  # pyarrow converting
                                # df_results[col] = df_results[col].astype(dtypes[col])
                                
                                if dtypes[col] == 'datetime64':
                                    df_results[col] = pd.to_datetime(df_results[col], errors='coerce')
                                else:
                                    df_results[col] = df_results[col].astype(dtypes[col])  # pandas 1.5.3 

                            df_results = df_results.set_index(index)  # 'symbol'
                            df_results = df_results.sort_index()

                            if verbose:
                                if retry: print("retry success")
                            return df_results, query
                            return df_results

                        elif pods[1]['class'] == 'Result:DocumentTrendsResult':
                            data    =    pods[1]['content']['data']
                            trends  =   pods[1]['content']['data']['trends']
                            total_matches = trends[0]['total_matches']
                            buckets = trends[0]['buckets']

                            df_results = pd.DataFrame(buckets)
                            
                            if verbose:
                                if retry: print("retry success")
                            return df_results, query
                            return df_results

                        else:
                            if verbose:
                                if retry: print("retry success")
                            return pods[1]['content'], query
                            return pods[1]['content']
            
            except Exception as e:
                retry = True
                _count += 1
                if verbose:
                    print("Exception query log:", query)
                    print(e)
                    print(_count)
                if _count > max_count:
                    print(f'max count exceeded: {query}')
                    return [None], query
                    return [None]
                time.sleep(5)
                continue





    @classmethod
    async def compute_legacy(cls, category, section, params, locale='ko_KR'):
        assert type(params) is dict
        # url = os.path.join(cls._COMPUTE_API, category, section, '_search?')
        url = os.path.join('https://api.ddi.deepsearch.com/haystack/v1', category, section, '_search?')
        async with aiohttp.ClientSession() as sess:
            async with sess.get( url=url, auth=aiohttp.BasicAuth(cls._AUTH_ID, cls._AUTH_PW), params=params, timeout=120 ) as co_resp:
                response_json = await co_resp.json()
                if (co_resp.status != 200):# or (not response_json['found']):
                    print("Response code, Success status:", co_resp.status)#, response_json['found'])
                    print("Exception query log:", co_resp.url)
                    print(response_json)
                    return None
        return response_json['data']




class DeepSearchAPI(object):
    _COMPUTE_API = "{}/v1/compute".format('https://api.deepsearch.com')
    _AUTH_ID = os.getenv('_AUTH_ID')
    _AUTH_PW = os.getenv('_AUTH_PW')
    _AUTH = HTTPBasicAuth(_AUTH_ID, _AUTH_PW)

    @classmethod
    def compute(cls, query, locale='ko_KR', debug=False, timeout=120):
        params = {
            'input': query,
            'locale': locale
        } 

        response = requests.post( url=cls._COMPUTE_API, auth=cls._AUTH, data=params, timeout=timeout )

        if (response.status_code != 200) or (not response.json()['success']):
            print("Response code:", response.status_code)
            print("AUTH info:", cls._AUTH_ID, cls._AUTH_PW)
            print("Exception query log:", query)
            if debug:
                return response
            return None

        pods = response.json()['data']['pods']  # pods[0]: input

        if pods[1]['class'] == 'Result:DataFrame':
            data    =    pods[1]['content']['data']
            index   =   pods[1]['content']['index']
            dtypes  =  pods[1]['content']['dtypes']
            columns = pods[1]['content']['columns']

            results = []

            no_obs = len(data[columns[0]])
            for i in range(no_obs):
                item = dict()
                for col in columns:
                    item[col] = data[col][i]
                results.append(item)

            df_results = pd.DataFrame(results)

            if df_results.empty:
                return None

            for col in dtypes.keys():  # pyarrow converting
                if None in df_results[col].values:
                    df_results[col] = df_results[col].ffill()
                
                if dtypes[col] == 'datetime64':
                    df_results[col] = pd.to_datetime(df_results[col], errors='coerce')
                else:
                    df_results[col] = df_results[col].astype(dtypes[col])  # pandas 1.5.3 

            df_results = df_results.set_index(index)  # 'symbol'
            df_results = df_results.sort_index()

            return df_results

        elif pods[1]['class'] == 'Result:DocumentTrendsResult':
            data    =    pods[1]['content']['data']
            trends  =   pods[1]['content']['data']['trends']
            total_matches = trends[0]['total_matches']
            buckets = trends[0]['buckets']

            df_results = pd.DataFrame(buckets)
            
            return df_results

        else:
            return pods[1]['content']


class WaveletAPI(object):
    _COMPUTE_API_INDEX = 'https://api.ddi.deepsearch.com/wavelet/v1/indices' 
    _COMPUTE_API = 'https://api.ddi.deepsearch.com/wavelet/v1/prices'
    _AUTH_ID = os.getenv('_AUTH_ID')
    _AUTH_PW = os.getenv('_AUTH_PW')
    _AUTH = HTTPBasicAuth(_AUTH_ID, _AUTH_PW)

    @classmethod
    def compute(cls, symbol, date_from, date_to, interval=None):
        assert type(symbol) == list
        num_of_pdf = len(symbol)
        symbol_str = ','.join(symbol)
        return_dict = dict()
        
        if symbol in [['KOSPI'], ['KOSDAQ']]:
            query = f'{cls._COMPUTE_API_INDEX}/{symbol_str}?from={date_from}&to={date_to}'
        else:
            query = f'{cls._COMPUTE_API}/{symbol_str}?from={date_from}&to={date_to}'

        response = requests.get(query, auth=cls._AUTH)
        
        if (response.status_code != 200):
            print("Response code:", response.status_code)
            print("AUTH info:", cls._AUTH_ID, cls._AUTH_PW)
            print("Exception query log:", query)
            return None
            
        # print(query)

        if symbol in [['KOSPI'], ['KOSDAQ']]:
            data = response.json()['data'][0]
            points = data['points']

            df = pd.DataFrame.from_dict(points)
            df = df.set_index(['timestamp'])
            df.index = pd.to_datetime(df.index)

            return_dict[symbol[0]] = df  #! 인덱스 리턴은 하나밖에 못한다가 됨
            return return_dict

        else:
            for i in range(num_of_pdf):
                try:
                    data = response.json()['data'][i]
                    points = data['points']

                    df = pd.DataFrame.from_dict(points)
                    df = df.set_index(['timestamp'])
                    df.index = pd.to_datetime(df.index)

                    if num_of_pdf == 1:
                        return_dict[data['exchange'] + ':' + data['symbol']] = df
                        return return_dict
                
                    return_dict[data['exchange'] + ':' + data['symbol']] = df
                except:  
                    print("Response code:", response.status_code)
                    print("Exception query log:", query)
                    break

            return return_dict


class asyncWaveletAPI(object):
    _COMPUTE_API_INDEX = 'https://api.ddi.deepsearch.com/wavelet/v1/indices' 
    _COMPUTE_API = 'https://api.ddi.deepsearch.com/wavelet/v1/prices'
    _AUTH_ID = os.getenv('_AUTH_ID')
    _AUTH_PW = os.getenv('_AUTH_PW')
    _AUTH = HTTPBasicAuth(_AUTH_ID, _AUTH_PW)

    @classmethod
    def compute():
        return


class HaystackAPI(object):
    """
    api.ddi.deepsearch.com/haystack/v1/news/_search?query=삼성전자&count=1
        - https://help.deepsearch.com/ddi/haystack/search

    @category - section: 
        - news
            politics, economy, society, culture, world, tech, entertainment, opinion
        - research
            market, strategy, company, industry, economy, bond   
        - company
            ir, disclosure
        - patent
            patent
    """
    _COMPUTE_API = "{}/v1".format('https://api.ddi.deepsearch.com/haystack')
    _AUTH_ID = os.getenv('_AUTH_ID')
    _AUTH_PW = os.getenv('_AUTH_PW')
    _AUTH = HTTPBasicAuth(_AUTH_ID, _AUTH_PW)

    @classmethod
    def compute(cls, category, section, params, module='_search?', group_by='securities.symbol', locale='ko_KR'):
        assert type(params) is dict
        url = os.path.join(cls._COMPUTE_API, category, section, module)
        if module == '_aggregation?':
            params['groupby'] = group_by
        response = requests.get( url=url, auth=cls._AUTH, params=params, timeout=30 )

        if (response.status_code != 200) or (not response.json()['found']):
            print("Response code, Found status:", response.status_code, response.json()['found'])
            print("Exception query log:", response.url)
            return None

        return response.json()['data']


class asyncHaystackAPI(object):
    """
    api.ddi.deepsearch.com/haystack/v1/news/_search?query=삼성전자&count=1
        - https://help.deepsearch.com/ddi/haystack/search

    @category - section: 
        - news
            politics, economy, society, culture, world, tech, entertainment, opinion
        - research
            market, strategy, company, industry, economy, bond   
        - company
            ir, disclosure
        - patent
            patent
    """
    _COMPUTE_API = "{}/v1".format('https://api.ddi.deepsearch.com/haystack')
    _AUTH_ID = os.getenv('_AUTH_ID')
    _AUTH_PW = os.getenv('_AUTH_PW')
    _AUTH = HTTPBasicAuth(_AUTH_ID, _AUTH_PW)

    @classmethod
    async def compute(cls, category, section, params, locale='ko_KR'):
        assert type(params) is dict
        url = os.path.join(cls._COMPUTE_API, category, section, '_search?')
        async with aiohttp.ClientSession() as sess:
            async with sess.get( url=url, auth=aiohttp.BasicAuth(cls._AUTH_ID, cls._AUTH_PW), params=params, timeout=120 ) as co_resp:
                response_json = await co_resp.json()
                if (co_resp.status != 200):# or (not response_json['found']):
                    print("Response code, Success status:", co_resp.status)#, response_json['found'])
                    print("Exception query log:", co_resp.url)
                    print(response_json)
                    return None
        return response_json['data']



class backtest(object):
    _aum = 100_000_000_000.0
    deepsearch = DeepSearchAPI()
    async_deepsearch = asyncDeepSearchAPI()
    # wavelet = WaveletAPI()
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    # fdr_krx = fdr.StockListing('KRX')
    # fdr_krx_delisted = fdr.StockListing('KRX-DELISTING')

    def _split_phases(cls, deepsearch_df:pd.DataFrame) -> dict:
        return_dict = dict()
        phases = deepsearch_df.index.unique()
        for p in phases:
            pdf = deepsearch_df.loc[p]
            return_dict[p] = pdf
        return return_dict

    def _is_business_day(date) -> bool:
        return bool(len(pd.bdate_range(date, date)))

    def _datetime_reformer(date:str) -> datetime:
        formats = [
            "%Y-%m-%d", 
            "%m/%d/%Y",
        ]
        checked = False
        for i in formats:
            try: _datetime = datetime.strptime(date, i)
            except: _datetime = date
            checked = True
        if not checked:
            print("Date format is not valid. Check the date format.")
            print("Date format should be one of the following:")
            print(formats)
            print("Your date format is:")
            print(date)
        return _datetime  #! formats 에 없는 형식일 경우 에러 : "%Y-%m-%d", "%m/%d/%Y"

    @classmethod
    async def _async_main(cls, symbol_list, date_from, date_to, krx=True) -> list or None:
        start = "'"
        separator = "', '"
        query = f"GetStockPrices(([{start + separator.join(symbol_list) + start}]), columns=['change_rate'], date_from={date_from}, date_to={date_to})"
        # if krx:
        #     if "NICE" in [i.split(":")[0] for i in symbol_list]:
        #         query = ' '.join(symbol_list) + f' {date_from}-{date_to} 주가'  #! 주가수익률은 해당말일을 기준으로 한 점만 보여준다
        #     else:
        #         start = "'"
        #         separator = "', '"
        #         # query = f"GetStockPrices(([{start + separator.join(symbol_list) + start}]), columns=['close'], date_from={date_from}, date_to={date_to})"
        #         query = f"GetStockPrices(([{start + separator.join(symbol_list) + start}]), columns=['change_rate'], date_from={date_from}, date_to={date_to})"
        #     # print(query)
        # else:
        #     start = "'"
        #     separator = "', '"
        #     # query = f'Global.GetStockPrices(([{start + separator.join(symbol_list) + start}]), columns=["close"], date_from={date_from}, date_to={date_to})'
        #     query = f'Global.GetStockPrices(([{start + separator.join(symbol_list) + start}]), columns=["change_rate"], date_from={date_from}, date_to={date_to})'
        #     # print(query)
        task = [cls.async_deepsearch.compute(query)]
        result = await asyncio.gather(*task)
        return result

    def _async_main_wrapper(cls, chunk_krx, chunk_krx_not, _date_from, _date_to, krx=True):
        async_data_krx = cls.loop.run_until_complete( cls._async_main( [i for i in chunk_krx], _date_from, _date_to ) )
        if len(chunk_krx_not) > 0:
            async_data_krx_not = cls.loop.run_until_complete( cls._async_main( [i for i in chunk_krx_not], _date_from, _date_to, krx=False) )
            async_data_krx_not = [ cls._nonkrx_handler(async_data_krx_not[0], _date_from, _date_to) ]
            async_data = [ pd.concat([async_data_krx[0], async_data_krx_not[0]]) ]
        else:
            async_data = async_data_krx
        return async_data


    @classmethod
    def _nonkrx_handler(cls, async_data_krx_not_df, _date_from, _date_to) -> pd.DataFrame:
        won_dollar = cls.deepsearch.compute('QueryBankOfKoreaSeriesData("BOK:731Y001.0000001")')
        async_data_krx_not = async_data_krx_not_df.rename({'close':f'주가 {_date_from}-{_date_to}'}, axis=1)
        wd_stockprice = pd.merge(async_data_krx_not.reset_index(), won_dollar.reset_index()).set_index(['date', 'symbol'])
        wd_stockprice[f'주가 {_date_from}-{_date_to}'] = wd_stockprice.loc[:, f'주가 {_date_from}-{_date_to}'] * wd_stockprice.loc[:, 'QueryBankOfKoreaSeriesData(BOK:731Y001.0000001)']
        async_data_krx_not[f'주가 {_date_from}-{_date_to}'] = wd_stockprice[f'주가 {_date_from}-{_date_to}']
        return async_data_krx_not


    @classmethod
    def _fdr_handler(cls, symbol, _date_from, _date_to):
        if "KRX:" in symbol: symbol = symbol.split(":")[-1]
        if "NICE:" in symbol: symbol = symbol.split(":")[-1]
        _resp = fdr.DataReader(symbol,_date_from,_date_to)
        if symbol in list(cls.fdr_krx["Symbol"]): 
            _entity_name = cls.fdr_krx[cls.fdr_krx["Symbol"] == symbol]["Name"].values[0]
        else: 
            _entity_name = cls.fdr_krx_delisted[cls.fdr_krx_delisted["Symbol"] == symbol]["Name"].values[0]
        _resp["symbol"] = "KRX:"+symbol
        _resp["entity_name"] = _entity_name
        _resp = _resp.reset_index()[["Date", "symbol", "entity_name", "Close"]].sort_values(by=["Date"])
        _resp.columns = ["date", "symbol", "entity_name", f"주가 {_date_from}-{_date_to}"]
        _resp = _resp.set_index(["date", "symbol"])
        return _resp


    @classmethod
    def _pdr_naver_handler(cls, chunk_krx, ticker_name_df, _date_from, _date_to) -> list:
        """
        _date_from 은 change_rate 과 호환되어야 한다. 
        """
        # 220630 맘스터치 상폐 / 007460 무증
        resp_basket = pd.DataFrame()
        for idx, ticker in enumerate(chunk_krx):
            _ticker = ticker.replace("KRX:", "")#.replace(" ", "")

            #!  XML or text declaration not at start of entity: line 3, column 0 : 없는 티커
            _resp = pdr.DataReader(_ticker, "naver", start=(pd.to_datetime(_date_from) -relativedelta(months=1)).strftime("%Y-%m-%d"), end=_date_to)[["Open", "High", "Low", "Close", "Volume"]]
            _resp = _resp.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}).reset_index()
            _resp['entity_name'] = ticker_name_df.loc["KRX:"+_ticker].values[-1][0]
            _resp['symbol'] = "KRX:"+_ticker
            _resp['date'] = _resp['Date']
            _resp["change_rate"] = _resp["close"].astype(float).pct_change()
            _resp = _resp[["date", "symbol", "entity_name", "change_rate"]]

            date_for_change_rate = ((_resp["date"] < pd.to_datetime(_date_from))).replace(False, np.nan).dropna()
            if len(date_for_change_rate) == 0: pass  # _start 이전 데이터가 없는 경우
            else:
                # resp = resp.iloc[((resp["date"] > pd.to_datetime(_start))).replace(False, np.nan).dropna().index[0]:]
                _resp = _resp.iloc[date_for_change_rate.index[-1] +1:]  #! ??? : resp = _resp.iloc[date_for_change_rate.index[-1] +1:] 이렇게 되어있었음
            resp_basket = pd.concat([resp_basket, _resp], axis=0)  #! ??? : resp_basket = pd.concat([resp_basket, resp], axis=0) 이렇게 되어있었음
        async_data = [resp_basket.sort_values(["date", "symbol"]).set_index(["date", "symbol"])]
        return async_data


    @classmethod
    def compute(cls, deepsearch_df, df_to_upload_bool=False, debug=False, fdr=False, naver=False):
        
        if naver:
            ticker_name_dict = dict()
            ticker_nice_dict = dict()
            ticker_name_df = deepsearch_df.reset_index()[["symbol_listed", "entity_name"]].drop_duplicates().set_index("symbol_listed")
            ticker_nice_df = deepsearch_df.reset_index()[["symbol_listed", "symbol"]].drop_duplicates().set_index("symbol_listed")


        df = cls._split_phases(cls, deepsearch_df)
        _rebalancing_dates = list(df.keys())
        for idx, date in enumerate(_rebalancing_dates):
            if datetime.today() < cls._datetime_reformer(date):
                print(_rebalancing_dates, _rebalancing_dates[:idx])
                _rebalancing_dates = _rebalancing_dates[:idx]
                break

        """ 
            종가매수 : 오늘 홀딩스 업데이트 한 경우, 종가매수 후 작업이 포트폴리오 계산에 반영되지 않으므로 제외한다.
        """
        if _rebalancing_dates[-1].strftime("%m/%d/%Y") == datetime.today().strftime("%m/%d/%Y"): 
            rebalancing_dates = _rebalancing_dates[:-1]



        cls._aum = 100_000_000_000.0  #! 변수 초기화

        _async_batch_size = 10
        total_return = pd.DataFrame()
        for idx, date in enumerate(rebalancing_dates):  # idx starts from 0
            print(idx, date, rebalancing_dates)
            """
                rebalancing_dates 는 holdings 파일의 날짜를 의미하며
                date 는 종가리밸런싱이 수행되는 날짜를 의미한다.
                바뀐 포트폴리오의 주가변동은 익일부터 적용된다. 
                만약 홀딩스 파일 기준 date가 휴일이면, 해당 날짜가 휴일이 아닐 때까지 계속해서 다음날로 넘어간다.
                    - ex 24.05.01
                        24년 5월 1일 자 종가 매수 후, 포트폴리오 수익률은 익일은 5월 2일의 수익률부터 반영.
                    - ex 24.05.05 
                        24년 5월 5일은 일요일 휴일. 5월 6일은 대체공휴일. 리밸런싱 날짜는 5월 7일로 넘어간다.

                05.10 수정내역
                    - 05.01 , 05.05 , 05.10 으로 테스팅 한 결과, 
                        첫 번째 페이즈는 2일부터 5일을 포함하고, 두 번째 페이즈는 7일부터 10일을 포함하고 있었다 (말일 종가매수 예외처리 적용). 
                        즉, 1일의 종가에 매수하여 2일과 3일의 수익률을 반영하고, 3일의 종가에 매수하여 7일부터 10일의 수익률을 반영했다. 
                        휴일 이슈를 제외하면, 7일의 수익률이 두 번째 페이즈에 반영되는 것이 옳으나,
                        * 5월 5일이 리밸런싱 일자이므로 다음 거래일의 종가에 매수가 이루어지면, 첫번 째 페이즈는 2일부터 7일까지를 포함해야 한다.
                        * 기존방식인 두 번쨰 페이즈가 7일을 포함한다는 것은, 5일이 휴일이므로 직전 거래일의 종가에 매수함을 의미한다. 
                        ? 휴일의 종가에 매수한다는 것은 어떤 매매를 의도한 것인가? 포트폴리오 작성 시점에, 5일이 휴일이라는 것을 알지 않았다면?
                        
            """
            async_result = pd.DataFrame()
            if isinstance(df[date], pd.Series): _df = pd.DataFrame(df[date]).T
            else: _df = df[date]
            ratio = _df.reset_index().set_index(['symbol'])['weight'].astype(float)  # 단축코드, 비중(비중의합은1)
            ratio.index = ratio.index.str.replace(" ", "")
            pdf = list(_df['symbol'])  # 0 은 iter item (timestamp)

            if naver: pdf = list(_df["symbol_listed"])

            delisted_firm_dict = dict()
            delisted_firm = _df[_df['symbol'] != _df['symbol_listed']]
            for _, row in delisted_firm.iterrows(): delisted_firm_dict[row['symbol_listed']] = row['symbol']

            date = cls._datetime_reformer(date)

            b_days = 0
            while True:
                if not cls._is_business_day(date): date, b_days = date +relativedelta(days=1), b_days +1
                else: break


            if idx+1 != len(rebalancing_dates):  #* if not the last phase
                # _date_from = datetime.strftime(date -relativedelta(days=1), "%Y-%m-%d")
                _date_from_for_close_column = datetime.strftime(date -relativedelta(days=1), "%Y-%m-%d")  # close 기반 하루전날 데이터
                #* 240307 변경(추가) 코드
                # _date_from = datetime.strftime(date, "%Y-%m-%d")  # change_rate 기반 당일 데이터 (당일 수익률 데이터)
                #* 익일의 당일수익률부터 반영
                _date_from = datetime.strftime(date +relativedelta(days=1), "%Y-%m-%d")  #! 휴일이면 안된다 (api 별로 익일을 가져오는지 전일을 가져오는지가 다름). 

                _date_to_for_close_column = datetime.strftime(cls._datetime_reformer(rebalancing_dates[idx+1]) -relativedelta(days=1), "%Y-%m-%d")  # 리밸런싱 전날
                _date_to = datetime.strftime(cls._datetime_reformer(rebalancing_dates[idx+1])-relativedelta(days=0), "%Y-%m-%d")  # 리밸런싱 당일 종가가 기존포트의 수익률에 포함됨

                for i in range(len(pdf)//_async_batch_size +1):
                    chunk_start, chunk_end = i*_async_batch_size, (i+1)*_async_batch_size

                    chunk = pdf[chunk_start:chunk_end]
                    chunk_krx = [i for i in chunk if (i.startswith('KRX:') | i.startswith('NICE:'))]  # ['KRX:007070', 'KRX:023530', 'KRX:139480', 'KRX:097950']
                    chunk_krx_not = list(set(chunk) - set(chunk_krx))

                    if len(chunk) != len(chunk_krx):
                        print(chunk)
                        print(chunk_krx)

                    if len(chunk) == 0: break
                    if naver:
                        async_data = []
                        try: _async_data = cls._pdr_naver_handler(chunk_krx, ticker_name_df, _date_from, _date_to)
                        except: _async_data = cls._pdr_naver_handler(cls, chunk_krx, ticker_name_df, _date_from, _date_to)
                        async_data = async_data +_async_data
                    else:   
                        try: async_data = cls._async_main_wrapper( chunk_krx, chunk_krx_not, _date_from, _date_to)
                        except: async_data = cls._async_main_wrapper(cls, chunk_krx, chunk_krx_not, _date_from, _date_to)


                    for data in async_data:  # wrapper return datatype handler
                        # data.columns = ['entity_name', 'close']  #! 데이터가 안받아져 왔을 시 죽는다
                        try:
                            data.columns = ['entity_name', 'change_rate']  #! 데이터가 안받아져 왔을 시 죽는다
                        except:
                            import pdb
                            pdb.set_trace()
                        async_result = pd.concat([async_result, data], axis=0)

            else:  #* if the last phase
                _date_from_for_close_column = datetime.strftime(date -relativedelta(days=1), "%Y-%m-%d")  # close 기반 하루전날 데이터 
                #* 240307 변경(추가) 코드
                # _date_from = datetime.strftime(date, "%Y-%m-%d")  # change_rate 기반 당일 데이터
                _date_from = datetime.strftime(date +relativedelta(days=1), "%Y-%m-%d")  #! 휴일이면 안된다 (api 별로 익일을 가져오는지 전일을 가져오는지가 다름). 
                _date_to = datetime.strftime(datetime.today().date(), "%Y-%m-%d")

                for i in range(len(pdf)//_async_batch_size +1):
                    chunk_start, chunk_end = i*_async_batch_size, (i+1)*_async_batch_size
                    
                    chunk = pdf[chunk_start:chunk_end]
                    chunk_krx = [i for i in chunk if (i.startswith('KRX:') | i.startswith('NICE:'))]
                    chunk_krx_not = set(chunk) - set(chunk_krx)

                    if len(chunk) != len(chunk_krx):
                        print(chunk)
                        print(chunk_krx)

                    if len(chunk) == 0: break
                    if naver:
                        async_data = []
                        try: _async_data = cls._pdr_naver_handler(chunk_krx, ticker_name_df, _date_from, _date_to)
                        except: _async_data = cls._pdr_naver_handler(cls, chunk_krx, ticker_name_df, _date_from, _date_to)
                        async_data = async_data +_async_data
                    else:   
                        try: async_data = cls._async_main_wrapper(chunk_krx, chunk_krx_not, _date_from, _date_to)
                        except: async_data = cls._async_main_wrapper(cls,  chunk_krx, chunk_krx_not, _date_from, _date_to)


                    for data in async_data:
                        # data.columns = ['entity_name', 'close']
                        data.columns = ['entity_name', 'change_rate']  #! 데이터가 안받아져 왔을 시 죽는다
                        async_result = pd.concat([async_result, data], axis=0)

            async_result_reset = async_result.reset_index()

            
            #####################################################################################################################
            #* close
            # pdf_returns_ds = async_result_reset.drop_duplicates(subset=['date', 'symbol'], keep='first').pivot(index='date', columns='symbol', values='close').ffill()
            # pdf_returns_async = (pdf_returns_ds.pct_change().fillna(0) +1).cumprod()  #! NICE가 없다

            #* change_rate
            pdf_returns_ds = async_result_reset.drop_duplicates(subset=['date', 'symbol'], keep='first').pivot(index='date', columns='symbol', values='change_rate').ffill()
            pdf_returns_async = (pdf_returns_ds +1).cumprod()
            #####################################################################################################################
            
            # pdf_returns_ds.iloc[0, :] = 0  #* 주가수익률로 계산했을 시기의 코드 
            # pdf_returns_async = (pdf_returns_ds +1).cumprod()  #* 주가수익률로 계산했을 시기의 코드 
            pdf_returns_async.columns = [ delisted_firm_dict[i] if i in delisted_firm_dict.keys() else i for i in pdf_returns_async.columns ]

            inherited_budget = ratio * cls._aum  # 시작분배금  #! NICE가 있다 / ratio는 가장 최근의 리밸비중 / 여기서의 cls._aum 은 다음 값으로 업데이트 되기 전임
            #* 시작일은 base_point를 남기고 그 이후부터는 첫날의 리밸런싱 무수익을 떨군다

            inherited_budget.index = inherited_budget.index.astype(str)
            pdf_returns_async.columns = pdf_returns_async.columns.astype(str)
            if idx > 0: 
                #* 기존 코드 : 종가리밸런싱일자 익일 수익률부터 반영하지만, 종가리밸런싱일자의 하루치 수익률이 들어가 있다
                # _aum_change_async = pdf_returns_async[datetime.strptime(_date_from, "%Y-%m-%d").date() +relativedelta(days=1):] *inherited_budget
                #* 240307 변경 코드
                _aum_change_async = pdf_returns_async[datetime.strptime(_date_from, "%Y-%m-%d").date() +relativedelta(days=0):] *inherited_budget
            else:  # 최초 상장
                _aum_change_async = pdf_returns_async *inherited_budget
                

            # cls._aum = _aum_change_async.sum(axis=1)[-1]  # deprecation caution informed
            cls._aum = _aum_change_async.sum(axis=1).iloc[-1]
            total_return = pd.concat([total_return, _aum_change_async])
            print(cls._aum)


        if debug == True:
            import pdb
            pdb.set_trace()

        total_return = total_return.groupby(total_return.index).first()

        if df_to_upload_bool:
            total_return = total_return.groupby(total_return.index).first()
            base_point = 1000
            daily_aum = total_return.sum(axis=1)
            daily_aum.index = pd.to_datetime(daily_aum.index)
            index_calc_start_date = cls._datetime_reformer(rebalancing_dates[0])

            """
            //2023-01-19//
            close 기반 기존의 계산 -> 시가매수
            change_rate 기반 계산 -> 종가매수 
            """
            import copy
            daily_aum_for_change_rate = copy.deepcopy(daily_aum)
            daily_aum_for_change_rate = dict(daily_aum_for_change_rate)
            daily_aum_for_change_rate[index_calc_start_date] = 100_000_000_000
            daily_aum_for_change_rate = pd.Series(daily_aum_for_change_rate).sort_index()

            daily_aum = daily_aum_for_change_rate

            try:
                daily_idx = daily_aum / daily_aum[datetime.strftime(index_calc_start_date, "%Y-%m-%d")] *base_point
            except:
                print(f'error check [{rebalancing_dates[0]}] - date index not exists, call the most recent previous date')
                daily_idx = daily_aum / daily_aum[:datetime.strftime(index_calc_start_date, "%Y-%m-%d")].iloc[-1] *base_point
            daily_idx = daily_idx[datetime.strftime(index_calc_start_date, "%Y-%m-%d"):]


            resp = pdr.DataReader("KOSPI", "naver", start=datetime.strftime(index_calc_start_date, '%Y-%m-%d'), end=datetime.strftime(datetime.today().date(), '%Y-%m-%d'))[["Open", "High", "Low", "Close", "Volume"]]
            resp = resp.astype(float)
            resp["symbol"] = "KRX:KOSPI"
            resp["entity_name"] = "코스피"
            resp = resp.reset_index()[["Date", "symbol", "entity_name", "Close"]].sort_values(by=["Date"])
            resp.columns = ["date", "symbol", "entity_name", f"주가 {datetime.strftime(index_calc_start_date, '%Y-%m-%d')}-{datetime.strftime(datetime.today().date(), '%Y-%m-%d')}"]
            resp = resp.set_index(["date", "symbol"])
            kospi = resp.reset_index().set_index('date')
            kospi.columns = ['symbol', 'entity_name', 'close']
            kospi.index = pd.to_datetime(kospi.index).date

            #! 한국주식과 미국주식을 섞으면 공휴일이 다르다 
            _excel_date_format = "%Y-%m-%d"
            try:
                daily_idx_date_reviewed = daily_idx.loc[kospi.index]
            except:
                daily_idx.index = pd.to_datetime(daily_idx.index).date
                daily_idx_date_reviewed = daily_idx
            
            #! 2.0.2 updated
            #! TypeError: Cannot compare Timestamp with datetime.date. Use ts == pd.Timestamp(date) or ts.date() == date instead.
            kospi.index = pd.to_datetime(kospi.index)
            daily_idx_date_reviewed.index = pd.to_datetime(daily_idx_date_reviewed.index)
            kospi.index = pd.to_datetime(kospi.index)
            
            df_to_upload = pd.concat([daily_idx_date_reviewed, kospi["close"]], axis=1).sort_index(ascending=True).bfill()
            df_to_upload.columns = ['index', 'KOSPI']
            df_to_upload.index = pd.to_datetime(df_to_upload.index, format="%Y-%m-%d")
            df_to_upload.index = df_to_upload.index.strftime(_excel_date_format)
            df_to_upload = df_to_upload.reset_index()
            df_to_upload.columns = ['date', 'index', 'KOSPI']

            df_to_upload["index"] = df_to_upload["index"] / df_to_upload["index"].iloc[0] * base_point
            df_to_upload["KOSPI"] = df_to_upload["KOSPI"] / df_to_upload["KOSPI"].iloc[0] * base_point


            df_to_upload['date'] = df_to_upload['date'].astype(str)

            return df_to_upload
        return total_return




class _backtest(object):
    _aum = 100_000_000_000.0
    deepsearch = DeepSearchAPI()
    async_deepsearch = asyncDeepSearchAPI()
    wavelet = WaveletAPI()

    def _split_phases(cls, deepsearch_df):
        return_dict = dict()
        phases = deepsearch_df.index.unique()
        for p in phases:
            pdf = deepsearch_df.loc[p]
            return_dict[p] = pdf
        return return_dict

    def _is_business_day(date):
        return bool(len(pd.bdate_range(date, date)))

    @classmethod
    async def _async_main(cls, symbol_list, date_from, date_to):
        query = ' '.join(symbol_list) + f' {date_from}-{date_to} 주가'  #! 주가수익률은 해당말일을 기준으로 한 점만 보여준다
        task = [cls.async_deepsearch.compute(query)]
        result = await asyncio.gather(*task)
        return result

    @classmethod
    def compute(cls, deepsearch_df, df_to_upload_bool=False, debug=False):
        df = cls._split_phases(cls, deepsearch_df)
        rebalancing_dates = list(df.keys())
        for idx, date in enumerate(rebalancing_dates):
            if datetime.today() < (datetime.strptime(date, "%m/%d/%Y")):
                print(rebalancing_dates, rebalancing_dates[:idx])
                rebalancing_dates = rebalancing_dates[:idx]
                break



        loop = asyncio.get_event_loop()
        _async_batch_size = 10


        total_return = pd.DataFrame()
        for idx, date in enumerate(rebalancing_dates):  # idx starts from 0
            async_result = pd.DataFrame()
            if isinstance(df[date], pd.Series): _df = pd.DataFrame(df[date]).T
            else: _df = df[date]
            ratio = _df.reset_index().set_index(['symbol'])['weight'].astype(float)  # 단축코드, 비중(비중의합은1)
            ratio.index = ratio.index.str.replace(" ", "")
            pdf = list(_df['symbol'])  # 0 은 iter item (timestamp)

            delisted_firm_dict = dict()
            delisted_firm = _df[_df['symbol'] != _df['symbol_listed']]
            for _, row in delisted_firm.iterrows(): delisted_firm_dict[row['symbol_listed']] = row['symbol']

            date = datetime.strptime(date, "%m/%d/%Y")

            b_days = 0
            while True:
                if not cls._is_business_day(date): date, b_days = date +relativedelta(days=1), b_days +1
                else: break


            if idx+1 != len(rebalancing_dates):  #* if not the last phase
                _date_from = datetime.strftime(date -relativedelta(days=1), "%Y-%m-%d")
                _date_to = datetime.strftime(datetime.strptime(rebalancing_dates[idx+1], "%m/%d/%Y") -relativedelta(days=1), "%Y-%m-%d")

                for i in range(len(pdf)//_async_batch_size +1):
                    chunk_start, chunk_end = i*_async_batch_size, (i+1)*_async_batch_size
                    chunk = pdf[chunk_start:chunk_end]
                    if len(chunk) == 0: break
                    #! 왜 다른가?
                    try: async_data = loop.run_until_complete( cls._async_main( cls, [i for i in chunk], _date_from, _date_to ) )
                    except: async_data = loop.run_until_complete( cls._async_main( [i for i in chunk], _date_from, _date_to ) )
                    for data in async_data: 
                        data.columns = ['entity_name', 'close']  #! 데이터가 안받아져 왔을 시 죽는다
                        async_result = pd.concat([async_result, data], axis=0)
            else:  #* if the last phase
                _date_from = datetime.strftime(date -relativedelta(days=1), "%Y-%m-%d")
                _date_to = datetime.strftime(datetime.today().date(), "%Y-%m-%d")

                for i in range(len(pdf)//_async_batch_size +1):
                    chunk_start, chunk_end = i*_async_batch_size, (i+1)*_async_batch_size
                    chunk = pdf[chunk_start:chunk_end]
                    if len(chunk) == 0: break
                    #! 왜 다른가?
                    try: async_data = loop.run_until_complete( cls._async_main( cls, [i for i in chunk], _date_from, _date_to) )  # datetime.strftime(datetime.today(), "%Y-%m-%d")
                    except: async_data = loop.run_until_complete( cls._async_main( [i for i in chunk], _date_from, _date_to) )  # datetime.strftime(datetime.today(), "%Y-%m-%d")
                    for data in async_data:
                        data.columns = ['entity_name', 'close']
                        async_result = pd.concat([async_result, data], axis=0)

            async_result_reset = async_result.reset_index()
            pdf_returns_ds = async_result_reset.drop_duplicates(subset=['date', 'symbol'], keep='first').pivot(index='date', columns='symbol', values='close')
            pdf_returns_async = (pdf_returns_ds.pct_change().fillna(0) +1).cumprod()  #! NICE가 없다
            # pdf_returns_ds.iloc[0, :] = 0  #* 주가수익률로 계산했을 시기의 코드 
            # pdf_returns_async = (pdf_returns_ds +1).cumprod()  #* 주가수익률로 계산했을 시기의 코드 
            pdf_returns_async.columns = [ delisted_firm_dict[i] if i in delisted_firm_dict.keys() else i for i in pdf_returns_async.columns ]

            inherited_budget = ratio * cls._aum  # 시작분배금  #! NICE가 있다 / ratio는 가장 최근의 리밸비중 / 여기서의 cls._aum 은 다음 값으로 업데이트 되기 전임
            #* 시작일은 base_point를 남기고 그 이후부터는 첫날의 리밸런싱 무수익을 떨군다

            try: _prev_aum_change_async = _aum_change_async
            except: pass
            inherited_budget.index = inherited_budget.index.astype(str)
            pdf_returns_async.columns = pdf_returns_async.columns.astype(str)
            if idx > 0: 
                _aum_change_async = pdf_returns_async[datetime.strptime(_date_from, "%Y-%m-%d").date() +relativedelta(days=1):] *inherited_budget
            else: _aum_change_async = pdf_returns_async *inherited_budget

            cls._aum = _aum_change_async.sum(axis=1)[-1]
            total_return = pd.concat([total_return, _aum_change_async])
            print(cls._aum)

            # total_return = pd.concat([total_return, _aum_change_wavelet])

        if debug == True:
            import pdb
            pdb.set_trace()

        total_return = total_return.groupby(total_return.index).first()

        cls._aum = 100_000_000_000.0  #! 변수 초기화

        if df_to_upload_bool:
            total_return = total_return.groupby(total_return.index).first()
            base_point = 1000
            daily_aum = total_return.sum(axis=1)
            try:
                daily_idx = daily_aum / daily_aum[datetime.strftime(cls._datetime_reformer(rebalancing_dates[0]), "%Y-%m-%d")] *base_point
            except:
                print(f'error check [{rebalancing_dates[0]}] - date index not exists, call the most recent previous date')
                daily_idx = daily_aum / daily_aum[:datetime.strftime(cls._datetime_reformer(rebalancing_dates[0]), "%Y-%m-%d")].iloc[-1] *base_point
            daily_idx = daily_idx[datetime.strftime(cls._datetime_reformer(rebalancing_dates[0]), "%Y-%m-%d"):]
            
            """
            daily_aum.index = pd.to_datetime(daily_aum.index)
            daily_idx = daily_aum / daily_aum[datetime.strftime(datetime.strptime(rebalancing_dates[0], "%m/%d/%Y"), "%Y-%m-%d")] *base_point
            daily_idx = daily_idx[datetime.strftime(datetime.strptime(rebalancing_dates[0], "%m/%d/%Y"), "%Y-%m-%d"):]
            # daily_idx.index = daily_idx.index.date
            """

            #* rebalancing_dates[0] 은 해당일 종가매수를 의미한다.
            #* 즉, 월요일부터의 수익률을 보고싶은 경우, 리밸런싱 날짜는 월요일이 아닌 직전 거래일(금요일)을 넣어야 한다.
            _query_kospi = f"코스피 지수 {datetime.strftime(cls._datetime_reformer(rebalancing_dates[0]), '%Y-%m-%d')}-{datetime.strftime(datetime.today().date(), '%Y-%m-%d')}"
            resp = cls.deepsearch.compute(_query_kospi).reset_index().set_index('date')
            resp.columns = ['close' if '지수' in i else i for i in resp.columns]
            kospi = resp

            # import FinanceDataReader as fdr
            # from pandas_datareader import data 
            # resp = data.DataReader("KOSPI", "naver", start=datetime.strftime(cls._datetime_reformer(rebalancing_dates[0]), '%Y-%m-%d'), end=datetime.strftime(datetime.today().date(), '%Y-%m-%d'))[["Open", "High", "Low", "Close", "Volume"]]
            # resp = resp.astype(float)
            # resp["symbol"] = "KRX:KOSPI"
            # resp["entity_name"] = "코스피"
            # resp = resp.reset_index()[["Date", "symbol", "entity_name", "Close"]].sort_values(by=["Date"])
            # resp.columns = ["date", "symbol", "entity_name", f"주가 {datetime.strftime(cls._datetime_reformer(rebalancing_dates[0]), '%Y-%m-%d')}-{datetime.strftime(datetime.today().date(), '%Y-%m-%d')}"]
            # resp = resp.set_index(["date", "symbol"])
            # kospi = resp.reset_index().set_index('date')
            # kospi.columns = ['symbol', 'entity_name', 'close']
            # kospi.index = pd.to_datetime(kospi.index).date

            #! 한국주식과 미국주식을 섞으면 공휴일이 다르다 
            try:
                daily_idx_date_reviewed = daily_idx.loc[kospi.index]
            except:
                import pdb
                pdb.set_trace()
            # kospi_ret = kospi['close'].loc[daily_idx.index].pct_change()  # 당일의 종가수익률이 아니라 판다스에서 추가적으로 계산된 값이므로 첫날의 수익률은 누락 #! 그런데 첫날이 월요일이면 -1day때문에 길이가 안맞는다
            kospi_ret = kospi['close'].pct_change()

            daily_kospi = (kospi_ret+1).cumprod().fillna(1) *base_point  #* 엑셀 holdings 파일의 date 는 종가매수의 기준일이므로, 날짜를 월요일로 잡아도 월요일 종가매수를 의미한다. 
            # daily_kospi.index = daily_kospi.index.date
            #업로드용 파일 가공
            _excel_date_format = "%Y-%m-%d"
            # df_to_upload = pd.concat([daily_idx, daily_kospi], axis=1)
            df_to_upload = pd.concat([daily_idx_date_reviewed, daily_kospi], axis=1)
            df_to_upload.columns = ['index', 'KOSPI']
            df_to_upload.index = pd.to_datetime(df_to_upload.index, format="%Y-%m-%d")
            df_to_upload.index = df_to_upload.index.strftime(_excel_date_format)
            df_to_upload = df_to_upload.reset_index()
            df_to_upload.columns = ['date', 'index', 'KOSPI']
            df_to_upload['date'] = df_to_upload['date'].astype(str)

            """
            _excel_date_format = "%d/%m/%Y"
            df_to_upload = pd.concat([daily_idx, daily_kospi], axis=1)
            df_to_upload.columns = ['index', 'KOSPI']
            df_to_upload.index = pd.to_datetime(df_to_upload.index, format="%Y-%m-%d")
            df_to_upload.index = df_to_upload.index.strftime(_excel_date_format)
            df_to_upload = df_to_upload.reset_index()
            """

            return df_to_upload
        return total_return





#* ================================================================================================================================
#*        ██████████                                █████████                                        █████                          
#*       ░░███░░░░███                              ███░░░░░███                                      ░░███         
#*        ░███   ░░███  ██████   ██████  ████████ ░███    ░░░   ██████   ██████   ████████   ██████  ░███████     
#*        ░███    ░███ ███░░███ ███░░███░░███░░███░░█████████  ███░░███ ░░░░░███ ░░███░░███ ███░░███ ░███░░███    
#*        ░███    ░███░███████ ░███████  ░███ ░███ ░░░░░░░░███░███████   ███████  ░███ ░░░ ░███ ░░░  ░███ ░███    
#*        ░███    ███ ░███░░░  ░███░░░   ░███ ░███ ███    ░███░███░░░   ███░░███  ░███     ░███  ███ ░███ ░███    
#*        ██████████  ░░██████ ░░██████  ░███████ ░░█████████ ░░██████ ░░████████ █████    ░░██████  ████ █████   
#*       ░░░░░░░░░░    ░░░░░░   ░░░░░░   ░███░░░   ░░░░░░░░░   ░░░░░░   ░░░░░░░░ ░░░░░      ░░░░░░  ░░░░ ░░░░░    
#*                                       ░███                                                                     
#*                                       █████                                                                    
#*                                      ░░░░░                                                                     
#*                        ████████                                                                                
#*                       ███░░░░███                                                                               
#*        █████ █████   ░░░    ░███                                                                               
#*       ░░███ ░░███       ███████                                                                                
#*        ░███  ░███      ███░░░░                                                                                 
#*        ░░███ ███      ███      █                                                                               
#*         ░░█████      ░██████████                                                                               
#*          ░░░░░       ░░░░░░░░░░                                  DeepSearch version 2 API                                              
#* ================================================================================================================================
            

# stock_api/base.py
import requests
from urllib.parse import quote, urlencode
from typing import Dict, Any, Union, List, Optional

class BaseAPIClient:
    """Base class for API clients"""
    def __init__(self, api_key: str = None, base_url: str = None):
        """
            https://api-v2-internal.deepsearch.com/v2/markets/indice
        """
        self.api_key = api_key or os.getenv("DEEPSEARCH_API_KEY")
        self.base_url = base_url or "https://api-v2-internal.deepsearch.com"
        self.service_key = os.getenv("DEEPSEARCH_SERVICE_KEY")

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, headers: Dict[str, Any] = None) -> dict:
        """Make HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        if self.api_key:
            params["api_key"] = self.api_key

        if headers is None:
            headers = {}
            if self.service_key:
                headers["X-INTERNAL-SERVICE-KEY"] = self.service_key
        
        # Remove None parameters
        params = {k: v for k, v in params.items() if v is not None}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {str(e)}")
            raise


class DeepSearchGlobalAPI(BaseAPIClient):
    """DeepSearch API Client for stock and news data"""
    
    VALID_GROUP_BY_FIELDS = {
        'companies.name', 'company.company_name',
        'companies.symbol', 'company.company_symbol',
        'companies.exchange', 'company.company_exchange',
        'companies.sentiment', 'company.sentiment',
        'sections', 'published_at', 'esg.category'
    }

    def __init__(self, api_key: str = None, base_url: str = None):
        super().__init__(api_key, base_url)

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, headers: Dict[str, Any] = None) -> dict:
        """Make HTTP request to the API"""
        return super()._make_request(endpoint, params, headers)

    # def _get_full_url(self, endpoint: str, params: Dict[str, Any]) -> str:
    #     """Get full URL with parameters"""
    #     params["api_key"] = self.api_key
    #     return f"{self.base_url}{endpoint}?{urlencode(params)}"

    def get_company_stock(self, 
                         symbol: str, 
                         page: int = 1, 
                         page_size: int = 10000, 
                         date_from: Optional[str] = None,
                         date_to: Optional[str] = None, 
                         period: str = "1m", 
                         delay: bool = False) -> dict:
        try:
            date_from = datetime.strftime(date_from, "%Y-%m-%d")
            date_to = datetime.strftime(date_to, "%Y-%m-%d")
        except: pass
        
        all_data = []

        while True:
            # 현재 페이지 데이터 가져오기
            response = self._make_request(
                endpoint=f"/v2/companies/{symbol}/stock",
                params={
                    "page": page,
                    "page_size": page_size,
                    "date_from": date_from,
                    "date_to": date_to,
                    "period": period
                }
            )
            # print(response)
            
            # 데이터가 없으면 종료
            if not response.get('data'):
                break
                
            # 데이터 추가
            all_data.extend(response['data'])
            
            # 마지막 페이지 체크 (데이터가 page_size보다 적으면 마지막 페이지)
            if len(response['data']) < page_size:
                break
                
            # 다음 페이지로
            page += 1
        all_data = pd.DataFrame(all_data)
        if len(all_data) == 0:
            return None
        all_data["date"] = pd.to_datetime(all_data["date"]).dt.date
        all_data["pct_change"] = all_data["change_percent"] / 100
        all_data = all_data.sort_values(by="date").reset_index(drop=True)
        return all_data
    

    async def get_company_stock_async(
        self, 
        session: aiohttp.ClientSession, 
        symbol: str, 
        date_from: str, 
        date_to: str, 
        region: str,
        period: str = "1m", 
        page_size: int = 10000
    ) -> Optional[pd.DataFrame]:
        """
        Asynchronously fetch all pages of company stock data for a given symbol.

        Parameters:
        - session (aiohttp.ClientSession): The HTTP session to use for requests.
        - symbol (str): The stock symbol to fetch data for.
        - date_from (str): The start date for data fetching in 'YYYY-MM-DD' format.
        - date_to (str): The end date for data fetching in 'YYYY-MM-DD' format.
        - period (str): The period for which to fetch the data. Default is "1m".
        - page_size (int): Number of records per page. Default is 10000.

        Returns:
        - Optional[pd.DataFrame]: DataFrame containing the aggregated stock data or None if no data is found.


        import asyncio
        import aiohttp

        async with aiohttp.ClientSession() as session:
            tasks = [deepsearch_global.get_company_stock_async(session, i, date_from="2024-01-01", date_to="2025-02-24") for i in _tickers_all]
            resp = await asyncio.gather(*tasks)

        price_matrix = pd.DataFrame()
        for i in resp:
            price_matrix = pd.concat([price_matrix, i.pivot(index="date", columns="symbol", values="pct_change")], axis=1)

        ///
        price_data, mktcap_data = await deepsearch_global.get_price_market_data_async(_tickers_all, (pd.to_datetime(TODAY)-relativedelta(years=1)).strftime("%Y-%m-%d"), TODAY, region='us')


        """
        assert region in ["us", "kr"]

        # https://api-v2-internal.deepsearch.com
        
        all_data = []
        page = 1  # Start from the first page

        if region == 'kr':
            endpoint = f"/v2/companies/{symbol}/stock"

            # while True:
            base_params = {
                "api_key": self.api_key,
                "date_from": date_from,
                "date_to": date_to,
                "period": period,
                # "page": page,
                "page_size": page_size
            }
            url = f"{self.base_url}{endpoint}"
            headers = {}
            if self.service_key:
                headers["X-INTERNAL-SERVICE-KEY"] = self.service_key

        # elif region == 'us':
        #     endpoint = "/v2/companies/stocks_list"  # 엔드포인트를 심볼이 포함되지 않는 고정 경로로 변경합니다.

        #     # while True:  # 새 API에서는 심볼을 쿼리 파라미터로 전달합니다.
        #     base_params = {
        #         "api_key": self.api_key,
        #         "symbol": f"{symbol},",  # 예: '003620' -> '003620,'
        #         "date_from": date_from,
        #         "date_to": date_to,
        #         # "period": period,        # period 파라미터가 새 API에 필요없다면 제거합니다.
        #         # "page": page,
        #         "page_size": page_size
        #     }
        #     url = f"{self.base_url}{endpoint}"  # base_url과 endpoint를 결합하여 최종 URL을 구성합니다.
        #     headers = None
        elif region == 'us':
            # 잘못된 stocks_list → 정확한 /{symbol}/stock 로 교체
            endpoint = f"/v2/companies/{symbol}/stock"
            url = f"{self.base_url}{endpoint}"
            headers = None          # 공개 엔드포인트는 서비스-키 불필요
            base_params = {
                "api_key": self.api_key,
                "date_from": date_from,
                "date_to": date_to,
                "period": period,
                "page_size": page_size
            }




        while True:  # 새 API에서는 심볼을 쿼리 파라미터로 전달합니다.
            params = base_params.copy()
            params['page'] = page
            try:
                # if region == "kr":
                #     headers = headers
                # else:
                #     headers = None
                # async with session.get(url, params=params) as response:
                async with session.get(url, params=params, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    data_page = data.get('data', [])

                if not data_page:
                    # No more data to fetch
                    break

                all_data.extend(data_page)

                if len(data_page) < page_size:
                    # Last page reached
                    break

                page += 1  # Move to the next page

            except Exception as e:
                print(f"Error fetching data for {symbol} on page {page}: {str(e)}")
                return None

        if not all_data:
            return None  # Return None if no data was fetched
        
        # Convert aggregated data to DataFrame
        df = pd.DataFrame(all_data)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["pct_change"] = df["change_percent"] / 100
        df = df.sort_values(by="date").reset_index(drop=True)
        df["symbol"] = symbol

        return df
    

    def get_company_financials(self, symbol, date_from, date_to, period):
        """https://api-v2.deepsearch.com/v2/companies/{symbol}/financials"""

        """
            period: 1d, 1w, 1m, 3m, 6m, 1y, 5y
            date_from, date_to: YYYY-MM-DD
            
            returns get fiscal year end data
        """
        endpoint = f"/v2/companies/{symbol}/financials"
        params = {}
        try:
            date_from = datetime.strftime(date_from, "%Y-%m-%d")
            date_to = datetime.strftime(date_to, "%Y-%m-%d")
        except: pass

        if date_from is not None:
            params["date_from"] = date_from
        if date_to is not None:
            params["date_to"] = date_to
        if period is not None:
            params["period"] = period

        resp = self._make_request(endpoint, params)["data"]
        resp = pd.DataFrame(resp)
        if len(resp) == 0:
            print(f"No financial data found for {symbol}")
            return None
        resp["fiscal_end_date"] = pd.to_datetime(resp["fiscal_end_date"])
        resp = resp.sort_values(by="fiscal_end_date").reset_index(drop=True)
        return resp
    
    # def get_company_financials(self, symbol, date_from, date_to, period):
    #     """https://api-v2.deepsearch.com/v2/companies/{symbol}/financials"""

    #     try:
    #         endpoint = f"/v2/companies/{symbol}/financials"
    #         params = {}  # symbol 제거
            
    #         if date_from is not None:
    #             params["date_from"] = date_from
    #         if date_to is not None:
    #             params["date_to"] = date_to
    #         if period is not None:
    #             params["period"] = period

    #         return self._make_request(endpoint, params)
    #     except Exception as e:
    #         print(f"Error fetching company stock data for {symbol}: {str(e)}")
    #         raise


    def get_market_index(self, 
                         symbol: str = None, 
                         page: int = 1, 
                         page_size: int = 10000, 
                         country_code: str = "us",
                         date_from: Optional[str] = None,
                         date_to: Optional[str] = None, 
                         period: str = None,
                         ) -> dict:
        """
            https://api-v2.deepsearch.com/v2/markets/indice
            https://api-v2-internal.deepsearch.com/v2/markets/indice
        """
        endpoint = "/v2/markets/indice"

        try:
            date_from = datetime.strftime(date_from, "%Y-%m-%d")
            date_to = datetime.strftime(date_to, "%Y-%m-%d")
        except: pass

        params = {
            "symbol": symbol,
            "page": page,
            "page_size": page_size
        }
        
        if country_code is not None:
            params["country_code"] = country_code
        if date_from is not None:
            params["date_from"] = date_from
        if date_to is not None:
            params["date_to"] = date_to
        # if period is not None:
        #     params["period"] = period

        all_data = []
        current_page = page

        while True:
            params["page"] = current_page
            response = self._make_request(endpoint, params)
            if not response.get('data'):
                break
            all_data.extend(response['data'])
            if len(response['data']) < page_size:
                break
            current_page += 1

        all_data = pd.DataFrame(all_data)
        if len(all_data) == 0:
            return None
            
        all_data["date"] = pd.to_datetime(all_data["date"]).dt.date
        all_data["pct_change"] = all_data["change_percent"] / 100
        all_data = all_data.sort_values(by="date").reset_index(drop=True)
        
        return all_data



    def get_global_articles(self, 
                          keyword: str,
                          symbol: Optional[str] = None,
                          page: int = 1,
                          page_size: int = 10,
                          date_from: Optional[str] = None,
                          date_to: Optional[str] = None,
                          symbol_companies_only: bool = False) -> dict:
        """Fetch global articles"""
        endpoint = "/v1/global-articles"
        
        params = {
            "keyword": quote(keyword),
            "page": page,
            "page_size": page_size,
            "date_from": date_from,
            "date_to": date_to,
            "symbol_companies_only": str(symbol_companies_only).lower()
        }
        if symbol is not None:
            params["symbol"] = symbol
        
        return self._make_request(endpoint, params)

    def get_global_articles_aggregate(self,
                                    section: Optional[str] = None,
                                    group_by: Union[str, List[str]] = None,
                                    keyword: str = None,
                                    company_name: Optional[str] = None,
                                    symbols: Optional[str] = None,
                                    date_from: Optional[str] = None,
                                    date_to: Optional[str] = None,
                                    size: Optional[int] = None) -> dict:
        """Aggregate global articles

            companies.name, company.company_name (기업이름)
            companies.symbol, company.company_symbol (기업 종목코드)
            companies.exchange, company.company_exchange (거래소)
            companies.sentiment, company.sentiment (기업 감정)
        
        """
        if type(section) == str:
            section = section
        else:
            section = "aggregation"
        endpoint = f"/v1/global-articles/{section}"

        if keyword is None and company_name is None and symbols is None:
            raise ValueError("One of the keyword, company_name, or symbols must be provided")
        
        if isinstance(group_by, str):
            group_by = [group_by]
            
        # invalid_fields = set(group_by) - self.VALID_GROUP_BY_FIELDS
        # if invalid_fields:
        #     raise ValueError(f"Invalid group_by fields: {invalid_fields}. "
        #                    f"Valid fields are: {self.VALID_GROUP_BY_FIELDS}")

        # params = {
        #     "group_by": ",".join(group_by),
        # }
        params = {}
        if section is not None:
            params["section"] = ",".join(section)
        if group_by is not None:
            params["group_by"] = ",".join(group_by)
        if keyword is not None:
            params["keyword"] = keyword
        if company_name is not None:
            params["company_name"] = company_name
        if symbols is not None:
            params["symbols"] = symbols
        if date_from is not None:
            params["date_from"] = date_from
        if date_to is not None:
            params["date_to"] = date_to
        if size is not None:
            params["size"] = size

        return self._make_request(endpoint, params)
    

    def get_global_disclosure_aggregate(self, 
                                        group_by: Union[str, List[str]] = None,
                                        keyword: str = None,
                                        company_name: Optional[str] = None,
                                        symbols: Optional[str] = None,
                                        date_from: Optional[str] = None,
                                        date_to: Optional[str] = None,
                                        size: Optional[int] = None) -> dict:
        """
        Aggregate global disclosure
            - https://api-v2.deepsearch.com/v2/document/redoc#tag/%EA%B3%B5%EC%8B%9C/operation/aggregate_filings_v1_filings_aggregation_get

            company_name
            filing_type
        """
        endpoint = "/v1/filings/aggregation"

        params = {}
        if group_by is not None:
            params["group_by"] = group_by
        if keyword is not None:
            params["keyword"] = keyword
        if company_name is not None:
            params["company_name"] = company_name
        if symbols is not None:
            params["symbols"] = symbols
        if date_from is not None:
            params["date_from"] = date_from
        if date_to is not None:
            params["date_to"] = date_to
        if size is not None:
            params["size"] = size

        return self._make_request(endpoint, params) 
    
        




    #* codes for backtesting

    def get_price_market_data(self, symbol_list, date_from, date_to=datetime.today().strftime("%Y-%m-%d")):
        """특정 기간의 종목 수익률 데이터 가져오기"""
        import tqdm
        price_data = pd.DataFrame()
        mktcap_data = pd.DataFrame()
        for symbol in tqdm.tqdm(symbol_list):
            _price = self.get_company_stock(symbol=symbol, date_from=date_from, date_to=date_to, period="1m")[["date", "symbol", "close", "pct_change", "market_cap"]]
            price_data = pd.concat([price_data, _price[["date", "symbol", "pct_change"]]])
            mktcap_data = pd.concat([mktcap_data, _price[["date", "symbol", "market_cap"]]])

        price_data = price_data.pivot(index="date", columns="symbol", values="pct_change")
        mktcap_data = mktcap_data.pivot(index="date", columns="symbol", values="market_cap")
        price_data.index = pd.to_datetime(price_data.index)
        mktcap_data.index = pd.to_datetime(mktcap_data.index)

        return price_data, mktcap_data
    

    async def get_price_market_data_async(
        self, 
        symbol_list: list, 
        date_from: str, 
        date_to: Optional[str] = None, 
        region: str = "ko",
        period: str = "1m",
        special_verbose: bool = False
    ) -> Optional[tuple]:
        """
        Asynchronously fetch percent change and market cap data for a list of symbols over a date range.

        Parameters:
        - symbol_list (list): List of stock symbols.
        - date_from (str): Start date in 'YYYY-MM-DD' format.
        - date_to (Optional[str]): End date in 'YYYY-MM-DD' format. Defaults to today's date.
        - period (str): The period for which to fetch the data. Default is "1m".

        Returns:
        - Optional[tuple]: Tuple containing price_data (DataFrame) and mktcap_data (DataFrame) or None if no data is fetched.
        """
        if date_to is None:
            date_to = datetime.today().strftime("%Y-%m-%d")
        else:
            if isinstance(date_to, pd.Timestamp):
                date_to = date_to.strftime('%Y-%m-%d')
        if isinstance(date_from, pd.Timestamp):
            date_from = date_from.strftime('%Y-%m-%d')

        price_data_list = []
        mktcap_data_list = []

        # Configure connector with higher limits
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=300)  # Increased timeout to handle multiple pages

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [
                asyncio.create_task(
                    self.get_company_stock_async(session, symbol, date_from, date_to, region, period)
                ) for symbol in symbol_list
            ]

            responses = await asyncio.gather(*tasks, return_exceptions=True)

        for symbol, df in zip(symbol_list, responses):
            if isinstance(df, Exception):
                print(f"An error occurred while fetching data for {symbol}: {df}")
                continue
            if df is not None and not df.empty:
                price_data_list.append(df[["date", "symbol", "pct_change"]])
                if "market_cap" in df.columns:
                    mktcap_data_list.append(df[["date", "symbol", "market_cap"]])
                else:
                    print(f"Warning: 'market_cap' column missing for {symbol}")

        if price_data_list:
            price_data = pd.concat(price_data_list)
            price_data = price_data.pivot(index="date", columns="symbol", values="pct_change")
            price_data.index = pd.to_datetime(price_data.index)
        else:
            price_data = pd.DataFrame()

        if mktcap_data_list:
            mktcap_data = pd.concat(mktcap_data_list)
            mktcap_data = mktcap_data.pivot(index="date", columns="symbol", values="market_cap")
            mktcap_data.index = pd.to_datetime(mktcap_data.index)
        else:
            mktcap_data = pd.DataFrame()

        if price_data.empty and mktcap_data.empty:
            return None

        return price_data, mktcap_data
    


    def get_global_articles(self,
                        symbols: Union[str, List[str]],
                        date_from: str,
                        date_to: str,
                        page: int = 1,
                        page_size: int = 1000,
                        locale: str = None,
                        sections: Union[str, List[str]] = None,
                        sentiment: bool = None) -> pd.DataFrame:
        """
        /v1/global-articles 엔드포인트 래퍼

        Parameters
        ----------
        symbols : Union[str, List[str]]
            예) "NYSE:AAPL" 또는 ["NYSE:AAPL", "MSFT"]
        date_from : str
            'YYYY-MM-DD'
        date_to : str
            'YYYY-MM-DD'
        page : int, optional
            페이지 번호 (기본 1)
        page_size : int, optional
            페이지당 개수 (기본 1000)
        locale : str, optional
            로케일(필요 시)
        sections : Union[str, List[str]], optional
            기사 섹션 필터
        sentiment : bool, optional
            감성 지표 포함 여부 (API 지원 시)

        Returns
        -------
        pd.DataFrame
            기사 목록. 없으면 빈 DataFrame.
        """
        # symbols 정상화
        if isinstance(symbols, (list, tuple, set)):
            symbols_param = ",".join(symbols)
        else:
            symbols_param = symbols

        # sections 정상화
        if sections is None:
            sections_param = None
        elif isinstance(sections, (list, tuple, set)):
            sections_param = ",".join(sections)
        else:
            sections_param = sections

        params = {
            "symbols": symbols_param,
            "date_from": date_from,
            "date_to": date_to,
            "page": page,
            "page_size": page_size,
            "locale": locale,
            "sections": sections_param,
            "sentiment": str(sentiment).lower() if isinstance(sentiment, bool) else None,
        }

        response = self._make_request(
            endpoint="/v1/global-articles",
            params=params
        )

        data = response.get("data", []) if isinstance(response, dict) else []
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        # 날짜 컬럼 정규화
        for col in ["published_at", "created_at", "updated_at"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df




    
    def _backtest_global(self, portfolio_holdings, price_data, initial_capital=100_000_000_000, verbose=0, fee=0.0025):
        """
        포트폴리오 백테스트를 수행하는 함수
        
        Parameters:
        -----------
        portfolio_holdings : DataFrame
            리밸런싱 일자별 포트폴리오 정보를 담은 데이터프레임
            (date, symbol, weight 컬럼 필수)
        price_data : DataFrame
            일별 수익률 데이터 (index: date, columns: symbols)
        initial_capital : float
            초기 투자금액
        verbose : int
            0: 출력 없음
            1: 리밸런싱 시점의 포트폴리오 가치만 출력
            2: 상세 정보 출력
        fee : float
            수수료
        Returns:
        --------
        tuple
            (포트폴리오 전체 가치 변화, 종목별 가치 변화)
        """
        
        def calculate_period_returns(start_date, end_date, symbols, weights, capital):
            """특정 기간의 수익률을 계산"""
            period_data = price_data.loc[start_date:end_date, symbols].iloc[1:]
            
            # 초기 투자금 분배
            initial_distribution = weights * capital
            initial_weights = initial_distribution.reindex(
                columns=['weight'], 
                index=period_data.columns
            )
            
            if verbose >= 2:
                print(f"\nInitial distribution for period {start_date} to {end_date}:")
                print(initial_distribution)
            
            # 수익률 계산 (1을 더해 복리 수익률 계산)
            return period_data.add(1).cumprod().multiply(initial_weights['weight'], axis=1)
        
        # 포트폴리오 데이터 전처리
        # print(portfolio_holdings)
        test_port = portfolio_holdings.copy().set_index(["date"])
        rebalancing_dates = test_port.index.unique()
        
        if verbose >= 1:
            print(f"\nStarting backtest with initial capital: {initial_capital:,.0f}")
            print(f"Number of rebalancing periods: {len(rebalancing_dates)}")
        
        # 백테스트 실행
        portfolio_value = pd.DataFrame()
        current_capital = initial_capital
        
        for idx, date in enumerate(rebalancing_dates):
            if verbose >= 2:
                print(f"\n{'='*50}")
                print(f"Processing rebalancing period {idx+1}/{len(rebalancing_dates)}")
                print(f"Date: {date}")
            
            # 리밸런싱 기간 설정
            start_date = rebalancing_dates[idx]
            try:
                end_date = rebalancing_dates[idx + 1]
            except IndexError:
                end_date = datetime.today().date()
                
            # 현재 포트폴리오 구성 가져오기
            current_symbols = test_port.loc[test_port.index == date]["symbol"].tolist()
            current_weights = test_port.loc[test_port.index == date][["symbol", "weight"]].set_index("symbol")
            
            if verbose >= 2:
                print(f"\nCurrent portfolio composition:")
                print(current_weights)
            
            # 기간별 수익률 계산
            period_value = calculate_period_returns(
                start_date, 
                end_date, 
                current_symbols, 
                current_weights, 
                current_capital
            )
            
            # 다음 리밸런싱을 위한 포트폴리오 가치 업데이트
            try:
                previous_capital = current_capital
                current_capital = period_value.iloc[-1].sum()
                
                if verbose >= 1:
                    period_return = (current_capital - previous_capital) / previous_capital * 100
                    print(f"Period {idx+1} ({start_date.date()} to {end_date.date()}): Portfolio value: {current_capital:,.0f} ({period_return:+.2f}%)")
                    
                if verbose >= 2:
                    print("\nTop gainers and losers:")
                    period_returns = (period_value.iloc[-1] - period_value.iloc[0]) / period_value.iloc[0] * 100
                    print("\nTop 5 gainers:")
                    print(period_returns.nlargest(5))
                    print("\nTop 5 losers:")
                    print(period_returns.nsmallest(5))
                    
            except Exception as e:
                if verbose >= 1:
                    print(f"\nError updating portfolio value: {e}")
                pass
                
            # 결과 저장
            portfolio_value = pd.concat([portfolio_value, period_value])
        
        # 전체 포트폴리오 가치 계산
        total_value = portfolio_value.sum(axis=1)
        
        if verbose >= 1:
            total_return = (total_value.iloc[-1] - initial_capital) / initial_capital * 100
            print(f"\nBacktest completed:")
            print(f"Final portfolio value: {total_value.iloc[-1]:,.0f}")
            print(f"Total return: {total_return:+.2f}%")
            print(f"Number of trading days: {len(total_value)}")
            
        if verbose >= 2:
            print("\nTop gainers and losers:")
            try:
                if len(period_value) > 0:  # 데이터가 있는 경우에만 계산
                    # 각 종목의 기간 수익률 계산
                    period_returns = (period_value.iloc[-1] - period_value.iloc[0]) / period_value.iloc[0] * 100
                    
                    # 수익률과 함께 금액 변화도 표시
                    period_analysis = pd.DataFrame({
                        'start_value': period_value.iloc[0],
                        'end_value': period_value.iloc[-1],
                        'abs_change': period_value.iloc[-1] - period_value.iloc[0],
                        'pct_change': period_returns
                    })
                    
                    print("\nTop 5 gainers:")
                    print(period_analysis.nlargest(5, 'pct_change').round(2))
                    print("\nTop 5 losers:")
                    print(period_analysis.nsmallest(5, 'pct_change').round(2))
                else:
                    print("No data available for this period")
            except Exception as e:
                print(f"Error calculating period returns: {e}")
        
        return total_value, portfolio_value


    def backtest_global(self, portfolio_holdings, price_data, initial_capital=100_000_000_000, verbose=0, fee=0.0025):
        """
        포트폴리오 백테스트를 수행하는 함수
        
        Parameters:
        -----------
        portfolio_holdings : DataFrame
            리밸런싱 일자별 포트폴리오 정보를 담은 데이터프레임
            (date, symbol, weight 컬럼 필수)
        price_data : DataFrame
            일별 수익률 데이터 (index: date, columns: symbols)
        initial_capital : float
            초기 투자금액
        verbose : int
            0: 출력 없음
            1: 리밸런싱 시점의 포트폴리오 가치만 출력
            2: 상세 정보 출력
        fee : float
            수수료 (회전율에 대한 비율)
        Returns:
        --------
        tuple
            (포트폴리오 전체 가치 변화, 종목별 가치 변화)
        """
        
        def calculate_period_returns(start_date, end_date, symbols, weights, capital):
            """특정 기간의 수익률을 계산"""
            period_data = price_data.loc[start_date:end_date, symbols].iloc[1:]
            
            # 초기 투자금 분배
            initial_distribution = weights * capital
            initial_weights = initial_distribution.reindex(
                columns=['weight'], 
                index=period_data.columns
            )
            
            if verbose >= 2:
                print(f"\nInitial distribution for period {start_date} to {end_date}:")
                print(initial_distribution)
            
            # 수익률 계산 (1을 더해 복리 수익률 계산)
            return period_data.add(1).cumprod().multiply(initial_weights['weight'], axis=1)
        
        def calculate_turnover(previous_weights, new_weights, previous_capital, current_capital):
            """포트폴리오 회전율 계산"""
            # 이전 포트폴리오의 현재 가치 기준 비중 계산
            if previous_weights is None:
                # 첫 리밸런싱인 경우 회전율 0
                return 0.0
            
            # 이전 포트폴리오의 최종 비중 (가치 변동 반영)
            prev_weights_dict = {}
            for symbol in previous_weights.index:
                if symbol in previous_capital.index:
                    prev_weights_dict[symbol] = previous_capital[symbol] / current_capital
                else:
                    prev_weights_dict[symbol] = 0
            
            # 새 포트폴리오 비중
            new_weights_dict = {}
            for symbol in new_weights.index:
                new_weights_dict[symbol] = new_weights.loc[symbol, 'weight']
            
            # 모든 종목 리스트 (이전 + 새로운)
            all_symbols = set(prev_weights_dict.keys()) | set(new_weights_dict.keys())
            
            # 회전율 계산: sum(|이전 비중 - 새 비중|) / 2
            turnover = 0
            for symbol in all_symbols:
                prev_weight = prev_weights_dict.get(symbol, 0)
                new_weight = new_weights_dict.get(symbol, 0)
                turnover += abs(new_weight - prev_weight)
            
            # Single-sided turnover (매수 또는 매도 중 하나만 계산)
            return turnover / 2
        
        # 포트폴리오 데이터 전처리
        test_port = portfolio_holdings.copy().set_index(["date"])
        rebalancing_dates = test_port.index.unique()
        
        if verbose >= 1:
            print(f"\nStarting backtest with initial capital: {initial_capital:,.0f}")
            print(f"Number of rebalancing periods: {len(rebalancing_dates)}")
            print(f"Transaction fee rate: {fee:.4f}")
        
        # 백테스트 실행
        portfolio_value = pd.DataFrame()
        current_capital = initial_capital
        previous_weights = None
        previous_period_value = None
        total_fees_paid = 0  # 누적 수수료 추적
        
        for idx, date in enumerate(rebalancing_dates):
            if verbose >= 2:
                print(f"\n{'='*50}")
                print(f"Processing rebalancing period {idx+1}/{len(rebalancing_dates)}")
                print(f"Date: {date}")
            
            # 리밸런싱 기간 설정
            start_date = rebalancing_dates[idx]
            try:
                end_date = rebalancing_dates[idx + 1]
            except IndexError:
                end_date = datetime.today().date()
                
            # 현재 포트폴리오 구성 가져오기
            current_symbols = test_port.loc[test_port.index == date]["symbol"].tolist()
            current_weights = test_port.loc[test_port.index == date][["symbol", "weight"]].set_index("symbol")
            
            # 리밸런싱 수수료 계산 (첫 번째 리밸런싱 제외)
            if idx > 0 and previous_period_value is not None:
                # 이전 기간 종료 시점의 각 종목별 가치
                turnover = calculate_turnover(
                    previous_weights, 
                    current_weights,
                    previous_period_value.iloc[-1] if len(previous_period_value) > 0 else pd.Series(),
                    current_capital
                )
                
                # 수수료 적용
                transaction_cost = turnover * current_capital * fee
                current_capital -= transaction_cost
                total_fees_paid += transaction_cost
                
                if verbose >= 1:
                    print(f"Rebalancing turnover: {turnover:.2%}")
                    print(f"Transaction cost: {transaction_cost:,.0f}")
                    print(f"Capital after fees: {current_capital:,.0f}")
            
            if verbose >= 2:
                print(f"\nCurrent portfolio composition:")
                print(current_weights)
            
            # 기간별 수익률 계산
            period_value = calculate_period_returns(
                start_date, 
                end_date, 
                current_symbols, 
                current_weights, 
                current_capital
            )
            
            # 다음 리밸런싱을 위한 정보 저장
            previous_weights = current_weights
            previous_period_value = period_value
            
            # 다음 리밸런싱을 위한 포트폴리오 가치 업데이트
            try:
                previous_capital = current_capital
                current_capital = period_value.iloc[-1].sum()
                
                if verbose >= 1:
                    period_return = (current_capital - previous_capital) / previous_capital * 100
                    print(f"Period {idx+1} ({start_date.date()} to {end_date.date()}): Portfolio value: {current_capital:,.0f} ({period_return:+.2f}%)")
                    
                if verbose >= 2:
                    print("\nTop gainers and losers:")
                    period_returns = (period_value.iloc[-1] - period_value.iloc[0]) / period_value.iloc[0] * 100
                    print("\nTop 5 gainers:")
                    print(period_returns.nlargest(5))
                    print("\nTop 5 losers:")
                    print(period_returns.nsmallest(5))
                    
            except Exception as e:
                if verbose >= 1:
                    print(f"\nError updating portfolio value: {e}")
                pass
                
            # 결과 저장
            portfolio_value = pd.concat([portfolio_value, period_value])
        
        # 전체 포트폴리오 가치 계산
        total_value = portfolio_value.sum(axis=1)
        
        if verbose >= 1:
            total_return = (total_value.iloc[-1] - initial_capital) / initial_capital * 100
            print(f"\nBacktest completed:")
            print(f"Final portfolio value: {total_value.iloc[-1]:,.0f}")
            print(f"Total return: {total_return:+.2f}%")
            print(f"Total transaction fees paid: {total_fees_paid:,.0f}")
            print(f"Fees as % of initial capital: {total_fees_paid/initial_capital:.2%}")
            print(f"Number of trading days: {len(total_value)}")
            
        if verbose >= 2:
            print("\nTop gainers and losers:")
            try:
                if len(period_value) > 0:  # 데이터가 있는 경우에만 계산
                    # 각 종목의 기간 수익률 계산
                    period_returns = (period_value.iloc[-1] - period_value.iloc[0]) / period_value.iloc[0] * 100
                    
                    # 수익률과 함께 금액 변화도 표시
                    period_analysis = pd.DataFrame({
                        'start_value': period_value.iloc[0],
                        'end_value': period_value.iloc[-1],
                        'abs_change': period_value.iloc[-1] - period_value.iloc[0],
                        'pct_change': period_returns
                    })
                    
                    print("\nTop 5 gainers:")
                    print(period_analysis.nlargest(5, 'pct_change').round(2))
                    print("\nTop 5 losers:")
                    print(period_analysis.nsmallest(5, 'pct_change').round(2))
                else:
                    print("No data available for this period")
            except Exception as e:
                print(f"Error calculating period returns: {e}")
        
        return total_value, portfolio_value