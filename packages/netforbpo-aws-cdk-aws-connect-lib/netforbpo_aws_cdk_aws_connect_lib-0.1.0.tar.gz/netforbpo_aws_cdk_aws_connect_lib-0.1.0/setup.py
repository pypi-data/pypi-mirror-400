import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "netforbpo-aws-cdk-aws-connect-lib",
    "version": "0.1.0",
    "description": "@netforbpo/aws-cdk-aws-connect-lib",
    "license": "Apache-2.0",
    "url": "https://github.com/netforbpo/aws-cdk-aws-connect-lib.git",
    "long_description_content_type": "text/markdown",
    "author": "netforbpo",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/netforbpo/aws-cdk-aws-connect-lib.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_cdk_connect_lib",
        "aws_cdk_connect_lib._jsii"
    ],
    "package_data": {
        "aws_cdk_connect_lib._jsii": [
            "aws-cdk-aws-connect-lib@0.1.0.jsii.tgz"
        ],
        "aws_cdk_connect_lib": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.233.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.122.0, <2.0.0",
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
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
