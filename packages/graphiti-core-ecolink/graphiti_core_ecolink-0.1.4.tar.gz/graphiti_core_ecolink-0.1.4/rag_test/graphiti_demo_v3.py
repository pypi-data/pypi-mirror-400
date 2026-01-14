"""
Graphiti 智能社区管理演示 V3
结合文档处理、实体生成和智能社区管理
实现：若在group_id的限制下，若没有社区存在则创建，若存在则尝试更新，若可以产生新的社区，则创建
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import List, Optional, Tuple

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（rag_test的父目录）
project_root = os.path.dirname(current_dir)

# 添加项目根目录到Python路径
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入V2版本的功能
from graphiti_crud_demo_v2 import GraphitiCRUD

# 导入必要的模块
from graphiti_core_ecolink.nodes import CommunityNode, EntityNode, get_community_node_from_record
from graphiti_core_ecolink.utils.maintenance.community_operations import (
    get_community_clusters,
    build_communities,
    update_community,
    determine_entity_community, build_community
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


class SmartCommunityManager(GraphitiCRUD):
    """智能社区管理器 - 继承自GraphitiCRUD，添加智能社区管理功能"""

    def __init__(self, uri: str, user: str, password: str, api_key: str,
                 base_url: Optional[str] = None, model_config: str = "balanced"):
        """
        初始化智能社区管理器

        Args:
            uri: Neo4j数据库URI
            user: Neo4j用户名
            password: Neo4j密码
            api_key: API密钥
            base_url: API基础URL
            model_config: 模型配置名称
        """
        super().__init__(uri, user, password, api_key, base_url, model_config)
        self.community_cache = {}  # 社区缓存，避免重复查询

    async def check_existing_communities(self, group_id: str) -> List[CommunityNode]:
        """
        检查指定group_id下是否已存在社区

        Args:
            group_id: 组ID

        Returns:
            List[CommunityNode]: 现有的社区列表
        """
        try:
            if self.graphiti is None:
                raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")

            # 查询现有社区
            records, _, _ = await self.graphiti.driver.execute_query(
                """
                MATCH (c:Community {group_id: $group_id})
                RETURN c.uuid AS uuid, c.name AS name, c.group_id AS group_id,
                       c.created_at AS created_at, c.summary AS summary,
                       c.name_embedding AS name_embedding
                ORDER BY c.created_at DESC
                """,
                group_id=group_id
            )

            communities = []
            for record in records:
                community = get_community_node_from_record(record)
                communities.append(community)

            logger.info(f"组 {group_id} 下找到 {len(communities)} 个现有社区")
            return communities

        except Exception as e:
            logger.error(f"检查现有社区失败: {e}")
            return []

    async def get_entities_by_group(self, group_id: str) -> List[EntityNode]:
        """
        获取指定group_id下的所有实体

        Args:
            group_id: 组ID

        Returns:
            List[EntityNode]: 实体列表
        """
        try:
            if self.graphiti is None:
                raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")

            entities = await EntityNode.get_by_group_ids(self.graphiti.driver, [group_id])
            logger.info(f"组 {group_id} 下找到 {len(entities)} 个实体")
            return entities

        except Exception as e:
            logger.error(f"获取实体失败: {e}")
            return []

    async def smart_community_management(self, group_id: str, force_rebuild: bool = False) -> Tuple[
        List[CommunityNode], List]:
        """
        智能社区管理：根据情况创建、更新或重建社区

        Args:
            group_id: 组ID
            force_rebuild: 是否强制重建所有社区

        Returns:
            Tuple[List[CommunityNode], List]: (社区列表, 边列表)
        """
        try:
            if self.graphiti is None:
                raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")

            logger.info(f"开始智能社区管理，组ID: {group_id}")

            # 1. 检查现有社区
            existing_communities = await self.check_existing_communities(group_id)

            # 2. 获取所有实体
            entities = await self.get_entities_by_group(group_id)

            if not entities:
                logger.warning(f"组 {group_id} 下没有实体，跳过社区管理")
                return [], []

            # 3. 根据情况决定处理策略
            if force_rebuild or not existing_communities:
                # 情况1：强制重建或没有现有社区 -> 创建新社区
                logger.info("执行策略：创建新社区")
                return await self._create_new_communities(group_id)

            else:
                # 情况2：有现有社区 -> 尝试更新或创建新社区
                logger.info("执行策略：智能更新社区")
                return await self._smart_update_communities(group_id, existing_communities, entities)

        except Exception as e:
            logger.error(f"智能社区管理失败: {e}")
            raise

    async def _create_new_communities(self, group_id: str) -> Tuple[List[CommunityNode], List]:
        """
        创建新社区（使用Leiden算法）

        Args:
            group_id: 组ID

        Returns:
            Tuple[List[CommunityNode], List]: (社区列表, 边列表)
        """
        try:
            logger.info(f"为组 {group_id} 创建新社区")

            # 使用V2版本的方法创建社区
            communities, edges = await build_communities(
                self.graphiti.driver,
                self.graphiti.clients.llm_client,
                [group_id]
            )

            # 保存社区到数据库
            saved_communities, saved_edges = await self.fix_and_save_communities(communities, edges)

            logger.info(f"成功创建 {len(saved_communities)} 个新社区，{len(saved_edges)} 条边")
            return saved_communities, saved_edges

        except Exception as e:
            logger.error(f"创建新社区失败: {e}")
            raise

    async def _smart_update_communities(self, group_id: str, existing_communities: List[CommunityNode],
                                        entities: List[EntityNode]) -> Tuple[List[CommunityNode], List]:
        """
        智能更新社区：尝试更新现有社区，必要时创建新社区

        Args:
            group_id: 组ID
            existing_communities: 现有社区列表
            entities: 实体列表

        Returns:
            Tuple[List[CommunityNode], List]: (社区列表, 边列表)
        """
        try:
            logger.info(f"智能更新组 {group_id} 的社区")

            updated_communities = []
            updated_edges = []

            # 1. 尝试更新现有社区
            for entity in entities:
                try:
                    # 使用update_community尝试更新
                    communities, edges = await update_community(
                        self.graphiti.driver,
                        self.graphiti.clients.llm_client,
                        self.graphiti.clients.embedder,
                        entity
                    )

                    if communities:  # 如果成功更新
                        updated_communities.extend(communities)
                        updated_edges.extend(edges)
                        logger.info(f"成功更新实体 {entity.uuid} 的社区")
                    else:
                        logger.info(f"实体 {entity.uuid} 无法更新到现有社区")

                except Exception as e:
                    logger.warning(f"更新实体 {entity.uuid} 的社区失败: {e}")
                    continue

            # 2. 检查是否有实体没有被分配到社区
            unassigned_entities = await self._get_unassigned_entities(group_id, entities)

            if unassigned_entities:
                logger.info(f"发现 {len(unassigned_entities)} 个未分配的实体，尝试创建新社区")

                # 为未分配的实体创建新社区
                new_communities, new_edges = await self._create_communities_for_entities(
                    group_id, unassigned_entities
                )

                updated_communities.extend(new_communities)
                updated_edges.extend(new_edges)

            # 3. 检查是否需要重新聚类（如果实体数量变化很大）
            if await self._should_recluster(group_id, existing_communities, entities):
                logger.info("检测到需要重新聚类，执行完整重建")
                return await self._create_new_communities(group_id)

            logger.info(f"智能更新完成：{len(updated_communities)} 个社区，{len(updated_edges)} 条边")
            return updated_communities, updated_edges

        except Exception as e:
            logger.error(f"智能更新社区失败: {e}")
            raise

    async def _get_unassigned_entities(self, group_id: str, entities: List[EntityNode]) -> List[EntityNode]:
        """
        获取未分配到社区的实体

        Args:
            group_id: 组ID
            entities: 实体列表

        Returns:
            List[EntityNode]: 未分配的实体列表
        """
        try:
            unassigned = []

            for entity in entities:
                # 检查实体是否已有社区
                community, _ = await determine_entity_community(self.graphiti.driver, entity)
                if community is None:
                    unassigned.append(entity)

            logger.info(f"找到 {len(unassigned)} 个未分配的实体")
            return unassigned

        except Exception as e:
            logger.error(f"获取未分配实体失败: {e}")
            return entities  # 如果出错，返回所有实体

    async def _create_communities_for_entities(self, group_id: str, entities: List[EntityNode]) -> Tuple[
        List[CommunityNode], List]:
        """
        为指定实体创建社区

        Args:
            group_id: 组ID
            entities: 实体列表

        Returns:
            Tuple[List[CommunityNode], List]: (社区列表, 边列表)
        """
        try:
            if not entities:
                return [], []

            logger.info(f"为 {len(entities)} 个实体创建新社区")

            # 使用Leiden算法对这些实体进行聚类
            from graphiti_core_ecolink.utils.maintenance.community_operations import leiden_community_detection
            from graphiti_core_ecolink.utils.maintenance.community_operations import Neighbor

            # 构建投影矩阵
            projection = {}
            for entity in entities:
                # 查询实体的邻居
                records, _, _ = await self.graphiti.driver.execute_query(
                    """
                    MATCH (n:Entity {group_id: $group_id, uuid: $uuid})-[r:RELATES_TO]-(m:Entity {group_id: $group_id})
                    WITH count(r) AS count, m.uuid AS uuid
                    RETURN uuid, count
                    """,
                    uuid=entity.uuid,
                    group_id=group_id
                )

                projection[entity.uuid] = [
                    Neighbor(node_uuid=record['uuid'], edge_count=record['count'])
                    for record in records
                ]

            # 使用Leiden算法聚类
            cluster_uuids = leiden_community_detection(projection)

            # 构建社区
            communities = []
            edges = []

            for i, cluster in enumerate(cluster_uuids):
                if not cluster:
                    continue

                # 获取实体对象
                cluster_entities = [e for e in entities if e.uuid in cluster]

                if cluster_entities:
                    # 创建社区
                    community, community_edges = await build_community(
                        self.graphiti.clients.llm_client,
                        cluster_entities
                    )

                    communities.append(community)
                    edges.extend(community_edges)

            # 保存社区
            saved_communities, saved_edges = await self.fix_and_save_communities(communities, edges)

            logger.info(f"为实体创建了 {len(saved_communities)} 个新社区")
            return saved_communities, saved_edges

        except Exception as e:
            logger.error(f"为实体创建社区失败: {e}")
            raise

    async def _should_recluster(self, group_id: str, existing_communities: List[CommunityNode],
                                entities: List[EntityNode]) -> bool:
        """
        判断是否需要重新聚类

        Args:
            group_id: 组ID
            existing_communities: 现有社区列表
            entities: 实体列表

        Returns:
            bool: 是否需要重新聚类
        """
        try:
            # 简单的启发式规则：
            # 1. 如果实体数量增加超过50%，考虑重新聚类
            # 2. 如果社区数量与实体数量比例不合理，考虑重新聚类

            entity_count = len(entities)
            community_count = len(existing_communities)

            if entity_count == 0:
                return False

            # 规则1：实体数量变化很大
            if community_count > 0:
                # 估算每个社区的平均实体数
                avg_entities_per_community = entity_count / community_count

                # 如果平均每个社区的实体数太少（<2）或太多（>20），考虑重新聚类
                if avg_entities_per_community < 2 or avg_entities_per_community > 20:
                    logger.info(f"平均每个社区实体数 {avg_entities_per_community:.1f}，建议重新聚类")
                    return True

            # 规则2：实体数量增加很多
            # 这里可以添加更复杂的逻辑，比如比较历史数据

            return False

        except Exception as e:
            logger.error(f"判断是否需要重新聚类失败: {e}")
            return False

    async def process_documents_with_smart_communities(self, doc_dir: str = "doc",
                                                       group_id: str = "default",
                                                       max_tokens: int = 2048,
                                                       overlap: int = 100,
                                                       force_rebuild: bool = False) -> Tuple[
        List[str], List[CommunityNode], List]:
        """
        处理文档并智能管理社区

        Args:
            doc_dir: 文档目录路径
            group_id: 组ID
            max_tokens: 每个分片的最大token数量
            overlap: 分片之间的重叠token数量
            force_rebuild: 是否强制重建社区

        Returns:
            Tuple[List[str], List[CommunityNode], List]: (episode UUID列表, 社区列表, 边列表)
        """
        try:
            logger.info(f"开始处理文档并智能管理社区，组ID: {group_id}")

            # 1. 处理文档，生成实体
            episode_uuids = await self.process_documents_from_directory(
                doc_dir=doc_dir,
                max_tokens=max_tokens,
                overlap=overlap,
                group_id=group_id
            )

            logger.info(f"文档处理完成，生成了 {len(episode_uuids)} 个episode")

            # 2. 智能管理社区
            communities, edges = await self.smart_community_management(
                group_id=group_id,
                force_rebuild=force_rebuild
            )

            logger.info(f"社区管理完成：{len(communities)} 个社区，{len(edges)} 条边")

            return episode_uuids, communities, edges

        except Exception as e:
            logger.error(f"处理文档并智能管理社区失败: {e}")
            raise

    async def get_community_summary(self, group_id: str) -> dict:
        """
        获取社区摘要信息

        Args:
            group_id: 组ID

        Returns:
            dict: 社区摘要信息
        """
        try:
            if self.graphiti is None:
                raise RuntimeError("Graphiti实例未初始化，请先调用connect()方法")

            # 获取社区信息
            communities = await self.check_existing_communities(group_id)

            # 获取实体信息
            entities = await self.get_entities_by_group(group_id)

            # 统计信息
            community_count = len(communities)
            entity_count = len(entities)

            # 计算每个社区的实体数量
            community_entity_counts = []
            for community in communities:
                # 查询社区中的实体数量
                records, _, _ = await self.graphiti.driver.execute_query(
                    """
                    MATCH (c:Community {uuid: $community_uuid})-[:HAS_MEMBER]->(e:Entity)
                    RETURN count(e) AS entity_count
                    """,
                    community_uuid=community.uuid
                )

                entity_count_in_community = records[0]['entity_count'] if records else 0
                community_entity_counts.append({
                    'community_name': community.name,
                    'entity_count': entity_count_in_community,
                    'summary': community.summary[:100] + '...' if len(community.summary) > 100 else community.summary
                })

            summary = {
                'group_id': group_id,
                'total_communities': community_count,
                'total_entities': entity_count,
                'average_entities_per_community': entity_count / community_count if community_count > 0 else 0,
                'communities': community_entity_counts,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            return summary

        except Exception as e:
            logger.error(f"获取社区摘要失败: {e}")
            return {'error': str(e)}


async def main():
    """主函数 - 演示智能社区管理功能"""

    # 配置参数
    NEO4J_URI = "bolt://192.168.4.20:9687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password"
    API_KEY = "sk-12924ea745d84ff59c6aea09ffe2a343"
    ALIYUN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # 创建智能社区管理器实例
    manager = SmartCommunityManager(
        NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, API_KEY,
        ALIYUN_BASE_URL, model_config="balanced"
    )

    try:
        # 连接数据库
        await manager.connect()

        print("=" * 80)
        print("智能社区管理演示 V3")
        print("=" * 80)

        # 设置组ID
        group_id = "888"

        # 1. 处理文档并智能管理社区
        print(f"\n1. 处理文档并智能管理社区 (组ID: {group_id})")
        print("-" * 60)

        episode_uuids, communities, edges = await manager.process_documents_with_smart_communities(
            doc_dir="/Users/admin/Desktop/woker/deal/graphiti/rag_test/doc",
            group_id=group_id,
            max_tokens=2048,
            overlap=100,
            force_rebuild=False  # 不强制重建，使用智能更新
        )

        print(f"✓ 文档处理完成：{len(episode_uuids)} 个episode")
        print(f"✓ 社区管理完成：{len(communities)} 个社区，{len(edges)} 条边")

        # 2. 获取社区摘要
        print(f"\n2. 获取社区摘要")
        print("-" * 60)

        # summary = await manager.get_community_summary(group_id)
        #
        # if 'error' not in summary:
        #     print(f"组ID: {summary['group_id']}")
        #     print(f"总社区数: {summary['total_communities']}")
        #     print(f"总实体数: {summary['total_entities']}")
        #     print(f"平均每个社区实体数: {summary['average_entities_per_community']:.1f}")
        #
        #     print(f"\n社区详情:")
        #     for i, comm in enumerate(summary['communities'], 1):
        #         print(f"  {i}. {comm['community_name']} ({comm['entity_count']} 个实体)")
        #         print(f"     摘要: {comm['summary']}")
        # else:
        #     print(f"获取摘要失败: {summary['error']}")

        # # 3. 演示强制重建
        # print(f"\n3. 演示强制重建社区")
        # print("-" * 60)
        #
        # communities_rebuilt, edges_rebuilt = await manager.smart_community_management(
        #     group_id=group_id,
        #     force_rebuild=True
        # )
        #
        # print(f"✓ 强制重建完成：{len(communities_rebuilt)} 个社区，{len(edges_rebuilt)} 条边")
        #
        # # 4. 最终摘要
        # print(f"\n4. 最终社区摘要")
        # print("-" * 60)
        #
        # final_summary = await manager.get_community_summary(group_id)
        #
        # if 'error' not in final_summary:
        #     print(f"最终状态:")
        #     print(f"  总社区数: {final_summary['total_communities']}")
        #     print(f"  总实体数: {final_summary['total_entities']}")
        #     print(f"  平均每个社区实体数: {final_summary['average_entities_per_community']:.1f}")
        #
        # print("\n" + "=" * 80)
        # print("智能社区管理演示完成！")
        # print("=" * 80)

    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        print(f"错误: {e}")

    finally:
        # 关闭连接
        await manager.close()


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
