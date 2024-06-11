import os
import requests
from typing import Literal, List, Optional
from datetime import datetime
import pytz

from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint

class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        HOME_ASSISTANT_URL: str = ""
        HOME_ASSISTANT_TOKEN: str = ""
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def get_current_time(self) -> str:
            """
            Get the current time in EST.

            :return: The current time in EST.
            """
            now_est = datetime.now(pytz.timezone('US/Eastern'))  # Get the current time in EST
            current_time = now_est.strftime("%H:%M:%S %Z%z")
            return f"Current Time = {current_time}"

        def get_all_lights(self) -> dict[str, str]:
            """
            Fetch all light entities from Home Assistant.

            :return: A dictionary of light entity names and their IDs.
            """
            if self.pipeline.valves.HOME_ASSISTANT_URL == "" or self.pipeline.valves.HOME_ASSISTANT_TOKEN == "":
                return "Home Assistant URL or token not set, ask the user to set it up."
            else:
                url = f"{self.pipeline.valves.HOME_ASSISTANT_URL}/api/states"
                headers = {
                    "Authorization": f"Bearer {self.pipeline.valves.HOME_ASSISTANT_TOKEN}",
                    "Content-Type": "application/json",
                }

                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                data = response.json()

                lights = {entity["attributes"]["friendly_name"]: entity["entity_id"]
                          for entity in data if entity["entity_id"].startswith("light.")}

                return lights

        def turn_light_on(self, light_name: str) -> str:
            """
            Turn on a light in Home Assistant by its friendly name.

            :param light_name: The friendly name of the light to turn on.
            :return: The status of the light after the command.
            """
            lights = self.get_all_lights()
            light_entity_id = lights.get(light_name)

            if not light_entity_id:
                return f"Light named '{light_name}' not found."

            url = f"{self.pipeline.valves.HOME_ASSISTANT_URL}/api/services/light/turn_on"
            headers = {
                "Authorization": f"Bearer {self.pipeline.valves.HOME_ASSISTANT_TOKEN}",
                "Content-Type": "application/json",
            }
            data = {
                "entity_id": light_entity_id,
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return f"Light '{light_name}' turned on."

        def turn_light_off(self, light_name: str) -> str:
            """
            Turn off a light in Home Assistant by its friendly name.

            :param light_name: The friendly name of the light to turn off.
            :return: The status of the light after the command.
            """
            lights = self.get_all_lights()
            light_entity_id = lights.get(light_name)

            if not light_entity_id:
                return f"Light named '{light_name}' not found."

            url = f"{self.pipeline.valves.HOME_ASSISTANT_URL}/api/services/light/turn_off"
            headers = {
                "Authorization": f"Bearer {self.pipeline.valves.HOME_ASSISTANT_TOKEN}",
                "Content-Type": "application/json",
            }
            data = {
                "entity_id": light_entity_id,
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return f"Light '{light_name}' turned off."

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