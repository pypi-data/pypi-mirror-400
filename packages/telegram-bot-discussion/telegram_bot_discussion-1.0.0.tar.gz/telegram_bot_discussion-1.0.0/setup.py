from os import path
from setuptools import setup, find_packages, find_namespace_packages

from datetime import datetime, timezone


def readme():
    with open("README.md", "r") as f:
        return f.read()


def get_timestamp():
    return int(datetime.now(timezone.utc).timestamp() * 1000000)


if __name__ == "__main__":
    setup(
        name="telegram-bot-discussion",
        version=f"1.0.0",  # f"1.0.{get_timestamp()}"
        author="ILYA",
        description="Telegram-bot framework `telegram-bot-discussion` based on native Telegram Bot API Python-library `python-telegram-bot`.",
        long_description=readme(),
        long_description_content_type="text/markdown",
        packages=find_packages(),
        install_requires=["python-telegram-bot>=22.0"],
        classifiers=[
            "Programming Language :: Python :: 3.9",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Build Tools",
            "Operating System :: OS Independent",
        ],
        keywords="Python Telegram-bot Framework",
        # project_urls={"Documentation": "link"},
        python_requires=">=3.9",
    )
