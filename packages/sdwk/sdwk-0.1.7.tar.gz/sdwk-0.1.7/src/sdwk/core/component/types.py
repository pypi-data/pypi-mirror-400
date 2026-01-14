"""输入输出类型定义."""

from enum import Enum


class InputType(str, Enum):
    """输入类型枚举.

    这些类型会映射到 sdw 平台的对应输入组件
    """

    # 文本/字符串输入
    MESSAGE_TEXT = "MessageTextInput"  # 消息文本输入
    MULTILINE = "MultilineInput"  # 多行文本输入
    MULTILINE_SECRET = "MultilineSecretInput"  # 多行密文输入
    SECRET = "SecretStrInput"  # 密文输入
    STR = "StrInput"  # 字符串输入
    PROMPT = "PromptInput"  # 提示词输入
    QUERY = "QueryInput"  # 查询输入
    CODE = "CodeInput"  # 代码输入

    # 布尔输入
    BOOL = "BoolInput"  # 布尔值输入

    # 数值输入
    INT = "IntInput"  # 整数输入
    FLOAT = "FloatInput"  # 浮点数输入
    SLIDER = "SliderInput"  # 滑动条输入

    # 选择输入
    DROPDOWN = "DropdownInput"  # 下拉选择
    MULTISELECT = "MultiselectInput"  # 多选输入

    # 文件/链接输入
    FILE = "FileInput"  # 文件上传
    LINK = "LinkInput"  # 链接输入

    # 数据/结构输入
    DICT = "DictInput"  # 字典输入
    NESTED_DICT = "NestedDictInput"  # 嵌套字典输入
    SORTABLE_LIST = "SortableListInput"  # 可排序列表输入
    TABLE = "TableInput"  # 表格输入
    DATA = "DataInput"  # 数据输入
    DATAFRAME = "DataFrameInput"  # DataFrame输入

    # 系统/连接输入
    AUTH = "AuthInput"  # 认证输入
    CONNECTION = "ConnectionInput"  # 连接输入
    HANDLE = "HandleInput"  # 句柄输入
    MCP = "McpInput"  # MCP输入
    TOOLS = "ToolsInput"  # 工具输入
    MESSAGE = "MessageInput"  # 消息输入

    # UI/其他
    TAB = "TabInput"  # 标签页输入


class OutputType(str, Enum):
    """输出类型枚举.

    定义组件的输出数据类型
    """

    # 基础类型
    TEXT = "Text"  # 文本输出
    DATA = "Data"  # 通用数据输出
    JSON = "JSON"  # JSON 格式输出

    # 结构化类型
    DICT = "Dict"  # 字典输出
    LIST = "List"  # 列表输出

    # 特殊类型
    MESSAGE = "Message"  # 消息输出
    DOCUMENT = "Document"  # 文档输出
    ANY = "Any"  # 任意类型


# LFX 映射表（用于导出到 langflow 平台）
LFX_INPUT_MAPPING = {
    InputType.MESSAGE_TEXT: "MessageTextInput",
    InputType.MULTILINE: "MultilineInput",
    InputType.MULTILINE_SECRET: "MultilineSecretInput",
    InputType.SECRET: "SecretStrInput",
    InputType.STR: "StrInput",
    InputType.PROMPT: "PromptInput",
    InputType.QUERY: "QueryInput",
    InputType.CODE: "CodeInput",
    InputType.BOOL: "BoolInput",
    InputType.INT: "IntInput",
    InputType.FLOAT: "FloatInput",
    InputType.SLIDER: "SliderInput",
    InputType.DROPDOWN: "DropdownInput",
    InputType.MULTISELECT: "MultiselectInput",
    InputType.FILE: "FileInput",
    InputType.LINK: "LinkInput",
    InputType.DICT: "DictInput",
    InputType.NESTED_DICT: "NestedDictInput",
    InputType.SORTABLE_LIST: "SortableListInput",
    InputType.TABLE: "TableInput",
    InputType.DATA: "DataInput",
    InputType.DATAFRAME: "DataFrameInput",
    InputType.AUTH: "AuthInput",
    InputType.CONNECTION: "ConnectionInput",
    InputType.HANDLE: "HandleInput",
    InputType.MCP: "McpInput",
    InputType.TOOLS: "ToolsInput",
    InputType.MESSAGE: "MessageInput",
    InputType.TAB: "TabInput",
}

LFX_OUTPUT_MAPPING = {
    OutputType.TEXT: "Text",
    OutputType.DATA: "Data",
    OutputType.JSON: "JSON",
    OutputType.DICT: "Dict",
    OutputType.LIST: "List",
    OutputType.MESSAGE: "Message",
    OutputType.DOCUMENT: "Document",
    OutputType.ANY: "Any",
}
