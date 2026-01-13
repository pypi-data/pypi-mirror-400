"""
ReadImageToolResolver - 图片识别工具解析器

使用视觉模型（vl_model）分析图片内容，支持多图片路径（逗号分割）。
"""

import base64
import mimetypes
from pathlib import Path
from typing import Optional, List

import byzerllm
from loguru import logger

from autocoder.common import AutoCoderArgs
from autocoder.common.v2.agent.agentic_edit_tools.base_tool_resolver import (
    BaseToolResolver,
)
from autocoder.common.v2.agent.agentic_edit_types import ReadImageTool, ToolResult
from autocoder.utils.llms import get_single_llm
import typing

if typing.TYPE_CHECKING:
    from autocoder.common.v2.agent.agentic_edit import AgenticEdit


class ReadImageToolResolver(BaseToolResolver):
    """图片识别工具解析器

    使用 args.vl_model 指定的视觉模型读取和分析图片内容。
    支持多个图片路径（用逗号分割）。
    """

    # 支持的图片格式
    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

    def __init__(
        self, agent: Optional["AgenticEdit"], tool: ReadImageTool, args: AutoCoderArgs
    ):
        super().__init__(agent, tool, args)
        self.tool: ReadImageTool = tool

    def _get_vl_llm(self) -> Optional[byzerllm.ByzerLLM]:
        """获取视觉模型 LLM 实例"""
        vl_model = self.args.vl_model
        if not vl_model:
            return None

        try:
            return get_single_llm(vl_model, product_mode=self.args.product_mode)
        except Exception as e:
            logger.warning(f"Failed to get vl_model '{vl_model}': {e}")
            return None

    def _validate_image_path(self, path: str) -> tuple[bool, str]:
        """验证图片路径

        Returns:
            tuple[bool, str]: (是否有效, 错误信息或空字符串)
        """
        if not path:
            return False, "Empty path"

        image_path = Path(path)

        # 检查文件是否存在
        if not image_path.exists():
            return False, f"File not found: {path}"

        # 检查是否是文件
        if not image_path.is_file():
            return False, f"Not a file: {path}"

        # 检查文件扩展名
        ext = image_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            return (
                False,
                f"Unsupported image format '{ext}'. Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}",
            )

        return True, ""

    def _load_image_as_data_uri(self, image_path: str) -> str:
        """将本地图片加载为 data URI 格式

        Args:
            image_path: 图片文件路径

        Returns:
            data URI 格式的字符串，如 "data:image/png;base64,..."
        """
        mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
        with open(image_path, "rb") as f:
            base64_data = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{base64_data}"

    def _read_images(
        self,
        vl_llm: byzerllm.ByzerLLM,
        image_paths: List[str],
        query: str,
    ) -> tuple[bool, str]:
        """读取并分析图片（支持单张或多张）

        使用 OpenAI Vision 标准格式。

        Args:
            vl_llm: 视觉模型 LLM 实例
            image_paths: 图片文件路径列表
            query: 用户查询

        Returns:
            tuple[bool, str]: (是否成功, 分析结果或错误信息)
        """
        try:
            # 构建 content 列表，使用 OpenAI Vision 标准格式
            content = [{"type": "text", "text": query}]

            # 添加所有图片
            for image_path in image_paths:
                image_data_uri = self._load_image_as_data_uri(image_path)
                content.append(
                    {"type": "image_url", "image_url": {"url": image_data_uri}}
                )

            # 构建对话消息
            conversations = [{"role": "user", "content": content}]

            # 调用视觉模型
            response = vl_llm.chat_oai(conversations=conversations)

            if response and len(response) > 0:
                return True, response[0].output
            else:
                return False, "No response from vision model"

        except Exception as e:
            logger.exception(f"Error analyzing images: {image_paths}")
            return False, f"Error analyzing images: {e}"

    def resolve(self) -> ToolResult:
        """解析并执行图片识别请求"""
        # 检查 vl_model 配置
        if not self.args.vl_model:
            return ToolResult(
                success=False,
                message="Vision model not configured. Please set 'vl_model' in args to use read_image tool.",
            )

        # 获取视觉模型实例
        vl_llm = self._get_vl_llm()
        if not vl_llm:
            return ToolResult(
                success=False,
                message=f"Failed to initialize vision model '{self.args.vl_model}'.",
            )

        # 解析图片路径（支持逗号分割的多个路径）
        raw_path = self.tool.path or ""
        paths = [p.strip() for p in raw_path.split(",") if p.strip()]

        if not paths:
            return ToolResult(success=False, message="'path' is required")

        query = self.tool.query or "请描述这张图片的内容"

        # 验证所有路径
        valid_paths: List[str] = []
        failures: List[str] = []

        for i, image_path in enumerate(paths):
            valid, error_msg = self._validate_image_path(image_path)
            if valid:
                valid_paths.append(image_path)
            else:
                failures.append(f"[{i + 1}] {error_msg}")

        if not valid_paths:
            return ToolResult(
                success=False,
                message="No valid images found. " + "; ".join(failures),
            )

        # 一次调用分析所有有效图片
        success, result = self._read_images(vl_llm, valid_paths, query)

        if not success:
            return ToolResult(success=False, message=result)

        # 构建返回结果
        summary = f"Analyzed {len(valid_paths)} image(s): {', '.join(valid_paths)}"
        if failures:
            summary += f" | skipped: {'; '.join(failures)}"

        return ToolResult(
            success=True,
            message=summary,
            content=result,
        )
