"""
Graphiti Evaluation Framework 实现示例

本示例展示了如何使用基于 RAGAS 理念的评估框架来评估 Graphiti 知识图谱系统。

评估维度：
1. Episode 处理质量（忠实度、覆盖率）
2. 实体提取质量（召回率、精确率）
3. 关系抽取质量（准确性、类型正确性）
4. 查询质量（相关性、精确率、召回率）
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from graphiti_core_ecolink import Graphiti
from graphiti_core_ecolink.llm_client import LLMClient
from graphiti_core_ecolink.embedder import EmbedderClient
from graphiti_core_ecolink.nodes import EpisodicNode, EntityNode
from graphiti_core_ecolink.edges import EntityEdge
from graphiti_core_ecolink.search.search_config import SearchResults

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 数据模型 ====================

class EpisodeEvaluationSample(BaseModel):
    """Episode 评估样本"""
    episode: EpisodicNode
    extracted_nodes: list[EntityNode]
    extracted_edges: list[EntityEdge]
    ground_truth_nodes: Optional[list[EntityNode]] = None
    ground_truth_edges: Optional[list[EntityEdge]] = None


class QueryEvaluationSample(BaseModel):
    """查询评估样本"""
    query: str
    search_results: SearchResults
    ground_truth_results: Optional[list[EntityEdge]] = None


class EpisodeEvaluationResult(BaseModel):
    """Episode 评估结果"""
    faithfulness: float
    coverage: float
    uniqueness: float


class QueryEvaluationResult(BaseModel):
    """查询评估结果"""
    relevance: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None


class FullEvaluationResult(BaseModel):
    """完整评估结果"""
    episode_metrics: dict[str, float]
    query_metrics: dict[str, float]
    overall_score: float


# ==================== 评估器实现 ====================

class GraphitiEvaluator:
    """Graphiti 评估器"""
    
    def __init__(
        self,
        llm_client: LLMClient,
        embedder: EmbedderClient
    ):
        self.llm_client = llm_client
        self.embedder = embedder
    
    async def evaluate_episode_faithfulness(
        self,
        episode: EpisodicNode,
        extracted_nodes: list[EntityNode],
        extracted_edges: list[EntityEdge]
    ) -> float:
        """
        评估 Episode 忠实度
        
        评估从 Episode 中提取的实体和关系是否忠实于原文
        """
        
        logger.info(f"评估 Episode 忠实度: {episode.name}")
        
        # 构建评估提示词
        node_list = "\n".join([f"- {node.name}" for node in extracted_nodes])
        edge_list = "\n".join([
            f"- {edge.source.name} --[{edge.type}]--> {edge.target.name}"
            for edge in extracted_edges
        ])
        
        prompt = f"""
你是一个知识图谱评估器。评估从文本中提取的实体和关系是否忠实于原文。

原文：
{episode.content[:1000]}...

提取的实体：
{node_list}

提取的关系：
{edge_list}

任务：判断每个提取的实体和关系是否能在原文中找到依据。

返回 JSON 格式：
{{
    "verified_count": 已验证的提取项数量,
    "total_count": 总提取项数量,
    "faithfulness_score": 忠实度分数 (0.0-1.0),
    "detailed_analysis": "详细分析"
}}
"""
        
        # 调用 LLM 进行评估
        from langchain_core.messages import HumanMessage
        response = await self.llm_client.agenerate([HumanMessage(content=prompt)])
        
        # 解析结果（简化实现）
        try:
            # 假设 LLM 返回 JSON
            import json
            result = json.loads(response.content[0].text)
            faithfulness = result.get("faithfulness_score", 0.5)
        except:
            # 如果解析失败，使用启发式方法
            # 这里应该实现更健壮的解析
            faithfulness = 0.5
        
        return faithfulness
    
    async def evaluate_episode_coverage(
        self,
        episode: EpisodicNode,
        extracted_nodes: list[EntityNode],
        extracted_edges: list[EntityEdge],
        ground_truth: Optional[EpisodeEvaluationSample]
    ) -> float:
        """
        评估 Episode 覆盖率
        
        评估提取的实体和关系是否覆盖了原文中的主要信息
        """
        
        if ground_truth is None or ground_truth.ground_truth_nodes is None:
            logger.warning("缺少 ground truth，跳过覆盖率评估")
            return 0.0
        
        # 简化的覆盖率计算
        extracted_node_names = {node.name for node in extracted_nodes}
        ground_truth_names = {node.name for node in ground_truth.ground_truth_nodes}
        
        if len(ground_truth_names) == 0:
            return 1.0
        
        coverage = len(extracted_node_names & ground_truth_names) / len(ground_truth_names)
        
        return coverage
    
    async def evaluate_entity_uniqueness(
        self,
        extracted_nodes: list[EntityNode]
    ) -> float:
        """
        评估实体唯一性
        
        评估实体去重的效果
        """
        
        # 简化的实现：检查是否有语义相似的节点
        if len(extracted_nodes) <= 1:
            return 1.0
        
        # 使用嵌入模型计算相似度
        # 这里是简化实现
        unique_nodes = set()
        total_count = len(extracted_nodes)
        
        for node in extracted_nodes:
            # 简化：使用名称作为唯一性判断
            if node.name not in unique_nodes:
                unique_nodes.add(node.name)
        
        uniqueness = len(unique_nodes) / total_count if total_count > 0 else 1.0
        
        return uniqueness
    
    async def evaluate_query_relevance(
        self,
        query: str,
        search_results: SearchResults
    ) -> float:
        """
        评估查询相关性
        
        评估查询返回的结果是否与查询相关
        """
        
        logger.info(f"评估查询相关性: {query}")
        
        # 构建评估提示词
        node_list = "\n".join([f"- {node.name}" for node in search_results.nodes[:5]])
        edge_list = "\n".join([
            f"- {edge.source.name} --[{edge.type}]--> {edge.target.name}"
            for edge in search_results.edges[:5]
        ])
        
        prompt = f"""
你是一个查询评估器。评估搜索结果与查询的相关性。

查询：{query}

返回的实体：
{node_list}

返回的关系：
{edge_list}

任务：判断每个搜索结果是否与查询相关。

返回 JSON 格式：
{{
    "relevant_count": 相关结果数量,
    "total_count": 总结果数量,
    "relevance_score": 相关性分数 (0.0-1.0)
}}
"""
        
        # 调用 LLM 进行评估
        from langchain_core.messages import HumanMessage
        response = await self.llm_client.agenerate([HumanMessage(content=prompt)])
        
        # 解析结果（简化实现）
        try:
            import json
            result = json.loads(response.content[0].text)
            relevance = result.get("relevance_score", 0.5)
        except:
            relevance = 0.5
        
        return relevance
    
    async def evaluate_query_precision(
        self,
        search_results: SearchResults,
        ground_truth: list[EntityEdge]
    ) -> float:
        """
        评估查询精确率
        
        评估查询返回结果中相关结果的比例
        """
        
        if ground_truth is None or len(ground_truth) == 0:
            return None
        
        # 简化的精确率计算
        returned_uuids = {edge.uuid for edge in search_results.edges}
        ground_truth_uuids = {edge.uuid for edge in ground_truth}
        
        true_positives = len(returned_uuids & ground_truth_uuids)
        total_returned = len(search_results.edges)
        
        precision = true_positives / total_returned if total_returned > 0 else 0.0
        
        return precision
    
    async def evaluate_query_recall(
        self,
        search_results: SearchResults,
        ground_truth: list[EntityEdge]
    ) -> float:
        """
        评估查询召回率
        
        评估查询是否返回了所有相关的结果
        """
        
        if ground_truth is None or len(ground_truth) == 0:
            return None
        
        # 简化的召回率计算
        returned_uuids = {edge.uuid for edge in search_results.edges}
        ground_truth_uuids = {edge.uuid for edge in ground_truth}
        
        true_positives = len(returned_uuids & ground_truth_uuids)
        total_relevant = len(ground_truth)
        
        recall = true_positives / total_relevant if total_relevant > 0 else 0.0
        
        return recall


# ==================== 评估流程 ====================

async def evaluate_episode_processing(
    evaluator: GraphitiEvaluator,
    sample: EpisodeEvaluationSample
) -> EpisodeEvaluationResult:
    """评估 Episode 处理质量"""
    
    logger.info(f"开始评估 Episode: {sample.episode.name}")
    
    # 评估忠实度
    faithfulness = await evaluator.evaluate_episode_faithfulness(
        sample.episode,
        sample.extracted_nodes,
        sample.extracted_edges
    )
    
    # 评估覆盖率
    coverage = await evaluator.evaluate_episode_coverage(
        sample.episode,
        sample.extracted_nodes,
        sample.extracted_edges,
        sample
    )
    
    # 评估唯一性
    uniqueness = await evaluator.evaluate_entity_uniqueness(
        sample.extracted_nodes
    )
    
    return EpisodeEvaluationResult(
        faithfulness=faithfulness,
        coverage=coverage,
        uniqueness=uniqueness
    )


async def evaluate_query_quality(
    evaluator: GraphitiEvaluator,
    sample: QueryEvaluationSample
) -> QueryEvaluationResult:
    """评估查询质量"""
    
    logger.info(f"开始评估查询: {sample.query}")
    
    # 评估相关性
    relevance = await evaluator.evaluate_query_relevance(
        sample.query,
        sample.search_results
    )
    
    # 评估精确率和召回率（如果有 ground truth）
    precision = None
    recall = None
    
    if sample.ground_truth_results:
        precision = await evaluator.evaluate_query_precision(
            sample.search_results,
            sample.ground_truth_results
        )
        recall = await evaluator.evaluate_query_recall(
            sample.search_results,
            sample.ground_truth_results
        )
    
    return QueryEvaluationResult(
        relevance=relevance,
        precision=precision,
        recall=recall
    )


async def batch_evaluate(
    evaluator: GraphitiEvaluator,
    episodes: list[EpisodeEvaluationSample],
    queries: list[QueryEvaluationSample]
) -> FullEvaluationResult:
    """批量评估"""
    
    logger.info("开始批量评估...")
    
    # 评估所有 episodes
    episode_results = await asyncio.gather(*[
        evaluate_episode_processing(evaluator, sample)
        for sample in episodes
    ])
    
    # 计算 Episode 指标平均值
    avg_faithfulness = sum(r.faithfulness for r in episode_results) / len(episode_results)
    avg_coverage = sum(r.coverage for r in episode_results) / len(episode_results)
    avg_uniqueness = sum(r.uniqueness for r in episode_results) / len(episode_results)
    
    # 评估所有查询
    query_results = await asyncio.gather(*[
        evaluate_query_quality(evaluator, sample)
        for sample in queries
    ])
    
    # 计算查询指标平均值
    avg_relevance = sum(r.relevance for r in query_results if r.relevance) / len([r for r in query_results if r.relevance])
    avg_precision = sum(r.precision for r in query_results if r.precision) / len([r for r in query_results if r.precision])
    avg_recall = sum(r.recall for r in query_results if r.recall) / len([r for r in query_results if r.recall])
    
    # 计算综合评分
    overall_score = (
        avg_faithfulness * 0.3 +
        avg_coverage * 0.2 +
        avg_uniqueness * 0.1 +
        avg_relevance * 0.25 +
        (avg_precision if avg_precision else 0) * 0.05 +
        (avg_recall if avg_recall else 0) * 0.05
    )
    
    return FullEvaluationResult(
        episode_metrics={
            "faithfulness": avg_faithfulness,
            "coverage": avg_coverage,
            "uniqueness": avg_uniqueness
        },
        query_metrics={
            "relevance": avg_relevance,
            "precision": avg_precision,
            "recall": avg_recall
        },
        overall_score=overall_score
    )


# ==================== 使用示例 ====================

async def main():
    """主函数：展示评估框架的使用"""
    
    # 1. 初始化 Graphiti 和评估器
    # 注意：这里需要实际的配置
    graphiti = Graphiti(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password"
    )
    
    evaluator = GraphitiEvaluator(
        llm_client=graphiti.llm_client,
        embedder=graphiti.embedder
    )
    
    # 2. 准备评估数据
    # 示例：添加一个 episode
    result = await graphiti.add_episode(
        name="测试 Episode",
        episode_body="爱因斯坦是一位物理学家，他提出了相对论。他出生于德国。",
        source_description="测试来源",
        reference_time=datetime.now()
    )
    
    # 创建评估样本
    episode_sample = EpisodeEvaluationSample(
        episode=result.episode,
        extracted_nodes=result.nodes,
        extracted_edges=result.edges
    )
    
    # 3. 评估 Episode 处理
    episode_eval = await evaluate_episode_processing(evaluator, episode_sample)
    
    print("Episode 评估结果:")
    print(f"  忠实度: {episode_eval.faithfulness:.2f}")
    print(f"  覆盖率: {episode_eval.coverage:.2f}")
    print(f"  唯一性: {episode_eval.uniqueness:.2f}")
    
    # 4. 评估查询
    search_results = await graphiti.search("爱因斯坦的贡献")
    
    query_sample = QueryEvaluationSample(
        query="爱因斯坦的贡献",
        search_results=SearchResults(edges=search_results, nodes=[], episodes=[], communities=[])
    )
    
    query_eval = await evaluate_query_quality(evaluator, query_sample)
    
    print("\n查询评估结果:")
    print(f"  相关性: {query_eval.relevance:.2f}")
    
    # 5. 批量评估（如果有多个样本）
    full_result = await batch_evaluate(
        evaluator,
        episodes=[episode_sample],
        queries=[query_sample]
    )
    
    print("\n综合评估结果:")
    print(f"  整体评分: {full_result.overall_score:.2f}")
    
    # 6. 清理
    await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())
    logger.info("评估完成")

