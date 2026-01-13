from setuptools import setup

setup(
    name="littlescribe",
    version="1.0.0",
    description="Real-time audio transcription with AI summarization",
    py_modules=["littlescribe"],
    install_requires=[
        "pyaudio",
        "numpy", 
        "amazon-transcribe",
        "boto3"
    ],
    entry_points={
        "console_scripts": [
            "littlescribe=littlescribe:main"
        ]
    }
)
