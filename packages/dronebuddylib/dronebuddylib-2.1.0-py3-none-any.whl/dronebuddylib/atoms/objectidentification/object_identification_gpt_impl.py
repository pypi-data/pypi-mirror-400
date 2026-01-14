import base64
import json
import os
import threading

import cv2
from openai import OpenAI

from dronebuddylib.atoms.objectidentification import IObjectIdentification
from dronebuddylib.models import AtomicEngineConfigurations, EngineConfigurations
from dronebuddylib.utils.logger import Logger

logger = Logger()

OBJECT_MEMORY_DIR = "object_memory"


class ObjectIdentificationGPTImpl:
    pass


def hook_fn(module, input, output):
    intermediate_features.append(output)


class ObjectIdentificationResnetImpl(IObjectIdentification):
    SYSTEM_PROMPT_OBJECT_IDENTIFICATION = """
       You are a helpful assistant.

       When the instruction "REMEMBER_AS(object name)" is given with an image of the object, 
       remember the object and return an acknowledgement in the format of:

       {
           "status": "SUCCESS" / "UNSUCCESSFUL",
           "message": "description"
       }

       When the instruction "IDENTIFY" is given with an image, 
       return all identified objects in this format:
       {
           "description": "specific, spoken-style description for blind users",
           "data": [
               {
                   "class_name": "class the object belongs to",
                   "object_name": "known object name or 'unknown'",
                   "description": "visual description",
                   "confidence": 0.0-1.0
               }
           ]
       }
       """

    def __init__(self, engine_configurations: EngineConfigurations):
        super().__init__(engine_configurations)
        os.makedirs(OBJECT_MEMORY_DIR, exist_ok=True)
        configs = engine_configurations.get_configurations_for_engine(self.get_class_name())
        self.logger = Logger()
        self.intermediate_features = []
        self.open_ai_key = configs.get(AtomicEngineConfigurations.INTENT_RECOGNITION_OPEN_AI_API_KEY.name,
                                       configs.get(
                                           AtomicEngineConfigurations.INTENT_RECOGNITION_OPEN_AI_API_KEY))
        self.model_name = configs.get(AtomicEngineConfigurations.INTENT_RECOGNITION_OPEN_AI_MODEL.name,
                                      configs.get(
                                          AtomicEngineConfigurations.INTENT_RECOGNITION_OPEN_AI_MODEL))

        self.client = OpenAI(api_key=self.open_ai_key)  # Assumes OPENAI_API_KEY is set in your environment

    def remember_object(self, object_name, image=None, image_folder_path=None) -> bool:
        global intermediate_features

        try:
            save_path = os.path.join(OBJECT_MEMORY_DIR, f"{object_name}.jpg")
            if image is not None:
                cv2.imwrite(save_path, image)
            elif image_folder_path:
                for file in os.listdir(image_folder_path):
                    if file.lower().endswith((".jpg", ".jpeg", ".png")):
                        cv2.imwrite(save_path, cv2.imread(os.path.join(image_folder_path, file)))
                        break
            logger.log_info(self.get_class_name(), f"Remembered object: {object_name}")
            return True
        except Exception as e:
            logger.log_error(self.get_class_name(), f"Failed to remember object: {e}")
            return False

    def identify_object(self, image) -> str:
        temp_path = "query_temp.jpg"
        cv2.imwrite(temp_path, image)
        b64img = self._image_to_base64(temp_path)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT_OBJECT_IDENTIFICATION},
                {"role": "user", "content": [
                    {"type": "text", "text": "IDENTIFY"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64img}"}}
                ]}
            ],
            max_tokens=1000
        )

        reply = response.choices[0].message.content.strip()
        try:
            return json.loads(reply)
        except json.JSONDecodeError:
            logger.log_error(self.get_class_name(), f"Invalid JSON response: {reply}")
            return {
                "description": "Unable to interpret object clearly.",
                "data": []
            }

    def _image_to_base64(self, path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def get_required_params(self) -> list:
        return [AtomicEngineConfigurations.INTENT_RECOGNITION_OPEN_AI_API_KEY]

    def get_optional_params(self) -> list:
        return [AtomicEngineConfigurations.INTENT_RECOGNITION_OPEN_AI_MODEL]

    def get_class_name(self) -> str:
        return "OBJECT_IDENTIFICATION_GPT"

    def get_algorithm_name(self) -> str:
        return "ObjectIdentificationGPTImpl"

    progress_event = threading.Event()
import json
import os
import pickle
import re
import threading
import time
from asyncio import Future
from pathlib import Path

import cv2
import openai
import pkg_resources
from openai import OpenAI

from tqdm import tqdm

from dronebuddylib.atoms.llmintegration.agent_factory import AgentFactory
from dronebuddylib.atoms.llmintegration.models.image_validator_results import ImageValidatorResults
from dronebuddylib.atoms.objectidentification.i_object_identification import IObjectIdentification
from dronebuddylib.atoms.objectidentification.object_identification_result import IdentifiedObjects, \
    IdentifiedObjectObject
from dronebuddylib.exceptions.llm_exception import LLMException
from dronebuddylib.models.engine_configurations import EngineConfigurations
from dronebuddylib.models.enums import AtomicEngineConfigurations
from dronebuddylib.utils.enums import LLMAgentNames
from dronebuddylib.utils.logger import Logger

logger = Logger()


class ObjectIdentificationGPTImpl(IObjectIdentification):
    """
    A class to perform object identification using ResNet and GPT integration.
    """
    progress_event = threading.Event()

    def __init__(self, engine_configurations: EngineConfigurations):
        """
        Initializes the ResNet object detection engine with the given engine configurations.

        Args:
            engine_configurations (EngineConfigurations): The engine configurations for the object detection engine.
        """
        super().__init__(engine_configurations)

        configs = engine_configurations.get_configurations_for_engine(self.get_class_name())

        openai_api_key = configs.get(AtomicEngineConfigurations.OBJECT_IDENTIFICATION_GPT_API_KEY.name,
                                     configs.get(AtomicEngineConfigurations.OBJECT_IDENTIFICATION_GPT_API_KEY))
        self.model = "gpt-4o"
        self.openai_api_key = openai_api_key
        self.client = OpenAI(api_key=self.openai_api_key)

        self.agent_picker = AgentFactory(self.model, self.openai_api_key, None)
        self.object_identifier = self.agent_picker.get_agent(LLMAgentNames.OBJECT_IDENTIFIER)
        self.image_validator = self.agent_picker.get_agent(LLMAgentNames.IMAGE_VALIDATOR)
        self.image_describer = self.agent_picker.get_agent(LLMAgentNames.IMAGE_DESCRIBER)

    def create_memory_on_the_fly(self, changes=None):
        """
        Creates memory on the fly by reading known objects from a JSON file and
        sending them to the object identifier for processing.

        Args:
            changes: Optional parameter to pass changes if any.
        """
        file_path = pkg_resources.resource_filename(__name__, "resources/known_object_list.json")
        with open(file_path, 'r') as file:
            json_content = json.load(file)
            known_object_list = json_content['known_objects']
            for obj in known_object_list:
                self.object_identifier.send_image_message_to_llm_queue("user", "REMEMBER_AS( " + obj['name'] + ")",
                                                                       obj['url'])
                print(obj)
        print("Memory created successfully")

    def identify_object(self, image) -> IdentifiedObjects:
        """
        Identifies the objects in the given image using the ResNet object detection engine.

        Args:
            image_path (str): The path to the image of the objects to identify.

        Returns:
            IdentifiedObjects: The identified objects with their associated probabilities.
        """
        self.object_identifier.send_encoded_image_message_to_llm_queue("user", "IDENTIFY", image)
        result = self.object_identifier.get_response_from_llm().content
        formatted_result = self.format_answers(result)
        return formatted_result

    def identify_object_image_path(self, image_path) -> IdentifiedObjects:
        """
        Identifies the objects in the given image using the ResNet object detection engine.

        Args:
            image_path (str): The path to the image of the objects to identify.

        Returns:
            IdentifiedObjects: The identified objects with their associated probabilities.
        """
        self.object_identifier.send_image_message_to_llm_queue("user", "IDENTIFY", image_path)
        result = self.object_identifier.get_response_from_llm().content
        formatted_result = self.format_answers(result)
        print(result)
        return formatted_result

    def format_answers(self, result):
        """
        Formats the raw result from the object identifier into IdentifiedObjects.

        Args:
            result (str): The raw JSON result from the object identifier.

        Returns:
            IdentifiedObjects: The formatted identified objects.
        """
        formatted_result = json.loads(result)
        identified_objects = IdentifiedObjects([], [])
        for result in formatted_result['data']:
            object_name = result['object_name']
            obj = IdentifiedObjectObject(result['class_name'], result['object_name'], result['description'],
                                         result['confidence'])
            if object_name == "unknown":
                identified_objects.add_available_object(obj)
            else:
                identified_objects.add_identified_object(obj)

        return identified_objects

    def remember_object(self, image=None, type=None, name=None):
        """
        Remembers a new object by sending its image and type to the object identifier.

        Args:
            image: The image of the object to remember.
            type: The type of the object.
            name: The name of the object.

        Returns:
            success_result: The result from the object identifier after processing.
        """
        logger.log_info(self.get_class_name(), 'Starting to remember object: type : ' + type + ' : ' + name)
        validation_result = self.validate_reference_image(image, type)
        if validation_result.is_valid:
            success_result = self.object_identifier.send_encoded_image_message_to_llm_queue("user",
                                                                                            "REMEMBER_AS( " + name + ")",
                                                                                            image)
            return success_result
        else:
            logger.log_error(self.get_class_name(), 'Image validation failed. Please try again with a different image.')
            return LLMException('Image validation failed. Please try again with a different image.', 500,
                                str(validation_result))

    def validate_reference_image(self, image, image_type) -> ImageValidatorResults:
        """
        Validates the reference image using the object validator.

        Args:
            image: The image to validate.
            image_type: The type of the image.

        Returns:
            ImageValidatorResults: The result of the image validation.
        """
        validity = self.image_validator.send_encoded_image_message_to_llm_queue("user",
                                                                                "VALIDATE( " + image_type + ")",
                                                                                image)
        return validity

    def describe_image(self, frame):
        """
        Describes the image using the GPT model.

        Args:
            frame: The image to describe.

        Returns:
            str: The description of the image.
        """
        description = self.image_describer.get_response_for_image_queries("DESCRIBE", frame)
        return description

    def get_class_name(self) -> str:
        """
        Gets the class name of the object detection implementation.

        Returns:
            str: The class name of the object detection implementation.
        """
        return 'OBJECT_IDENTIFICATION_GPT'

    def get_algorithm_name(self) -> str:
        """
        Gets the algorithm name of the object detection implementation.

        Returns:
            str: The algorithm name of the object detection implementation.
        """
        return 'Chat GPT object identification'

    def get_required_params(self) -> list:
        """
        Gets the list of required configuration parameters for the GPT object detection engine.

        Returns:
            list: The list of required configuration parameters.
        """
        return [AtomicEngineConfigurations.OBJECT_IDENTIFICATION_GPT_API_KEY]

    def get_optional_params(self) -> list:
        """
        Gets the list of optional configuration parameters for the GPT object detection engine.

        Returns:
            list: The list of optional configuration parameters.
        """
        return [AtomicEngineConfigurations.OBJECT_IDENTIFICATION_GPT_MODEL]
