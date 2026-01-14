from setuptools import setup, find_packages

setup(
    name="ethan_super_ai_wrapper",  # <--- CHANGE THIS to something unique
    version="0.1.1",
    description="The easiest AI wrapper for OpenAI, Anthropic, and HuggingFace",
    author="Ethan",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
)