import asyncio
from typing import Awaitable, Callable
from .base import Milvuser, AMilvuser
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError('pip install sentence-transformers')


class STMilvuser(Milvuser):
    """使用SentenceTransformer加载模型
    """
    def __init__(self, url:str, model_name_or_path:str, default_col:str, datas_to_waits_func:Callable[[list[dict]], list], 
                 user: str = "", password: str = "", db_name: str = "", 
                 device:str='cpu'):
        
        super().__init__(url, get_model=lambda: SentenceTransformer(model_name_or_path, device=device), 
                         default_col=default_col, datas_to_waits_func=datas_to_waits_func,
                         waits_to_vectors_func=lambda model,ls: model.encode(ls), 
                         user=user, password=password, db_name=db_name)
           
class ASTMilvuser(AMilvuser):
    """使用SentenceTransformer加载模型
    """
    async def _awaits_to_vectors_func(self, model, waits):
        return await asyncio.to_thread(model.encode, waits)
    
    def __init__(self, url:str, model_name_or_path:str, default_col:str, adatas_to_waits_func:Callable[[list[dict]], Awaitable[list]], 
                 user: str = "", password: str = "", db_name: str = "", 
                 device:str='cpu', async_limit: int = 200):
        super().__init__(url, get_model=lambda: SentenceTransformer(model_name_or_path, device=device), 
                         default_col=default_col, adatas_to_waits_func=adatas_to_waits_func,
                         awaits_to_vectors_func=self._awaits_to_vectors_func, 
                         user=user, password=password, db_name=db_name, async_limit=async_limit)