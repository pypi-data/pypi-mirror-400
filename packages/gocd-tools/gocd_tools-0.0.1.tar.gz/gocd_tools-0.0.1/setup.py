import os
from setuptools import setup, find_packages

cur_dir = os.path.abspath(os.path.dirname(__file__))


def read(path):
    with open(path, "r") as _file:
        return _file.read()


def read_req(name):
    path = os.path.join(cur_dir, name)
    return [req.strip() for req in read(path).splitlines() if req.strip()]


# Get the current package version.
version_ns = {}
version_path = os.path.join(cur_dir, "gocd_tools", "_version.py")
version_content = read(version_path)
exec(version_content, {}, version_ns)


long_description = open("README.rst").read()
setup(
    name="gocd-tools",
    version=version_ns["__version__"],
    description="A tool for managing the gocd server",
    long_description=long_description,
    author="Rasmus Munk",
    author_email="munk1@live.dk",
    packages=find_packages(),
    url="https://github.com/rasmunk/gocd-tools",
    license="MIT",
    keywords=["GoCD", "CI", "CD"],
    install_requires=read_req("requirements.txt"),
    extras_require={"dev": read_req("requirements-dev.txt")},
    entry_points={"console_scripts": ["gocd-tools = gocd_tools.cli.cli:run"]},
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
