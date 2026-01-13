"""Setup configuration for veridex package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="veridex",
    version="0.2.0",
    author="Veridex Contributors",
    author_email="adityamahakali@aisolve.org",
    description="A modular, probabilistic, and research-grounded AI content detection library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ADITYAMAHAKALI/veridex",
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "text": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "nltk>=3.8",
        ],
        "image": [
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "diffusers>=0.20.0",
            "Pillow>=9.0.0",
            "opencv-python-headless>=4.0.0",
            "scikit-image>=0.19.0",
        ],
        "audio": [
            "torch>=2.0.0",
            "torchaudio>=2.0.0",
            "transformers>=4.30.0",
            "librosa>=0.10.0",
            "soundfile>=0.12.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "ipython>=8.0.0",
        ],
        "video": [
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "opencv-python-headless>=4.0.0",
            "scipy>=1.7.0",
            "librosa>=0.10.0",
            "mediapipe>=0.10.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
