# Graphiti 智能查询系统 - include_expired 参数使用指南

## 概述

`include_expired` 参数允许您控制查询结果是否包含失效的历史关系。这对于需要查看完整关系历史的场景非常有用。

## 参数说明

- **`include_expired=False`** (默认): 只返回当前有效的关系，不包含失效的关系
- **`include_expired=True`**: 返回所有关系，包括当前有效和已失效的关系

## 技术实现

### 正确的实现方式

系统使用 `SearchFilters` 来控制是否包含失效关系，而不是在 `EdgeSearchConfig` 中设置不存在的参数：

```python
# 创建搜索过滤器
if include_expired:
    # 如果要包含失效关系，不设置时间过滤条件
    search_filter = SearchFilters()
else:
    # 如果不包含失效关系，设置过滤条件排除失效的关系
    from graphiti_core.search.search_filters import ComparisonOperator
    from datetime import datetime, timezone
    
    current_time = datetime.now(timezone.utc)
    search_filter = SearchFilters(
        expired_at=[[{"date": current_time, "comparison_operator": ComparisonOperator.is_null}]],
        invalid_at=[[{"date": current_time, "comparison_operator": ComparisonOperator.is_null}]]
    )

# 使用过滤器进行搜索
results = await self.graphiti.search_(user_query, config=search_config, search_filter=search_filter)
```

### 为什么使用 SearchFilters？

1. **`EdgeSearchConfig` 没有 `include_expired` 参数**: 查看源码确认，`EdgeSearchConfig` 只包含搜索方法和重排序配置
2. **`SearchFilters` 是正确的方式**: 通过设置 `expired_at` 和 `invalid_at` 过滤条件来控制结果
3. **时间过滤逻辑**: 当 `include_expired=False` 时，只返回 `expired_at` 和 `invalid_at` 为 `null` 的关系

## 使用方法

### 1. 基本查询 - 不包含失效关系

```python
# 默认查询，不包含失效关系
result = await query_handler.handle_user_query(
    user_query="我和帅帅是什么关系",
    strategy="smart",
    include_expired=False  # 默认值，可省略
)
```

### 2. 查询包含失效关系

```python
# 查询包含失效关系
result = await query_handler.handle_user_query(
    user_query="我和帅帅是什么关系",
    strategy="smart",
    include_expired=True   # 包含失效关系
)
```

### 3. 直接调用特定查询策略

```python
# 关系查询策略，包含失效关系
result = await query_handler.smart_router.relationship_focused_search(
    user_query="我和帅帅是什么关系",
    intent={"type": "relationship_query"},
    include_expired=True
)
```

### 4. 时间上下文查询

```python
# 查询包含历史关系
historical_results = await query_handler.search_with_time_context(
    user_query="我和帅帅的关系变化",
    include_historical=True
)
```

## 配置说明

当 `include_expired=True` 时，系统会：

1. **创建空的 SearchFilters**: 不设置任何时间过滤条件
2. **包含所有关系**: 包括当前有效和已失效的关系
3. **传递过滤器**: 将 `search_filter` 传递给 `graphiti.search_()` 方法

当 `include_expired=False` 时，系统会：

1. **创建过滤条件**: 设置 `expired_at` 和 `invalid_at` 为 `null`
2. **排除失效关系**: 只返回当前有效的关系
3. **时间过滤**: 使用当前时间作为参考点

## 结果标识

在查询结果中，失效的关系会被标识：

- **`invalid_at`**: 关系失效的时间
- **`expired_at`**: 关系过期的时间
- **状态显示**: 在回答中会显示 "(已失效)" 或 "(已过期)"

## 使用场景

### 1. 关系历史追踪
```python
# 查看完整的关系变化历史
result = await query_handler.handle_user_query(
    user_query="我和帅帅的关系变化",
    include_expired=True
)
```

### 2. 审计和合规
```python
# 查看所有关系记录，包括失效的
result = await query_handler.handle_user_query(
    user_query="所有与五环相关的关系",
    include_expired=True
)
```

### 3. 时间线分析
```python
# 分析关系的时间变化
historical_results = await query_handler.search_with_time_context(
    user_query="五环的职位变化",
    include_historical=True
)
```

## 注意事项

1. **性能影响**: 包含失效关系会增加查询结果数量，可能影响性能
2. **数据完整性**: 失效关系仍然存在于数据库中，只是被标记为不可见
3. **查询策略**: 所有查询策略都支持此参数
4. **结果排序**: 结果会按时间排序，最新的关系在前
5. **正确实现**: 使用 `SearchFilters` 而不是不存在的配置参数

## 示例输出

### 不包含失效关系
```
找到以下关系信息：
• 我和帅帅是朋友关系 (相似度: 0.850)
```

### 包含失效关系
```
**注意：本次查询包含了失效的历史关系信息**

找到以下关系信息：
• 我和帅帅是朋友关系 (相似度: 0.850)
• 我和帅帅是同学关系 (已失效) (相似度: 0.750)
```

## 测试

运行测试脚本验证功能：

```bash
# 测试参数传递功能
python test_include_expired.py

# 测试修正后的搜索实现
python test_corrected_search.py

# 运行完整示例
python user_query.py
```

## 技术实现细节

- **参数传递**: 通过函数参数链式传递，支持所有查询策略
- **过滤器创建**: 根据 `include_expired` 参数动态创建 `SearchFilters`
- **时间过滤**: 使用 `ComparisonOperator.is_null` 来排除失效关系
- **结果处理**: 在 `generate_answer` 中标识失效关系
- **日志记录**: 记录是否包含失效关系的查询状态
- **错误修正**: 使用正确的 `SearchFilters` 而不是不存在的配置参数
