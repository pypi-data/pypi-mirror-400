from typing import Callable, Union
from pydantic import BaseModel, Field


class Tool(BaseModel):
    name: str = Field(examples=["get_weather"])
    description: str = Field(examples=["Get the current weather in a given location"])
    input_schema: dict
    callable: Callable = Field(exclude=True)
    input_model: type[BaseModel] = Field(exclude=True)


ToolOutput = Union[str, list[str]]
