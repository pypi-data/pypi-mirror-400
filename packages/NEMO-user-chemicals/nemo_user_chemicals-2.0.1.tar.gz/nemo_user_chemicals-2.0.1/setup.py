from setuptools import find_namespace_packages, setup

VERSION = '2.0.1'

setup(
    name="NEMO-user-chemicals",
    version=VERSION,
    description="User chemical request and inventory management plugin for NEMO",
    packages=find_namespace_packages(),
    author="David Barth",
    author_email="dsbarth@seas.upenn.edu",
    url="https://gitlab.com/nemo-community/upenn/nemo_user_chemicals",
    include_package_data=True,
    install_requires=[
        "django",
    ],
    extras_require={
        "NEMO": ["NEMO>=7.0.0"],
        "dev-tools": ["pre-commit", "djlint", "black"],
    },
    keywords=["NEMO"],
)
