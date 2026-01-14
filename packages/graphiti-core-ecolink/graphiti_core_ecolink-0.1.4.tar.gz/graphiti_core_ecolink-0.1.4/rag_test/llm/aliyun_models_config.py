"""
阿里云百联模型配置
支持多种模型配置以适应不同的使用场景
"""

# 阿里云API配置
ALIYUN_API_CONFIG = {
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_version": "2024-01-01"
}

# 模型配置字典
MODEL_CONFIGS = {
    "fast": {
        "description": "快速响应配置",
        "chat_model": "qwen-turbo",
        "embedding_model": "text-embedding-v1",
        "temperature": 0.1,
        "max_tokens": 2048
    },
    "balanced": {
        "description": "平衡配置",
        "chat_model": "qwen-plus-2025-07-28",
        "embedding_model": "text-embedding-v1",
        "temperature": 0.3,
        "max_tokens": 4096
    },
    "performance": {
        "description": "高性能配置",
        "chat_model": "qwen-turbo",
        "embedding_model": "text-embedding-v1",
        "temperature": 0.2,
        "max_tokens": 8192
    },
    "longtext": {
        "description": "长文本处理配置",
        "chat_model": "qwen-max-longcontext",
        "embedding_model": "text-embedding-v1",
        "temperature": 0.1,
        "max_tokens": 32768
    }
}

def get_model_config(config_name: str = "balanced"):
    """
    获取模型配置
    
    Args:
        config_name: 配置名称 ("fast", "balanced", "performance", "longtext")
        
    Returns:
        dict: 模型配置字典
        
    Raises:
        ValueError: 当配置名称不存在时
    """
    if config_name not in MODEL_CONFIGS:
        available_configs = list(MODEL_CONFIGS.keys())
        raise ValueError(f"未知的模型配置 '{config_name}'。可用配置: {available_configs}")
    
    return MODEL_CONFIGS[config_name]

def list_available_configs():
    """
    列出所有可用的模型配置
    
    Returns:
        dict: 配置名称和描述的字典
    """
    return {name: config["description"] for name, config in MODEL_CONFIGS.items()}
