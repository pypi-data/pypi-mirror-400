import requests
import json
import time
import polars as pl
import re   # for indicator searching
import warnings
from importlib.resources import files
warnings.filterwarnings('ignore')

__doc__ = '''
Data from China National Bureau of Statistics (NBS)

- list databases
- query region code (province-level or city-level)
- query indicator code for each database
- query data with the queried indicator code, region code (for regional database only) and period
'''

HDR = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36',
    'X-Requested-With': 'XMLHttpRequest',
}
host = 'https://data.stats.gov.cn/easyquery.htm'
dbcode_map = {
    'hgyd': 'A01',
    'hgjd': 'B01',
    'hgnd': 'C01',
    'fsyd': 'E0101',
    'fsjd': 'E0102',
    'fsnd': 'E0103',
    'csyd': 'E0104',
    'csnd': 'E0105'
}
   
class NBS:
    def __init__(self):
        self.databases = {
            'hgyd': '宏观月度',   # macro monthly, hongguan yuedu
            'hgjd': '宏观季度',   # macro quarterly, hongguan ji du
            'hgnd': '宏观年度',   # macro annual, hongguan nian du
            'fsyd': '分省月度',   # regional monthly, fen sheng yue du
            'fsjd': '分省季度',   # regional quarterly, fen sheng ji du
            'fsnd': '分省年度',   # regional annual, fen sheng nian du
            'csyd': '城市月度',   # city monthly, cheng shi yue du
            'csnd': '城市年度'    # city annual, cheng shi nian du
        }
    def regioncode(self, reg: str, *, city: bool = False) -> str:
        '''
        Get region code by region name
        **Parameters**
        - reg: short name for province-level or city-level region, e.g. "浙江" (NOT "浙江省"), "上海" (NOT "上海市")
        - city: kwd only, if True, search codes of 70 main cities
        **Returns**: region code. e.g. "330000" for "浙江", "330100" for "杭州"
        **Example**
        from nbsdata import NBS
        bs = NBS()
        bs.regioncode('浙江')   # 330000
        bs.regioncode('杭州', city = True)   # 330100
        '''
        pth = 'citycodes.csv' if city else 'provincecodes.csv'
        with files('nbsdata').joinpath('asset', pth).open('rb') as f:
            df = pl.read_csv(f, schema_overrides = {'code': pl.String})
        res = df.filter(
            pl.col('reg').str.contains(reg)
        )[0, 'code']
        return res
    def indicatorcode(self, db: str, pat: str, *, literal: bool = False) -> pl.DataFrame:
        '''
        NBS code for statistical indicator
        **Note**: ONLY those indicators in the left searching bar are included
        Indicators only appear in the right table are NOT included. Use `leafindicators()` to get these leaf indicators.
        **Parameters**
        - db: database name, e.g. 'hgnd', 'fsjd', 'csnd'
        - pat: search pattern, e.g. '人均可支配收入'
        - literal: kwd only, regexp or literal    
        **Returns**: DataFrame, searching result
        **Example**
        from nbsdata import NBS
        bs = NBS()
        bs.indicatorcode('csnd', '生产总值')
        bs.indicatorcode('hgyd', '消费价格.+上月=100')
        '''
        fl = f'indicator_{db}.csv'
        with files('nbsdata').joinpath('asset', fl).open('rb') as f:
            df = pl.read_csv(f)
        res = df.filter(
            ~pl.col('isparent'),
            pl.col('indname').str.contains(pat, literal = literal)
        )
        return res        
    def __querynbs(self, db: str, indicator: str, period: str, region: str = None, ntry: int = 5) -> dict:
        '''
        PRIVATE function to query into nbs
        **Parameters**
        - db: database, e.g. 'hgnd', 'fsnd', 'csyd'
        - indicator: indicator code. e.g. 'A020101' for '地区生产总值' in database 'fsnd' 
        - period:
            * 'LAST5', 'LAST10': recent 5 (10) periods (year for annual data, quarter for quarterly data)
            * '2025' (year 2025); '2025D' (2025Q4), '202512' (Dec., 2025)
            * '2018-2022': year 2018 to 2022 for annual data; '2018A-2022D': 2018Q1 to 2022Q4 for quarterly data
              '201801-202212': Jan. 2018 to Dec. 2022 for monthly data
        - region: region code. e.g. '330000' for '浙江' (fsnd, fsjd or fsyd); '330100' for '杭州' (csnd, csyd)
          when region is None, ALL region in regional data included
          NB: only effective for regional database, i.e. 'fsnd', 'fsjd', 'fsyd', 'csnd', 'csyd'
        - ntry: maximum numbers of trial    
        **Returns**: dict, keys: 'datanodes', 'freshsort', 'hasdatacount', 'wdnodes'
            * datanodes: list, each item is a dict of dicts ("code", "data", "wds")
            * wdnodes: list of 3 elements ('zb' (指标), 'reg' (地区), 'sj' (时间))    
        ''' 
        params = {
            'm': 'QueryData',
            'dbcode': db,
            'rowcode': 'reg' if (db[:2] in ('fs', 'cs')) and (region is None) else 'zb',
            'colcode': 'sj',
            'k1': str(int(time.time() * 1000)),
            'dfwds': '[{"wdcode":"zb","valuecode":"' + indicator + '"}, {"wdcode":"sj","valuecode":"' + period + '"}]',
            'h': '1'
        }
        if (db[:2] in ('fs', 'cs')) and (region is not None):
            params['wds'] = '[{"wdcode":"reg","valuecode":"' + region + '"}]'        
        else:
            params['wds'] = '[]'    
        ref = f'https://data.stats.gov.cn/easyquery.htm?cn={dbcode_map.get(db)}'
        HDR['Referer'] = ref
        i = 0
        while i <= ntry:
            try:
                r = requests.get(host, params = params, headers = HDR, verify = False)
                r.encoding = r.apparent_encoding
                return r.json()["returndata"]
            except:
                print("server is busy")
                time.sleep(1)
            i += 1
    def leafindicators(self, db: str, indicator: str) -> pl.DataFrame:
        '''
        Leaf indicators for a given indicator
        **Parameters**
        - db: database name, e.g. 'hgnd', 'fsjd', 'csnd'
        - indicator: non-parent indicator code queried from indicatorcode(), e.g. 'A0301' (居民人均可支配收入) in database 'fsjd'
        **Returns**: DataFrame, searching result
        **Example**
        from nbsdata import NBS
        bs = NBS()
        bs.leafindicators('fsjd', 'A0301')
        '''
        reg = None if db[:2].lower() == 'hg' else '110000'
        res = self.__querynbs(db, indicator, 'LAST5', reg)
        df = pl.from_dicts(
            res['wdnodes'][0]['nodes'],
            schema = ['code', 'name', 'unit']
        )
        return df    
    def nationaldata(self, db: str, indicator: str, period: str) -> pl.DataFrame:
        '''
        Data from database 'hgnd', 'hgjd', 'hgyd'
        **Parameters**
        - db: database, e.g. 'hgnd', 'hgjd', 'hgyd'
        - indicator: indicator code. e.g. 'A0301' for '总人口' in database 'hgnd'
        - period:
            * 'LAST5', 'LAST10': recent 5 (10) periods (year for annual data, quarter for quarterly data)
            * '2025' (year 2025); '2025D' (2025Q4), '202512' (Dec., 2025)
            * '2018-2022': year 2018 to 2022 for annual data; '2018A-2022D': 2018Q1 to 2022Q4 for quarterly data
        **Returns**: DataFrame with columns: indicator_code, indicator_name, period, value, unit
        **Example**:
        from nbsdata import NBS
        bs = NBS()
        bs.nationaldata('hgnd', 'A0301', '2010-2024')
        '''
        assert db in ('hgnd', 'hgjd', 'hgyd'), 'db out of range of national database'
        res = self.__querynbs(db, indicator, period)
        df_data = pl.from_dicts(
            res['datanodes'],
            schema = ['data', 'wds']
        ).select(
            pl.when(pl.col('data').struct.field('hasdata'))
            .then(pl.col('data').struct.field('data').cast(pl.Float64))
            .otherwise(pl.lit(None)).alias('value'),
            pl.col('wds').list.get(0).struct.field('valuecode').alias('indicator_code'),
            pl.col('wds').list.get(1).struct.field('valuecode').alias('period')
        )
        df_ind_code_name = pl.from_dicts(
            res['wdnodes'][0]['nodes'],
            schema = ['code', 'name', 'unit']
        ).rename({'code': 'indicator_code', 'name': 'indicator_name'})
        df = df_data.join(
            df_ind_code_name,
            on = 'indicator_code',
            how = 'left'
        ).select(
            pl.col('indicator_code'),
            pl.col('indicator_name'),
            pl.col('period'),
            pl.col('value'),
            pl.col('unit')
        ).sort(['indicator_code', 'period'])
        return df        
    def regionaldata(self, db: str, indicator: str, period: str, region: str = None) -> pl.DataFrame:
        '''
        Regional level data, i.e. data from database 'fsnd', 'fsjd', 'fsyd', 'csnd', 'csyd'
        **Parameters**
        - db: database, e.g. 'fsnd', 'fsjd', 'fsyd', 'csnd', 'csyd'
        - indicator: indicator code. e.g. 'A030102' for '城镇居民人均可支配收入累计值' in database 'fsjd'
          NB: For regional data, when region is None (all regions), ONLY leaf indicator is allowed!
        - period:
            * 'LAST5', 'LAST10': recent 5 (10) periods (year for annual data, quarter for quarterly data)
            * '2025' (year 2025); '2025D' (2025Q4), '202512' (Dec., 2025)
            * '2018-2022': year 2018 to 2022 for annual data; '2018A-2022D': 2018Q1 to 2022Q4 for quarterly data
        - region: region code. e.g. '330000' for '浙江'; '330100' for '杭州'
        **Returns**: DataFrame with columns: region_code, region_name, indicator_code, indicator_name, date, value
        **Example**
        from nbsdata import NBS
        bs = NBS()
        bs.regionaldata('fsjd', 'A0301', '2010A-2025C', '330000')
        '''
        assert db in ('fsnd', 'fsjd', 'fsyd', 'csnd', 'csyd'), 'db out of range of regional database'
        res = self.__querynbs(db, indicator, period, region)
        df_data = pl.from_dicts(
            res['datanodes'],
            schema = ['data', 'wds']
        ).select(
            pl.when(pl.col('data').struct.field('hasdata'))
            .then(pl.col('data').struct.field('data').cast(pl.Float64))
            .otherwise(pl.lit(None)).alias('value'),
            pl.col('wds').list.get(0).struct.field('valuecode').alias('indicator_code'),
            pl.col('wds').list.get(1).struct.field('valuecode').alias('region_code'),
            pl.col('wds').list.get(2).struct.field('valuecode').alias('period')
        )
        df_ind_code_name = pl.from_dicts(
            res['wdnodes'][0]['nodes'],
            schema = ['code', 'name', 'unit']
        ).rename({'code': 'indicator_code', 'name': 'indicator_name'})
        df_reg_code_name = pl.from_dicts(
            res['wdnodes'][1]['nodes'],
            schema = ['code', 'name']
        ).rename({'code': 'region_code', 'name': 'region_name'})
        df = df_data.join(
            df_ind_code_name,
            on = 'indicator_code',
            how = 'left'
        ).join(
            df_reg_code_name,
            on = 'region_code',
            how = 'left'
        ).select(
            pl.col('region_code'),
            pl.col('region_name'),
            pl.col('indicator_code'),
            pl.col('indicator_name'),
            pl.col('period'),
            pl.col('value'),
            pl.col('unit')
        ).sort(
            ['indicator_code', 'region_code', 'period']
        )
        return df
