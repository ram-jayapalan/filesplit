
from distutils.core import setup
import os


def get_long_desc():

    if not os.path.isfile('README.rst'):
        return

    with open('README.rst') as f:
        desc = f.read()

    return desc


setup(
    name="filesplit",
    packages=["fsplit"],
    version="1.0.3",
    description="Module to split file of any size into multiple chunks",
    long_description=get_long_desc(),
    author="Ram Prakash Jayapalan",
    author_email="ramp16888@gmail.com",
    url="https://github.com/ram-jayapalan/filesplit",
    download_url="https://github.com/ram-jayapalan/filesplit/archive/1.0.4.tar.gz",
    keywords="file split filesplit splitfile chunks splits",
    classifiers=[],
)

