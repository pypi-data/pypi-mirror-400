import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "renovosolutions.aws-cdk-aurora-native-backup",
    "version": "0.1.0",
    "description": "AWS CDK construct library for Aurora backup and restore using ECS on a schedule, storing backups in S3.",
    "license": "Apache-2.0",
    "url": "https://github.com/RenovoSolutions/cdk-library-aurora-native-backup.git",
    "long_description_content_type": "text/markdown",
    "author": "Renovo Solutions<webmaster+cdk@renovo1.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/RenovoSolutions/cdk-library-aurora-native-backup.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "renovosolutions_aurora_native_backup",
        "renovosolutions_aurora_native_backup._jsii"
    ],
    "package_data": {
        "renovosolutions_aurora_native_backup._jsii": [
            "cdk-library-aurora-native-backup@0.1.0.jsii.tgz"
        ],
        "renovosolutions_aurora_native_backup": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.233.0, <3.0.0",
        "cdk-ecr-deployment>=4.0.5, <5.0.0",
        "cdk-nag==2.37.55",
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
