# Graphiti Core Ecolink

Enhanced graph-based retrieval-augmented generation (RAG) system with ecolink optimizations.

## Installation

```bash
pip install graphiti-core-ecolink
```

## Quick Start

```python
from graphiti_core_ecolink import Graphiti
from graphiti_core_ecolink.driver import Neo4jDriver

# 创建 Graphiti 实例
graphiti = Graphiti(
    driver=Neo4jDriver(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password"
    )
)

# 添加数据
await graphiti.add_episode(
    name="测试对话",
    content="用户询问关于帅帅的信息",
    group_id="test_group"
)

# 搜索
results = await graphiti.search_(
    query="帅帅干啥了",
    group_ids=["test_group"]
)
```

## Features

- 🚀 **Enhanced Performance**: Optimized for ecolink use cases
- 🔍 **Advanced Search**: BM25, Cosine Similarity, and BFS search methods
- 📊 **RRF Scoring**: Reciprocal Rank Fusion for better result ranking
- 🌐 **Multi-tenant Support**: Group-based data isolation
- 🔧 **Easy Integration**: Simple API for Django and FastAPI projects

## Dependencies

- Neo4j 5.26.0+
- Python 3.10+
- Pydantic 2.11.5+
- OpenAI 1.91.0+

## License

Apache-2.0
