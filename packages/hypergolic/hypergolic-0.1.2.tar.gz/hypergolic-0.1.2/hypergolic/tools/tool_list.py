from .schemas import Tool

from .command_line import CommandLineTool

ALL_TOOLS: list[Tool] = [CommandLineTool]
ALL_TOOLS_FORMATTED = [t.model_dump() for t in ALL_TOOLS]
TOOL_MAP = {t.name: t for t in ALL_TOOLS}
