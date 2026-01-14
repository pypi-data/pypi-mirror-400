"""Artifact 数据模型定义."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """成果物类型."""

    DATAFRAME = "dataframe"
    FILE = "file"
    TEXT = "text"
    JSON = "json"
    IMAGE = "image"
    BINARY = "binary"


class ArtifactInfo(BaseModel):
    """成果物信息.

    描述单个成果物的元数据。
    """

    name: str = Field(..., description="成果物名称")
    type: ArtifactType = Field(..., description="成果物类型")
    format: str = Field(..., description="文件格式 (parquet, csv, json, png 等)")
    uri: str = Field(..., description="存储位置 URI (file://, s3://, http:// 等)")
    size: int = Field(..., description="文件大小(字节)")
    hash: str = Field(..., description="文件哈希值 (sha256:...)")
    rows: int | None = Field(default=None, description="数据行数(仅 DataFrame)")
    cols: int | None = Field(default=None, description="数据列数(仅 DataFrame)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="额外元数据")

    class Config:
        use_enum_values = True


class ArtifactManifest(BaseModel):
    """成果物清单.

    包含所有输出成果物的元数据列表。
    """

    workflow_id: str | None = Field(default=None, description="工作流 ID")
    node_id: str | None = Field(default=None, description="节点 ID")
    outputs: list[ArtifactInfo] = Field(default_factory=list, description="输出成果物列表")
    metadata: dict[str, Any] = Field(default_factory=dict, description="额外元数据")

    def add_output(self, artifact: ArtifactInfo):
        """添加输出成果物."""
        self.outputs.append(artifact)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典."""
        return self.model_dump(exclude_none=True)

    def to_simple_result(self, result_json_uri: str) -> dict[str, Any]:
        """转换为简化的结果格式.

        只包含 4 个核心字段,用于 stdout 输出。

        Args:
            result_json_uri: result.json 文件的 URI

        Returns:
            简化的结果字典
        """
        # 判断输出类型
        if len(self.outputs) == 0:
            output_type = "string"
        elif len(self.outputs) == 1:
            output_type = self.outputs[0].type
        else:
            # 多个输出,类型为 json
            output_type = "json"

        return {
            "flow_id": self.workflow_id,
            "node_id": self.node_id,
            "type": output_type,
            "value": result_json_uri
        }
