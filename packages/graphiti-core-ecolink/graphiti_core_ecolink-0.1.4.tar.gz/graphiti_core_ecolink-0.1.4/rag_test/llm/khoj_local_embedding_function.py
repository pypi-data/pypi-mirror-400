"""
基于Khoj的本地向量化函数
提供独立的本地向量化功能，可直接替换Graphiti中的云端向量化调用
"""

import asyncio
import logging
import time
from typing import List, Union, Optional
import torch
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

class KhojLocalEmbedding:
    """
    基于Khoj的本地向量化类
    使用Sentence Transformers实现本地向量化，完全替换云端API调用
    """
    
    def __init__(self, 
                 model_name: str = "thenlper/gte-small",
                 device: str = "auto",
                 normalize_embeddings: bool = True,
                 max_seq_length: int = 512,
                 batch_size: int = 32):
        """
        初始化本地向量化器
        
        Args:
            model_name: 模型名称，默认使用Khoj的模型
            device: 设备类型 ("auto", "cpu", "cuda", "mps")
            normalize_embeddings: 是否归一化向量
            max_seq_length: 最大序列长度
            batch_size: 批处理大小
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.normalize_embeddings = normalize_embeddings
        self.max_seq_length = max_seq_length
        self.batch_size = batch_size
        self.model = None
        self.embedding_dim = None
        
        # 初始化模型
        self._load_model()
    
    def _get_device(self, device: str) -> str:
        """自动选择设备"""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"  # Apple Silicon GPU
            else:
                return "cpu"
        return device
    
    def _load_model(self):
        """加载Sentence Transformer模型"""
        try:
            logger.info(f"正在加载本地向量化模型: {self.model_name}")
            start_time = time.time()
            
            # 检查是否是本地路径
            import os
            if os.path.exists(self.model_name):
                logger.info(f"使用本地模型路径: {self.model_name}")
                model_path = self.model_name
            else:
                logger.info(f"使用Hugging Face模型名称: {self.model_name}")
                model_path = self.model_name
            
            # 加载模型
            self.model = SentenceTransformer(
                model_path,
                device=self.device,
                cache_folder=None
            )
            
            # 设置最大序列长度
            if hasattr(self.model, 'max_seq_length'):
                self.model.max_seq_length = self.max_seq_length
            
            # 测试模型并获取向量维度
            test_embedding = self.model.encode(
                ["test"], 
                normalize_embeddings=self.normalize_embeddings
            )
            self.embedding_dim = len(test_embedding[0])
            
            load_time = time.time() - start_time
            logger.info(f"模型加载完成，耗时: {load_time:.2f}秒，向量维度: {self.embedding_dim}")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """
        单个查询向量化（兼容Khoj接口）
        
        Args:
            query: 查询文本
            
        Returns:
            List[float]: 向量化结果
        """
        if not query.strip():
            return [0.0] * self.embedding_dim
        
        try:
            embedding = self.model.encode(
                [query],
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=False,
                convert_to_tensor=False
            )[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"查询向量化失败: {e}")
            return [0.0] * self.embedding_dim
    
    def embed_documents(self, docs: List[str]) -> List[List[float]]:
        """
        批量文档向量化（兼容Khoj接口）
        
        Args:
            docs: 文档列表
            
        Returns:
            List[List[float]]: 向量化结果列表
        """
        if not docs:
            return []
        
        # 过滤空文档
        valid_docs = [doc for doc in docs if doc.strip()]
        if not valid_docs:
            return [[0.0] * self.embedding_dim] * len(docs)
        
        try:
            embeddings = self.model.encode(
                valid_docs,
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=True,
                convert_to_tensor=False,
                batch_size=self.batch_size
            )
            
            # 处理空文档的占位符
            result = []
            valid_idx = 0
            for doc in docs:
                if doc.strip():
                    result.append(embeddings[valid_idx].tolist())
                    valid_idx += 1
                else:
                    result.append([0.0] * self.embedding_dim)
            
            return result
        except Exception as e:
            logger.error(f"文档向量化失败: {e}")
            return [[0.0] * self.embedding_dim] * len(docs)
    
    async def embed_query_async(self, query: str) -> List[float]:
        """异步单个查询向量化"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed_query, query)
    
    async def embed_documents_async(self, docs: List[str]) -> List[List[float]]:
        """异步批量文档向量化"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed_documents, docs)
    
    def get_embedding_dimension(self) -> int:
        """获取向量维度"""
        return self.embedding_dim
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "device": self.device,
            "normalize_embeddings": self.normalize_embeddings,
            "max_seq_length": self.max_seq_length,
            "batch_size": self.batch_size
        }


# ==================== 全局实例和便捷函数 ====================

# 全局向量化实例
_global_embedder: Optional[KhojLocalEmbedding] = None

def initialize_khoj_embedding(model_name: str = "thenlper/gte-small", 
                             device: str = "auto",
                             normalize_embeddings: bool = True,
                             max_seq_length: int = 512,
                             batch_size: int = 32) -> KhojLocalEmbedding:
    """
    初始化全局Khoj向量化实例
    
    Args:
        model_name: 模型名称
        device: 设备类型
        normalize_embeddings: 是否归一化向量
        max_seq_length: 最大序列长度
        batch_size: 批处理大小
    
    Returns:
        KhojLocalEmbedding: 向量化实例
    """
    global _global_embedder
    _global_embedder = KhojLocalEmbedding(
        model_name=model_name,
        device=device,
        normalize_embeddings=normalize_embeddings,
        max_seq_length=max_seq_length,
        batch_size=batch_size
    )
    return _global_embedder

def get_khoj_embedding() -> KhojLocalEmbedding:
    """获取全局向量化实例"""
    global _global_embedder
    if _global_embedder is None:
        _global_embedder = initialize_khoj_embedding()
    return _global_embedder

# ==================== 直接替换函数 ====================

def khoj_embed_query(query: str) -> List[float]:
    """
    直接替换函数：查询向量化
    替换原来的云端API调用
    
    Args:
        query: 查询文本
        
    Returns:
        List[float]: 向量化结果
    """
    embedder = get_khoj_embedding()
    return embedder.embed_query(query)

def khoj_embed_documents(docs: List[str]) -> List[List[float]]:
    """
    直接替换函数：文档向量化
    替换原来的云端API调用
    
    Args:
        docs: 文档列表
        
    Returns:
        List[List[float]]: 向量化结果列表
    """
    embedder = get_khoj_embedding()
    return embedder.embed_documents(docs)

async def khoj_embed_query_async(query: str) -> List[float]:
    """异步查询向量化"""
    embedder = get_khoj_embedding()
    return await embedder.embed_query_async(query)

async def khoj_embed_documents_async(docs: List[str]) -> List[List[float]]:
    """异步文档向量化"""
    embedder = get_khoj_embedding()
    return await embedder.embed_documents_async(docs)

# ==================== 预设配置 ====================

def create_lightweight_embedding() -> KhojLocalEmbedding:
    """创建轻量级配置"""
    return KhojLocalEmbedding(
        model_name="thenlper/gte-small",
        device="auto",
        normalize_embeddings=True,
        max_seq_length=512,
        batch_size=16
    )

def create_high_performance_embedding() -> KhojLocalEmbedding:
    """创建高性能配置"""
    return KhojLocalEmbedding(
        model_name="thenlper/gte-large",
        device="auto",
        normalize_embeddings=True,
        max_seq_length=512,
        batch_size=64
    )

def create_chinese_embedding() -> KhojLocalEmbedding:
    """创建中文优化配置"""
    return KhojLocalEmbedding(
        model_name="shibing624/text2vec-base-chinese",
        device="auto",
        normalize_embeddings=True,
        max_seq_length=512,
        batch_size=32
    )

def create_local_path_embedding(model_path: str) -> KhojLocalEmbedding:
    """创建本地路径模型配置"""
    return KhojLocalEmbedding(
        model_name=model_path,  # 直接使用本地路径
        device="auto",
        normalize_embeddings=True,
        max_seq_length=512,
        batch_size=32
    )

def create_khoj_style_embedding() -> KhojLocalEmbedding:
    """创建Khoj风格的本地向量化配置"""
    return KhojLocalEmbedding(
        model_name="thenlper/gte-small",  # Khoj默认模型
        device="auto",
        normalize_embeddings=True,
        max_seq_length=512,
        batch_size=32
    )

# ==================== 测试函数 ====================

def test_khoj_embedding(text: str = "这是一个测试文本") -> dict:
    """
    测试Khoj向量化功能
    
    Args:
        text: 测试文本
        
    Returns:
        dict: 测试结果
    """
    try:
        # 初始化
        embedder = get_khoj_embedding()
        
        # 测试单个文本
        start_time = time.time()
        embedding = embedder.embed_query(text)
        single_time = time.time() - start_time
        
        # 测试批量文本
        test_texts = [f"测试文本{i}" for i in range(5)]
        start_time = time.time()
        batch_embeddings = embedder.embed_documents(test_texts)
        batch_time = time.time() - start_time
        
        return {
            "success": True,
            "single_embedding_time": single_time,
            "batch_embedding_time": batch_time,
            "embedding_dimension": len(embedding),
            "model_info": embedder.get_model_info()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 使用示例 ====================

if __name__ == "__main__":
    print("测试Khoj本地向量化功能...")
    print("=" * 50)
    
    # 方式1: 使用Hugging Face模型名称（推荐）
    print("方式1: 使用Hugging Face模型名称")
    print("-" * 30)
    
    # 初始化
    initialize_khoj_embedding(model_name="thenlper/gte-small")
    
    # 测试
    result = test_khoj_embedding("这是一个测试文本")
    print(f"测试结果: {result}")
    
    # 使用向量化函数
    query_embedding = khoj_embed_query("用户查询")
    print(f"查询向量维度: {len(query_embedding)}")
    
    docs_embeddings = khoj_embed_documents(["文档1", "文档2", "文档3"])
    print(f"文档向量数量: {len(docs_embeddings)}")
    
    print("\n" + "=" * 50)
    
    # 方式2: 使用本地模型路径（如果有本地模型）
    print("方式2: 使用本地模型路径")
    print("-" * 30)
    
    # 示例：如果有本地模型文件
    # local_model_path = "/path/to/your/local/model"
    # if os.path.exists(local_model_path):
    #     local_embedder = create_local_path_embedding(local_model_path)
    #     print(f"本地模型加载成功: {local_model_path}")
    # else:
    #     print("本地模型路径不存在，跳过测试")
    
    print("注意：要使用本地模型路径，请确保模型文件存在且格式正确")
    
    print("\n" + "=" * 50)
    print("支持的模型名称格式:")
    print("1. Hugging Face模型名称: 'thenlper/gte-small'")
    print("2. 本地模型路径: '/path/to/your/model'")
    print("3. 相对路径: './models/my_model'")
