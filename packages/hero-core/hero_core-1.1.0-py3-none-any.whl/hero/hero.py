"""
Hero package
"""

import json
import random
import shutil
import string
import sys
from hero.build_in_tool.prompt.reasoner import get_reasoner_protocol
from hero.task import ExistedTask, InitialTask
from hero.build_in_model.model import BasicModel
from hero_base import CommonToolWrapper
from typing import List, Optional
import os
from datetime import datetime
from hero.compressor.compressor import CustomCompress
from hero.build_in_tool import (
    final_answer,
    write_a_note,
    read_file,
    execute_shell,
    extract_key_info_from_file,
    reflect_and_brainstorm,
    program,
    experiment_report,
    plan,
    ls,
    glob,
)


class Hero:
    def __init__(self, model: BasicModel, workspace_root="_workspace", return_format: str = "xml"):
        """
        初始化 Hero
        """
        self.default_model = model
        self.workspace_root = workspace_root
        self.return_format = return_format
        self.__tools: List[CommonToolWrapper] = []
        self.character_setting = ""
        self.background_info = ""
        self.tooltips = []
        self.best_practices = ""
        self.tone_and_style = ""
        self.additional_reminders_list = []
        self.additional_reminders = ""
        self.custom_compress: Optional[CustomCompress] = None
        self.rules = ""
        self.final_answer = final_answer.custom({"model": model})

        self.read_file = read_file
        self.execute_shell = execute_shell
        self.extract_key_info_from_file = extract_key_info_from_file.custom(
            {"model": model}
        )

        self.write_a_note = write_a_note
        self.reflect_and_brainstorm = reflect_and_brainstorm.custom({"model": model})
        self.experiment_report = experiment_report
        self.plan = plan
        self.ls = ls
        self.glob = glob
        self.program = program.custom({"coder": model})

        self.add_tool(
            self.final_answer,
            self.write_a_note,
            self.read_file,
            self.execute_shell,
            self.extract_key_info_from_file,
            self.reflect_and_brainstorm,
            self.program,
            self.experiment_report,
            self.plan,
            self.ls,
            self.glob,
        )

    def compressor(self, compress_func: CustomCompress):
        self.custom_compress = compress_func

        def wrapper(*args, **kwargs):
            pass

        return wrapper

    def set_character_setting(self, character_setting: str):
        self.character_setting = character_setting

    def set_background_info(self, background_info: str):
        self.background_info = background_info

    def add_tooltips(self, tooltips: list[str]):
        self.tooltips = list(set(self.tooltips + tooltips))

    def add_reminders(self, reminders: list[str] | str):
        if isinstance(reminders, list):
            self.additional_reminders_list.extend(reminders)
        else:
            self.additional_reminders += "\n" + reminders 

    def set_best_practices(self, best_practices: str):
        self.best_practices = best_practices

    def set_tone_and_style(self, tone_and_style: str):
        self.tone_and_style = tone_and_style

    def set_rules(self, rules: str):
        self.rules = rules

    def get_tool(self, tool_name: str) -> CommonToolWrapper | None:
        for tool in self.__tools:
            if tool.get_name() == tool_name:
                return tool

    def add_tool(self, *tools: CommonToolWrapper):
        for tool in tools:
            tool_name = tool.get_name()
            index = next(
                (i for i, t in enumerate(self.__tools) if t.get_name() == tool_name),
                None,
            )
            if index is not None:
                self.__tools[index] = tool
            else:
                self.__tools.append(tool)

    def custom_tools(self, *tools: CommonToolWrapper):
        self.__tools.clear()
        self.__tools.extend(tools)

    def __get_tools_name(self):
        return [tool.get_name() for tool in self.__tools]

    def __get_tools_prompt(self):
        prompt = ""
        for tool in self.__tools:
            schema = tool.get_params().model_json_schema()
            type = schema.get("type", "object")
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            parameters = {
                "type": type,
                "properties": properties,
            }
            if required:
                parameters["required"] = required
            prompt += f"""<tool>
    {{
        "name": "{tool.get_name()}",
        "description": "{schema.get("description", "")}",
        "parameters": {json.dumps(parameters, indent=4)},
    }}
</tool>
"""
        return prompt

    def __new_workspace(self, workspace_id: str):
        if not workspace_id:
            workspace_id = (
                datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                + "_"
                + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            )
        workspace_root = os.path.abspath(self.workspace_root)
        working_dir = os.path.join(workspace_root, workspace_id, "working")
        os.makedirs(working_dir, exist_ok=True)
        log_dir = os.path.join(workspace_root, workspace_id, "log")
        os.makedirs(log_dir, exist_ok=True)
        return workspace_id

    def __get_all_tool_tips(self):
        tool_tips = []
        for tool in self.__tools:
            if tool.tool_tips:
                tool_tips.extend(tool.tool_tips)
        return list(set(tool_tips + self.tooltips))

    async def new_task(
        self,
        question: str = "",
        question_file: str = "",
        attachments: List[str] = [],
        workspace_id: str = "",
        max_turn: int = sys.maxsize,
        restart_turn: int = sys.maxsize,
    ) -> InitialTask:
        workspace_id = self.__new_workspace(workspace_id)
        workspace = os.path.join(self.workspace_root, workspace_id)
        if question_file:
            try:
                with open(question_file, "r") as f:
                    question = f.read()
            except Exception as e:
                raise e
        attachments_info = ""
        if attachments:
            attachments_info = "\n\nThe following files are attached to this task:"
            for attachment in attachments:
                try:
                    # if the attachment is a directory, copy it to the workspace
                    if os.path.isdir(attachment):
                        shutil.copytree(
                            attachment,
                            os.path.join(
                                workspace, "working", os.path.basename(attachment)
                            ),
                        )
                        attachments_info += f"\n- (Directory) {os.path.basename(attachment)}"
                    # if the attachment is a file, copy it to the workspace
                    else:
                        with open(attachment, "r") as f:
                            shutil.copy(attachment, os.path.join(workspace, "working"))
                        attachments_info += f"\n- {os.path.basename(attachment)}"
                except Exception as e:
                    raise e

        reasoner_prompt = get_reasoner_protocol(
            tools = self.__get_tools_prompt(),
            character_setting = self.character_setting,
            background_info = self.background_info,
            best_practices = self.best_practices,
            tone_and_style = self.tone_and_style,
            tooltips = self.__get_all_tool_tips(),
            additional_reminders =  "\n".join(["- " + item for item in self.additional_reminders_list]) + self.additional_reminders,
            build_in_tools = self.__get_tools_name(),
            rules = self.rules,
            return_format = self.return_format,
        )

        return InitialTask(
            model=self.default_model,
            tools=self.__tools,
            reasoner_prompt=reasoner_prompt,
            question=question + attachments_info,
            workspace_root=self.workspace_root,
            workspace_id=workspace_id,
            max_turn=max_turn,
            restart_turn=restart_turn,
            custom_compress=self.custom_compress,
            return_format=self.return_format,
        )

    async def continue_task(
        self,
        workspace_id: str = "",
        new_max_turn: int = sys.maxsize,
        restart_turn: int = sys.maxsize,
    ) -> ExistedTask:
        reasoner_prompt = get_reasoner_protocol(
            tools = self.__get_tools_prompt(),
            character_setting = self.character_setting,
            background_info = self.background_info,
            best_practices = self.best_practices,
            tone_and_style = self.tone_and_style,
            tooltips = self.__get_all_tool_tips(),
            additional_reminders =  "\n".join(["- " + item for item in self.additional_reminders_list]) + self.additional_reminders,
            build_in_tools = self.__get_tools_name(),
            rules = self.rules,
            return_format = self.return_format,
        )
        existed_task = ExistedTask(
            model=self.default_model,
            tools=self.__tools,
            workspace_root=self.workspace_root,
            workspace_id=workspace_id,
            reasoner_prompt=reasoner_prompt,
            new_max_turn=new_max_turn,
            restart_turn=restart_turn,
            custom_compress=self.custom_compress,
            return_format=self.return_format,
        )
        await existed_task._recover_task()
        return existed_task

    async def recover_task(
        self,
        workspace_id: str = "",
        new_max_turn: int = sys.maxsize,
        restart_turn: int = sys.maxsize,
    ) -> ExistedTask:
        reasoner_prompt = get_reasoner_protocol(
            tools = self.__get_tools_prompt(),
            character_setting = self.character_setting,
            background_info = self.background_info,
            best_practices = self.best_practices,
            tone_and_style = self.tone_and_style,
            tooltips = self.__get_all_tool_tips(),
            additional_reminders =  "\n".join(["- " + item for item in self.additional_reminders_list]) + self.additional_reminders,
            build_in_tools = self.__get_tools_name(),
            rules = self.rules,
            return_format = self.return_format,
        )
        existed_task = ExistedTask(
            model=self.default_model,
            tools=self.__tools,
            workspace_root=self.workspace_root,
            workspace_id=workspace_id,
            reasoner_prompt=reasoner_prompt,
            new_max_turn=new_max_turn,
            restart_turn=restart_turn,
            custom_compress=self.custom_compress,
            return_format=self.return_format,
        )
        await existed_task._recover_task()
        return existed_task
