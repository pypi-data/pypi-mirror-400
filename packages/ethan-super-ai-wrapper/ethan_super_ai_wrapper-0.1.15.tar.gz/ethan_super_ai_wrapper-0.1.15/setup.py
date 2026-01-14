from setuptools import setup, find_packages
from pathlib import Path

# --- MAGIC LINES: Read the README file ---
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
# -----------------------------------------

setup(
    name="ethan_super_ai_wrapper",
    version="0.1.15",  # Updated version
    description="The easiest AI wrapper for OpenAI, Anthropic, Gemini, and HuggingFace",
    
    # --- MAGIC LINES: Send README to PyPI ---
    long_description=long_description,
    long_description_content_type='text/markdown',
    # ----------------------------------------
    
    author="Ethan",
    packages=find_packages(),
    install_requires=[
        "requests",
        "huggingface_hub",
    ],
)