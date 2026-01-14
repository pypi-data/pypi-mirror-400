"""组件执行入口

这个文件是组件的执行入口，用户可以在这里定义自己的组件。

可以通过以下方式运行：
1. 本地测试: uv run -m {{ project_name_snake }}.{{ node_name }}
2. 平台调用: uv run -m {{ project_name_snake }}.{{ node_name }} --mode=platform --input-json='{"input_value": "xxx"}'
"""

import json
import sys

import click

from sdwk import Component, Data, Input, InputType, Output, OutputType
# from .utils import example_helper  # 示例：导入公共工具（utils 目录下）

class {{ node_class_name }}(Component):
    """{{ node_display_name }}

    {{ node_description }}
    """

    # 组件元信息
    name = "{{ node_name }}"
    display_name = "{{ node_display_name }}"
    description = "{{ node_description }}"
    documentation = "https://docs.sdwplatform.org/components-custom-components"
    icon = "code"

    # 定义输入
    inputs = [
        Input(
            name="input_value",
            display_name="Input Value",
            description="Input for {{ node_display_name }}",
            type=InputType.MESSAGE_TEXT,
            value="Default Value",
            tool_mode=True,
        ),
    ]

    # 定义输出
    outputs = [
        Output(
            name="output",
            display_name="Output",
            description="Output from {{ node_display_name }}",
            type=OutputType.DATA,
        ),
    ]

    def run(self) -> Data:
        """执行组件核心逻辑"""
        # ========== 1. 获取输入值 ==========
        input_value = self.input_value

        self.log("INFO", f"[{self.name}] 开始处理输入: {input_value}")

        # ========== 2. 执行业务逻辑 ==========
        # result = example_helper() 
        result = f"{{ node_display_name }} processed: {input_value}"

        self.log("INFO", f"[{self.name}] 处理完成，结果: {result}")

        # ========== 3. 创建输出数据 ==========
        data = Data(
            value=result,
            metadata={
                "input": input_value,
                "component": self.name,
            },
        )

        # 设置状态
        self.status = data
        return data


@click.command()
@click.option("--mode", default="test", type=click.Choice(["test", "platform"]), help="运行模式：test=本地测试, platform=平台调用")
@click.option("--user_id", default=None, help="用户ID（平台模式）")
@click.option("--node_id", default=None, help="节点ID（平台模式）")
@click.option("--flow_id", default=None, help="工作流ID（平台模式）")
@click.option("--job_id", default=None, help="任务ID（平台模式）")
@click.option("--input-file-path", default=None, help="输入文件路径（平台模式）")
def main(mode: str, user_id: str | None, node_id: str | None, flow_id: str | None, job_id: str | None, input_file_path: str | None, **kwargs):
    """主函数"""
    if input_file_path and mode == "platform":
         # 从文件读取参数
        try:
             with open(input_file_path, 'r', encoding='utf-8') as f:
                file_kwargs = json.load(f)
                kwargs.update(file_kwargs)
        except Exception as e:
            print(json.dumps({
                "type": "error",
                "value": f"Failed to load input file: {e}"
            }, ensure_ascii=False))
            sys.exit(1)

    component = {{ node_class_name }}(
        _user_id=user_id or "",
        _node_id=node_id or "",
        _flow_id=flow_id or "",
        _job_id=job_id or "",
    )

    if mode == "platform":
        try:
            result = component.execute(**kwargs)
            # 输出统一的 4 字段格式
            output = {
                "flow_id": flow_id or "",
                "node_id": node_id or "",
                "type": "string",
                "value": result.value
            }
            print(json.dumps(output, ensure_ascii=False))

        except Exception as e:
            import traceback
            error_output = {
                "flow_id": flow_id or "",
                "node_id": node_id or "",
                "type": "error",
                "value": traceback.format_exc()
            }
            print(json.dumps(error_output, ensure_ascii=False))
            sys.exit(1)

    else:
        # 本地测试模式
        print(f"Running component: {component.display_name}")
        result = component.execute()
        print(f"Result: {result.value}")


if __name__ == "__main__":
    main()
