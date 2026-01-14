from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md for long description
long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="AutoPX",  # Package name
    version="1.1.0",  # Incremented version for new release
    author="Mudassar Hussain",
    author_email="mudassarjutt65030@gmail.com",
    description="AutoPX – Automatic NLP Preprocessing with Explainable Reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),  # Automatically find all packages in your project
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "tensorflow",
        "deepface",
        "reportlab"
    ],
    url="https://github.com/MudassarGill/AutoPX",
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
        "Intended Audience :: Developers",
    ],
)
