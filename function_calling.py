import os
import requests
from typing import Literal, List, Optional
from datetime import datetime

from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint

class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        # Add your custom parameters here
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def get_current_time() -> str:
            """
            Get the current time in the system's local timezone.

            :return: The current time in the local timezone.
            """
            now = datetime.now()  # Get the current local time
            is_dst = time.localtime().tm_isdst > 0  # Check if daylight saving time is in effect
            offset_seconds = time.altzone if is_dst else time.timezone  # Get the timezone offset in seconds
            offset_hours = -offset_seconds // 3600  # Convert offset to hours
            current_time = now.strftime("%H:%M:%S")
            return f"Current Time (UTC{offset_hours:+03d}:00) = {current_time}"

        def calculator(self, equation: str) -> str:
            """
            Calculate the result of an equation.

            :param equation: The equation to calculate.
            """

            # Avoid using eval in production code
            # https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
            try:
                result = eval(equation)
                return f"{equation} = {result}"
            except Exception as e:
                print(e)
                return "Invalid equation"

    def __init__(self):
        super().__init__()
        # Optionally, you can set the id and name of the pipeline.
        # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        # self.id = "my_tools_pipeline"
        self.name = "My Tools Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
            },
        )
        self.tools = self.Tools(self)