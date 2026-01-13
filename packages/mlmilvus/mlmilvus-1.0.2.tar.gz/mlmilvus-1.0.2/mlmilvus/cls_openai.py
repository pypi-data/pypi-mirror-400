from typing import Awaitable, Callable
from .base import Milvuser, AMilvuser
try:
    from openai import OpenAI, AsyncOpenAI, NOT_GIVEN
except ImportError:
    raise ImportError('pip install openai')


class OpenaiMilvuser(Milvuser):
    """使用openai接口加载模型
    """
    def _waits_to_vectors_func(self, model, waits):
        datas = model.embeddings.create(input=waits, model=self.embeddings_model, dimensions=self.dimension).data
        return [data.embedding for data in datas]
        
    def __init__(self, url:str, openai_url:str, embeddings_model:str, default_col:str, datas_to_waits_func:Callable[[list[dict]], list],
                 api_key:str='EMPTY', user: str = "", password: str = "", db_name: str = "", dimensions:int=None, **_):
        super().__init__(url, get_model=lambda: OpenAI(base_url=openai_url,api_key=api_key), 
                         default_col=default_col, datas_to_waits_func=datas_to_waits_func,
                         waits_to_vectors_func=self._waits_to_vectors_func, 
                        user=user, password=password, db_name=db_name)
        self.dimension=dimensions or NOT_GIVEN
        self.embeddings_model=embeddings_model

class AOpenaiMilvuser(AMilvuser):
    """使用openai接口加载模型
    """
    async def _waits_to_vectors_func(self, model, waits):
        datas = (await model.embeddings.create(input=waits, model=self.embeddings_model, dimensions=self.dimension)).data
        return [data.embedding for data in datas]
        
    def __init__(self, url:str, openai_url:str, embeddings_model:str, default_col:str, adatas_to_waits_func:Callable[[list[dict]], Awaitable[list]],
                 api_key:str='EMPTY', user: str = "", password: str = "", db_name: str = "", dimensions:int=None, async_limit: int = 200, **_):
        super().__init__(url, get_model=lambda: AsyncOpenAI(base_url=openai_url,api_key=api_key), 
                         default_col=default_col, adatas_to_waits_func=adatas_to_waits_func,
                         awaits_to_vectors_func=self._waits_to_vectors_func, 
                        user=user, password=password, db_name=db_name, async_limit=async_limit)
        self.dimension=dimensions or NOT_GIVEN
        self.embeddings_model=embeddings_model