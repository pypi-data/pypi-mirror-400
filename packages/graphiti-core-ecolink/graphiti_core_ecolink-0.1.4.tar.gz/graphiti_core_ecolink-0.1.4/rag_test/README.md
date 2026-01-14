# Graphiti CRUD 演示项目

本项目演示了如何使用Graphiti实现完整的CRUD操作，连接Neo4j数据库，并集成了阿里云百联模型。

## 功能特性

- **完整的CRUD操作**: 创建、读取、更新、删除数据
- **阿里云百联模型集成**: 使用阿里云通义千问系列模型
- **Neo4j数据库支持**: 图数据库存储和查询
- **多种模型配置**: 支持快速、平衡、高性能、长文本等不同配置
- **向量搜索**: 支持语义搜索和相似度匹配

## 项目结构

```
rag_test/
├── graphiti_crud_demo.py    # 主要的CRUD演示代码
├── llm/                     # LLM客户端和配置
│   ├── __init__.py
│   ├── aliyun_models_config.py    # 阿里云模型配置
│   └── aliyun_llm_client.py       # 阿里云LLM客户端
├── requirements.txt         # 依赖包列表
└── README.md               # 项目说明文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 1. 阿里云API配置

在使用前，您需要配置阿里云API密钥：

```python
# 配置参数
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password"
API_KEY = "your_aliyun_api_key"  # 阿里云API密钥

# 阿里云API配置
ALIYUN_BASE_URL = "https://dashscope.aliyuncs.com/v1"
```

**重要**: 阿里云百联API使用兼容模式端点，支持OpenAI格式的API调用：
- 聊天完成API: `/chat/completions`
- 向量嵌入API: `/embeddings`

### 2. 模型配置

项目支持多种模型配置：

- **fast**: 快速响应配置 (qwen-turbo)
- **balanced**: 平衡配置 (qwen-plus) - 默认
- **performance**: 高性能配置 (qwen-max)
- **longtext**: 长文本处理配置 (qwen-max-longcontext)

```python
# 创建CRUD实例，使用performance配置
crud = GraphitiCRUD(
    NEO4J_URI, 
    NEO4J_USER, 
    NEO4J_PASSWORD, 
    API_KEY, 
    ALIYUN_BASE_URL, 
    model_config="performance"
)
```

## 使用方法

### 1. 基本CRUD操作

```python
import asyncio
from graphiti_crud_demo import GraphitiCRUD

async def main():
    # 创建CRUD实例
    crud = GraphitiCRUD(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="your_password",
        api_key="your_aliyun_api_key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_config="balanced"
    )
    
    try:
        # 连接数据库
        await crud.connect()
        
        # CREATE - 创建数据
        episode_uuid = await crud.add_episode(
            name="人物信息",
            content="张三是一名软件工程师，在北京工作，擅长Python和机器学习。",
            description="用户输入的人物信息"
        )
        
        # READ - 搜索数据
        results = await crud.search_edges("软件工程师", num_results=5)
        
        # UPDATE - 更新数据（通过添加新版本）
        updated_uuid = await crud.add_updated_episode(
            name="张三信息更新",
            content="张三是一名高级软件工程师，有5年工作经验。",
            description="更新后的人物信息"
        )
        
        # DELETE - 删除数据（谨慎使用）
        # await crud.delete_all_data()
        
    finally:
        # 关闭连接
        await crud.close()

# 运行
asyncio.run(main())
```

### 2. 搜索功能

```python
# 搜索边（关系）
edge_results = await crud.search_edges("工程师", num_results=10)

# 搜索节点
node_results = await crud.search_nodes("Python", num_results=10)

# 基于中心节点的搜索
if edge_results:
    center_uuid = edge_results[0].source_node_uuid
    center_results = await crud.search_with_center_node(
        "工程师", center_uuid, num_results=5
    )
```

### 3. JSON数据支持

```python
# 添加JSON格式的episode
person_data = {
    "name": "李四",
    "age": 30,
    "profession": "数据科学家",
    "location": "上海",
    "skills": ["Python", "R", "SQL", "机器学习"]
}

episode_uuid = await crud.add_json_episode(
    name="李四信息",
    data=person_data,
    description="JSON格式的人物信息"
)
```

## 阿里云百联模型集成

### 实现原理

本项目基于OpenAI客户端实现了阿里云百联模型的集成：

1. **AliyunLLMClient**: 继承自LLMClient，使用OpenAI客户端格式
2. **模型配置**: 支持多种阿里云通义千问模型配置
3. **API兼容**: 通过兼容模式端点支持OpenAI格式的API调用

### 支持的模型

- **qwen-turbo**: 快速响应，适合实时对话
- **qwen-plus**: 平衡性能和速度
- **qwen-max**: 高性能，适合复杂任务
- **qwen-max-longcontext**: 长文本处理

### 配置示例

```python
# 在aliyun_models_config.py中定义模型配置
MODEL_CONFIGS = {
    "performance": {
        "description": "高性能配置",
        "chat_model": "qwen-max",
        "embedding_model": "text-embedding-v1",
        "temperature": 0.2,
        "max_tokens": 8192
    }
}
```

## 注意事项

1. **API密钥安全**: 请妥善保管您的阿里云API密钥，不要提交到版本控制系统
2. **数据库连接**: 确保Neo4j数据库正在运行并可访问
3. **删除操作**: 删除操作会清空所有数据，请谨慎使用
4. **模型选择**: 根据您的需求选择合适的模型配置
5. **错误处理**: 代码包含完整的错误处理和重试机制

## 故障排除

### 常见问题

1. **导入错误**: 确保所有依赖包已正确安装
2. **连接失败**: 检查Neo4j数据库是否运行，网络连接是否正常
3. **API错误**: 验证阿里云API密钥是否正确，账户余额是否充足
4. **模型错误**: 确认使用的模型名称在阿里云API中可用

### 日志调试

项目使用详细的日志记录，可以通过调整日志级别来调试问题：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### API测试

运行测试脚本验证API配置：

```bash
cd rag_test
python test_aliyun_compatible_api.py
```

## 相关链接

- [阿里云通义千问API文档](https://help.aliyun.com/zh/dashscope/)
- [阿里云API密钥管理](https://dashscope.console.aliyun.com/apiKey)
- [阿里云模型列表](https://dashscope.console.aliyun.com/model)
