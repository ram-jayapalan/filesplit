from distutils.core import setup
import os


def get_long_desc() -> str:

    if not os.path.isfile("README.rst"):
        return ""

    with open("README.rst") as f:
        desc = f.read()

    return desc


setup(
    name="filesplit",
    packages=["fsplit"],
    version="3.0.2",
    description="Module to split file of any size into multiple chunks",
    long_description=get_long_desc(),
    author="Ram Prakash Jayapalan",
    author_email="ramp16888@gmail.com",
    url="https://github.com/ram-jayapalan/filesplit",
    download_url="https://github.com/ram-jayapalan/filesplit/archive/v3.0.2.tar.gz",
    keywords="file split filesplit splitfile chunks splits",
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
    ],
)
