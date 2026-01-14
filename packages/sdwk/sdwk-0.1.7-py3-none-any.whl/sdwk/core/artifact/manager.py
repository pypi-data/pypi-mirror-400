"""Artifact 管理器.

负责成果物的保存、转换和清单生成。
"""

import json
from pathlib import Path
from typing import Any
import pyarrow as pa
import pyarrow.parquet as pq

from loguru import logger

from .models import ArtifactInfo, ArtifactManifest, ArtifactType
from .storage import ArtifactStorage, FileSystemStorage
from pandas import DataFrame


class ArtifactManager:
    """成果物管理器.

    提供统一的接口来处理各种类型的成果物。
    """

    def __init__(
        self,
        storage: ArtifactStorage | None = None,
        workflow_id: str | None = None,
        node_id: str | None = None,
    ):
        """初始化管理器.

        Args:
            storage: 存储后端,默认使用文件系统存储
            workflow_id: 工作流 ID
            node_id: 节点 ID
        """
        self.storage = storage or FileSystemStorage("./artifacts")
        self.workflow_id = workflow_id
        self.node_id = node_id
        self.manifest = ArtifactManifest(workflow_id=workflow_id, node_id=node_id)

    def save_dataframe(
        self,
        df: Any,
        name: str,
        format: str = "parquet",
        **kwargs,
    ) -> ArtifactInfo:
        """保存 DataFrame 为 Parquet 或其他格式.

        Args:
            df: DataFrame 对象 (pandas/polars)
            name: 成果物名称
            format: 保存格式 (parquet, csv, arrow)
            **kwargs: 额外参数传递给保存方法

        Returns:
            成果物信息
        """
        import io

        # 检测 DataFrame 类型
        df_type = type(df).__name__
        logger.debug(f"Saving DataFrame of type {df_type} as {format}")

        # 生成文件名
        filename = f"{name}.{format}"

        # 转换为字节流
        buffer = io.BytesIO()

        if format == "parquet":
            self._save_as_parquet(df, buffer, **kwargs)
        elif format == "csv":
            self._save_as_csv(df, buffer, **kwargs)
        elif format == "arrow":
            self._save_as_arrow(df, buffer, **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format}")

        data = buffer.getvalue()
        uri = self.storage.save(data, filename)
        hash_value = self.storage.calculate_hash(data)

        # 获取行列数
        rows, cols = self._get_dataframe_shape(df)

        artifact = ArtifactInfo(
            name=name,
            type=ArtifactType.DATAFRAME,
            format=format,
            uri=uri,
            size=len(data),
            hash=hash_value,
            rows=rows,
            cols=cols,
        )

        self.manifest.add_output(artifact)
        logger.info(f"Saved DataFrame '{name}' ({rows} rows, {cols} cols) to {uri}")
        return artifact

    def save_file(
        self,
        file_path: str | Path,
        name: str | None = None,
        artifact_type: ArtifactType = ArtifactType.FILE,
    ) -> ArtifactInfo:
        """保存文件.

        Args:
            file_path: 文件路径
            name: 成果物名称,默认使用文件名
            artifact_type: 成果物类型

        Returns:
            成果物信息
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        name = name or file_path.stem
        format = file_path.suffix.lstrip(".")

        with open(file_path, "rb") as f:
            data = f.read()

        uri = self.storage.save(data, file_path.name)
        hash_value = self.storage.calculate_hash(data)

        artifact = ArtifactInfo(
            name=name,
            type=artifact_type,
            format=format,
            uri=uri,
            size=len(data),
            hash=hash_value,
        )

        self.manifest.add_output(artifact)
        logger.info(f"Saved file '{name}' ({len(data)} bytes) to {uri}")
        return artifact

    def save_json(
        self,
        data: Any,
        name: str,
    ) -> ArtifactInfo:
        """保存 JSON 数据.

        Args:
            data: 要保存的数据
            name: 成果物名称

        Returns:
            成果物信息
        """
        filename = f"{name}.json"
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        json_bytes = json_str.encode("utf-8")

        uri = self.storage.save(json_bytes, filename)
        hash_value = self.storage.calculate_hash(json_bytes)

        artifact = ArtifactInfo(
            name=name,
            type=ArtifactType.JSON,
            format="json",
            uri=uri,
            size=len(json_bytes),
            hash=hash_value,
        )

        self.manifest.add_output(artifact)
        logger.info(f"Saved JSON '{name}' ({len(json_bytes)} bytes) to {uri}")
        return artifact

    def export_manifest(self, output_path: str | Path | None = None) -> dict[str, Any]:
        """导出清单为 JSON.

        Args:
            output_path: 输出路径,如果为 None 则只返回字典

        Returns:
            清单字典
        """
        manifest_dict = self.manifest.to_dict()

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(manifest_dict, f, ensure_ascii=False, indent=2)
            logger.info(f"Exported manifest to {output_path}")

        return manifest_dict

    def _save_as_parquet(self, df: Any, buffer: Any, **kwargs):
        """保存为 Parquet 格式."""
        try:
            # 尝试 pandas
            if hasattr(df, "to_parquet"):
                df.to_parquet(buffer, **kwargs)
                return
        except Exception as e:
            logger.warning(f"Failed to save as parquet using pandas: {e}")

        try:
            # 尝试 polars
            if hasattr(df, "write_parquet"):
                df.write_parquet(buffer, **kwargs)
                return
        except Exception as e:
            logger.warning(f"Failed to save as parquet using polars: {e}")

        raise ValueError("DataFrame must be pandas or polars DataFrame")

    def _save_as_csv(self, df: DataFrame, buffer: Any, **kwargs):
        """保存为 CSV 格式."""
        if hasattr(df, "to_csv"):
            df.to_csv(buffer, index=False, **kwargs)
        elif hasattr(df, "write_csv"):
            df.write_csv(buffer, **kwargs)
        else:
            raise ValueError("DataFrame must have to_csv or write_csv method")

    def _save_as_arrow(self, df: Any, buffer: Any, **kwargs):
        """保存为 Arrow 格式."""
        try:
            # 转换为 Arrow Table
            if hasattr(df, "to_arrow"):
                table = df.to_arrow()
            else:
                table = pa.Table.from_pandas(df)

            pq.write_table(table, buffer, **kwargs)
        except ImportError:
            raise ImportError("pyarrow is required for arrow format")

    def _get_dataframe_shape(self, df: Any) -> tuple[int, int]:
        """获取 DataFrame 的行列数."""
        if hasattr(df, "shape"):
            return df.shape
        elif hasattr(df, "height") and hasattr(df, "width"):
            return df.height, df.width
        else:
            return 0, 0