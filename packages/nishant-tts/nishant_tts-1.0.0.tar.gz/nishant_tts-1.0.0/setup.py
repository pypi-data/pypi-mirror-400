from setuptools import setup, find_packages

setup(
    name="nishant_tts",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "modal",
        "numpy",
    ],
    author="Nishant",
    description="Client library for cached F5-TTS inference on Modal",
)
