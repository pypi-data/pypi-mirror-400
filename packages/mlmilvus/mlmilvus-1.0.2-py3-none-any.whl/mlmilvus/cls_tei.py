from typing import Awaitable, Callable
from .base import Milvuser, AMilvuser
try:
    from httpx import AsyncClient, Client
except ImportError:
    raise ImportError('pip install httpx')


class TEIMilvuser(Milvuser):
    """使用tei接口加载模型
    """
    def _waits_to_vectors_func(self, model:Client, waits):
        rep = model.post(
                self.tei_url,
                json={"inputs": waits}
            )
        result = rep.json()
        assert isinstance(result, list), f"tei接口返回数据异常 {result}"
        return result
        
    def __init__(self, url:str, tei_url:str, default_col:str, datas_to_waits_func:Callable[[list[dict]], list],
                 user: str = "", password: str = "", db_name: str = "", **_):
        super().__init__(url, get_model=lambda: Client(timeout=15), 
                         default_col=default_col, datas_to_waits_func=datas_to_waits_func,
                         waits_to_vectors_func=self._waits_to_vectors_func, 
                        user=user, password=password, db_name=db_name)
        self.tei_url = tei_url.strip('/') + '/embed'
        
class ATEIMilvuser(AMilvuser):
    """使用tei接口加载模型
    """
    async def _waits_to_vectors_func(self, model:AsyncClient, waits):
        rep = await model.post(
                        self.tei_url,
                        json={"inputs": waits}
                    )
        result = rep.json()
        assert isinstance(result, list), f"tei接口返回数据异常 {result}"
        return result
        
    def __init__(self, url:str, tei_url:str, default_col:str, adatas_to_waits_func:Callable[[list[dict]], Awaitable[list]],
                 user: str = "", password: str = "", db_name: str = "", async_limit: int = 200, **_):
        super().__init__(url, get_model=lambda: AsyncClient(timeout=15), 
                         default_col=default_col, adatas_to_waits_func=adatas_to_waits_func,
                         awaits_to_vectors_func=self._waits_to_vectors_func, 
                        user=user, password=password, db_name=db_name, async_limit=async_limit)
        self.tei_url = tei_url.strip('/') + '/embed'