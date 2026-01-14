"""Template management for SDW projects."""

import os
from pathlib import Path
import shutil
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template
from rich.console import Console

from .project_config import ProjectConfig

console = Console()


class TemplateManager:
    """模板管理器."""

    def __init__(self):
        self.sdk_root = Path(__file__).parent.parent
        self.templates_dir = self.sdk_root / "templates"

    def get_available_templates(self) -> list[str]:
        """获取可用的模板列表."""
        if not self.templates_dir.exists():
            return []

        templates = []
        for item in self.templates_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                templates.append(item.name)
        return templates

    def create_project(self, project_info: dict[str, Any], output_dir: str = ".") -> Path:
        """创建新项目."""
        project_name = project_info["name"]
        project_type = project_info["type"]

        # 创建项目配置
        config = ProjectConfig(
            name=project_name, 
            type=project_type, 
            description=project_info.get("description", ""), 
            platform_url=project_info.get("platform_url", "https://platform.sdw.com"),
            category=project_info.get("category"),
            nodes=project_info.get("nodes") if project_info.get("nodes") else None,
        )

        # 确定模板路径
        template_path = self.templates_dir / project_type
        if not template_path.exists():
            raise ValueError(f"模板不存在: {project_type}")

        # 创建项目目录
        output_path = Path(output_dir) / project_name
        if output_path.exists():
            raise ValueError(f"项目目录已存在: {output_path}")

        # 复制模板并渲染
        self._copy_and_render_template(template_path, output_path, config)

        if project_type == "group" and hasattr(config, "nodes") and config.nodes:
            self._generate_group_nodes(output_path, config, template_path)

        # 保存项目配置
        config_path = output_path / "sdw.json"
        config.to_file(config_path)

        return output_path

    def _generate_group_nodes(self, output_path: Path, config: ProjectConfig, template_path: Path):
        """生成Group类型的节点文件."""
        template_context = config.get_template_context()
        project_name_snake = template_context["project_name_snake"]
        package_dir = output_path / "src" / project_name_snake
        
        # 读取节点模板内容
        # 此时我们假设在 group 模板根目录下有一个 _node_template.py 文件
        node_template_path = template_path / "_node_template.py"
        if not node_template_path.exists():
            console.print("[yellow]警告: 未找到节点模板文件 _node_template.py，跳过节点生成[/yellow]")
            return

        with open(node_template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
            
        env = Environment(loader=FileSystemLoader(str(template_path)))
        template = env.from_string(template_content)

        # 遍历节点并生成文件
        for node in config.nodes:  # nodes is now a list of dict thanks to pydantic or ProjectConfig changes
            # node 可能是 dict (从 create.py 传入) 或 NodeItem 对象 (如果 ProjectConfig 已经生效)
            # 但 create_project 里直接传的是 ProjectConfig 对象，config.nodes 是 list[dict] 因 ProjectConfig 定义如此
            
            node_name = node["name"] if isinstance(node, dict) else node.name
            entry_file = node["entry"] if isinstance(node, dict) else node.entry

            # 准备节点上下文
            node_context = template_context.copy()
            node_context.update({
                "node_name": node_name,
                "node_display_name": node.get("display_name", node_name),
                "node_description": node.get("description", ""),
                "node_class_name": "".join(x.title() for x in node_name.replace("-", "_").split("_")) + "Component"
            })
            
            rendered_code = template.render(**node_context)
            
            target_file = package_dir / entry_file
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(rendered_code)
                
        # 清理生成的 _node_template.py (它也被 copy_and_render 复制过去了)
        copied_template = output_path / "_node_template.py"
        if copied_template.exists():
            os.remove(copied_template)

    def _copy_and_render_template(self, template_path: Path, output_path: Path, config: ProjectConfig):
        """复制并渲染模板."""
        template_context = config.get_template_context()
        project_name_snake = template_context["project_name_snake"]

        # 创建Jinja2环境
        env = Environment(loader=FileSystemLoader(str(template_path)), keep_trailing_newline=True)

        # 遍历模板目录
        for root, _dirs, files in os.walk(template_path):
            root_path = Path(root)
            relative_path = root_path.relative_to(template_path)

            # 特殊处理：将 src/ 目录下的内容放到 src/{project_name_snake}/ 下
            if relative_path == Path("src"):
                # src/ 目录本身，创建 src/{project_name_snake}/
                current_output_dir = output_path / "src" / project_name_snake
                current_output_dir.mkdir(parents=True, exist_ok=True)
            elif relative_path.parts and relative_path.parts[0] == "src":
                # src/ 下的子目录，映射到 src/{project_name_snake}/子目录
                sub_path = Path(*relative_path.parts[1:]) if len(relative_path.parts) > 1 else Path(".")
                current_output_dir = output_path / "src" / project_name_snake / sub_path
                current_output_dir.mkdir(parents=True, exist_ok=True)
            else:
                # 其他目录正常创建
                current_output_dir = output_path / relative_path
                current_output_dir.mkdir(parents=True, exist_ok=True)

            # 处理文件
            for file_name in files:
                # 跳过 sdw.json（由系统动态生成）和 _node_template.py（仅用于生成节点）
                if file_name in ("sdw.json", "_node_template.py"):
                    continue

                src_file = root_path / file_name

                # 渲染文件名（支持模板变量）
                rendered_file_name = self._render_string(file_name, template_context)
                dst_file = current_output_dir / rendered_file_name

                # 判断是否需要模板渲染
                if self._should_render_file(src_file):
                    # 渲染文件内容
                    try:
                        # 确保路径使用正斜杠，Jinja2 在所有平台上都期望使用正斜杠
                        template_path_str = str(src_file.relative_to(template_path)).replace("\\", "/")
                        template = env.get_template(template_path_str)
                        rendered_content = template.render(**template_context)

                        with open(dst_file, "w", encoding="utf-8") as f:
                            f.write(rendered_content)
                    except Exception as e:
                        console.print(f"[red]错误: 渲染文件失败 {src_file}[/red]")
                        console.print(f"[red]详细错误: {type(e).__name__}: {e}[/red]")
                        console.print(f"[yellow]模板上下文变量: {list(template_context.keys())}[/yellow]")
                        # 如果渲染失败，直接复制文件
                        shutil.copy2(src_file, dst_file)
                else:
                    # 直接复制二进制文件
                    shutil.copy2(src_file, dst_file)

    def _should_render_file(self, file_path: Path) -> bool:
        """判断文件是否需要模板渲染."""
        # 文本文件扩展名
        text_extensions = {".py", ".txt", ".md", ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini", ".conf", ".sh", ".bat", ".ps1", ".dockerfile", ".gitignore", ".gitattributes", ".editorconfig"}

        # 检查扩展名
        if file_path.suffix.lower() in text_extensions:
            return True

        # 检查无扩展名的常见配置文件
        return file_path.name.lower() in {"dockerfile", "makefile", "readme", "license"}

    def _render_string(self, template_string: str, context: dict[str, Any]) -> str:
        """渲染字符串模板."""
        try:
            template = Template(template_string)
            return template.render(**context)
        except Exception:
            # 如果渲染失败，返回原字符串
            return template_string

    def validate_project(self, project_path: Path) -> bool:
        """验证项目结构."""
        config_file = project_path / "sdw.json"
        if not config_file.exists():
            return False

        try:
            ProjectConfig.from_file(config_file)
            return True
        except Exception:
            return False
