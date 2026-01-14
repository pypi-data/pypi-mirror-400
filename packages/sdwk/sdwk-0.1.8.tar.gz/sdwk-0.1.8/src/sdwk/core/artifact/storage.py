"""Artifact 存储层.

提供不同存储后端的抽象接口。
"""

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from loguru import logger


class ArtifactStorage(ABC):
    """成果物存储抽象基类."""

    @abstractmethod
    def save(self, data: bytes, filename: str) -> str:
        """保存数据并返回 URI.

        Args:
            data: 要保存的数据
            filename: 文件名

        Returns:
            存储位置的 URI
        """
        pass

    @abstractmethod
    def get_uri(self, filename: str) -> str:
        """获取文件的 URI.

        Args:
            filename: 文件名

        Returns:
            文件的 URI
        """
        pass

    def calculate_hash(self, data: bytes) -> str:
        """计算数据的 SHA256 哈希值.

        Args:
            data: 数据

        Returns:
            哈希值字符串 (格式: sha256:...)
        """
        hash_obj = hashlib.sha256(data)
        return f"sha256:{hash_obj.hexdigest()}"


class FileSystemStorage(ArtifactStorage):
    """文件系统存储实现."""

    def __init__(self, base_path: str | Path):
        """初始化文件系统存储.

        Args:
            base_path: 基础存储路径
        """
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Initialized FileSystemStorage at {self.base_path}")

    def save(self, data: bytes, filename: str) -> str:
        """保存数据到文件系统."""
        file_path = self.base_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(data)

        logger.debug(f"Saved artifact to {file_path}")
        return self.get_uri(filename)

    def get_uri(self, filename: str) -> str:
        """获取文件 URI."""
        file_path = self.base_path / filename
        return file_path.as_uri()
