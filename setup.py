"""Installation setup for Magic-Spoiler."""

import setuptools

# Necessary for TOX
setuptools.setup(
    name="Magic-Spoiler",
    version="0.1.0",
    author="Zach Halpern",
    author_email="zach@cockatrice.us",
    url="https://github.com/Cockatrice/Magic-Spoiler/",
    description="Build XML files for distribution of MTG spoiler cards",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    license="GPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    keywords="Magic: The Gathering, MTG, XML, Card Games, Collectible, Trading Cards",
    packages=setuptools.find_packages(),
)
