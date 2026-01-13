"""Setup script for zephyr-test-linker."""

from setuptools import setup

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="zephyr-jira-linker",
    version="0.1.1",
    description="A command-line tool for linking test cases in Zephyr Scale to Jira issues",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pandiyaraj Karuppasamy",
    author_email="pandiyarajk@live.com",
    url="https://github.com/yourusername/zephyr-test-linker",
    packages=["zephyr_test_linker"],
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "zephyr-jira-linker=zephyr_jira_linker.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.7",
    keywords="zephyr jira test-management automation devops",
)
