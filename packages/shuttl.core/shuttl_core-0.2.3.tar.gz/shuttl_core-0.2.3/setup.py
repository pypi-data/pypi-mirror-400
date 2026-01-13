import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "shuttl.core",
    "version": "0.2.3",
    "description": "The JSII library for Shuttl AI models",
    "license": "MIT",
    "url": "https://github.com/shuttl-io/shuttl.git",
    "long_description_content_type": "text/markdown",
    "author": "Shuttl AI<developers@shuttl.io>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/shuttl-io/shuttl.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "shuttl.core",
        "shuttl.core._jsii"
    ],
    "package_data": {
        "shuttl.core._jsii": [
            "core@0.2.3.jsii.tgz"
        ],
        "shuttl.core": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "jsii>=1.120.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard==2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
