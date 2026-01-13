import pathlib
from setuptools import setup

HERE   = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

with (HERE / "requirements.txt").open() as f:
    requirements = f.read().splitlines()


setup(
    name="reqst",
    version="0.1.2",
    description="A Python CLI program to send requests.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hstoklosa/reqst",
    author="hstoklosa",
    author_email="hubert.stoklosa23@gmail.com",
    license="MIT",
    entry_points={
        'console_scripts': [
            'reqst = reqst.__main__:main',
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=["reqst"],
    include_package_data=True,
    install_requires=requirements,
)