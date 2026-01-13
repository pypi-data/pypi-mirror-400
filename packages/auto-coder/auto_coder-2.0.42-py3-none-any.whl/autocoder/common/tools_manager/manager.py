"""
Tools Manager Core Implementation

工具管理器的核心实现，负责动态加载和管理 .autocodertools 目录中的工具命令。
"""

import os
import shutil
import platform
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger
import byzerllm

from .models import ToolCommand, ToolsLoadResult
from .utils import is_tool_command_file, extract_tool_help, get_project_name
from ..priority_directory_finder import (
    PriorityDirectoryFinder,
    FinderConfig,
    SearchStrategy,
    ValidationMode,
)


def check_command_exists(command: str) -> bool:
    """
    检查命令是否存在于系统 PATH 中

    Args:
        command: 命令名称

    Returns:
        bool: 命令是否存在
    """
    return shutil.which(command) is not None


def get_dev_tools_status() -> Dict[str, bool]:
    """
    检测开发工具的安装状态

    Returns:
        Dict[str, bool]: 工具名称到是否可用的映射
    """
    return {
        "go": check_command_exists("go"),
        "bun": check_command_exists("bun"),
        "uv": check_command_exists("uv"),
    }


class ToolsManager:
    """
    工具管理器

    负责从多个优先级目录中加载和管理工具命令文件。
    支持的目录优先级（从高到低）：
    1. 当前项目/.autocodertools
    2. .auto-coder/.autocodertools
    3. ~/.auto-coder/.autocodertools
    4. ~/.auto-coder/.autocodertools/repos/<项目名>
    """

    def __init__(self, tools_dirs: Optional[List[str]] = None):
        """
        初始化工具管理器

        Args:
            tools_dirs: 自定义工具目录列表，如果为None则使用默认查找策略
        """
        self.tools_dirs = tools_dirs or self._find_tools_directories()
        self._result_cache: Optional[ToolsLoadResult] = None

    def _find_tools_directories(self) -> List[str]:
        """
        查找所有有效的工具目录

        Returns:
            List[str]: 有效的工具目录路径列表
        """

        config = FinderConfig(strategy=SearchStrategy.MERGE_ALL)

        # 添加标准目录路径
        current_dir = Path.cwd()
        project_name = get_project_name()

        # 1. 当前项目/.autocodertools (最高优先级)
        config.add_directory(
            str(current_dir / ".autocodertools"),
            priority=1,
            validation_mode=ValidationMode.HAS_FILES,
        )

        # 2. .auto-coder/.autocodertools
        config.add_directory(
            str(current_dir / ".auto-coder" / ".autocodertools"),
            priority=2,
            validation_mode=ValidationMode.HAS_FILES,
        )

        # 3. ~/.auto-coder/.autocodertools
        home_dir = Path.home()
        config.add_directory(
            str(home_dir / ".auto-coder" / ".autocodertools"),
            priority=3,
            validation_mode=ValidationMode.HAS_FILES,
        )

        # 4. ~/.auto-coder/.autocodertools/repos/<项目名> (最低优先级)
        config.add_directory(
            str(home_dir / ".auto-coder" / ".autocodertools" / "repos" / project_name),
            priority=4,
            validation_mode=ValidationMode.HAS_FILES,
        )

        finder = PriorityDirectoryFinder(config)
        result = finder.find_directories()

        if result.success:
            logger.info(f"找到工具目录: {result.all_valid_directories}")
            return result.all_valid_directories
        else:
            logger.warning("未找到任何工具目录")
            return []

    def load_tools(self, force_reload: bool = False) -> ToolsLoadResult:
        """
        加载所有工具命令

        Args:
            force_reload: 是否强制重新加载

        Returns:
            ToolsLoadResult: 加载结果
        """
        if not force_reload and self._result_cache is not None:
            return self._result_cache

        all_tools = []
        failed_count = 0

        for tools_dir in self.tools_dirs:
            if not os.path.exists(tools_dir):
                continue

            logger.debug(f"扫描工具目录: {tools_dir}")

            try:
                for item in os.listdir(tools_dir):
                    item_path = os.path.join(tools_dir, item)

                    if os.path.isfile(item_path) and is_tool_command_file(item_path):
                        try:
                            tool = self._create_tool_command(item_path, tools_dir)
                            if tool:
                                all_tools.append(tool)
                                logger.debug(f"加载工具: {tool.name}")
                            else:
                                failed_count += 1
                        except Exception as e:
                            logger.warning(f"加载工具文件失败 {item_path}: {e}")
                            failed_count += 1

            except OSError as e:
                logger.warning(f"读取工具目录失败 {tools_dir}: {e}")
                continue

        # 去重：如果多个目录中有同名工具，优先使用高优先级目录中的
        unique_tools = self._deduplicate_tools(all_tools)

        result = ToolsLoadResult(
            success=True, tools=unique_tools, failed_count=failed_count
        )
        self._result_cache = result

        return result

    def _create_tool_command(
        self, file_path: str, source_dir: str
    ) -> Optional[ToolCommand]:
        """
        创建工具命令对象

        Args:
            file_path: 工具文件路径
            source_dir: 来源目录

        Returns:
            Optional[ToolCommand]: 工具命令对象
        """
        path = Path(file_path)

        # 提取帮助信息
        help_text = extract_tool_help(file_path)

        # 检查是否可执行
        is_executable = os.access(file_path, os.X_OK)

        return ToolCommand(
            name=path.name,
            path=file_path,
            help_text=help_text,
            is_executable=is_executable,
            file_extension=path.suffix,
            source_directory=source_dir,
        )

    def _deduplicate_tools(self, tools: List[ToolCommand]) -> List[ToolCommand]:
        """
        去重工具列表，保留高优先级目录中的工具

        Args:
            tools: 工具列表

        Returns:
            List[ToolCommand]: 去重后的工具列表
        """
        # 创建目录优先级映射
        dir_priority = {dir_path: idx for idx, dir_path in enumerate(self.tools_dirs)}

        # 按工具名称分组
        tools_by_name: Dict[str, List[ToolCommand]] = {}
        for tool in tools:
            if tool.name not in tools_by_name:
                tools_by_name[tool.name] = []
            tools_by_name[tool.name].append(tool)

        # 对每个工具名称，选择优先级最高的工具
        unique_tools = []
        for name, tool_list in tools_by_name.items():
            if len(tool_list) == 1:
                unique_tools.append(tool_list[0])
            else:
                # 选择优先级最高的工具
                best_tool = min(
                    tool_list, key=lambda t: dir_priority.get(t.source_directory, 999)
                )
                unique_tools.append(best_tool)

                # 记录被覆盖的工具
                for tool in tool_list:
                    if tool != best_tool:
                        logger.debug(
                            f"工具 {name} 在 {tool.source_directory} 被 {best_tool.source_directory} 中的版本覆盖"
                        )

        return unique_tools

    def get_tool_by_name(self, name: str) -> Optional[ToolCommand]:
        """
        根据名称获取工具命令

        Args:
            name: 工具名称

        Returns:
            Optional[ToolCommand]: 工具命令对象
        """
        result = self.load_tools()
        if not result.success:
            return None

        for tool in result.tools:
            if tool.name == name:
                return tool
        return None

    def list_tool_names(self) -> List[str]:
        """
        获取所有工具名称列表

        Returns:
            List[str]: 工具名称列表
        """
        result = self.load_tools()
        if not result.success:
            return []
        return [tool.name for tool in result.tools]

    @byzerllm.prompt()
    def get_tools_prompt(self) -> str:
        """
        # Available External(or Custom) Tool Commands

        Project Name: {{ project_name }}
        Current Project Path: {{ project_path }}
        Total Tools: {{ tools_count }}
        {% if failed_count > 0 %}
        Failed to Load: {{ failed_count }} tools
        {% endif %}

        ## Tool Directories
        {% for dir in tools_directories %}
        - {{ dir }}
        {% endfor %}

        ## Tool List

        {% if tools_count == 0 %}
        No available tool commands found.
        {% else %}
        {% for tool in tools_info %}
        ### {{ tool.name }}{{ tool.file_extension }}

        **Source Directory**: {{ tool.source_directory }}
        **Executable**: {% if tool.is_executable %}Yes{% else %}No{% endif %}

        **Usage Instructions**:
        ```
        {{ tool.help_text }}
        ```

        ---
        {% endfor %}
        {% endif %}

        ## How to Create External Tools

        ### Directory Structure (Priority Order)
        Tools are loaded from these directories in priority order (highest to lowest):
        1. **Project-specific**: `./.autocodertools/` (**recommended**)
        2. **Project config**: `./.auto-coder/.autocodertools/`
        3. **Global user**: `~/.auto-coder/.autocodertools/`
        4. **Project-specific global**: `~/.auto-coder/.autocodertools/repos/{{ project_name }}/` (lowest priority)

        **Note**:
        - Tools with identical names in higher priority directories will override those in lower priority directories.
        - The source code of the tools is in the directory `{{ autocoder_home }}/.auto-coder/tool_repos/`.
        - To inspect tools or tool_repos content, use `execute_command` tool (e.g., `ls`) since the `.auto-coder` directory is excluded from `search_files` results.

        ### Supported File Types
        - **Executable binaries** (compiled tools, **recommended**)
        - **Script files** (`.sh`, `.py`, `.js`, `.rb`, etc.)

        ### Tool Development Guidelines

        Please use SubAgent to create new tools. Before invoke the subagent, you should create the project directory in {{ autocoder_home }}/.auto-coder/tool_repos/ first
        and then go in to the project directory and then echo '<prompt>' | auto-coder.run --model <model_name> --is-sub-agent to invoke the subagent.
        New tools should follow the same guidelines as existing tools.

        #### 1. Help Information (Required)
        Your tool must provide help information using one of these methods:

        **Method 1: Command-line help (Recommended)**
        ```bash
        your_tool help
        your_tool -h
        your_tool --help
        ```

        **Notes**:
        - `your_tool --help` can be used to view CLI help for most tools.
        - `your_tool --skill` can be used to view the full skill document of the command, but this parameter is optional and
          not all tools provide it.

        **Method 2: File header comments**
        ```python
        #!/usr/bin/env python3
        # Description: Brief description of your tool
        # Usage: tool_name [options] [arguments]
        #
        # Options:
        #   -h, --help     Show this help message
        #   -v, --verbose  Enable verbose output
        ```

        #### 2. File Permissions
        - **Binary files** (no extension): Must be executable (`chmod +x`)
        - **Script files** (`.py`, `.sh`, etc.): Must be readable (`chmod +r`)

        #### 3. Tool Execution
        Use the built-in `execute_external_tool` tool to run your custom tools.
        If the tool requires sensitive credentials (accounts/passwords/API keys), you must use `execute_external_tool` instead.

        #### 3.1 Credentials / Sensitive Parameters (Recommended)
        Some external tools require sensitive information (e.g., `api_key`, `token`, `username`, `password`), and different
        subcommands may require different credentials.

        - Store sensitive values in a YAML file named `<tool_name>.key` (same directory as the tool file).
        - This `.key` file supports `global` params and nested multi-level `subcommands` configuration.
        - The `execute_external_tool` tool will automatically inject these params into the command line, and will mask
          sensitive values in display/logs.

        **⚠️ IMPORTANT: If a `.key` file exists for the tool, you DO NOT read the key file and DO NOT need to pass credentials (accounts/passwords/API keys)
        when calling the tool. The system will automatically inject them from the `.key` file. Just call the tool with
        other required parameters only.**

        Example `.key` file (supports multi-level subcommands):
        ```yaml
        global:
          api_key: "sk-xxxx"
          username: "user"

        # Multi-level subcommands with _params for each level
        subcommands:
          config:
            _params:              # params for "config" subcommand
              verbose: "true"
            set:
              _params:            # params for "config,set" subcommands
                format: "json"
              proxy:
                _params:          # params for "config,set,proxy" subcommands
                  timeout: "30"
          upload:
            _params:
              token: "yyy"

        # Optional formatting settings
        param_style: "space"      # "space" => --key value, "equals" => --key=value
        param_prefix: "--"        # or "-"
        ```

        **Usage Example**:
        - With `.key` file: `tool_name config set proxy --url http://example.com` (credentials auto-injected)
        - Multi-level subcommands: Use comma-separated format like `<subcommands>config,set,proxy</subcommands>`

        #### 4. **Tool is now available** - the AI assistant will discover and use it freely

        ## Important Rules

        ### Rule 1: Help Parameter (MANDATORY)
        All tools MUST support `help` or `-h` parameter for detailed usage information.

        ### Rule 2: Use SubAgent to Create Tools (REQUIRED)
        - **NEVER** create tools directly in the current agent
        - **ALWAYS** use a sub agent with proper timeout (e.g., 1800s)

        ### Rule 3: Preferred Language Priority

        **Development Tools Status**:
        | Priority | Language | Package Manager | Status |
        |----------|----------|-----------------|--------|
        | 1st      | **Go**   | go mod          | {% if dev_tools.go %}✅ Available{% else %}❌ Not Installed{% endif %} |
        | 2nd      | Node.js  | bun             | {% if dev_tools.bun %}✅ Available{% else %}❌ Not Installed{% endif %} |
        | 3rd      | Python   | uv              | {% if dev_tools.uv %}✅ Available{% else %}❌ Not Installed{% endif %} |

        {% if not dev_tools.go and not dev_tools.bun and not dev_tools.uv %}
        ⚠️ **WARNING**: No development tools detected! Please install Go first (recommended).
        {% elif not dev_tools.go %}
        💡 **Recommendation**: Go is not installed. Consider installing Go for better tool development experience.
        {% endif %}

        {% if not dev_tools.go %}
        ### Go Installation Guide

        **{{ os_type }}**:
        {% if os_type == "macOS" %}
        ```bash
        # Using Homebrew (recommended)
        brew install go

        # Or download from official website
        # https://go.dev/dl/
        ```
        {% elif os_type == "Linux" %}
        ```bash
        # Ubuntu/Debian
        sudo apt update && sudo apt install golang-go

        # Or using snap
        sudo snap install go --classic

        # Or download from official website
        # https://go.dev/dl/
        ```
        {% elif os_type == "Windows" %}
        ```powershell
        # Using winget (recommended)
        winget install GoLang.Go

        # Using Chocolatey
        choco install golang

        # Or download from official website
        # https://go.dev/dl/
        ```
        {% endif %}

        After installation, verify with:
        ```bash
        go version
        ```
        {% endif %}

        ### Rule 4: Tool Creation Workflow (Step-by-Step)

        **Step 1**: Create project directory

        Linux/macOS:
        ```bash
        mkdir -p {{ autocoder_home }}/.auto-coder/tool_repos/<tool_name>
        ```

        Windows (PowerShell):
        ```powershell
        New-Item -ItemType Directory -Force -Path "{{ autocoder_home }}\.auto-coder\tool_repos\<tool_name>"
        ```

        **Step 2**: Invoke SubAgent to develop the tool

        Linux/macOS:
        ```bash
        cd {{ autocoder_home }}/.auto-coder/tool_repos/<tool_name> && echo '<your_prompt>' | auto-coder.run --model <model_name> --is-sub-agent
        ```

        Windows (PowerShell):
        ```powershell
        cd "{{ autocoder_home }}\.auto-coder\tool_repos\<tool_name>"; echo '<your_prompt>' | auto-coder.run --model <model_name> --is-sub-agent
        ```

        **Step 3**: Copy the compiled binary to tools directory

        Linux/macOS:
        ```bash
        cp {{ autocoder_home }}/.auto-coder/tool_repos/<tool_name>/<binary_name> {{ project_path }}/.autocodertools/
        ```

        Windows (PowerShell):
        ```powershell
        Copy-Item "{{ autocoder_home }}\.auto-coder\tool_repos\<tool_name>\<binary_name>.exe" "{{ project_path }}\.autocodertools\"
        ```

        **Step 4**: Verify
        - If no binary found, ask SubAgent to rebuild
        - Test the tool with `<tool_name> --help` (Linux/macOS) or `<tool_name>.exe --help` (Windows)
        """

        # 加载所有工具
        result = self.load_tools()

        # 检测开发工具状态
        dev_tools = get_dev_tools_status()

        # 检测操作系统类型
        system = platform.system()
        if system == "Darwin":
            os_type = "macOS"
        elif system == "Windows":
            os_type = "Windows"
        else:
            os_type = "Linux"

        if not result.success:
            return {
                "project_name": get_project_name(),
                "project_path": os.getcwd(),
                "autocoder_home": os.path.expanduser("~"),
                "tools_count": 0,
                "tools_info": [],
                "failed_count": 0,
                "tools_directories": self.tools_dirs,
                "error_message": result.error_message or "未找到任何工具",
                "dev_tools": dev_tools,
                "os_type": os_type,
            }  # type: ignore[return]

        tools_info = []
        for tool in result.tools:
            tools_info.append(
                {
                    "name": tool.name,
                    "help_text": tool.help_text,
                    "is_executable": tool.is_executable,
                    "file_extension": tool.file_extension,
                    "source_directory": tool.source_directory,
                }
            )

        project_name = get_project_name()

        return {
            "project_name": project_name,
            "project_path": os.getcwd(),
            "autocoder_home": os.path.expanduser("~"),
            "tools_count": len(result.tools),
            "tools_info": tools_info,
            "failed_count": result.failed_count,
            "tools_directories": self.tools_dirs,
            "dev_tools": dev_tools,
            "os_type": os_type,
        }  # type: ignore[return]
