import shlex
import subprocess

from pydantic import BaseModel, Field

from .enums import ToolName
from .schemas import Tool, ToolOutput


class CommandLineToolInput(BaseModel):
    cmd: str = Field(description="The command to run")


class CommandLineToolOutput(BaseModel):
    returncode: int
    stderr: str
    stdout: str


def issue_cmd(input: CommandLineToolInput) -> ToolOutput:
    output = subprocess.run(input.cmd, shell=True, capture_output=True, text=True)
    result = CommandLineToolOutput(
        returncode=output.returncode,
        stderr=output.stderr,
        stdout=output.stdout,
    )
    return result.model_dump_json()


CommandLineTool = Tool(
    name=ToolName.COMMAND_LINE,
    description="Issue a subprocess to a user's MacOS local machine",
    input_schema={
        "type": "object",
        "properties": {
            "cmd": {
                "type": "string",
                "description": "The command to run",
            }
        },
    },
    callable=issue_cmd,
    input_model=CommandLineToolInput,
)
