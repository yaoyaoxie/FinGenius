"""
Ollama客户端包装器，确保base_url不被修改
"""
import httpx
from openai import AsyncOpenAI
from src.logger import logger


class OllamaAsyncOpenAI(AsyncOpenAI):
    """
    专门为Ollama设计的AsyncOpenAI包装器
    确保base_url不会被SDK内部逻辑修改
    """
    
    def __init__(self, base_url: str, api_key: str = "ollama", **kwargs):
        # 记录原始base_url
        self._original_base_url = base_url
        logger.info(f"OllamaAsyncOpenAI initializing with base_url: {base_url}")
        
        # 创建自定义HTTP客户端，确保请求发送到正确的地址
        http_client = httpx.AsyncClient(
            base_url=base_url,
            timeout=kwargs.get('timeout', 300.0),
            follow_redirects=False,  # 禁用重定向
        )
        
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            http_client=http_client,
            **kwargs
        )
        
        logger.info(f"OllamaAsyncOpenAI initialized successfully")
        logger.info(f"  - Original base_url: {self._original_base_url}")
        logger.info(f"  - SDK base_url: {self.base_url}")
    
    async def chat_completions_create(self, **kwargs):
        """
        重写chat.completions.create方法，添加调试信息
        """
        logger.info(f"Ollama API call:")
        logger.info(f"  - Target URL: {self._original_base_url}")
        logger.info(f"  - Model: {kwargs.get('model', 'Unknown')}")
        logger.info(f"  - Stream: {kwargs.get('stream', False)}")
        
        try:
            response = await super().chat.completions.create(**kwargs)
            logger.info(f"Ollama API call successful")
            return response
        except Exception as e:
            logger.error(f"Ollama API call failed: {str(e)}")
            logger.error(f"  - Exception type: {type(e).__name__}")
            raise
