from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="PlayBaghChal",
    version="3.0.0",
    author="Bhishan Pangeni",
    author_email="bhishanpangeni2003@gmail.com",
    description="A Pygame implementation of the Bagh-Chal (Tiger and Goat) board game.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bhishanP/PlayBaghChal",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "playbaghchal": ["assets/*.png", "assets/*.jpg"],
    },
    install_requires=[
        "pygame",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "playbaghchal=playbaghchal.PlayGame:start_game",
        ],
    },
    keywords="pygame baghchal tiger goat board game",
)