from abc import ABC, abstractmethod
import threading
from typing import Dict, Any, Optional, List, Union
import logging

logger = logging.getLogger(__name__)


class UniversalModelAdapter(ABC):
    """
    通用模型适配器基类
    用户继承这个类，在一个类中实现所有模型
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._grpc_stub = None
        self._current_mission_id = None

    def set_grpc_stub(self, grpc_stub):
        """设置gRPC stub（可选）"""
        self._grpc_stub = grpc_stub

    def set_current_mission_id(self, mission_id: str):
        """设置当前任务ID（可选）"""
        self._current_mission_id = mission_id

    @property
    @abstractmethod
    def protocol_name(self) -> str:
        pass

    @abstractmethod
    def execute_model(self, inputs: Any, **kwargs) -> Any:
        """
        执行模型预测

        Args:
            model_id: 模型ID
            inputs: 输入数据
            **kwargs: 模型特定参数

        Returns:
            预测结果
        """
        pass


    @abstractmethod
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        返回所有支持的模型信息

        Returns:
            {
                "model_id": "模型唯一ID",  # 必填
                "model_name": "模型显示名称",  # 必填
                "category": "nlp/speech/vision/multimodal",  # 必填
                "description": "模型功能描述",  # 必填
                "subtype": "具体用途描述",  # 必填，用户自定义
                "provider": "提供者",
                "version": "版本",
                "input_formats": ["支持的输入格式"],
                "output_formats": ["支持的输出格式"]
            }
        """
        pass




