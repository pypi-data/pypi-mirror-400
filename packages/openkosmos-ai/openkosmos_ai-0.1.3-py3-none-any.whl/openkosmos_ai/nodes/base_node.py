import os

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import load_prompt


class BaseFlowNode:

    @staticmethod
    def create_tool_result_message(messages, content="done", tool_call_index=0, tool_call_message_index=-1):
        tool_calls = messages[tool_call_message_index].tool_calls
        return {"role": "tool", "content": content, "tool_call_id": tool_calls[tool_call_index]['id']}

    @staticmethod
    def create_tool_message(content: str | list[str | dict] | None = None):
        return ToolMessage(content=content)

    @staticmethod
    def create_ai_message(content: str | list[str | dict] | None = None):
        return AIMessage(content=content)

    @staticmethod
    def create_user_message(content: str | list[str | dict] | None = None):
        return HumanMessage(content=content)

    @staticmethod
    def create_system_message(content: str | list[str | dict] | None = None):
        return SystemMessage(content=content)

    @staticmethod
    def get_prompt(template_name: str, template_dir=None, template_ext=".yml"):
        template_base_dir = template_dir
        if template_base_dir is None:
            template_base_dir = os.getenv("KOSMOS_TEMPLATE_DIR", default="./templates")

        return load_prompt(f"{template_base_dir}/{template_name}{template_ext}", encoding="utf8")
