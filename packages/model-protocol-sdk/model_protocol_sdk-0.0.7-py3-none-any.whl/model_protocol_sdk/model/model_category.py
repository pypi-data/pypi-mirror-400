from dataclasses import dataclass
from enum import Enum
@dataclass
class ModelCategory(Enum):
    """模型分类"""
    NLP = "nlp"  # 自然语言处理
    SPEECH = "speech"  # 语音
    VISION = "vision"  # 计算机视觉
    MULTIMODAL = "multimodal"  # 多模态