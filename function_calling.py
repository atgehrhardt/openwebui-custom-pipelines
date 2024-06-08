import os
import requests
from typing import Literal, List, Optional
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint


class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        # Add your custom parameters here
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def get_location(self) -> dict:
            """
            Get the current geographical location using the IP address.

            :return: A dictionary with latitude and longitude.
            """
            response = requests.get('https://ipinfo.io')
            data = response.json()
            location = data['loc'].split(',')
            return {'latitude': location[0], 'longitude': location[1]}

        def get_current_time(self) -> str:
            """
            Get the current local time based on location.

            :return: The current local time.
            """
            location = self.get_location()
            latitude = float(location['latitude'])
            longitude = float(location['longitude'])

            geolocator = Nominatim(user_agent="geoapiExercises")
            timezone_finder = TimezoneFinder()

            timezone_str = timezone_finder.timezone_at(lat=latitude, lng=longitude)
            if timezone_str:
                timezone = pytz.timezone(timezone_str)
                now = datetime.now(timezone)
                current_time = now.strftime("%Y-%m-%d %H:%M:%S %Z%z")
                return f"Current Local Time = {current_time}"
            else:
                return "Could not determine the time zone."

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