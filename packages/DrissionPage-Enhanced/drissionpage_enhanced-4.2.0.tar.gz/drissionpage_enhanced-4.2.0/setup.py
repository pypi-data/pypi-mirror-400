# -*- coding:utf-8 -*-
from setuptools import setup, find_packages
# from DrissionPage import __version__
from setuptools import setup, find_packages
import pathlib

version = {}
version_file = pathlib.Path("DrissionPage/version.py")
exec(version_file.read_text(), version)
with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="DrissionPage-Enhanced",
    version=version["__version__"],
    author="g1879 (Enhanced by Community)",
    author_email="g1879@qq.com",
    description="Enhanced DrissionPage with proxy authentication, advanced resource blocking, and WebSocket monitoring.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="DrissionPage browser automation proxy websocket selenium playwright",
    url="https://github.com/yourusername/DrissionPage-Enhanced",
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "lxml",
        "requests",
        "cssselect",
        "DownloadKit>=2.0.7",
        "websocket-client",
        "click",
        "tldextract>=3.4.4",
        "psutil",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        # "License :: OSI Approved :: BSD License",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "dp = DrissionPage._functions.cli:main",
        ],
    },
)
