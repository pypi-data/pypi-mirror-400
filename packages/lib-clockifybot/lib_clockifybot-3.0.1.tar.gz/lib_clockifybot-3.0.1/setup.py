from setuptools import setup, find_packages


def read_requirements(file):
    with open(file) as f:
        return f.read().splitlines()


setup(
    name="lib_clockifybot",
    version="3.0.1",
    author="retr0err0r - veininvein",
    packages=find_packages(),
    install_requires=read_requirements("requirements.txt"),
)
