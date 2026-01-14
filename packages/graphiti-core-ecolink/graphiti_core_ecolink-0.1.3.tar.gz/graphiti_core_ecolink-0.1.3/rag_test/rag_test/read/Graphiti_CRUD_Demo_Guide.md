# Graphiti 原生 API CRUD Demo 使用指南

## 目录
- [概述](#概述)
- [环境准备](#环境准备)
- [Graphiti原生API](#graphiti原生api)
- [核心功能](#核心功能)
- [使用示例](#使用示例)
- [高级搜索功能](#高级搜索功能)
- [数据管理](#数据管理)
- [最佳实践](#最佳实践)

## 概述

本Demo展示了如何使用Graphiti框架的原生API实现完整的CRUD（创建、读取、更新、删除）操作。Graphiti提供了丰富的原生方法，无需额外封装即可实现各种知识图谱操作。

### 主要特性
- **原生API调用**：直接使用Graphiti提供的方法
- **完整的CRUD操作**：支持创建、读取、更新、删除操作
- **高级搜索功能**：多种搜索策略和重排序方法
- **灵活的数据管理**：支持批量操作和自定义配置
- **时序数据支持**：内置时间维度的数据管理

## 环境准备

### 1. 系统要求
- Python 3.8+
- Neo4j数据库（本地或远程）
- 支持的LLM服务API密钥（OpenAI、Azure OpenAI、Anthropic Claude、Google Gemini等）

### 2. 依赖安装
```bash
# 安装Graphiti Core
pip install graphiti-core

# 或者从源码安装
git clone https://github.com/your-repo/graphiti.git
cd graphiti
pip install -e .
```

### 3. 环境配置
```python
# 配置环境变量
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
OPENAI_API_KEY = "your_openai_api_key"
```

## Graphiti原生API

### 1. 核心类和方法

#### Graphiti主类
```python
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from datetime import datetime, timezone

# 初始化Graphiti实例
graphiti = Graphiti(
    uri=NEO4J_URI,
    user=NEO4J_USER,
    password=NEO4J_PASSWORD,
    llm_client=llm_client,      # 可选：自定义LLM客户端
    embedder=embedder,          # 可选：自定义嵌入器
    cross_encoder=cross_encoder  # 可选：自定义重排序器
)

# 构建索引和约束
await graphiti.build_indices_and_constraints()

# 关闭连接
await graphiti.close()
```

#### 主要API方法
```python
# 数据创建
await graphiti.add_episode()           # 添加episode
await graphiti.add_triplet()           # 添加三元组

# 数据查询
await graphiti.search()                # 基础搜索
await graphiti.search_()               # 高级搜索
await graphiti.get_nodes_and_edges_by_episode()  # 按episode获取数据

# 数据删除
await graphiti.remove_episode()        # 删除episode
```

## 核心功能

### 1. CREATE 操作

#### 添加Episode（创建数据）
```python
async def create_episode_example():
    """使用Graphiti原生API创建episode"""
    
    # 创建文本episode
    result = await graphiti.add_episode(
        name="人物信息示例",
        episode_body="张三和李四都是腾讯公司的员工，张三是一名高级软件工程师，负责前端开发，李四是一名产品经理，负责用户增长产品。",
        source_description="用户输入的人物信息",
        reference_time=datetime.now(timezone.utc),
        source=EpisodeType.text,
        update_communities=True  # 启用社区更新
    )
    
    print(f"Episode创建成功，UUID: {result.episode.uuid}")
    print(f"提取的节点数量: {len(result.nodes)}")
    print(f"提取的关系数量: {len(result.edges)}")
    print(f"更新的社区数量: {len(result.communities)}")
    
    return result

# 创建JSON格式episode
async def create_json_episode_example():
    """创建JSON格式的episode"""
    
    json_data = {
        "company": "腾讯",
        "employees": [
            {"name": "张三", "position": "高级软件工程师", "department": "前端开发"},
            {"name": "李四", "position": "产品经理", "department": "用户增长"}
        ],
        "location": "深圳"
    }
    
    result = await graphiti.add_episode(
        name="公司组织架构",
        episode_body=json.dumps(json_data, ensure_ascii=False),
        source_description="公司组织信息JSON数据",
        reference_time=datetime.now(timezone.utc),
        source=EpisodeType.json,
        update_communities=True
    )
    
    return result
```

#### 添加三元组
```python
async def create_triplet_example():
    """使用add_triplet方法直接创建三元组"""
    
    from graphiti_core.nodes import EntityNode, EntityEdge
    
    # 创建源节点
    source_node = EntityNode(
        name="张三",
        entity_type="Person",
        group_id="default"
    )
    
    # 创建目标节点
    target_node = EntityNode(
        name="腾讯",
        entity_type="Company",
        group_id="default"
    )
    
    # 创建关系边
    edge = EntityEdge(
        source_node_uuid="",  # 将在add_triplet中设置
        target_node_uuid="",  # 将在add_triplet中设置
        fact="张三在腾讯工作",
        edge_type="WORKS_AT",
        group_id="default"
    )
    
    # 添加三元组到图
    await graphiti.add_triplet(source_node, edge, target_node)
    print("三元组添加成功")
```

### 2. READ 操作

#### 基础搜索
```python
async def basic_search_example():
    """使用Graphiti的基础搜索功能"""
    
    # 简单搜索
    print("=== 基础搜索 ===")
    results = await graphiti.search(
        query="张三在哪个公司工作？",
        num_results=5
    )
    
    print(f"找到 {len(results)} 个相关事实:")
    for i, result in enumerate(results, 1):
        print(f"{i}. UUID: {result.uuid}")
        print(f"   事实: {result.fact}")
        if hasattr(result, 'valid_at') and result.valid_at:
            print(f"   有效时间: {result.valid_at}")
        if hasattr(result, 'invalid_at') and result.invalid_at:
            print(f"   失效时间: {result.invalid_at}")
        print("---")
    
    return results

# 基于中心节点的搜索
async def center_node_search_example():
    """基于中心节点的搜索，提高结果相关性"""
    
    # 先搜索获取一个节点作为中心
    initial_results = await graphiti.search("张三", num_results=1)
    
    if initial_results:
        center_node_uuid = initial_results[0].source_node_uuid
        
        print(f"使用中心节点: {center_node_uuid}")
        
        # 基于中心节点重新搜索
        center_results = await graphiti.search(
            query="工作关系",
            center_node_uuid=center_node_uuid,
            num_results=5
        )
        
        print(f"基于中心节点找到 {len(center_results)} 个相关事实:")
        for result in center_results:
            print(f"- {result.fact}")
        
        return center_results
    
    return []
```

#### 高级搜索
```python
async def advanced_search_example():
    """使用Graphiti的高级搜索功能"""
    
    from graphiti_core.search.search_config import (
        SearchConfig, EdgeSearchConfig, EdgeSearchMethod, EdgeReranker
    )
    
    # 创建自定义搜索配置
    search_config = SearchConfig(
        edge_config=EdgeSearchConfig(
            search_methods=[EdgeSearchMethod.bm25, EdgeSearchMethod.cosine_similarity],
            reranker=EdgeReranker.cross_encoder  # 使用交叉编码器重排序
        ),
        limit=10
    )
    
    # 执行高级搜索
    results = await graphiti.search_(
        query="软件工程师的工作",
        config=search_config
    )
    
    print(f"高级搜索完成:")
    print(f"找到 {len(results.edges)} 个关系")
    print(f"找到 {len(results.nodes)} 个节点")
    
    # 显示搜索结果
    for edge in results.edges[:5]:
        print(f"- {edge.fact}")
    
    return results

# 按episode获取数据
async def get_episode_data_example():
    """获取特定episode的数据"""
    
    # 假设我们已经有一些episode UUID
    episode_uuids = ["uuid1", "uuid2"]  # 替换为实际的UUID
    
    results = await graphiti.get_nodes_and_edges_by_episode(episode_uuids)
    
    print(f"从指定episode获取到:")
    print(f"关系数量: {len(results.edges)}")
    print(f"节点数量: {len(results.nodes)}")
    
    return results
```

### 3. UPDATE 操作

由于Graphiti采用不可变数据模型，更新操作通过添加新版本实现：

```python
async def update_data_example():
    """通过添加新episode来"更新"数据"""
    
    # 添加更新后的信息
    updated_result = await graphiti.add_episode(
        name="张三信息更新",
        episode_body="张三现在是腾讯的高级前端工程师，负责React和Vue项目开发，有5年工作经验。",
        source_description="更新后的人物信息",
        reference_time=datetime.now(timezone.utc),
        source=EpisodeType.text,
        update_communities=True
    )
    
    print(f"更新episode创建成功，UUID: {updated_result.episode.uuid}")
    
    # 搜索更新后的信息
    updated_results = await graphiti.search("张三 前端工程师", num_results=3)
    
    print("更新后的搜索结果:")
    for result in updated_results:
        print(f"- {result.fact}")
    
    return updated_result
```

### 4. DELETE 操作

#### 删除Episode
```python
async def delete_episode_example():
    """删除指定的episode"""
    
    episode_uuid = "your_episode_uuid"  # 替换为实际的UUID
    
    try:
        await graphiti.remove_episode(episode_uuid)
        print(f"Episode {episode_uuid} 删除成功")
        
        # 验证删除结果
        try:
            # 尝试搜索已删除的episode
            results = await graphiti.search("已删除的内容", num_results=1)
            print("删除验证：未找到相关内容")
        except Exception:
            print("删除验证：episode已成功删除")
            
    except Exception as e:
        print(f"删除episode失败: {e}")
        raise

# 批量删除数据
async def bulk_delete_example():
    """批量删除多个episode"""
    
    episode_uuids = ["uuid1", "uuid2", "uuid3"]  # 替换为实际的UUID列表
    
    for uuid in episode_uuids:
        try:
            await graphiti.remove_episode(uuid)
            print(f"Episode {uuid} 删除成功")
        except Exception as e:
            print(f"删除Episode {uuid} 失败: {e}")
            continue
    
    print("批量删除操作完成")
```

## 使用示例

### 1. 完整的CRUD操作示例

```python
async def complete_crud_example():
    """完整的CRUD操作演示"""
    
    try:
        # 1. 创建数据
        print("=== 创建数据 ===")
        create_result = await graphiti.add_episode(
            name="完整示例数据",
            episode_body="这是一个完整的CRUD操作示例，展示了Graphiti的基本功能。",
            source_description="CRUD示例数据",
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.text
        )
        
        episode_uuid = create_result.episode.uuid
        print(f"创建成功，UUID: {episode_uuid}")
        
        # 2. 读取数据
        print("\n=== 读取数据 ===")
        search_results = await graphiti.search("CRUD示例", num_results=5)
        print(f"搜索到 {len(search_results)} 个结果")
        
        # 3. 更新数据（通过添加新版本）
        print("\n=== 更新数据 ===")
        update_result = await graphiti.add_episode(
            name="完整示例数据_更新版",
            episode_body="这是更新后的CRUD操作示例，包含了更多详细信息。",
            source_description="CRUD示例数据更新版",
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.text
        )
        print(f"更新成功，新UUID: {update_result.episode.uuid}")
        
        # 4. 删除数据
        print("\n=== 删除数据 ===")
        await graphiti.remove_episode(episode_uuid)
        print(f"原始episode {episode_uuid} 删除成功")
        
        print("\n=== CRUD操作演示完成 ===")
        
    except Exception as e:
        print(f"操作过程中发生错误: {e}")
        raise
```

### 2. 批量数据处理示例

```python
async def batch_processing_example():
    """批量处理多个episode"""
    
    # 准备批量数据
    episodes_data = [
        {
            "name": "员工信息_张三",
            "content": "张三是一名软件工程师，擅长Python和机器学习。",
            "description": "员工张三的基本信息"
        },
        {
            "name": "员工信息_李四", 
            "content": "李四是一名产品经理，负责用户增长产品设计。",
            "description": "员工李四的基本信息"
        },
        {
            "name": "公司信息",
            "content": "腾讯是一家互联网公司，总部位于深圳。",
            "description": "公司基本信息"
        }
    ]
    
    created_episodes = []
    
    print("开始批量处理...")
    
    for i, episode_data in enumerate(episodes_data, 1):
        try:
            result = await graphiti.add_episode(
                name=episode_data["name"],
                episode_body=episode_data["content"],
                source_description=episode_data["description"],
                reference_time=datetime.now(timezone.utc),
                source=EpisodeType.text,
                update_communities=True
            )
            
            created_episodes.append(result.episode.uuid)
            print(f"✓ Episode {i}/{len(episodes_data)} 创建成功: {episode_data['name']}")
            
        except Exception as e:
            print(f"✗ Episode {i}/{len(episodes_data)} 创建失败: {e}")
            continue
    
    print(f"\n批量处理完成，成功创建 {len(created_episodes)} 个episode")
    
    # 搜索批量创建的内容
    search_results = await graphiti.search("员工信息", num_results=10)
    print(f"搜索到 {len(search_results)} 个相关结果")
    
    return created_episodes
```

### 3. 高级搜索配置示例

```python
async def advanced_search_config_example():
    """演示不同的搜索配置"""
    
    from graphiti_core.search.search_config import (
        SearchConfig, EdgeSearchConfig, EdgeSearchMethod, EdgeReranker
    )
    
    # 配置1：BM25 + 余弦相似性 + RRF重排序
    config1 = SearchConfig(
        edge_config=EdgeSearchConfig(
            search_methods=[EdgeSearchMethod.bm25, EdgeSearchMethod.cosine_similarity],
            reranker=EdgeReranker.rrf
        ),
        limit=5
    )
    
    # 配置2：仅使用余弦相似性 + 交叉编码器重排序
    config2 = SearchConfig(
        edge_config=EdgeSearchConfig(
            search_methods=[EdgeSearchMethod.cosine_similarity],
            reranker=EdgeReranker.cross_encoder
        ),
        limit=5
    )
    
    # 配置3：混合搜索 + 节点距离重排序
    config3 = SearchConfig(
        edge_config=EdgeSearchConfig(
            search_methods=[EdgeSearchMethod.bm25, EdgeSearchMethod.cosine_similarity],
            reranker=EdgeReranker.node_distance
        ),
        limit=5
    )
    
    query = "软件工程师"
    
    print("=== 不同搜索配置的对比 ===")
    
    # 测试配置1
    results1 = await graphiti.search_(query, config=config1)
    print(f"配置1 (BM25+余弦+RRF): 找到 {len(results1.edges)} 个结果")
    
    # 测试配置2
    results2 = await graphiti.search_(query, config=config2)
    print(f"配置2 (余弦+交叉编码器): 找到 {len(results2.edges)} 个结果")
    
    # 测试配置3
    results3 = await graphiti.search_(query, config=config3)
    print(f"配置3 (混合+节点距离): 找到 {len(results3.edges)} 个结果")
    
    return results1, results2, results3
```

## 高级搜索功能

### 1. 搜索过滤器

```python
async def search_with_filters_example():
    """使用搜索过滤器进行精确搜索"""
    
    from graphiti_core.search.search_filters import SearchFilters
    
    # 创建搜索过滤器
    filters = SearchFilters(
        entity_types=["Person", "Company"],  # 只搜索特定类型的实体
        edge_types=["WORKS_AT", "FOUNDED"],  # 只搜索特定类型的关系
        min_confidence=0.7,                 # 最小置信度
        date_range={
            "start": datetime(2023, 1, 1, tzinfo=timezone.utc),
            "end": datetime(2024, 12, 31, tzinfo=timezone.utc)
        }
    )
    
    # 使用过滤器搜索
    results = await graphiti.search_(
        query="工作关系",
        search_filter=filters,
        num_results=10
    )
    
    print(f"使用过滤器搜索到 {len(results.edges)} 个结果")
    
    return results
```

### 2. 时间范围搜索

```python
async def temporal_search_example():
    """基于时间范围的搜索"""
    
    from graphiti_core.search.search_filters import SearchFilters
    
    # 搜索最近一个月的数据
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    filters = SearchFilters(
        date_range={
            "start": one_month_ago,
            "end": datetime.now(timezone.utc)
        }
    )
    
    results = await graphiti.search_(
        query="最新信息",
        search_filter=filters,
        num_results=10
    )
    
    print(f"最近一个月内找到 {len(results.edges)} 个结果")
    
    # 显示时间信息
    for edge in results.edges[:3]:
        if hasattr(edge, 'created_at') and edge.created_at:
            print(f"- {edge.fact} (创建时间: {edge.created_at})")
    
    return results
```

## 数据管理

### 1. 索引和约束管理

```python
async def index_management_example():
    """管理数据库索引和约束"""
    
    # 构建索引和约束
    print("正在构建索引和约束...")
    await graphiti.build_indices_and_constraints()
    print("索引和约束构建完成")
    
    # 注意：在生产环境中，这些操作通常只需要执行一次
    # 重复执行不会造成问题，但会增加不必要的开销
```

### 2. 社区管理

```python
async def community_management_example():
    """管理知识社区"""
    
    # 添加episode时自动更新社区
    result = await graphiti.add_episode(
        name="社区管理示例",
        episode_body="这是一个关于社区管理的示例，展示了如何自动构建知识社区。",
        source_description="社区管理示例",
        reference_time=datetime.now(timezone.utc),
        source=EpisodeType.text,
        update_communities=True  # 启用社区更新
    )
    
    print(f"社区更新完成，创建了 {len(result.communities)} 个社区")
    
    # 显示社区信息
    for community in result.communities:
        print(f"社区: {community.name} (成员数: {len(community.members)})")
    
    return result
```

## 最佳实践

### 1. 错误处理

```python
async def robust_operation_example():
    """健壮的操作示例，包含错误处理"""
    
    try:
        # 执行操作
        result = await graphiti.add_episode(
            name="错误处理示例",
            episode_body="这是一个测试内容。",
            source_description="错误处理测试",
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.text
        )
        
        print("操作成功")
        return result
        
    except Exception as e:
        print(f"操作失败: {e}")
        
        # 根据错误类型进行不同处理
        if "connection" in str(e).lower():
            print("连接错误，请检查数据库连接")
        elif "api" in str(e).lower():
            print("API错误，请检查API密钥和配置")
        else:
            print("未知错误，请查看详细日志")
        
        raise
```

### 2. 性能优化

```python
async def performance_optimization_example():
    """性能优化示例"""
    
    import time
    
    # 批量操作
    start_time = time.time()
    
    # 准备批量数据
    batch_data = [f"批量数据_{i}" for i in range(10)]
    
    # 批量处理
    for i, data in enumerate(batch_data):
        await graphiti.add_episode(
            name=f"批量示例_{i}",
            episode_body=data,
            source_description="批量处理示例",
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.text
        )
    
    end_time = time.time()
    print(f"批量处理完成，耗时: {end_time - start_time:.2f}秒")
    
    # 使用适当的搜索配置
    search_config = SearchConfig(
        edge_config=EdgeSearchConfig(
            search_methods=[EdgeSearchMethod.bm25, EdgeSearchMethod.cosine_similarity],
            reranker=EdgeReranker.rrf  # 使用RRF提高速度
        ),
        limit=10
    )
    
    # 执行优化搜索
    results = await graphiti.search_("批量数据", config=search_config)
    print(f"优化搜索完成，找到 {len(results.edges)} 个结果")
```

### 3. 资源管理

```python
async def resource_management_example():
    """资源管理示例"""
    
    # 使用上下文管理器或try-finally确保资源释放
    try:
        # 执行操作
        result = await graphiti.add_episode(
            name="资源管理示例",
            episode_body="这是一个关于资源管理的示例。",
            source_description="资源管理测试",
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.text
        )
        
        print("操作执行成功")
        return result
        
    finally:
        # 确保连接关闭
        await graphiti.close()
        print("资源已释放")

# 或者使用异步上下文管理器
async def context_manager_example():
    """使用异步上下文管理器的示例"""
    
    async with Graphiti(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD
    ) as graphiti:
        
        # 执行操作
        result = await graphiti.add_episode(
            name="上下文管理器示例",
            episode_body="使用异步上下文管理器的示例。",
            source_description="上下文管理器测试",
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.text
        )
        
        return result
    # 自动关闭连接
```

## 总结

本Demo展示了Graphiti框架原生API的强大功能，通过直接调用Graphiti提供的方法，开发者可以：

### 关键特性总结
1. **原生API调用**：直接使用Graphiti提供的方法，无需额外封装
2. **完整的CRUD操作**：支持所有基本的数据操作
3. **高级搜索功能**：多种搜索策略和重排序方法
4. **灵活的数据管理**：支持批量操作和自定义配置
5. **内置时序支持**：支持时间维度的数据管理

### 适用场景
- 知识图谱构建和管理
- 文档智能分析
- 关系数据挖掘
- 时序数据分析
- 企业知识管理

通过学习和实践这些原生API，开发者可以充分利用Graphiti框架的全部功能，构建出功能强大、性能优异的知识图谱应用。
