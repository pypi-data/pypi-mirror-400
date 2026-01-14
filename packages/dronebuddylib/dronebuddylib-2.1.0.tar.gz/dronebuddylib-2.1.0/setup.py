from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip()
        for line in fh
        if line.strip() and not line.strip().startswith("#")
    ]

setup(
    name="dronebuddylib",
    version="2.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={"dronebuddylib": ["resources/*"]},
    zip_safe=False,
    install_requires=requirements,   # ✅ fixed
    extras_require={
        "FACE_RECOGNITION": ["face-recognition"],
        "INTENT_RECOGNITION_GPT": ["openai", "tiktoken"],
        "INTENT_RECOGNITION_SNIPS": ["snips-nlu"],
        "OBJECT_DETECTION_MP": ["mediapipe"],
        "OBJECT_DETECTION_YOLO": ["ultralytics"],
        "TEXT_RECOGNITION": ["google-cloud-vision"],
        "SPEECH_RECOGNITION_MULTI": ["SpeechRecognition"],
        "SPEECH_RECOGNITION_VOSK": ["vosk"],
        "SPEECH_RECOGNITION_GOOGLE": ["google-cloud-speech"],
        "SPEECH_GENERATION": ["pyttsx3"],
        "OBJECT_IDENTIFICATION": ["openai", "tiktoken"],
        "LLM_INTEGRATION": ["openai", "tiktoken"],
        "PLACE_RECOGNITION": [
            "scikit-learn", "numpy", "torch", "torchvision", "Pillow", "tqdm", "opencv-python"
        ],
        "NAVIGATION_TELLO": ["djitellopy"],
    },
    python_requires=">=3.9",
    description="Everything to control and customize Tello",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NUS",
    author_email="malshadz@nus.edu.sg",
    license="MIT",
)
