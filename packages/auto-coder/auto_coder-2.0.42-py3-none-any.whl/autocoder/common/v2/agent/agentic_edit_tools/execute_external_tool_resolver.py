"""
Execute External Tool Resolver

执行外部工具（从 .autocodertools 加载的工具），自动补充敏感信息。
支持从工具所在目录读取 `工具名.key` 文件，自动添加账号、密码、API key 等参数。
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from loguru import logger
import yaml
import typing

from autocoder.common.v2.agent.agentic_edit_tools.base_tool_resolver import (
    BaseToolResolver,
)
from autocoder.common.v2.agent.agentic_edit_types import (
    ExecuteExternalToolTool,
    ToolResult,
)
from autocoder.common.tools_manager import ToolsManager
from autocoder.common.tools_manager.models import ToolCommand
from autocoder.common import AutoCoderArgs
from autocoder.common.shell_commands import (
    execute_command,
    execute_command_background,
    CommandTimeoutError,
    CommandExecutionError,
)
from autocoder.events.event_manager_singleton import get_event_manager
from autocoder.run_context import get_run_context

if typing.TYPE_CHECKING:
    from autocoder.common.v2.agent.agentic_edit import AgenticEdit


class KeyFileConfig:
    """表示 .key 文件的配置结构，支持多层级子命令"""

    def __init__(self, config_dict: Dict[str, Any]):
        self.raw_config = config_dict
        self.global_params: Dict[str, str] = config_dict.get("global", {})
        self.subcommands: Dict[str, Any] = config_dict.get("subcommands", {})
        # 参数风格: "space" (--key value) 或 "equals" (--key=value)
        self.param_style: str = config_dict.get("param_style", "space")
        # 参数前缀: "--" 或 "-" 或其他
        self.param_prefix: str = config_dict.get("param_prefix", "--")

    def get_params_for_subcommands(
        self, subcommands: Optional[str] = None
    ) -> Dict[str, str]:
        """
        获取指定子命令路径的参数，支持多层级
        沿路径收集所有层级的 _params 参数

        Args:
            subcommands: 逗号分隔的子命令字符串，如 "config,set,proxy"

        Returns:
            合并后的参数字典（global + 沿路径的所有 _params）
        """
        params = dict(self.global_params)  # 复制全局参数

        if subcommands:
            subcmd_list = [s.strip() for s in subcommands.split(",") if s.strip()]
            current = self.subcommands
            for sub in subcmd_list:
                if isinstance(current, dict) and sub in current:
                    node = current[sub]
                    if isinstance(node, dict) and "_params" in node:
                        # 收集当前层级的参数
                        params.update(node["_params"])
                    current = node
                else:
                    break

        return params

    def format_params_as_args(self, params: Dict[str, str]) -> str:
        """
        将参数字典格式化为命令行参数字符串

        Args:
            params: 参数字典 {key: value}

        Returns:
            格式化后的命令行参数字符串
        """
        if not params:
            return ""

        args_list: List[str] = []
        for key, value in params.items():
            # 跳过空值参数（空字符串、None）
            if value is None or (isinstance(value, str) and value.strip() == ""):
                continue

            if self.param_style == "equals":
                # --key=value 风格
                args_list.append(f"{self.param_prefix}{key}={value}")
            else:
                # --key value 风格（默认）
                args_list.append(f"{self.param_prefix}{key}")
                args_list.append(str(value))

        return " ".join(args_list)


class ExecuteExternalToolResolver(BaseToolResolver):
    """执行外部工具的解析器"""

    def __init__(
        self,
        agent: Optional["AgenticEdit"],
        tool: ExecuteExternalToolTool,
        args: AutoCoderArgs,
    ):
        super().__init__(agent, tool, args)
        self.tool: ExecuteExternalToolTool = tool  # 类型提示
        self.tools_manager = ToolsManager()

    def _find_tool(self) -> Optional[ToolCommand]:
        """
        根据工具名称查找工具

        Returns:
            ToolCommand 对象，如果找不到返回 None
        """
        return self.tools_manager.get_tool_by_name(self.tool.tool_name)

    def _load_key_file(self, tool: ToolCommand) -> Optional[KeyFileConfig]:
        """
        加载工具的 .key 文件

        Args:
            tool: 工具命令对象

        Returns:
            KeyFileConfig 对象，如果文件不存在或解析失败返回 None
        """
        tool_path = Path(tool.path)
        tool_dir = tool_path.parent
        tool_basename = tool_path.stem  # 不含扩展名的文件名

        # 构建 .key 文件路径
        key_file_path = tool_dir / f"{tool_basename}.key"

        if not key_file_path.exists():
            logger.debug(f"No .key file found for tool {tool.name} at {key_file_path}")
            return None

        try:
            with open(key_file_path, "r", encoding="utf-8") as f:
                config_dict = yaml.safe_load(f)

            if config_dict is None:
                logger.warning(f"Empty .key file: {key_file_path}")
                return None

            return KeyFileConfig(config_dict)

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse .key file {key_file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading .key file {key_file_path}: {e}")
            return None

    def _is_help_command(self) -> bool:
        """
        检测命令是否为帮助命令

        如果子命令或参数中包含帮助相关的标志，则返回 True。
        帮助命令不应该补充 .key 文件中的敏感参数。

        Returns:
            bool: 是否为帮助命令
        """
        help_flags = {"--help", "-h", "help", "--skill"}

        # 检查子命令
        if self.tool.subcommands:
            subcmd_list = [
                s.strip().lower() for s in self.tool.subcommands.split(",") if s.strip()
            ]
            for subcmd in subcmd_list:
                if subcmd in help_flags:
                    return True

        # 检查额外参数
        if self.tool.args:
            args_lower = self.tool.args.lower()
            for flag in help_flags:
                # 检查参数是否包含帮助标志（作为独立参数）
                if flag in args_lower.split():
                    return True

        return False

    def _build_command(
        self, tool: ToolCommand, key_config: Optional[KeyFileConfig]
    ) -> str:
        """
        构建完整的命令行

        Args:
            tool: 工具命令对象
            key_config: 敏感信息配置（可选）

        Returns:
            完整的命令行字符串
        """
        parts: List[str] = []

        # 工具路径
        parts.append(tool.path)

        # 多层级子命令：将逗号分隔转为空格分隔
        if self.tool.subcommands:
            subcmd_list = [
                s.strip() for s in self.tool.subcommands.split(",") if s.strip()
            ]
            parts.extend(subcmd_list)

        # 从 .key 文件添加参数（帮助命令不添加敏感参数）
        if key_config and not self._is_help_command():
            params = key_config.get_params_for_subcommands(self.tool.subcommands)
            key_args = key_config.format_params_as_args(params)
            if key_args:
                parts.append(key_args)

        # 用户额外参数
        if self.tool.args:
            parts.append(self.tool.args)

        return " ".join(parts)

    def _mask_sensitive_command(
        self, command: str, key_config: Optional[KeyFileConfig]
    ) -> str:
        """
        遮蔽命令中的敏感信息用于显示

        只遮蔽以参数格式出现的敏感值（如 --key value 或 --key=value），
        避免错误地替换命令路径等其他部分。

        Args:
            command: 完整命令行
            key_config: 敏感信息配置

        Returns:
            敏感信息被遮蔽的命令行
        """
        if not key_config:
            return command

        import re

        masked_command = command
        # 获取所有敏感值
        all_params = key_config.get_params_for_subcommands(self.tool.subcommands)
        prefix = key_config.param_prefix  # 如 "--" 或 "-"

        for key, value in all_params.items():
            if value is not None:
                value_str = str(value)

                # 跳过太短的值（可能会错误匹配命令的其他部分）
                if len(value_str) < 4:
                    continue

                # 生成遮蔽后的值
                if len(value_str) > 6:
                    masked_value = value_str[:2] + "****" + value_str[-2:]
                else:
                    masked_value = "****"

                # 方式1: 精确匹配 --key value 格式（空格分隔）
                # 使用 \s+ 匹配空格，然后精确匹配值
                pattern_space = (
                    re.escape(f"{prefix}{key}")
                    + r"\s+"
                    + re.escape(value_str)
                    + r"(?=\s|$)"
                )
                replacement_space = f"{prefix}{key} {masked_value}"
                masked_command = re.sub(
                    pattern_space, replacement_space, masked_command
                )

                # 方式2: 精确匹配 --key=value 格式（等号连接）
                pattern_equals = (
                    re.escape(f"{prefix}{key}=") + re.escape(value_str) + r"(?=\s|$)"
                )
                replacement_equals = f"{prefix}{key}={masked_value}"
                masked_command = re.sub(
                    pattern_equals, replacement_equals, masked_command
                )

        return masked_command

    def resolve(self) -> ToolResult:
        """
        执行外部工具

        Returns:
            ToolResult: 工具执行结果
        """
        tool_name = self.tool.tool_name
        source_dir = self.args.source_dir or "."

        # 1. 查找工具
        tool = self._find_tool()
        if not tool:
            available_tools = self.tools_manager.list_tool_names()
            return ToolResult(
                success=False,
                message=f"Tool '{tool_name}' not found in .autocodertools directories.\n"
                f"Available tools: {', '.join(available_tools) if available_tools else 'None'}",
                content={
                    "error_type": "tool_not_found",
                    "tool_name": tool_name,
                    "available_tools": available_tools,
                },
            )

        # 2. 加载 .key 文件
        key_config = self._load_key_file(tool)

        # 3. 构建命令
        command = self._build_command(tool, key_config)
        masked_command = self._mask_sensitive_command(command, key_config)

        logger.info(f"Executing external tool: {masked_command}")

        # 4. 用户确认（如果需要）
        if not self.args.enable_agentic_auto_approve and self.tool.requires_approval:
            try:
                if get_run_context().is_web():
                    answer = get_event_manager(self.args.event_file).ask_user(
                        prompt=f"Allow to execute external tool?\n\nCommand: {masked_command}",
                        options=["yes", "no"],
                    )
                    if answer != "yes":
                        return ToolResult(
                            success=False,
                            message=f"External tool execution denied by user.",
                        )
            except Exception as e:
                logger.error(
                    f"Error when asking user to approve external tool: {str(e)}"
                )
                return ToolResult(
                    success=False,
                    message=f"An unexpected error occurred while asking for approval: {str(e)}",
                )

        # 5. 执行命令
        try:
            if self.tool.background:
                # 后台执行
                process_info = execute_command_background(
                    command=command,
                    cwd=source_dir,
                    verbose=False,
                )

                pid = process_info["pid"]
                process_uniq_id = process_info.get("process_uniq_id", "")

                logger.info(
                    f"Started external tool in background: {masked_command} with PID: {pid}"
                )

                return ToolResult(
                    success=True,
                    message=f"External tool started in background with PID: {pid}, ID: {process_uniq_id}",
                    content={
                        "pid": pid,
                        "process_uniq_id": process_uniq_id,
                        "command": masked_command,
                        "tool_name": tool_name,
                        "background": True,
                        "status": "running",
                    },
                )
            else:
                # 前台执行
                timeout = self.tool.timeout
                exit_code, output = execute_command(
                    command, timeout=timeout, verbose=True, cwd=source_dir
                )

                logger.info(f"External tool executed: {masked_command}")
                logger.info(f"Return Code: {exit_code}")

                if exit_code == 0:
                    return ToolResult(
                        success=True,
                        message=f"External tool '{tool_name}' executed successfully.",
                        content={
                            "output": output,
                            "exit_code": exit_code,
                            "tool_name": tool_name,
                            "command": masked_command,
                        },
                    )
                else:
                    # 构建包含详细错误信息的消息
                    error_message = f"External tool '{tool_name}' failed with exit code {exit_code}."
                    if output:
                        # 限制输出长度，避免消息过长
                        output_preview = output.strip()
                        if len(output_preview) > 2000:
                            output_preview = (
                                output_preview[:2000] + "\n... (output truncated)"
                            )
                        error_message += f"\n\nError Output:\n{output_preview}"

                    return ToolResult(
                        success=False,
                        message=error_message,
                        content={
                            "output": output,
                            "exit_code": exit_code,
                            "tool_name": tool_name,
                            "command": masked_command,
                        },
                    )

        except CommandTimeoutError as e:
            logger.error(f"External tool timed out: {e}")
            return ToolResult(
                success=False,
                message=f"External tool '{tool_name}' timed out after {self.tool.timeout} seconds.",
                content={
                    "error_type": "timeout",
                    "timeout_seconds": self.tool.timeout,
                    "tool_name": tool_name,
                    "command": masked_command,
                },
            )
        except CommandExecutionError as e:
            logger.error(f"External tool execution failed: {e}")
            return ToolResult(
                success=False,
                message=f"External tool execution failed: {str(e)}",
                content={
                    "error_type": "execution_error",
                    "error": str(e),
                    "tool_name": tool_name,
                    "command": masked_command,
                },
            )
        except FileNotFoundError:
            return ToolResult(
                success=False,
                message=f"Error: External tool '{tool_name}' at '{tool.path}' was not found or not executable.",
                content={
                    "error_type": "file_not_found",
                    "tool_name": tool_name,
                    "tool_path": tool.path,
                    "command": masked_command,
                },
            )
        except PermissionError:
            return ToolResult(
                success=False,
                message=f"Error: Permission denied when trying to execute '{tool.path}'.",
                content={
                    "error_type": "permission_denied",
                    "tool_name": tool_name,
                    "tool_path": tool.path,
                    "command": masked_command,
                },
            )
        except Exception as e:
            logger.error(f"Error executing external tool '{tool_name}': {str(e)}")
            return ToolResult(
                success=False,
                message=f"An unexpected error occurred while executing external tool: {str(e)}",
                content={
                    "error_type": "unknown_error",
                    "error": str(e),
                    "tool_name": tool_name,
                    "command": masked_command,
                },
            )
