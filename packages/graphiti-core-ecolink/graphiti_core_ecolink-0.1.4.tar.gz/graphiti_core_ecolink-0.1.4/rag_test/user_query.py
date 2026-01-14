"""
Graphiti 简化查询系统
提供三种核心查询方式：
1. 关系查询 - 查找实体间的关系
2. 片段查询 - 查找文档内容
3. 全部查询 - 查找所有类型的信息
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

class SimpleQueryHandler:
    """简化查询处理器：提供三种核心查询方式"""
    
    def __init__(self, graphiti_instance, llm_client):
        self.graphiti = graphiti_instance
        self.llm_client = llm_client
    
    async def relationship_search(self, user_query: str, include_expired: bool = False, limit: int = 15, group_ids: list[str] = None):
        """关系查询：查找实体间的关系"""

        logger.info(f"关系查询: {user_query}, 包含失效关系: {include_expired}, 用户组: {group_ids}")
        
        try:
            from graphiti_core.search.search_config import (
                SearchConfig, EdgeSearchConfig, EdgeSearchMethod, EdgeReranker
            )
            from graphiti_core.search.search_filters import SearchFilters
            
            # 关系查询配置
            search_config = SearchConfig(
                edge_config=EdgeSearchConfig(
                    search_methods=[EdgeSearchMethod.bm25, EdgeSearchMethod.cosine_similarity],
                    reranker=EdgeReranker.rrf  # 改用 RRF，它提供更有意义的评分
                ),
                limit=limit,
                reranker_min_score=0.0
            )
            
            # 创建搜索过滤器
            search_filter = None
            if include_expired:
                # 包含失效关系
                search_filter = SearchFilters()
            else:
                # 排除失效关系
                from graphiti_core.search.search_filters import ComparisonOperator
                current_time = datetime.now(timezone.utc)
                search_filter = SearchFilters(
                    expired_at=[[{"date": current_time, "comparison_operator": ComparisonOperator.is_null}]],
                    invalid_at=[[{"date": current_time, "comparison_operator": ComparisonOperator.is_null}]]
                )
            
            results = await self.graphiti.search_(user_query, config=search_config, search_filter=search_filter, group_ids=group_ids)

            # 调试信息：打印原始结果结构
            logger.info(f"搜索结果类型: {type(results)}")
            logger.info(f"结果属性: {dir(results)}")
            if hasattr(results, 'edge_reranker_scores'):
                logger.info(f"边评分: {results.edge_reranker_scores}")
            if hasattr(results, 'edges'):
                logger.info(f"边数量: {len(results.edges)}")

            # 处理边结果，添加相似度评分
            edges_with_scores = []
            if hasattr(results, 'edges') and results.edges:
                edge_scores = getattr(results, 'edge_reranker_scores', [])
                logger.info(f"获取到的边评分: {edge_scores}")
                for i, edge in enumerate(results.edges):
                    score = edge_scores[i] if i < len(edge_scores) else 0.5
                    logger.info(f"边 {i}: {getattr(edge, 'fact', str(edge))} -> 评分: {score}")
                    edges_with_scores.append({
                        "edge": edge,
                        "similarity_score": score,
                        "created_at": getattr(edge, 'created_at', datetime.min)
                    })
            
            return {
                "edges": edges_with_scores,
                "nodes": [],
                "episodes": [],
                "search_type": "relationship",
                "include_expired": include_expired,
                "total_count": len(edges_with_scores)
            }
            
        except Exception as e:
            logger.error(f"关系查询失败: {e}")
            return {
                "edges": [],
                "nodes": [],
                "episodes": [],
                "search_type": "relationship",
                "include_expired": include_expired,
                "total_count": 0,
                "error": str(e)
            }

    async def episode_search(self, user_query: str, limit: int = 15, group_ids: list[str] = None):
        """片段查询：查找文档内容"""

        logger.info(f"片段查询: {user_query}, 用户组: {group_ids}")
        
        try:
            from graphiti_core.search.search_config import (
                SearchConfig, EpisodeSearchConfig, EpisodeSearchMethod, EpisodeReranker
            )
            
            # 片段查询配置
            search_config = SearchConfig(
                episode_config=EpisodeSearchConfig(
                    search_methods=[EpisodeSearchMethod.bm25],
                    reranker=EpisodeReranker.rrf  # 改用 RRF，它提供更有意义的评分
                ),
                limit=limit,
                reranker_min_score=0.0
            )

            results = await self.graphiti.search_(user_query, config=search_config, group_ids=group_ids)

            # 处理片段结果，添加相似度评分
            episodes_with_scores = []
            if hasattr(results, 'episodes') and results.episodes:
                episode_scores = getattr(results, 'episode_reranker_scores', [])
                for i, episode in enumerate(results.episodes):
                    score = episode_scores[i] if i < len(episode_scores) else 0.5
                    episodes_with_scores.append({
                        "episode": episode,
                        "similarity_score": score,
                        "created_at": getattr(episode, 'created_at', datetime.min)
                    })
            
            return {
                "edges": [],
                "nodes": [],
                "episodes": episodes_with_scores,
                "search_type": "episode",
                "total_count": len(episodes_with_scores)
            }
            
        except Exception as e:
            logger.error(f"片段查询失败: {e}")
            return {
                "edges": [],
                "nodes": [],
                "episodes": [],
                "search_type": "episode",
                "total_count": 0,
                "error": str(e)
            }

    async def comprehensive_search(self, user_query: str, include_expired: bool = False, limit: int = 20, group_ids: list[str] = None):
        """全部查询：查找所有类型的信息"""

        logger.info(f"全部查询: {user_query}, 包含失效关系: {include_expired}, 用户组: {group_ids}")
        
        try:
            from graphiti_core.search.search_config import (
                SearchConfig, EdgeSearchConfig, EdgeSearchMethod, EdgeReranker,
                NodeSearchConfig, NodeSearchMethod, NodeReranker,
                EpisodeSearchConfig, EpisodeSearchMethod, EpisodeReranker
            )
            from graphiti_core.search.search_filters import SearchFilters
            
            # 全部查询配置
            search_config = SearchConfig(
                edge_config=EdgeSearchConfig(
                    search_methods=[EdgeSearchMethod.bm25, EdgeSearchMethod.cosine_similarity],
                    reranker=EdgeReranker.rrf  # 改用 RRF，它提供更有意义的评分
                ),
                node_config=NodeSearchConfig(
                    search_methods=[NodeSearchMethod.bm25, NodeSearchMethod.cosine_similarity],
                    reranker=NodeReranker.rrf  # 改用 RRF，它提供更有意义的评分
                ),
                episode_config=EpisodeSearchConfig(
                    search_methods=[EpisodeSearchMethod.bm25],
                    reranker=EpisodeReranker.rrf  # 改用 RRF，它提供更有意义的评分
                ),
                limit=limit,
                reranker_min_score=0.0
            )
            
            # 创建搜索过滤器
            search_filter = None
            if include_expired:
                # 包含失效关系
                search_filter = SearchFilters()
            else:
                # 排除失效关系
                from graphiti_core.search.search_filters import ComparisonOperator
                current_time = datetime.now(timezone.utc)
                search_filter = SearchFilters(
                    expired_at=[[{"date": current_time, "comparison_operator": ComparisonOperator.is_null}]],
                    invalid_at=[[{"date": current_time, "comparison_operator": ComparisonOperator.is_null}]]
                )
            
            results = await self.graphiti.search_(user_query, config=search_config, search_filter=search_filter, group_ids=group_ids)

            # 处理边结果，添加相似度评分
            edges_with_scores = []
            if hasattr(results, 'edges') and results.edges:
                edge_scores = getattr(results, 'edge_reranker_scores', [])
                for i, edge in enumerate(results.edges):
                    score = edge_scores[i] if i < len(edge_scores) else 0.5
                    edges_with_scores.append({
                        "edge": edge,
                        "similarity_score": score,
                        "created_at": getattr(edge, 'created_at', datetime.min)
                    })
            
            # 处理节点结果，添加相似度评分
            nodes_with_scores = []
            if hasattr(results, 'nodes') and results.nodes:
                node_scores = getattr(results, 'node_reranker_scores', [])
                for i, node in enumerate(results.nodes):
                    score = node_scores[i] if i < len(node_scores) else 0.5
                    nodes_with_scores.append({
                        "node": node,
                        "similarity_score": score,
                        "created_at": getattr(node, 'created_at', datetime.min)
                    })
            
            # 处理片段结果，添加相似度评分
            episodes_with_scores = []
            if hasattr(results, 'episodes') and results.episodes:
                episode_scores = getattr(results, 'episode_reranker_scores', [])
                for i, episode in enumerate(results.episodes):
                    score = episode_scores[i] if i < len(episode_scores) else 0.5
                    episodes_with_scores.append({
                        "episode": episode,
                        "similarity_score": score,
                        "created_at": getattr(episode, 'created_at', datetime.min)
                    })
            
            return {
                "edges": edges_with_scores,
                "nodes": nodes_with_scores,
                "episodes": episodes_with_scores,
                "search_type": "comprehensive",
                "include_expired": include_expired,
                "total_count": len(edges_with_scores) + len(nodes_with_scores) + len(episodes_with_scores)
            }
            
        except Exception as e:
            logger.error(f"全部查询失败: {e}")
            return {
                "edges": [],
                "nodes": [],
                "episodes": [],
                "search_type": "comprehensive",
                "include_expired": include_expired,
                "total_count": 0,
                "error": str(e)
            }

    async def search(self, user_query: str, search_type: str = "comprehensive",
                    include_expired: bool = False, limit: int = 20, sort_by_similarity: bool = True,
                    group_ids: list[str] = None):
        """统一查询接口"""

        logger.info(f"查询: {user_query}, 类型: {search_type}, 用户组: {group_ids}")

        if search_type == "relationship":
            results = await self.relationship_search(user_query, include_expired, limit, group_ids)
        elif search_type == "episode":
            results = await self.episode_search(user_query, limit, group_ids)
        elif search_type == "comprehensive":
            results = await self.comprehensive_search(user_query, include_expired, limit, group_ids)
        else:
            logger.warning(f"未知查询类型: {search_type}，使用默认全部查询")
            results = await self.comprehensive_search(user_query, include_expired, limit, group_ids)

        # 按相似度排序
        if sort_by_similarity:
            results = self._sort_by_similarity(results)

            return results
        
    def _sort_by_similarity(self, results: dict) -> dict:
        """按相似度评分排序结果"""

        # 排序边结果
        if results.get("edges"):
            results["edges"] = sorted(
                results["edges"],
                key=lambda x: x["similarity_score"],
                reverse=True
            )

        # 排序节点结果
        if results.get("nodes"):
            results["nodes"] = sorted(
                results["nodes"],
                key=lambda x: x["similarity_score"],
                reverse=True
            )

        # 排序片段结果
        if results.get("episodes"):
            results["episodes"] = sorted(
                results["episodes"],
                key=lambda x: x["similarity_score"],
                reverse=True
            )

        return results

    async def generate_answer(self, search_results: dict, user_query: str):
        """根据搜索结果生成回答"""
        
        if search_results["total_count"] == 0:
            return "抱歉，我没有找到相关信息。请尝试用不同的方式描述您的问题。"
        
        answer_parts = []
        
        # 添加查询说明
        if search_results.get("include_expired"):
            answer_parts.append("**注意：本次查询包含了失效的历史关系信息**")
        
        # 1. 关系信息
        if search_results["edges"]:
            edge_info = []
            for edge_data in search_results["edges"][:10]:  # 最多10个关系
                edge = edge_data["edge"]
                score = edge_data["similarity_score"]
                
                # 检查关系是否失效
                edge_status = ""
                if hasattr(edge, 'invalid_at') and edge.invalid_at:
                    edge_status = " (已失效)"
                elif hasattr(edge, 'expired_at') and edge.expired_at:
                    edge_status = " (已过期)"
                
                if hasattr(edge, 'fact'):
                    edge_info.append(f"• {edge.fact}{edge_status} (相似度: {score:.3f})")
                else:
                    edge_info.append(f"• {str(edge)}{edge_status} (相似度: {score:.3f})")
            
            answer_parts.append(f"找到以下关系信息：\n" + "\n".join(edge_info))
        
        # 2. 实体信息
        if search_results["nodes"]:
            node_info = []
            for node_data in search_results["nodes"][:10]:  # 最多10个实体
                node = node_data["node"]
                score = node_data["similarity_score"]
                if hasattr(node, 'summary') and node.summary:
                    node_summary = node.summary[:100] + "..." if len(node.summary) > 100 else node.summary
                    node_info.append(f"• {node.name}: {node_summary} (相似度: {score:.3f})")
                else:
                    node_info.append(f"• {node.name} (相似度: {score:.3f})")
            answer_parts.append(f"找到以下实体信息：\n" + "\n".join(node_info))
        
        # 3. 文档信息
        if search_results["episodes"]:
            episode_info = []
            for episode_data in search_results["episodes"][:10]:  # 最多10个文档
                episode = episode_data["episode"]
                score = episode_data["similarity_score"]
                if hasattr(episode, 'episode_body'):
                    episode_summary = episode.episode_body[:150] + "..." if len(episode.episode_body) > 150 else episode.episode_body
                    episode_info.append(f"• {episode.name}: {episode_summary} (相似度: {score:.3f})")
                else:
                    episode_info.append(f"• {episode.name} (相似度: {score:.3f})")
            answer_parts.append(f"找到以下相关文档：\n" + "\n".join(episode_info))
        
        # 如果没有找到任何信息，返回默认回答
        if not answer_parts:
            return f"关于'{user_query}'，我找到了一些相关信息，但无法提供详细信息。"
        
        return "\n\n".join(answer_parts)
    

# 使用示例
async def main():
    """使用示例"""
    
    # 配置参数
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password"
    API_KEY = "sk-12924ea745d84ff59c6aea09ffe2a343"
    
    # 阿里云API配置
    ALIYUN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    try:
        # 导入必要的模块
        from graphiti_core import Graphiti
        from graphiti_core.llm_client import LLMConfig
        from graphiti_core.embedder.openai import OpenAIEmbedderConfig
        
        # 导入阿里云LLM客户端
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)
        from llm.aliyun_models_config import get_model_config
        from llm.aliyun_llm_client import AliyunLLMClient
        
        # 获取模型配置
        model_config = get_model_config("performance")
        
        # 创建LLM配置
        chat_model = model_config["chat_model"]
        print(f"使用聊天模型: {chat_model}")
        
        llm_config = LLMConfig(
            api_key=API_KEY,
            base_url=ALIYUN_BASE_URL,
            model=chat_model,
            temperature=model_config.get("temperature", 0.3),
            max_tokens=model_config.get("max_tokens", 4096)
        )
        
        # 创建阿里云LLM客户端
        llm_client = AliyunLLMClient(config=llm_config)
        
        # 创建嵌入客户端
        embedding_model = model_config["embedding_model"]
        print(f"使用向量模型: {embedding_model}")
        
        embedder_config = OpenAIEmbedderConfig(
            api_key=API_KEY,
            base_url=ALIYUN_BASE_URL,
            embedding_model=embedding_model
        )
        
        # 使用自定义的分批处理嵌入器
        from graphiti_core.embedder.client import EmbedderClient
        from openai import AsyncOpenAI
        
        class BatchLimitedOpenAIEmbedder(EmbedderClient):
            """自定义OpenAI嵌入器，实现分批处理以避免超过25个限制"""
            
            embedding_dim: int = 1536
            
            def __init__(self, config, client=None):
                self.config = config
                self.client = client or AsyncOpenAI(
                    api_key=config.api_key, 
                    base_url=config.base_url
                )
                self.batch_size = 20
                self.embedding_dim = getattr(config, 'embedding_dim', 1536)
            
            async def create(self, input_data):
                """单个文本嵌入"""
                if isinstance(input_data, str):
                    input_data = [input_data]
                elif isinstance(input_data, list) and len(input_data) == 1:
                    input_data = input_data
                else:
                    input_data = [input_data[0] if isinstance(input_data, list) else str(input_data)]
                
                result = await self.client.embeddings.create(
                    input=input_data,
                    model=self.config.embedding_model
                )
                return result.data[0].embedding
            
            async def create_batch(self, input_data_list):
                """分批处理，确保不超过25个限制"""
                if not input_data_list:
                    return []
                
                all_embeddings = []
                total_batches = (len(input_data_list) + self.batch_size - 1) // self.batch_size
                
                print(f"开始分批处理 {len(input_data_list)} 个文本，分 {total_batches} 批，每批最多 {self.batch_size} 个")
                
                for i in range(0, len(input_data_list), self.batch_size):
                    batch = input_data_list[i:i+self.batch_size]
                    batch_num = i // self.batch_size + 1
                    
                    print(f"处理第 {batch_num}/{total_batches} 批，包含 {len(batch)} 个文本")
                    
                    try:
                        result = await self.client.embeddings.create(
                            input=batch,
                            model=self.config.embedding_model
                        )
                        
                        batch_embeddings = [embedding.embedding for embedding in result.data]
                        all_embeddings.extend(batch_embeddings)
                        
                        print(f"第 {batch_num} 批处理成功，获得 {len(batch_embeddings)} 个嵌入向量")
                        
                        if i + self.batch_size < len(input_data_list):
                            await asyncio.sleep(0.5)
                            
                    except Exception as e:
                        print(f"第 {batch_num} 批处理失败: {e}")
                        # 如果某一批失败，尝试逐个处理
                        for j, text in enumerate(batch):
                            try:
                                single_result = await self.client.embeddings.create(
                                    input=[text],
                                    model=self.config.embedding_model
                                )
                                all_embeddings.append(single_result.data[0].embedding)
                            except Exception as single_e:
                                print(f"单个文本 {j+1}/{len(batch)} 处理失败: {single_e}")
                                all_embeddings.append([0.0] * self.embedding_dim)
                        
                        if i + self.batch_size < len(input_data_list):
                            await asyncio.sleep(1)
                
                print(f"分批处理完成，总共获得 {len(all_embeddings)} 个嵌入向量")
                return all_embeddings
        
        # 创建自定义嵌入器
        embedder = BatchLimitedOpenAIEmbedder(config=embedder_config)
        
        # 创建自定义的cross_encoder配置
        from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
        from graphiti_core.llm_client.config import LLMConfig
        
        cross_encoder_config = LLMConfig(
            api_key=API_KEY,
            base_url=ALIYUN_BASE_URL,
            model=chat_model
        )
        
        cross_encoder = OpenAIRerankerClient(config=cross_encoder_config)
        
        # 初始化Graphiti
        print("正在连接到Neo4j数据库...")
        graphiti = Graphiti(
            NEO4J_URI, 
            NEO4J_USER, 
            NEO4J_PASSWORD,
            llm_client=llm_client,
            embedder=embedder,
            cross_encoder=cross_encoder
        )
        
        # 初始化数据库索引和约束
        await graphiti.build_indices_and_constraints()
        print("成功连接到Neo4j数据库并初始化索引")
        
        # 创建查询处理器
        query_handler = SimpleQueryHandler(graphiti, llm_client)
        
        # 测试查询
        print("\n" + "=" * 60)
        print("开始测试简化查询系统")
        print("=" * 60)
        
        # 测试查询
        test_query = "小白是篮球运动员吗"

        print(f"\n测试查询: {test_query}")
            print("-" * 40)
            
        # 测试1: 关系查询（不指定用户组）
        print("测试1: 关系查询（不指定用户组）")
        result1 = await query_handler.search(
            user_query=test_query,
            search_type="relationship",
            include_expired=False,
            sort_by_similarity=True,
            group_ids=None  # 查询所有用户组的数据
        )
        print(f"查询类型: {result1['search_type']}")
        print(f"找到结果数量: {result1['total_count']}")
        print(f"包含失效关系: {result1.get('include_expired', False)}")

        # 显示前3个关系的相似度评分
        if result1['edges']:
            print("前3个关系的相似度评分:")
            for i, edge_data in enumerate(result1['edges'][:3]):
                edge = edge_data['edge']
                score = edge_data['similarity_score']
                fact = getattr(edge, 'fact', str(edge))
                print(f"  {i+1}. {fact} (相似度: {score:.3f})")

        # 测试2: 片段查询（指定特定用户组）
        print("\n测试2: 片段查询（指定特定用户组）")
        result2 = await query_handler.search(
            user_query=test_query,
            search_type="episode",
            sort_by_similarity=True,
            group_ids=["user_001"]  # 只查询特定用户组的数据
        )
        print(f"查询类型: {result2['search_type']}")
        print(f"找到结果数量: {result2['total_count']}")

        # 显示前3个片段的相似度评分
        if result2['episodes']:
            print("前3个片段的相似度评分:")
            for i, episode_data in enumerate(result2['episodes'][:3]):
                episode = episode_data['episode']
                score = episode_data['similarity_score']
                name = getattr(episode, 'name', str(episode))
                print(f"  {i+1}. {name} (相似度: {score:.3f})")

        # 测试3: 全部查询（指定多个用户组）
        print("\n测试3: 全部查询（指定多个用户组）")
        result3 = await query_handler.search(
            user_query=test_query,
            search_type="comprehensive",
            include_expired=False,
            sort_by_similarity=True,
            group_ids=["user_001", "user_002"]  # 查询多个用户组的数据
        )
        print(f"查询类型: {result3['search_type']}")
        print(f"找到结果数量: {result3['total_count']}")
        print(f"包含失效关系: {result3.get('include_expired', False)}")

        # 显示各类结果的前3个相似度评分
        if result3['edges']:
            print("前3个关系的相似度评分:")
            for i, edge_data in enumerate(result3['edges'][:3]):
                edge = edge_data['edge']
                score = edge_data['similarity_score']
                fact = getattr(edge, 'fact', str(edge))
                print(f"  关系 {i+1}. {fact} (相似度: {score:.3f})")

        if result3['nodes']:
            print("前3个实体的相似度评分:")
            for i, node_data in enumerate(result3['nodes'][:3]):
                node = node_data['node']
                score = node_data['similarity_score']
                name = getattr(node, 'name', str(node))
                print(f"  实体 {i+1}. {name} (相似度: {score:.3f})")

        if result3['episodes']:
            print("前3个片段的相似度评分:")
            for i, episode_data in enumerate(result3['episodes'][:3]):
                episode = episode_data['episode']
                score = episode_data['similarity_score']
                name = getattr(episode, 'name', str(episode))
                print(f"  片段 {i+1}. {name} (相似度: {score:.3f})")

        # 测试4: 查询特定用户组的关系
        print("\n测试4: 查询特定用户组的关系")
        result4 = await query_handler.search(
            user_query="小白和篮球的关系",
            search_type="relationship",
            include_expired=False,
            sort_by_similarity=True,
            group_ids=["user_001"]  # 只查询 user_001 用户组的数据
        )
        print(f"查询类型: {result4['search_type']}")
        print(f"找到结果数量: {result4['total_count']}")
        print(f"用户组: {['user_001']}")

        if result4['edges']:
            print("前3个关系的相似度评分:")
            for i, edge_data in enumerate(result4['edges'][:3]):
                edge = edge_data['edge']
                score = edge_data['similarity_score']
                fact = getattr(edge, 'fact', str(edge))
                print(f"  {i+1}. {fact} (相似度: {score:.3f})")

        # 生成回答
        print("\n生成回答:")
        answer = await query_handler.generate_answer(result3, test_query)
        print(answer)
        
        print("\n" + "=" * 60)
        print("简化查询系统测试完成！")
        print("=" * 60)
        
        # 关闭连接
        await graphiti.close()
        print("数据库连接已关闭")
        
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所需的依赖包")
    except Exception as e:
        print(f"运行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())