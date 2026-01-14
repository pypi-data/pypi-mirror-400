import asyncio
import logging
import time
from collections import defaultdict

from pydantic import BaseModel

from graphiti_core_ecolink.driver.driver import GraphDriver
from graphiti_core_ecolink.edges import CommunityEdge
from graphiti_core_ecolink.embedder import EmbedderClient
from graphiti_core_ecolink.helpers import semaphore_gather
from graphiti_core_ecolink.llm_client import LLMClient
from graphiti_core_ecolink.nodes import CommunityNode, EntityNode, get_community_node_from_record
from graphiti_core_ecolink.prompts import prompt_library
from graphiti_core_ecolink.prompts.summarize_nodes import Summary, SummaryDescription
from graphiti_core_ecolink.utils.datetime_utils import utc_now
from graphiti_core_ecolink.utils.maintenance.edge_operations import build_community_edges

MAX_COMMUNITY_BUILD_CONCURRENCY = 2

logger = logging.getLogger(__name__)


class Neighbor(BaseModel):
    node_uuid: str
    edge_count: int


# async def get_community_clusters(
#     driver: GraphDriver, group_ids: list[str] | None
# ) -> list[list[EntityNode]]:
#     community_clusters: list[list[EntityNode]] = []
#
#     if group_ids is None:
#         group_id_values, _, _ = await driver.execute_query(
#             """
#         MATCH (n:Entity)
#         WHERE n.group_id IS NOT NULL
#         RETURN
#             collect(DISTINCT n.group_id) AS group_ids
#         """,
#         )
#
#         group_ids = group_id_values[0]['group_ids'] if group_id_values else []
#
#     for group_id in group_ids:
#         projection: dict[str, list[Neighbor]] = {}
#         nodes = await EntityNode.get_by_group_ids(driver, [group_id])
#         for node in nodes:
#             records, _, _ = await driver.execute_query(
#                 """
#             MATCH (n:Entity {group_id: $group_id, uuid: $uuid})-[r:RELATES_TO]-(m: Entity {group_id: $group_id})
#             WITH count(r) AS count, m.uuid AS uuid
#             RETURN
#                 uuid,
#                 count
#             """,
#                 uuid=node.uuid,
#                 group_id=group_id,
#             )
#
#             projection[node.uuid] = [
#                 Neighbor(node_uuid=record['uuid'], edge_count=record['count']) for record in records
#             ]
#
#         cluster_uuids = label_propagation(projection)
#
#         community_clusters.extend(
#             list(
#                 await semaphore_gather(
#                     *[EntityNode.get_by_uuids(driver, cluster) for cluster in cluster_uuids]
#                 )
#             )
#         )
#
#     return community_clusters


async def get_community_clusters(
        driver: GraphDriver, group_ids: list[str] | None
) -> list[list[EntityNode]]:
    community_clusters: list[list[EntityNode]] = []

    if group_ids is None:
        group_id_values, _, _ = await driver.execute_query(
            """
            MATCH (n:Entity)
            WHERE n.group_id IS NOT NULL
            RETURN collect(DISTINCT n.group_id) AS group_ids
            """,
        )
        group_ids = group_id_values[0]['group_ids'] if group_id_values else []
    for group_id in group_ids:
        # �� 关键修复：一次性查询所有关系，避免N+1问题

        records, _, _two = await driver.execute_query(
            """
            MATCH (n:Entity {group_id: $group_id})-[r:RELATES_TO]-(m:Entity {group_id: $group_id})
            WITH n.uuid AS source_uuid, m.uuid AS target_uuid, count(r) AS edge_count
            RETURN source_uuid, target_uuid, edge_count
            """,
            group_id=group_id,
        )

        # 构建投影矩阵
        projection: dict[str, list[Neighbor]] = defaultdict(list)
        for record in records:
            source_uuid = record['source_uuid']
            target_uuid = record['target_uuid']
            edge_count = record['edge_count']

            projection[source_uuid].append(
                Neighbor(node_uuid=target_uuid, edge_count=edge_count)
            )
        cluster_uuids = leiden_community_detection(projection)

        # 🚀 关键修复：保持集群结构，不要用 extend
        for cluster_uuids in cluster_uuids:
            cluster_nodes = await EntityNode.get_by_uuids(driver, cluster_uuids)
            if cluster_nodes:  # 只添加非空集群
                community_clusters.append(cluster_nodes)

    return community_clusters


def label_propagation(projection: dict[str, list[Neighbor]]) -> list[list[str]]:
    # Implement the label propagation community detection algorithm.
    # 1. Start with each node being assigned its own community
    # 2. Each node will take on the community of the plurality of its neighbors
    # 3. Ties are broken by going to the largest community
    # 4. Continue until no communities change during propagation

    community_map = {uuid: i for i, uuid in enumerate(projection.keys())}
    while True:
        no_change = True
        new_community_map: dict[str, int] = {}

        for uuid, neighbors in projection.items():
            curr_community = community_map[uuid]

            community_candidates: dict[int, int] = defaultdict(int)
            for neighbor in neighbors:
                community_candidates[community_map[neighbor.node_uuid]] += neighbor.edge_count
            community_lst = [
                (count, community) for community, count in community_candidates.items()
            ]

            community_lst.sort(reverse=True)
            candidate_rank, community_candidate = community_lst[0] if community_lst else (0, -1)
            if community_candidate != -1 and candidate_rank > 1:
                new_community = community_candidate
            else:
                new_community = max(community_candidate, curr_community)

            new_community_map[uuid] = new_community

            if new_community != curr_community:
                no_change = False

        if no_change:
            break

        community_map = new_community_map

    community_cluster_map = defaultdict(list)
    for uuid, community in community_map.items():
        community_cluster_map[community].append(uuid)

    clusters = [cluster for cluster in community_cluster_map.values()]
    return clusters


async def summarize_pair(
    llm_client: LLMClient, summary_pair: tuple[str, str], ensure_ascii: bool = True
) -> str:
    # Prepare context for LLM
    context = {
        'node_summaries': [{'summary': summary} for summary in summary_pair],
        'ensure_ascii': ensure_ascii,
    }

    llm_response = await llm_client.generate_response(
        prompt_library.summarize_nodes.summarize_pair(context), response_model=Summary
    )

    pair_summary = llm_response.get('summary', '')

    return pair_summary


def leiden_community_detection(projection: dict[str, list[Neighbor]]) -> list[list[str]]:
    """
    使用Leiden算法进行社区检测，替代label_propagation
    Leiden算法比标签传播算法更稳定，性能更好

    入参: projection: dict[str, list[Neighbor]] - 投影矩阵
    出参: list[list[str]] - 社区列表，每个社区是节点UUID的列表

    Args:
        projection: 投影矩阵，键是节点UUID，值是邻居列表

    Returns:
        list[list[str]]: 社区列表，每个社区是节点UUID的列表
    """
    try:
        # 由于Leiden算法需要图数据，我们需要构建图结构
        # 这里我们使用一个简化的实现，基于连通分量和模块度优化

        # 构建邻接表和边权重
        adjacency = {}
        edge_weights = {}

        for uuid, neighbors in projection.items():
            adjacency[uuid] = []
            for neighbor in neighbors:
                adjacency[uuid].append(neighbor.node_uuid)
                # 存储边权重（双向）
                edge_key = tuple(sorted([uuid, neighbor.node_uuid]))
                edge_weights[edge_key] = neighbor.edge_count

        # 使用改进的连通分量算法（Leiden算法的简化版本）
        print('adjacency',adjacency)
        print("edge_weights",edge_weights)
        communities = _leiden_simplified(adjacency, edge_weights)

        return communities

    except Exception as e:
        logger.error(f"Leiden算法失败: {e}")
        # 如果失败，回退到简单的连通分量算法
        # return _fallback_connected_components(projection)


def _leiden_simplified(adjacency: dict[str, list[str]], edge_weights: dict[tuple, int]) -> list[list[str]]:
    """
    Leiden算法的简化实现
    基于模块度优化的社区检测
    """
    try:
        from collections import defaultdict

        # 初始化：每个节点作为单独的社区
        communities = {uuid: i for i, uuid in enumerate(adjacency.keys())}
        community_nodes = defaultdict(list)
        for uuid, comm_id in communities.items():
            community_nodes[comm_id].append(uuid)

        # 计算模块度增益
        def calculate_modularity_gain(node, from_comm, to_comm):
            """计算将节点从一个社区移动到另一个社区的模块度增益"""
            if from_comm == to_comm:
                return 0.0

            # 简化的模块度计算
            gain = 0.0

            # 计算与目标社区的连接强度
            for neighbor in adjacency[node]:
                if communities[neighbor] == to_comm:
                    edge_key = tuple(sorted([node, neighbor]))
                    gain += edge_weights.get(edge_key, 1)

            # 计算与源社区的连接强度
            for neighbor in adjacency[node]:
                if communities[neighbor] == from_comm:
                    edge_key = tuple(sorted([node, neighbor]))
                    gain -= edge_weights.get(edge_key, 1)

            return gain

        # 迭代优化
        max_iterations = 10  # 限制最大迭代次数
        for iteration in range(max_iterations):
            changes = 0

            # 随机遍历所有节点
            import random
            nodes = list(adjacency.keys())
            random.shuffle(nodes)

            for node in nodes:
                current_comm = communities[node]
                best_comm = current_comm
                best_gain = 0.0

                # 尝试移动到邻居的社区
                neighbor_communities = set()
                for neighbor in adjacency[node]:
                    neighbor_communities.add(communities[neighbor])

                for target_comm in neighbor_communities:
                    if target_comm != current_comm:
                        gain = calculate_modularity_gain(node, current_comm, target_comm)
                        if gain > best_gain:
                            best_gain = gain
                            best_comm = target_comm

                # 如果找到更好的社区，则移动
                if best_comm != current_comm and best_gain > 0:
                    # 从原社区移除
                    community_nodes[current_comm].remove(node)
                    # 添加到新社区
                    community_nodes[best_comm].append(node)
                    # 更新节点社区
                    communities[node] = best_comm
                    changes += 1

            # 如果没有任何变化，提前结束
            if changes == 0:
                break

        # # 构建结果
        # result = []
        # for comm_id, nodes in community_nodes.items():
        #     if len(nodes) > 1:  # 只保留有多个节点的社区
        #         result.append(nodes)
        #
        # # 如果没有检测到社区，返回每个节点作为单独的社区
        # if not result:
        #     result = [[uuid] for uuid in adjacency.keys()]
        #
        # return result
        # 构建结果 - 确保与label_propagation返回结构完全一致
        result = []
        for comm_id, nodes in community_nodes.items():
            # 与label_propagation保持一致：包含所有社区，包括单个节点的社区
            result.append(nodes)

        return result

    except Exception as e:
        logger.error(f"Leiden简化算法失败: {e}")
        # return _fallback_connected_components_simple(adjacency)


async def generate_summary_description(
    llm_client: LLMClient, summary: str, ensure_ascii: bool = True
) -> str:
    context = {
        'summary': summary,
        'ensure_ascii': ensure_ascii,
    }

    llm_response = await llm_client.generate_response(
        prompt_library.summarize_nodes.summary_description(context),
        response_model=SummaryDescription,
    )
    description = llm_response.get('description', '')

    return description


# async def build_community(
#     llm_client: LLMClient, community_cluster: list[EntityNode], ensure_ascii: bool = True
# ) -> tuple[CommunityNode, list[CommunityEdge]]:
#     summaries = [entity.summary for entity in community_cluster]
#     length = len(summaries)
#     print("lengthlengthlengthlengthlength",length)
#     while length > 1:
#         odd_one_out: str | None = None
#         if length % 2 == 1:
#             odd_one_out = summaries.pop()
#             length -= 1
#         new_summaries: list[str] = list(
#             await semaphore_gather(
#                 *[
#                     summarize_pair(
#                         llm_client, (str(left_summary), str(right_summary)), ensure_ascii
#                     )
#                     for left_summary, right_summary in zip(
#                         summaries[: int(length / 2)], summaries[int(length / 2) :], strict=False
#                     )
#                 ]
#             )
#         )
#         if odd_one_out is not None:
#             new_summaries.append(odd_one_out)
#         summaries = new_summaries
#         length = len(summaries)
#
#     summary = summaries[0]
#     name = await generate_summary_description(llm_client, summary, ensure_ascii)
#     now = utc_now()
#     community_node = CommunityNode(
#         name=name,
#         group_id=community_cluster[0].group_id,
#         labels=['Community'],
#         created_at=now,
#         summary=summary,
#     )
#
#     community_edges = build_community_edges(community_cluster, community_node, now)
#
#     logger.debug((community_node, community_edges))
#
#     return community_node, community_edges


async def build_community(
        llm_client: LLMClient, community_cluster: list[EntityNode], ensure_ascii: bool = True
) -> tuple[CommunityNode, list[CommunityEdge]]:
    """
    构建社区，限制摘要数量以避免API频率限制
    """
    # 限制摘要数量，避免API频率限制
    MAX_SUMMARIES = 50  # 最大摘要数量
    MAX_ENTITIES = 100  # 最大实体数量

    # 如果实体数量超过限制，只取前N个
    if len(community_cluster) > MAX_ENTITIES:
        logger.warning(f"社区实体数量 {len(community_cluster)} 超过限制 {MAX_ENTITIES}，只取前 {MAX_ENTITIES} 个")
        community_cluster = community_cluster[:MAX_ENTITIES]

    summaries = [entity.summary for entity in community_cluster]
    length = len(summaries)

    logger.info(f"开始构建社区，原始摘要数量: {length}")

    # 如果摘要数量超过限制，先进行预合并
    if length > MAX_SUMMARIES:
        logger.warning(f"摘要数量 {length} 超过限制 {MAX_SUMMARIES}，进行预合并")

        # 简单的预合并：将摘要分组合并
        batch_size = (length + MAX_SUMMARIES - 1) // MAX_SUMMARIES  # 向上取整
        pre_merged_summaries = []

        for i in range(0, length, batch_size):
            batch = summaries[i:i + batch_size]
            if len(batch) == 1:
                pre_merged_summaries.append(batch[0])
            else:
                # 简单合并：取前几个摘要的关键信息
                combined = " ".join(batch[:3])  # 只取前3个摘要
                if len(combined) > 1000:  # 限制长度
                    combined = combined[:1000] + "..."
                pre_merged_summaries.append(combined)

        summaries = pre_merged_summaries
        length = len(summaries)
        logger.info(f"预合并后摘要数量: {length}")

    # 正常的摘要合并过程
    while length > 1:
        odd_one_out: str | None = None
        if length % 2 == 1:
            odd_one_out = summaries.pop()
            length -= 1

        # 添加延迟，避免API频率限制
        await asyncio.sleep(0.5)

        new_summaries: list[str] = list(
            await semaphore_gather(
                *[
                    summarize_pair(
                        llm_client, (str(left_summary), str(right_summary)), ensure_ascii
                    )
                    for left_summary, right_summary in zip(
                        summaries[: int(length / 2)], summaries[int(length / 2):], strict=False
                    )
                ],
                max_coroutines=2  # 限制并发数
            )
        )

        if odd_one_out is not None:
            new_summaries.append(odd_one_out)
        summaries = new_summaries
        length = len(summaries)

        # 每次迭代后添加延迟
        await asyncio.sleep(1.0)

        logger.info(f"摘要合并后数量: {length}")

    summary = summaries[0]

    # 添加延迟，避免API频率限制
    await asyncio.sleep(0.5)

    name = await generate_summary_description(llm_client, summary, ensure_ascii)
    now = utc_now()
    community_node = CommunityNode(
        name=name,
        group_id=community_cluster[0].group_id,
        labels=['Community'],
        created_at=now,
        summary=summary,
    )
    community_edges = build_community_edges(community_cluster, community_node, now)

    logger.debug((community_node, community_edges))

    return community_node, community_edges


async def build_communities(
    driver: GraphDriver,
    llm_client: LLMClient,
    group_ids: list[str] | None,
    ensure_ascii: bool = True,
) -> tuple[list[CommunityNode], list[CommunityEdge]]:
    community_clusters = await get_community_clusters(driver, group_ids)
    semaphore = asyncio.Semaphore(MAX_COMMUNITY_BUILD_CONCURRENCY)

    async def limited_build_community(cluster):
        async with semaphore:
            return await build_community(llm_client, cluster, ensure_ascii)

    communities: list[tuple[CommunityNode, list[CommunityEdge]]] = list(
        await semaphore_gather(
            *[limited_build_community(cluster) for cluster in community_clusters]
        )
    )

    community_nodes: list[CommunityNode] = []
    community_edges: list[CommunityEdge] = []
    for community in communities:
        community_nodes.append(community[0])
        community_edges.extend(community[1])

    return community_nodes, community_edges


async def remove_communities(driver: GraphDriver):
    await driver.execute_query(
        """
    MATCH (c:Community)
    DETACH DELETE c
    """,
    )


async def determine_entity_community(
    driver: GraphDriver, entity: EntityNode
) -> tuple[CommunityNode | None, bool]:
    # Check if the node is already part of a community
    records, _, _ = await driver.execute_query(
        """
    MATCH (c:Community)-[:HAS_MEMBER]->(n:Entity {uuid: $entity_uuid})
    RETURN
        c.uuid AS uuid,
        c.name AS name,
        c.group_id AS group_id,
        c.created_at AS created_at,
        c.summary AS summary,
        c.name_embedding AS name_embedding
    """,
        entity_uuid=entity.uuid,
    )

    if len(records) > 0:
        return get_community_node_from_record(records[0]), False

    # If the node has no community, add it to the mode community of surrounding entities
    records, _, _ = await driver.execute_query(
        """
    MATCH (c:Community)-[:HAS_MEMBER]->(m:Entity)-[:RELATES_TO]-(n:Entity {uuid: $entity_uuid})
    RETURN
        c.uuid AS uuid,
        c.name AS name,
        c.group_id AS group_id,
        c.created_at AS created_at,
        c.summary AS summary,
        c.name_embedding AS name_embedding
    """,
        entity_uuid=entity.uuid,
    )

    communities: list[CommunityNode] = [
        get_community_node_from_record(record) for record in records
    ]

    community_map: dict[str, int] = defaultdict(int)
    for community in communities:
        community_map[community.uuid] += 1

    community_uuid = None
    max_count = 0
    for uuid, count in community_map.items():
        if count > max_count:
            community_uuid = uuid
            max_count = count

    if max_count == 0:
        return None, False

    for community in communities:
        if community.uuid == community_uuid:
            return community, True

    return None, False


async def update_community(
    driver: GraphDriver,
    llm_client: LLMClient,
    embedder: EmbedderClient,
    entity: EntityNode,
    ensure_ascii: bool = True,
) -> tuple[list[CommunityNode], list[CommunityEdge]]:
    community, is_new = await determine_entity_community(driver, entity)

    if community is None:
        return [], []

    new_summary = await summarize_pair(
        llm_client, (entity.summary, community.summary), ensure_ascii
    )
    new_name = await generate_summary_description(llm_client, new_summary, ensure_ascii)

    community.summary = new_summary
    community.name = new_name

    community_edges = []
    if is_new:
        community_edge = (build_community_edges([entity], community, utc_now()))[0]
        await community_edge.save(driver)
        community_edges.append(community_edge)

    await community.generate_name_embedding(embedder)

    await community.save(driver)

    return [community], community_edges
