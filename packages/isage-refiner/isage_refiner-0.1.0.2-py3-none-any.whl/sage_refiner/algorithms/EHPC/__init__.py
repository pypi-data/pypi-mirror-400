"""
EHPC (Efficient Prompt Compression with Evaluator Heads)
========================================================

EHPC 是一种基于 Evaluator Heads 的高效 Prompt 压缩算法。

核心思想:
    1. 通过 Needle-in-a-Haystack 探测找到最重要的 Evaluator Heads
    2. 使用这些 Evaluator Heads 在指定层对 prompt tokens 打分
    3. 选择 Top-K 重要的 tokens 来压缩 prompt

关键特性:
    - Evaluator Heads: 通过 offline probing 选出能准确定位关键信息的 attention heads
    - Head-restricted Selection: 只使用指定 heads 的注意力分数来选择 tokens
    - Window Preservation: 最后 window_size 个 tokens 永远不压缩，保留近期上下文

算法流程:
    1. Prefill (Selection Mode): 运行模型到指定层，触发 token selection
    2. Index Extraction: 从 attention layer 提取被选中的 token indices
    3. Input Reconstruction: 用 indices gather 原始 input_ids，拼接 window tokens
    4. Normal Inference: 用压缩后的 input_ids 进行正常推理

参考实现: AttentionCompressor/my_baseline/GemFilter/

Exports:
    - EHPCCompressor: 主压缩器类
    - EHPCConfig: 配置类
    - EHPCOperator: SAGE Pipeline 操作符
"""

from .compressor import EHPCCompressor
from .config import (
    EHPCConfig,
    get_config_for_model,
    MODEL_CONFIGS,
    LLAMA_31_8B_CONFIG,
    CODELLAMA_7B_CONFIG,
    MISTRAL_NEMO_CONFIG,
    PHI3_MINI_CONFIG,
)

__all__ = [
    "EHPCCompressor",
    "EHPCConfig",
    "get_config_for_model",
    "MODEL_CONFIGS",
    "LLAMA_31_8B_CONFIG",
    "CODELLAMA_7B_CONFIG",
    "MISTRAL_NEMO_CONFIG",
    "PHI3_MINI_CONFIG",
]

# Operator 需要 SAGE 依赖，可选导出
try:
    from .operator import EHPCOperator

    __all__.append("EHPCOperator")
except ImportError:
    EHPCOperator = None
