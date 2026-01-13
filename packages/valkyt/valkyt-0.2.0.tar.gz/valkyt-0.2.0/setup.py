from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.2.0'
DESCRIPTION = 'Utils'

setup(
    name="valkyt",
    version=VERSION,
    author="ryyos (Rio Dwi Saputra)",
    author_email="<riodwi12174@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['greenstalk', 'kafka-python', 'pika', 'loguru', 'redis', 'boto3', 'python-dateutil', 'dekimashita', 'requests', 'pyquery', 'bs4', 'click', 's3fs', 'yt_dlp', 'fake-useragent', "tqdm"],
    keywords=['valkyt', 'utils'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Operating System :: Microsoft :: Windows",
    ]
)