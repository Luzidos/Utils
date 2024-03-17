from setuptools import setup, find_packages

setup(
    name="luzidos_utils",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "datetime",
        "uuid",
        "botocore",
        "google",
        "google_auth_oauthlib",
        "googleapiclient",
        "email",
        "os",
        "base64",
        "bs4",
    ],
    author="Luzidos",
    author_email="contact@luzidos.com",
    description="Utils used for Luzidos agent project",   
)             