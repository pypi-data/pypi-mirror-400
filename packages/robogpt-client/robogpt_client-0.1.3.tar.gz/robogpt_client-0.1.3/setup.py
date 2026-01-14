from setuptools import setup, find_packages
import os

# Read the README file
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "RoboGPT gRPC Client for agent communication"

# Read requirements
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "grpcio>=1.50.0",
        "grpcio-tools>=1.50.0",
        "protobuf>=4.21.0",
    ]

setup(
    name="robogpt_client",
    version="0.1.3",
    author="Orangewood Labs",
    author_email="support@orangewood.co",
    description="RoboGPT gRPC Client for agent communication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/orangewood-co/robogpt",

    # Explicitly list packages since the structure is non-standard
    packages=["robogpt_client", "robogpt_client.agents", "robogpt_client.examples", "robogpt_client.robot_control", "robogpt_client.vision"],
    
    # Map the package to current directory
    package_dir={"robogpt_client": "."},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "robogpt-agent-demo=robogpt_client.examples.demo_agents:main",
            "robogpt-bot-control-demo=robogpt_client.examples.demo_bot_control:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
