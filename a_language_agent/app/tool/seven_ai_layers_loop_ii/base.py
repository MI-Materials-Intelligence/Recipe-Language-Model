from abc import ABC, abstractmethod
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class LayerSide(Enum):
    """Layer side enumeration"""
    LEFT = "left"
    RIGHT = "right"

class BaseLayer(ABC):
    def __init__(self, side: LayerSide = None):
        """
        Initialize base layer

        Args:
            side: Layer side (LEFT or RIGHT)
        """
        self.layer_name = self.__class__.__name__.lower()
        self.side = side
        # If side is specified, add it to the layer name
        if self.side:
            self.full_name = f"{self.side.value}_{self.layer_name}"
        else:
            self.full_name = self.layer_name

    @abstractmethod
    def process(self, task_id: str, data: str) -> str:
        """
        Abstract method for processing data

        Args:
            task_id: Task ID
            data: Input data

        Returns:
            str: Processed data
        """
        pass

    def log_info(self, task_id: str, message: str):
        """Log info message"""
        logger.info(f"[{self.full_name}][{task_id}] {message}")

    def log_error(self, task_id: str, message: str):
        """Log error message"""
        logger.error(f"[{self.full_name}][{task_id}] {message}")

