"""组件执行入口

这个文件是组件的执行入口，用户可以在这里定义自己的组件。

可以通过以下方式运行：
1. 本地测试: uv run -m {包名}.run
2. 平台调用: uv run -m {包名}.run --mode=platform --input-json='{"input_value": "xxx"}'

日志配置：
- 日志配置在 src/sdwk/config/default.yaml 中管理
- 通过环境变量 USER_ID 和 WORKFLOW_ID 指定工作流上下文
- 通过环境变量 SDWK_ENV 切换环境（development/production）
"""

import json
import sys

import click

from sdwk import Component, Data, Input, InputType, Output, OutputType

class {{ project_name_pascal }}(Component):
    """示例组件

    这是一个示例组件，展示如何定义输入、输出和执行逻辑。
    """

    # 组件元信息
    name = "{{ project_name }}"
    display_name = "{{ project_name }}"
    description = "Use as a template to create your own component."
    documentation = "https://docs.sdwplatform.org/components-custom-components"
    icon = "code"

    # 定义输入
    inputs = [
        Input(
            name="input_value",
            display_name="Input Value",
            description="This is a custom component Input",
            type=InputType.MESSAGE_TEXT,
            value="Hello, World!",
            tool_mode=True,
        ),
    ]

    # 定义输出
    outputs = [
        Output(
            name="output",
            display_name="Output",
            description="Component output data",
            type=OutputType.DATA,
        ),
    ]

    def run(self) -> Data:
        """执行组件核心逻辑

        这是组件的业务逻辑，你可以在这里实现自己的处理流程。

        Returns:
            Data: 输出数据
        """
        # ========== 1. 获取输入值 ==========
        input_value = self.input_value

        # 记录日志示例
        self.log("INFO", f"开始处理输入: {input_value}")

        # ========== 2. 获取其他节点的上下文数据（可选） ==========
        # 如果当前节点需要其他节点的输出，可以使用以下方法获取：

        # 示例：获取指定节点的特定字段
        # row_count = self.get_context("data_loader", "row_count")
        # summary = self.get_context("processor", "summary", default={})

        # 示例：列出所有可用的节点
        # available_nodes = self.list_context_nodes()
        # self.log("INFO", f"可用的节点: {available_nodes}")

        # ========== 3. 执行业务逻辑 ==========
        result = f"Processed: {input_value}"

        self.log("INFO", f"处理完成，结果: {result}")

        # ========== 4. 保存上下文字段供下游节点使用（可选） ==========
        # 如果需要将中间结果传递给下游节点，可以使用 save_to_context()
        # 注意：只保存必要的字段，大数据应使用 Artifact 机制

        # 示例：保存处理结果的统计信息
        # self.save_to_context("processed_count", 100, "处理的记录数")
        # self.save_to_context("result_summary", {"status": "success"}, "处理结果摘要")

        # ========== 5. 创建输出数据 ==========
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
def main(mode: str, user_id: str | None, node_id: str | None, flow_id: str | None, job_id: str | None, **kwargs):
    """主函数

    支持两种运行模式：
    1. test 模式：本地测试，执行完整的测试流程
    2. platform 模式：平台调用，只执行组件并输出 JSON 结果

    日志配置通过项目配置文件管理（src/sdwk/config/default.yaml）
    工作流上下文通过命令行参数传递
    用户参数通过额外的命令行参数传递（如 --param1=value1）
    """
    # 创建组件实例（配置会自动从项目配置系统加载）
    # 将平台传递的上下文参数传递给组件（使用 _ 前缀标记为内部参数）
    component = {{ project_name_pascal }}(
        _user_id=user_id or "",
        _node_id=node_id or "",
        _flow_id=flow_id or "",
        _job_id=job_id or "",
    )

    if mode == "platform":
        # 平台调用模式：执行组件并输出结果
        try:
            # 执行组件（用户参数通过 kwargs 传递）
            result = component.execute(**kwargs)

            # 检查是否有 artifact 输出
            # 如果组件使用了 artifact 机制，会自动调用 output_artifact_result()
            # 否则输出统一的 4 字段格式
            manager = component.get_artifact_manager()
            if len(manager.manifest.outputs) > 0:
                # 有 artifacts，输出 4 字段格式（type 为 artifact 类型，value 为 result.json URI）
                component.output_artifact_result("./result.json")
            else:
                # 无 artifacts，输出统一的 4 字段格式（type 为 string，value 为实际输出值）
                output = {
                    "flow_id": flow_id or "",
                    "node_id": node_id or "",
                    "type": "string",
                    "value": result.value
                }
                print(json.dumps(output, ensure_ascii=False))

        except Exception as e:
            # 输出错误信息（统一的 4 字段格式，type 为 error，value 为完整堆栈）
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
        # 本地测试模式：执行完整的测试流程
        print("=" * 60)
        print("Running MyComponent...")
        print("=" * 60)

        # 打印组件信息
        print("\nComponent Information:")
        print(json.dumps(component.to_dict(), indent=2, ensure_ascii=False))

        # 执行组件
        print("\n" + "=" * 60)
        print("Executing component...")
        print("=" * 60)

        result = component.execute()

        # 打印执行结果
        print("\nExecution Result:")
        print(f"Value: {result.value}")
        print(f"Metadata: {json.dumps(result.metadata, indent=2, ensure_ascii=False)}")

        # 测试不同的输入值
        print("\n" + "=" * 60)
        print("Testing with custom input...")
        print("=" * 60)

        result2 = component.execute(input_value="Custom Input Value")

        print("\nExecution Result:")
        print(f"Value: {result2.value}")
        print(f"Metadata: {json.dumps(result2.metadata, indent=2, ensure_ascii=False)}")

        # 导出为 LFX 格式
        print("\n" + "=" * 60)
        print("LFX Format Export:")
        print("=" * 60)
        print(json.dumps(component.to_lfx_format(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
