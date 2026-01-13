import asyncio
from threading import Thread, Lock
import time
from typing import Any, Callable, Awaitable
from pymilvus import MilvusClient, AsyncMilvusClient
from torch import Tensor


# def getMD5(bt: bytes)->str:
#     md5 = hashlib.md5()
#     md5.update(bt)
#     return md5.hexdigest()

def _limit(afunc):
    async def _main(self, *args, **kwargs):
        async with self._sem:
            return await afunc(self, *args, **kwargs)
    
    return _main

class Milvuser:
    def __init__(self, url:str, get_model:Callable, default_col:str, 
                 datas_to_waits_func:Callable[[list[dict]], list],
                 waits_to_vectors_func:Callable[[Any, list[Any]], list[list]],
                 user: str = "", password: str = "", db_name: str = ""):
        self.client:MilvusClient=None
        self._lock = Lock()
        self.url = url
        self.get_model = get_model
        self.default_col = default_col
        self.datas_to_waits_func=datas_to_waits_func
        self.waits_to_vectors_func=waits_to_vectors_func
        self._user = user
        self._pwd = password
        self._db_name = db_name
        self.model = None
    
    def init_model(self):
        self.model = self.model or self.get_model()
        
    def getClient(self)->AsyncMilvusClient:
        client = AsyncMilvusClient(self.url, self._user, self._pwd, self._db_name)
        return client
    
    def getClient(self)->MilvusClient:
        client = MilvusClient(self.url, self._user, self._pwd, self._db_name)
        return client
            
    def client_auto_reset(self, s=600):
        def temp():
            while True:
                time.sleep(s)
                with self._lock:
                    self.client.close()
                    self.client = self.getClient()
        Thread(target=temp, daemon=True).start()
        
    def create_collection(self, dimension:int, col:str=None, id_type:str='int', primary_field_name='id', max_length=None, **kwargs):
        self.client = self.client or self.getClient()
        if self.client.has_collection(col or self.default_col): return None
        return self.client.create_collection(
                                collection_name=col or self.default_col,
                                primary_field_name=primary_field_name,
                                dimension=dimension,  # 维度
                                id_type = id_type,
                                max_length=max_length,
                                **kwargs
                            )
            
    def drop_collection(self, col:str=None, **kwargs):
        self.client = self.client or self.getClient()
        if not self.client.has_collection(col or self.default_col): return None
        return self.client.create_collection(
                                collection_name=col or self.default_col,
                                **kwargs
                            )

    def update_insert(self, *datas:dict, col:str=None)->dict:
        self.init_model()
        waitvs = self.datas_to_waits_func(datas)
        vcs = self.waits_to_vectors_func(self.model, waitvs)
        rs = [{**data, 'vector': vector} for data, vector in zip(datas, vcs)]
        self.client = self.client or self.getClient()
        return self.client.insert(col or self.default_col, rs)
    
    def update(self, mid, data:dict, col:str=None)->bool:
        dts = self.query(ids=[mid])
        if not dts: return False
        dt = dts[0]
        rt = {**dt, **data}
        self.client = self.client or self.getClient()
        return bool(self.client.upsert(col or self.default_col, rt).get('upsert_count'))
    
    def search(self, *querys:Any|Tensor|list, min_similarity:float=0.5, limit:int=3, col:str=None, output_fields:list[str]=None,
               filter:str='', filter_params:dict=None, **kwargs)->list[dict]|list[list[dict]]:
        """
        向量相似度搜索, 默认余弦选相似度计算, 值与相似度成正比  
        返回字段包含id、distance、output_fields中的字段  
        is null语法在milvus lite中不支持  
        """
        if isinstance(querys[0], Tensor):
            vc = [v.tolist() for v in querys]
        elif isinstance(querys[0], list):
            vc = list(querys)
        else:
            self.init_model()
            vc = self.waits_to_vectors_func(self.model, querys)
        self.client = self.client or self.getClient()
        res = self.client.search(col or self.default_col, vc, limit=limit, 
                                output_fields=output_fields,
                                filter=filter,
                                filter_params=filter_params or {},
                                # 相似度取值范围
                                search_params={"params": {
                                                    "radius": min_similarity,
                                                # "range_filter": 1.0 # =最大值限制, 因为精度问题相同文件的值可能微大于1.0
                                                    }
                                                },
                                **kwargs)
        datas = [[{**dt.pop('entity'), **dt} for dt in cres] for cres in res]
        return datas if len(querys)>1 else datas[0]
    
    def query(self, limit:int=10, col:str=None, ids:list=None, output_fields:list=None,
              filter:str='', filter_params:dict=None, **kwargs)-> list[dict]:
        self.client = self.client or self.getClient()
        res = self.client.query(col or self.default_col, filter=filter, filter_params=filter_params or {}, 
                                limit=limit, ids=ids, output_fields=output_fields, **kwargs)
        return list(res)
    
    def delete(self, filter:str, filter_params:dict=None, ids:list=None, col:str = None)-> list[dict]:
        self.client = self.client or self.getClient()
        res = self.client.delete(col or self.default_col, filter=filter, filter_params=filter_params or {}, ids=ids)
        return res
    
    # def all_count(self, col:str=None, time_wait: float=3)->int:
    #     self.client = self.client or self.getClient()
    #     self.client.flush(col or self.default_col)
    #     time.sleep(time_wait)
    #     return self.client.get_collection_stats(col or self.default_col)['row_count']
    
class AMilvuser:
    def __init__(self, url:str, get_model:Callable, default_col:str,
                 adatas_to_waits_func:Callable[[list[dict]], Awaitable[list]],
                 awaits_to_vectors_func:Callable[[Any, list[Any]], Awaitable[list[list]]],
                 user: str = "", password: str = "", db_name: str = "",
                 async_limit: int = 200):
        self.client:AsyncMilvusClient=None
        self.url = url
        self.get_model = get_model
        self.default_col = default_col
        self.adatas_to_waits_func=adatas_to_waits_func
        self.awaits_to_vectors_func=awaits_to_vectors_func
        self._user = user
        self._pwd = password
        self._db_name = db_name
        self.model = None
        self._sem = asyncio.Semaphore(async_limit)
    
    def init_model(self):
        self.model = self.model or self.get_model()
        
    def getClient(self)->AsyncMilvusClient:
        client = AsyncMilvusClient(self.url, self._user, self._pwd, self._db_name)
        return client
    
    async def client_reset(self):
        if self.client: await self.client.close()
        self.client = self.getClient()
            
    async def client_auto_reset(self, s=600):
        while True:
            await asyncio.sleep(s)
            await self.client.close()
            self.client = self.getClient()

    @_limit
    async def create_collection(self, dimension:int, col:str=None, id_type:str='int', primary_field_name='id', max_length=None, **kwargs):
        self.client = self.client or self.getClient()
        if await self.client.has_collection(col or self.default_col): return None
        return await self.client.create_collection(
                                    collection_name=col or self.default_col,
                                    primary_field_name=primary_field_name,
                                    dimension=dimension,  # 维度
                                    id_type = id_type,
                                    max_length=max_length,
                                    **kwargs
                                )
    
    @_limit
    async def drop_collection(self, col:str=None, **kwargs):
        self.client = self.client or self.getClient()
        return await self.client.drop_collection(
                                    collection_name=col or self.default_col,
                                    **kwargs
                                )        
    
    @_limit
    async def update_insert(self, *datas:dict, col:str=None)->dict:
        self.init_model()
        waitvs = await self.adatas_to_waits_func(datas)
        vcs = await self.awaits_to_vectors_func(self.model, waitvs)
        rs = [{**data, 'vector': vector} for data, vector in zip(datas, vcs)]
        self.client = self.client or self.getClient()
        return await self.client.insert(col or self.default_col, rs)
    
    @_limit
    async def update(self, mid, data:dict, col:str=None)->bool:
        dts = await self.query(ids=[mid])
        if not dts: return False
        dt = dts[0]
        rt = {**dt, **data}
        self.client = self.client or self.getClient()
        # {'upsert_count': 1}
        return bool((await self.client.upsert(col or self.default_col, rt)).get('upsert_count'))
    
    @_limit
    async def search(self, *querys:Any|Tensor|list, min_similarity:float=0.5, limit:int=3, col:str=None, output_fields:list[str]=None, 
                      filter:str='', filter_params:dict=None, **kwargs)->list[dict]|list[list[dict]]:
        """
        向量相似度搜索, 默认余弦选相似度计算, 值与相似度成正比  
        返回字段包含id、distance、output_fields中的字段
        """
        if isinstance(querys[0], Tensor):
            vc = [v.tolist() for v in querys]
        elif isinstance(querys[0], list):
            vc = list(querys)
        else:
            self.init_model()
            vc = await self.awaits_to_vectors_func(self.model, querys)
        self.client = self.client or self.getClient()
        res = await self.client.search(col or self.default_col, vc, limit=limit, 
                                        output_fields=output_fields,
                                        filter=filter,
                                        filter_params=filter_params or {},
                                        # 相似度取值范围
                                        search_params={"params": {
                                                            "radius": min_similarity,
                                                        # "range_filter": 1.0 # =最大值限制, 因为精度问题相同文件的值可能微大于1.0
                                                            }
                                                        },
                                        **kwargs)
        datas = [[{**dt.pop('entity'), **dt} for dt in cres] for cres in res]
        return datas if len(querys)>1 else datas[0]    

    @_limit
    async def query(self, limit:int=10, col:str=None, ids:list=None, output_fields:list=None,
                     filter:str='', filter_params:dict=None, **kwargs)-> list[dict]:
        self.client = self.client or self.getClient()
        res = await self.client.query(col or self.default_col, filter=filter, filter_params=filter_params or {},
                                       limit=limit, ids=ids, output_fields=output_fields, **kwargs)
        return list(res)

    @_limit
    async def delete(self, filter:str, filter_params:dict=None, ids:list=None, col:str = None)-> list[dict]:
        self.client = self.client or self.getClient()
        res = await self.client.delete(col or self.default_col, filter=filter, filter_params=filter_params or {}, ids=ids)
        return res
    
    # async def all_count(self, col:str=None, time_wait: float=3)->int:
    #     self.client = self.client or self.getClient()
    #     await self.client.flush(col or self.default_col)
    #     await asyncio.sleep(time_wait)
    #     return (await self.client.get_collection_stats(col or self.default_col))['row_count']
    