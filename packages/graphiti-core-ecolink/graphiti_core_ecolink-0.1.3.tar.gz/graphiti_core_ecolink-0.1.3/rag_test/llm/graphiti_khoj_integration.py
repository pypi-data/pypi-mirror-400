"""
Graphiti与Khoj本地向量化集成
将Khoj的本地向量化功能直接集成到Graphiti中，替换云端API调用
"""

import asyncio
import logging
from typing import Optional, List
from graphiti_core import Graphiti
from graphiti_core.llm_client import LLMConfig
from graphiti_core.embedder.client import EmbedderClient

from llm.khoj_local_embedder import KhojLocalEmbedder, KhojLocalEmbedderConfig, create_khoj_embedder, create_preset_embedder
from llm.aliyun_llm_client import AliyunLLMClient

logger = logging.getLogger(__name__)

class GraphitiKhojIntegration:
    """
    Graphiti与Khoj本地向量化集成类
    提供完整的本地化RAG解决方案
    """
    
    def __init__(self, 
                 neo4j_uri: str,
                 neo4j_user: str, 
                 neo4j_password: str,
                 llm_api_key: str,
                 llm_base_url: str,
                 embedding_model_name: str = "thenlper/gte-small",
                 embedding_device: str = "auto"):
        """
        初始化Graphiti-Khoj集成
        
        Args:
            neo4j_uri: Neo4j数据库URI
            neo4j_user: Neo4j用户名
            neo4j_password: Neo4j密码
            llm_api_key: LLM API密钥
            llm_base_url: LLM API基础URL
            embedding_model_name: 本地向量化模型名称
            embedding_device: 向量化设备
        """
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.llm_api_key = llm_api_key
        self.llm_base_url = llm_base_url
        self.embedding_model_name = embedding_model_name
        self.embedding_device = embedding_device
        
        self.graphiti: Optional[Graphiti] = None
        self.embedder: Optional[KhojLocalEmbedder] = None
        self.llm_client: Optional[AliyunLLMClient] = None
    
    async def initialize(self, 
                        llm_model: str = "qwen-turbo",
                        temperature: float = 0.3,
                        max_tokens: int = 4096,
                        embedding_preset: str = "lightweight"):
        """
        初始化Graphiti实例，使用Khoj本地向量化
        
        Args:
            llm_model: LLM模型名称
            temperature: LLM温度参数
            max_tokens: 最大token数
            embedding_preset: 向量化预设配置
        """
        try:
            logger.info("正在初始化Graphiti-Khoj集成...")
            
            # 1. 创建LLM客户端
            llm_config = LLMConfig(
                api_key=self.llm_api_key,
                base_url=self.llm_base_url,
                model=llm_model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            self.llm_client = AliyunLLMClient(config=llm_config)
            logger.info(f"LLM客户端初始化完成: {llm_model}")
            
            # 2. 创建Khoj本地向量化嵌入器
            if embedding_preset in ["lightweight", "high_performance", "chinese", "multilingual"]:
                self.embedder = create_preset_embedder(embedding_preset)
            else:
                self.embedder = create_khoj_embedder(
                    model_name=self.embedding_model_name,
                    device=self.embedding_device
                )
            logger.info(f"本地向量化嵌入器初始化完成: {self.embedder.config.model_name}")
            
            # 3. 初始化Graphiti
            self.graphiti = Graphiti(
                self.neo4j_uri,
                self.neo4j_user,
                self.neo4j_password,
                llm_client=self.llm_client,
                embedder=self.embedder
            )
            
            # 4. 初始化数据库索引
            await self.graphiti.build_indices_and_constraints()
            logger.info("Graphiti初始化完成，数据库索引已构建")
            
            # 5. 输出配置信息
            model_info = self.embedder.get_model_info()
            logger.info(f"集成配置信息:")
            logger.info(f"  - LLM模型: {llm_model}")
            logger.info(f"  - 向量化模型: {model_info['model_name']}")
            logger.info(f"  - 向量维度: {model_info['embedding_dim']}")
            logger.info(f"  - 设备: {model_info['device']}")
            logger.info(f"  - 归一化: {model_info['normalize_embeddings']}")
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
    
    async def add_episode_with_local_embedding(self, 
                                             name: str, 
                                             content: str, 
                                             description: str = "用户输入",
                                             group_id: str = None) -> str:
        """
        使用本地向量化添加episode
        
        Args:
            name: episode名称
            content: episode内容
            description: episode描述
            group_id: 组ID
        
        Returns:
            str: episode的UUID
        """
        if self.graphiti is None:
            raise RuntimeError("Graphiti未初始化，请先调用initialize()方法")
        
        try:
            logger.info(f"正在添加episode（使用本地向量化）: {name}")
            
            # 使用Graphiti添加episode，会自动使用本地向量化
            result = await self.graphiti.add_episode(
                name=name,
                episode_body=content,
                source_description=description,
                group_id=group_id
            )
            
            logger.info(f"成功添加episode: {name}")
            return result.episode.uuid
            
        except Exception as e:
            logger.error(f"添加episode失败: {e}")
            raise
    
    async def search_with_local_embedding(self, 
                                        query: str, 
                                        search_type: str = "comprehensive",
                                        limit: int = 20,
                                        group_ids: List[str] = None) -> dict:
        """
        使用本地向量化进行搜索
        
        Args:
            query: 搜索查询
            search_type: 搜索类型
            limit: 结果数量限制
            group_ids: 组ID列表
        
        Returns:
            dict: 搜索结果
        """
        if self.graphiti is None:
            raise RuntimeError("Graphiti未初始化，请先调用initialize()方法")
        
        try:
            logger.info(f"正在搜索（使用本地向量化）: {query}")
            
            # 使用Graphiti进行搜索，会自动使用本地向量化
            from graphiti_core.search.search_config import SearchConfig, EdgeSearchConfig, NodeSearchConfig, EpisodeSearchConfig
            from graphiti_core.search.search_config import EdgeSearchMethod, NodeSearchMethod, EpisodeSearchMethod
            from graphiti_core.search.search_config import EdgeReranker, NodeReranker, EpisodeReranker
            
            search_config = SearchConfig(
                edge_config=EdgeSearchConfig(
                    search_methods=[EdgeSearchMethod.bm25, EdgeSearchMethod.cosine_similarity],
                    reranker=EdgeReranker.rrf
                ),
                node_config=NodeSearchConfig(
                    search_methods=[NodeSearchMethod.bm25, NodeSearchMethod.cosine_similarity],
                    reranker=NodeReranker.rrf
                ),
                episode_config=EpisodeSearchConfig(
                    search_methods=[EpisodeSearchMethod.bm25],
                    reranker=EpisodeReranker.rrf
                ),
                limit=limit,
                reranker_min_score=0.3
            )
            
            results = await self.graphiti.search_(
                query=query,
                config=search_config,
                group_ids=group_ids
            )
            
            logger.info(f"搜索完成，找到 {results.total_count} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise
    
    async def close(self):
        """关闭连接"""
        if self.graphiti:
            await self.graphiti.close()
            logger.info("Graphiti连接已关闭")
        
        if self.llm_client and hasattr(self.llm_client, 'close'):
            await self.llm_client.close()
            logger.info("LLM客户端已关闭")
    
    def get_embedding_info(self) -> dict:
        """获取向量化信息"""
        if self.embedder:
            return self.embedder.get_model_info()
        return {}
    
    def test_embedding(self, text: str = "测试文本") -> dict:
        """测试向量化功能"""
        if not self.embedder:
            return {"error": "嵌入器未初始化"}
        
        try:
            # 测试单个文本向量化
            start_time = asyncio.get_event_loop().time()
            embedding = self.embedder.embed_query(text)
            single_time = asyncio.get_event_loop().time() - start_time
            
            # 测试批量向量化
            test_texts = [f"测试文本{i}" for i in range(5)]
            start_time = asyncio.get_event_loop().time()
            batch_embeddings = self.embedder.embed_documents(test_texts)
            batch_time = asyncio.get_event_loop().time() - start_time
            
            return {
                "success": True,
                "single_embedding_time": single_time,
                "batch_embedding_time": batch_time,
                "embedding_dimension": len(embedding),
                "model_info": self.embedder.get_model_info()
            }
        except Exception as e:
            return {"error": str(e)}


# ==================== 便捷函数 ====================

async def create_graphiti_with_khoj_embedding(
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    llm_api_key: str,
    llm_base_url: str,
    embedding_preset: str = "lightweight",
    llm_model: str = "qwen-turbo"
) -> GraphitiKhojIntegration:
    """
    快速创建带有Khoj本地向量化的Graphiti实例
    
    Args:
        neo4j_uri: Neo4j数据库URI
        neo4j_user: Neo4j用户名
        neo4j_password: Neo4j密码
        llm_api_key: LLM API密钥
        llm_base_url: LLM API基础URL
        embedding_preset: 向量化预设配置
        llm_model: LLM模型名称
    
    Returns:
        GraphitiKhojIntegration: 初始化完成的集成实例
    """
    integration = GraphitiKhojIntegration(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        llm_api_key=llm_api_key,
        llm_base_url=llm_base_url
    )
    
    await integration.initialize(
        llm_model=llm_model,
        embedding_preset=embedding_preset
    )
    
    return integration


# ==================== 使用示例 ====================

async def example_usage():
    """使用示例"""
    # 配置参数
    NEO4J_URI = "bolt://192.168.3.102:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password"
    LLM_API_KEY = "sk-12924ea745d84ff59c6aea09ffe2a343"
    LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 创建集成实例
    integration = await create_graphiti_with_khoj_embedding(
        neo4j_uri=NEO4J_URI,
        neo4j_user=NEO4J_USER,
        neo4j_password=NEO4J_PASSWORD,
        llm_api_key=LLM_API_KEY,
        llm_base_url=LLM_BASE_URL,
        embedding_preset="lightweight"  # 使用轻量级配置
    )
    
    try:
        # 测试向量化功能
        test_result = integration.test_embedding("这是一个测试文本")
        print(f"向量化测试结果: {test_result}")
        
        # 添加episode
        episode_uuid = await integration.add_episode_with_local_embedding(
            name="测试episode",
            content="这是一个使用本地向量化的测试内容",
            description="本地向量化测试"
        )
        print(f"添加episode成功: {episode_uuid}")
        
        # 搜索
        search_results = await integration.search_with_local_embedding(
            query="测试内容",
            limit=5
        )
        print(f"搜索结果: {search_results}")
        
    finally:
        # 关闭连接
        await integration.close()


if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_usage())
