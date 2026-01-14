import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-managed-ad",
    "version": "0.0.20",
    "description": "AWS CDK constructs for Directory Service Managed AD",
    "license": "Apache-2.0",
    "url": "https://github.com/bpal410/cdk-managed-ad.git",
    "long_description_content_type": "text/markdown",
    "author": "bpal410<46696804+bpal410@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/bpal410/cdk-managed-ad.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_managed_ad",
        "cdk_managed_ad._jsii"
    ],
    "package_data": {
        "cdk_managed_ad._jsii": [
            "cdk-managed-ad@0.0.20.jsii.tgz"
        ],
        "cdk_managed_ad": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.173.2, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.125.0, <2.0.0",
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
