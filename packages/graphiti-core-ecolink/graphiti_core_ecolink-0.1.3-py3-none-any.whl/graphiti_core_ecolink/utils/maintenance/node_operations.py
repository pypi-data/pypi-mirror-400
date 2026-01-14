"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from time import time
from typing import Any

from pydantic import BaseModel

from graphiti_core_ecolink.graphiti_types import GraphitiClients
from graphiti_core_ecolink.helpers import MAX_REFLEXION_ITERATIONS, semaphore_gather
from graphiti_core_ecolink.llm_client import LLMClient
from graphiti_core_ecolink.llm_client.config import ModelSize
from graphiti_core_ecolink.nodes import EntityNode, EpisodeType, EpisodicNode, create_entity_node_embeddings
from graphiti_core_ecolink.prompts import prompt_library
from graphiti_core_ecolink.prompts.dedupe_nodes import NodeDuplicate, NodeResolutions
from graphiti_core_ecolink.prompts.extract_nodes import (
    EntitySummary,
    ExtractedEntities,
    ExtractedEntity,
    MissedEntities,
)
from graphiti_core_ecolink.search.search import search
from graphiti_core_ecolink.search.search_config import SearchResults
from graphiti_core_ecolink.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF
from graphiti_core_ecolink.search.search_filters import SearchFilters
from graphiti_core_ecolink.utils.datetime_utils import utc_now
from graphiti_core_ecolink.utils.maintenance.edge_operations import filter_existing_duplicate_of_edges

logger = logging.getLogger(__name__)


async def extract_nodes_reflexion(
    llm_client: LLMClient,
    episode: EpisodicNode,
    previous_episodes: list[EpisodicNode],
    node_names: list[str],
    ensure_ascii: bool = False,
) -> list[str]:
    # Prepare context for LLM
    context = {
        'episode_content': episode.content,
        'previous_episodes': [ep.content for ep in previous_episodes],
        'extracted_entities': node_names,
        'ensure_ascii': ensure_ascii,
    }

    llm_response = await llm_client.generate_response(
        prompt_library.extract_nodes.reflexion(context), MissedEntities
    )
    missed_entities = llm_response.get('missed_entities', [])

    return missed_entities


async def extract_nodes(
    clients: GraphitiClients,
    episode: EpisodicNode,
    previous_episodes: list[EpisodicNode],
    entity_types: dict[str, type[BaseModel]] | None = None,
    excluded_entity_types: list[str] | None = None,
) -> list[EntityNode]: #返回实体节点列表
    start = time()
    llm_client = clients.llm_client
    llm_response = {}
    custom_prompt = ''
    entities_missed = True
    reflexion_iterations = 0

    entity_types_context = [
        {
            'entity_type_id': 0,
            'entity_type_name': 'Entity',
            'entity_type_description': 'Default entity classification. Use this entity type if the entity is not one of the other listed types.',
        }
    ]

    entity_types_context += (
        [
            {
                'entity_type_id': i + 1,
                'entity_type_name': type_name,
                'entity_type_description': type_model.__doc__,
            }
            for i, (type_name, type_model) in enumerate(entity_types.items())
        ]
        if entity_types is not None
        else []
    )

    context = {
        'episode_content': episode.content,
        'episode_timestamp': episode.valid_at.isoformat(),
        'previous_episodes': [ep.content for ep in previous_episodes],
        'custom_prompt': custom_prompt,
        'entity_types': entity_types_context,
        'source_description': episode.source_description,
        'ensure_ascii': clients.ensure_ascii,
    }
    #提取实体
    #根据文档类型选择不同的提示词
    #反思机制，多次提取，防止遗漏
    while entities_missed and reflexion_iterations <= MAX_REFLEXION_ITERATIONS:
        if episode.source == EpisodeType.message:
            llm_response = await llm_client.generate_response(
                prompt_library.extract_nodes.extract_message(context), #提示词
                response_model=ExtractedEntities,
            )
        elif episode.source == EpisodeType.text:
            llm_response = await llm_client.generate_response(
                prompt_library.extract_nodes.extract_text(context), response_model=ExtractedEntities
            )
        elif episode.source == EpisodeType.json:
            llm_response = await llm_client.generate_response(
                prompt_library.extract_nodes.extract_json(context), response_model=ExtractedEntities
            )

        response_object = ExtractedEntities(**llm_response)
        print(response_object,'提取实体：response_objectresponse_object')
        extracted_entities: list[ExtractedEntity] = response_object.extracted_entities

        reflexion_iterations += 1
        if reflexion_iterations < MAX_REFLEXION_ITERATIONS:
            missing_entities = await extract_nodes_reflexion(
                llm_client,
                episode,
                previous_episodes,
                [entity.name for entity in extracted_entities],
                clients.ensure_ascii,
            )

            entities_missed = len(missing_entities) != 0

            custom_prompt = 'Make sure that the following entities are extracted: '
            for entity in missing_entities:
                custom_prompt += f'\n{entity},'

    filtered_extracted_entities = [entity for entity in extracted_entities if entity.name.strip()]
    end = time()
    logger.debug(f'Extracted new nodes: {filtered_extracted_entities} in {(end - start) * 1000} ms')
    # Convert the extracted data into EntityNode objects
    extracted_nodes = []
    for extracted_entity in filtered_extracted_entities:
        entity_type_name = entity_types_context[extracted_entity.entity_type_id].get(
            'entity_type_name'
        )

        # Check if this entity type should be excluded
        if excluded_entity_types and entity_type_name in excluded_entity_types:
            logger.debug(f'Excluding entity "{extracted_entity.name}" of type "{entity_type_name}"')
            continue

        labels: list[str] = list({'Entity', str(entity_type_name)})

        new_node = EntityNode(
            name=extracted_entity.name,
            group_id=episode.group_id,
            agent_id=episode.agent_id,
            file_id=episode.file_id,
            labels=labels,
            summary='',
            created_at=utc_now(),
        )
        extracted_nodes.append(new_node)
        logger.debug(f'Created new node: {new_node.name} (UUID: {new_node.uuid})')

    logger.debug(f'Extracted nodes: {[(n.name, n.uuid) for n in extracted_nodes]}')
    return extracted_nodes


async def resolve_extracted_nodes(
    clients: GraphitiClients,
    extracted_nodes: list[EntityNode], #新提取的实体
    episode: EpisodicNode | None = None, #文档
    previous_episodes: list[EpisodicNode] | None = None,#历史文档
    entity_types: dict[str, type[BaseModel]] | None = None,
    existing_nodes_override: list[EntityNode] | None = None,
) -> tuple[list[EntityNode], dict[str, str], list[tuple[EntityNode, EntityNode]]]:
    llm_client = clients.llm_client
    driver = clients.driver
    #为每个新提取的实体搜索现有实体
    search_results: list[SearchResults] = await semaphore_gather(
        *[
            search(
                clients=clients,
                query=node.name,
                group_ids=[node.group_id],
                search_filter=SearchFilters(),
                config=NODE_HYBRID_SEARCH_RRF,
            )
            for node in extracted_nodes
        ]
    )
    #收集所有候选节点(历史实体)：候选节点是指可能与新提取的实体重复的现有实体节点。它们是去重判断的"对比对象"。
    candidate_nodes: list[EntityNode] = (
        [node for result in search_results for node in result.nodes]
        if existing_nodes_override is None
        else existing_nodes_override
    )

    existing_nodes_dict: dict[str, EntityNode] = {node.uuid: node for node in candidate_nodes}

    existing_nodes: list[EntityNode] = list(existing_nodes_dict.values())

    # 为LLM准备现有节点的上下文信息
    existing_nodes_context = (
        [
            {
                **{
                    'idx': i, #节点索引
                    'name': candidate.name, #节点名称
                    'entity_types': candidate.labels, #节点类型标签
                },
                **candidate.attributes, #节点属性
            }
            for i, candidate in enumerate(existing_nodes)
        ],
    )

    entity_types_dict: dict[str, type[BaseModel]] = entity_types if entity_types is not None else {}

    # 为新提取的节点准备上下文
    extracted_nodes_context = [
        {
            'id': i,
            'name': node.name,
            'entity_type': node.labels,
            'entity_type_description': entity_types_dict.get(
                next((item for item in node.labels if item != 'Entity'), '')
            ).__doc__
            or 'Default Entity Type',
        }
        for i, node in enumerate(extracted_nodes)
    ]
    #准备完整的上下文信息
    context = {
        'extracted_nodes': extracted_nodes_context, # 新提取的节点
        'existing_nodes': existing_nodes_context, # 现有节点
        'episode_content': episode.content if episode is not None else '', # 当前文档内容
        'previous_episodes': [ep.content for ep in previous_episodes] # 历史文档
        if previous_episodes is not None
        else [],
        'ensure_ascii': clients.ensure_ascii,
    }
    # 调用LLM判断重复
    llm_response = await llm_client.generate_response(
        prompt_library.dedupe_nodes.nodes(context),
        response_model=NodeResolutions,
    )
    # 解析LLM响应
    node_resolutions: list[NodeDuplicate] = NodeResolutions(**llm_response).entity_resolutions

    resolved_nodes: list[EntityNode] = []
    uuid_map: dict[str, str] = {}
    node_duplicates: list[tuple[EntityNode, EntityNode]] = []
    for resolution in node_resolutions:
        resolution_id: int = resolution.id # 新节点的ID
        duplicate_idx: int = resolution.duplicate_idx  # 重复节点的索引

        extracted_node = extracted_nodes[resolution_id]
        # 如果找到重复，使用现有节点；否则使用新节点
        resolved_node = (
            existing_nodes[duplicate_idx]
            if 0 <= duplicate_idx < len(existing_nodes)
            else extracted_node
        )

        # resolved_node.name = resolution.get('name')

        resolved_nodes.append(resolved_node)
        uuid_map[extracted_node.uuid] = resolved_node.uuid
        # 记录重复节点对
        duplicates: list[int] = resolution.duplicates
        if duplicate_idx not in duplicates and duplicate_idx > -1:
            duplicates.append(duplicate_idx)
        for idx in duplicates:
            existing_node = existing_nodes[idx] if idx < len(existing_nodes) else resolved_node

            node_duplicates.append((extracted_node, existing_node))

    logger.debug(f'Resolved nodes: {[(n.name, n.uuid) for n in resolved_nodes]}')

    new_node_duplicates: list[
        tuple[EntityNode, EntityNode]
    ] = await filter_existing_duplicate_of_edges(driver, node_duplicates)
    #去重后节点列表，新旧节点的uuid映射关系，重复节点的配对信息
    return resolved_nodes, uuid_map, new_node_duplicates


async def extract_attributes_from_nodes(
    clients: GraphitiClients,
    nodes: list[EntityNode],
    episode: EpisodicNode | None = None,
    previous_episodes: list[EpisodicNode] | None = None,
    entity_types: dict[str, type[BaseModel]] | None = None,
) -> list[EntityNode]:
    llm_client = clients.llm_client
    embedder = clients.embedder
    updated_nodes: list[EntityNode] = await semaphore_gather(
        *[
            extract_attributes_from_node(
                llm_client,
                node,
                episode,
                previous_episodes,
                entity_types.get(next((item for item in node.labels if item != 'Entity'), ''))
                if entity_types is not None
                else None,
                clients.ensure_ascii,
            )
            for node in nodes
        ]
    )

    await create_entity_node_embeddings(embedder, updated_nodes)

    return updated_nodes


async def extract_attributes_from_node(
    llm_client: LLMClient,
    node: EntityNode,
    episode: EpisodicNode | None = None,
    previous_episodes: list[EpisodicNode] | None = None,
    entity_type: type[BaseModel] | None = None,
    ensure_ascii: bool = False,
) -> EntityNode:
    node_context: dict[str, Any] = {
        'name': node.name,
        'summary': node.summary,
        'entity_types': node.labels,
        'attributes': node.attributes,
    }

    attributes_context: dict[str, Any] = {
        'node': node_context,
        'episode_content': episode.content if episode is not None else '',
        'previous_episodes': [ep.content for ep in previous_episodes]
        if previous_episodes is not None
        else [],
        'ensure_ascii': ensure_ascii,
    }

    summary_context: dict[str, Any] = {
        'node': node_context,
        'episode_content': episode.content if episode is not None else '',
        'previous_episodes': [ep.content for ep in previous_episodes]
        if previous_episodes is not None
        else [],
        'ensure_ascii': ensure_ascii,
    }

    llm_response = (
        (
            await llm_client.generate_response(
                prompt_library.extract_nodes.extract_attributes(attributes_context),
                response_model=entity_type,
                model_size=ModelSize.small,
            )
        )
        if entity_type is not None
        else {}
    )

    summary_response = await llm_client.generate_response(
        prompt_library.extract_nodes.extract_summary(summary_context),
        response_model=EntitySummary,
        model_size=ModelSize.small,
    )

    if entity_type is not None:
        entity_type(**llm_response)

    node.summary = summary_response.get('summary', '')
    node_attributes = {key: value for key, value in llm_response.items()}

    node.attributes.update(node_attributes)

    return node
