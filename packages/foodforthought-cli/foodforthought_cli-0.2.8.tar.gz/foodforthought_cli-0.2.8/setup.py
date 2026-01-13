from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="foodforthought-cli",
    version="0.2.8",
    author="Kindly Robotics",
    author_email="hello@kindly.fyi",
    description="CLI tool for FoodforThought robotics repository platform - manage robot skills and data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://kindly.fyi/foodforthought",
    project_urls={
        "Homepage": "https://kindly.fyi",
        "Documentation": "https://kindly.fyi/foodforthought/cli",
        "Source": "https://github.com/kindlyrobotics/monorepo",
        "Bug Tracker": "https://github.com/kindlyrobotics/monorepo/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Version Control",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="robotics, robot-skills, machine-learning, data-management, cli",
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "robot-setup": [
            "pyserial>=3.5",
            "anthropic>=0.18.0",  # For AI-assisted labeling (optional)
        ],
        "detection": [
            "Pillow>=9.0.0",  # For color-based object detection
        ],
        "visual-labeling": [
            "pyserial>=3.5",
            "opencv-python>=4.5.0",  # Webcam capture for visual labeling
            "Pillow>=9.0.0",
        ],
        "all": [
            "pyserial>=3.5",
            "anthropic>=0.18.0",
            "Pillow>=9.0.0",
            "opencv-python>=4.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ate=ate.cli:main",
        ],
    },
)

