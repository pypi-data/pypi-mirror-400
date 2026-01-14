import os

import setuptools

current_directory = os.path.dirname(os.path.abspath(__file__))


try:
    with open(os.path.join(current_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = ""

setuptools.setup(
    name="branchkey",
    version="2.7.2",
    author="BranchKey",
    author_email="info@branchkey.com",
    description="Client application to interface with the BranchKey system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://branchkey.com",
    project_urls={
        "Homepage": "https://branchkey.com",
        "Repository": "https://gitlab.com/branchkey/client_application",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=["requests==2.32.3", "numpy==1.26.4",
                      "pika==1.3.2", "pysocks==1.7.1"],
)
