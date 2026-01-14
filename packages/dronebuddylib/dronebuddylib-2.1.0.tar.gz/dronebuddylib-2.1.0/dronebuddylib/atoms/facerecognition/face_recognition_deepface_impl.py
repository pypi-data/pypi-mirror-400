import cv2
import pkg_resources

from dronebuddylib.atoms.facerecognition.face_recognition_result import RecognizedFaces, RecognizedFaceObject
from dronebuddylib.atoms.facerecognition.i_face_recognition import IFaceRecognition
from dronebuddylib.models.engine_configurations import EngineConfigurations
from dronebuddylib.models.execution_status import ExecutionStatus
from dronebuddylib.utils import FileWritingException
from dronebuddylib.utils.logger import Logger

from deepface import DeepFace

logger = Logger()


class FaceRecognitionDeepFaceImpl(IFaceRecognition):
    """
    Implementation of the IFaceRecognition interface using DeepFace library.
    Uses DeepFace to match and verify faces using modern embedding models like ArcFace or Facenet.
    """
    current_status = None

    KNOWN_NAMES_FILE_PATH = pkg_resources.resource_filename(__name__, "resources/known_names.txt")
    IMAGE_PATH = "resources/images/"

    def __init__(self, engine_configurations: EngineConfigurations):
        self.current_status = ExecutionStatus(self.get_class_name(), "INIT", "INITIALIZATION", "COMPLETED")
        super().__init__(engine_configurations)

    def recognize_face(self, image) -> RecognizedFaces:
        self.current_status = ExecutionStatus(self.get_class_name(), "recognize_face", "initializing", "STARTED")
        recognized_faces = []

        # Save the incoming image temporarily
        input_path = "temp_input.jpg"
        cv2.imwrite(input_path, image)

        # Load known faces
        face_names = self.load_known_face_names()
        known_image_paths = [pkg_resources.resource_filename(__name__, self.IMAGE_PATH + name + ".jpg") for name in
                             face_names]

        self.current_status = ExecutionStatus(self.get_class_name(), "recognize_face", "matching_faces", "STARTED")

        for i, known_path in enumerate(known_image_paths):
            try:
                result = DeepFace.verify(img1_path=input_path, img2_path=known_path, model_name="ArcFace",
                                         enforce_detection=False)
                if result["verified"]:
                    recognized_faces.append(RecognizedFaceObject(face_names[i], result["distance"]))
            except Exception as e:
                logger.log_error(self.get_class_name(), f"Error verifying face: {e}")

        self.current_status = ExecutionStatus(self.get_class_name(), "recognize_face", "matching_faces", "COMPLETED")
        return RecognizedFaces(recognized_faces)

    def load_known_face_names(self):
        path = self.KNOWN_NAMES_FILE_PATH
        return self.read_file_into_list(path)

    def read_file_into_list(self, filename):
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
                return [line.strip() for line in lines if line.strip()]
        except FileNotFoundError as e:
            raise FileNotFoundError("The specified file is not found.", e) from e

    def remember_face(self, image_path=None, name=None) -> bool:
        self.current_status = ExecutionStatus(self.get_class_name(), "remember_face", "remember_face", "STARTED")
        try:
            with open(self.KNOWN_NAMES_FILE_PATH, 'a') as file:
                file.write(name + '\n')
        except IOError:
            logger.log_error(self.get_class_name(), "Error while writing to file: " + name)
            raise FileWritingException("Error while writing to the file: " + name)

        try:
            new_file_name = pkg_resources.resource_filename(__name__, self.IMAGE_PATH + name + ".jpg")
            loaded_image = cv2.imread(image_path)
            cv2.imwrite(new_file_name, loaded_image)
            self.current_status = ExecutionStatus(self.get_class_name(), "remember_face", "remember_face", "COMPLETED")
        except IOError:
            raise FileWritingException("Error while writing image file: ", new_file_name)
        return True

    def get_required_params(self) -> list:
        return []

    def get_optional_params(self) -> list:
        return []

    def get_class_name(self) -> str:
        return 'FACE_RECOGNITION_DEEPFACE'

    def get_algorithm_name(self) -> str:
        return 'DeepFace Verification'

    def get_current_status(self) -> dict:
        return self.current_status.to_dict() if self.current_status else {}
