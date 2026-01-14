# Graphiti 智能用户查询系统

## 🎯 系统概述

这是一个基于Graphiti的智能查询系统，专门为**百科全书式的大模型助手**设计，能够自动识别用户查询意图，选择合适的查询策略，返回完整准确的信息。

## 🌟 核心特性

### 1. **智能意图识别**
- 自动分析用户查询的意图和类型
- 支持各行各业、各种专业领域的查询
- 不局限于预定义类型，灵活适应各种查询需求

### 2. **多策略查询**
- **关系查询策略**：优先查询实体间关系
- **实体查询策略**：优先查询实体详细信息
- **内容查询策略**：优先查询文档内容
- **知识查询策略**：优先查询知识性内容
- **综合查询策略**：查询所有类型信息

### 3. **分层查询机制**
- 从精确到模糊，逐步扩展
- 三层查询：精确匹配 → 语义相似 → 模糊匹配
- 确保找到最相关的结果

### 4. **自适应查询**
- 根据用户历史行为调整查询策略
- 支持个性化查询偏好
- 持续优化查询效果

## 🔍 支持的查询类型

### **知识查询类**
- `concept_query`: 概念解释、定义查询
- `fact_query`: 事实信息、数据查询
- `how_to_query`: 方法步骤、操作指导
- `why_query`: 原因分析、原理解释

### **实体查询类**
- `person_query`: 人物信息、生平介绍
- `organization_query`: 组织信息、机构介绍
- `place_query`: 地点信息、地理介绍
- `thing_query`: 物品信息、产品介绍

### **关系查询类**
- `relationship_query`: 实体间关系、联系
- `comparison_query`: 比较分析、对比
- `influence_query`: 影响关系、因果关系

### **内容查询类**
- `document_query`: 文档资料、文献查询
- `research_query`: 研究信息、学术查询
- `news_query`: 新闻信息、事件查询

### **综合查询类**
- `comprehensive_query`: 综合信息、全面了解
- `analysis_query`: 分析研究、深度解析
- `summary_query`: 总结概括、要点提炼

### **专业领域类**
- `technical_query`: 技术问题、专业咨询
- `business_query`: 商业信息、市场分析
- `academic_query`: 学术问题、研究咨询
- `medical_query`: 医疗健康、医学咨询
- `legal_query`: 法律问题、法规咨询

## 🚀 使用方法

### **基本使用**

```python
from user_query import UserQueryHandler

# 创建查询处理器
query_handler = UserQueryHandler(graphiti, llm_client)

# 处理用户查询
result = await query_handler.handle_user_query(
    user_query="如何学习深度学习？",
    user_id="user123",
    strategy="smart"  # 可选: "smart", "layered", "adaptive"
)

# 获取结果
print(result["answer"])                    # 生成的回答
print(result["search_strategy"])           # 使用的查询策略
print(result["search_results"]["total_count"])  # 找到的结果数量
```

### **查询策略选择**

```python
# 1. 智能路由策略（推荐）
result = await query_handler.handle_user_query(
    user_query="Python是什么编程语言？",
    strategy="smart"
)

# 2. 分层查询策略
result = await query_handler.handle_user_query(
    user_query="人工智能的发展历史",
    strategy="layered"
)

# 3. 自适应查询策略
result = await query_handler.handle_user_query(
    user_query="区块链技术原理",
    strategy="adaptive"
)
```

## 📊 查询示例

### **实体查询示例**
```
用户查询: "清华大学怎么样？"
查询类型: person_query
策略: 实体查询策略
结果: 优先返回清华大学的详细信息、属性、摘要等
```

### **关系查询示例**
```
用户查询: "北京和上海有什么区别？"
查询类型: comparison_query
策略: 关系查询策略
结果: 优先返回两个城市的关系、对比信息等
```

### **知识查询示例**
```
用户查询: "如何学习深度学习？"
查询类型: how_to_query
策略: 知识查询策略
结果: 优先返回学习方法、步骤、指导等知识性内容
```

### **综合查询示例**
```
用户查询: "人工智能的发展历史和未来趋势"
查询类型: comprehensive_query
策略: 综合查询策略
结果: 返回所有相关信息，包括历史、现状、趋势等
```

## 🔧 配置说明

### **环境要求**
- Python 3.8+
- Graphiti Core
- Neo4j数据库
- 阿里云通义千问API（或其他LLM API）

### **配置参数**
```python
# Neo4j配置
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# 阿里云API配置
API_KEY = "your_api_key"
ALIYUN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

## 🎨 自定义扩展

### **添加新的查询类型**
```python
# 在analyze_user_intent方法中添加新的类型判断
elif intent["type"] == "custom_query":
    return await self.custom_search_strategy(user_query, intent)
```

### **自定义查询策略**
```python
async def custom_search_strategy(self, user_query: str, intent: Dict[str, Any]):
    """自定义查询策略"""
    # 实现您的查询逻辑
    pass
```

## 📈 性能优化

### **并发控制**
- 使用`semaphore_gather`控制并发数量
- 避免API限流和资源耗尽
- 可配置的并发限制

### **缓存策略**
- 查询结果缓存
- 用户意图缓存
- 减少重复计算

### **智能重试**
- 失败查询自动重试
- 降级策略支持
- 错误处理和恢复

## 🏁 总结

这个智能查询系统为百科全书式的大模型助手提供了：

1. **全面的查询类型支持** - 覆盖各行各业的需求
2. **智能的意图识别** - 自动理解用户真实意图
3. **灵活的查询策略** - 根据查询类型选择最佳策略
4. **高质量的结果** - 多维度信息整合，提供完整答案
5. **可扩展的架构** - 易于添加新的查询类型和策略

无论是技术问题、商业咨询、学术研究，还是日常生活问题，系统都能智能识别并提供最合适的查询策略，确保用户获得准确、完整、有用的信息。
