import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ComDaAn", # Replace with your own username
    version="0.0.1",
    author="Kevin Ottens",
    author_email="ervin@ipsquad.net",
    description="APIs to ease Community Data Analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://framagit.org/ervin/ComDaAn",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

