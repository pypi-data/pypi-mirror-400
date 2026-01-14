"""
GemFilter Components for EHPC
=============================

从 AttentionCompressor/my_baseline/GemFilter/ 移植的核心组件。

包含:
    - standard_dis_index: 计算 attention scores 并选择 top-k tokens
    - find_context: 触发 token selection 并保存 indices
    - EHPCAttentionMixin: 提供 EHPC 功能的 Mixin 类
    - load_ehpc_model: 加载并修改模型以支持 EHPC

关键实现细节:
    1. 使用最后 window_size 个 queries 的 attention 评估历史 tokens
    2. Head-restricted sum: 只在指定 heads 上求和得到 selection scores
    3. 池化平滑: 使用 avg_pool/max_pool 减少选择噪声
    4. Causal mask: 对最后 window_size 区域施加因果掩码
"""

from .utils import standard_dis_index, find_context
from .attention_mixin import EHPCAttentionMixin
from .model_loader import load_ehpc_model

__all__ = [
    "standard_dis_index",
    "find_context",
    "EHPCAttentionMixin",
    "load_ehpc_model",
]
