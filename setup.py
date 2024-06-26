from setuptools import setup, find_packages

setup(
    name="luzidos_utils",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "datetime",
        "botocore",
        "google-api-core",
        "google-api-python-client",
        "google-auth",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "googleapis-common-protos",
        "bs4",
        "charset-normalizer",
    ],
    author="Luzidos",
    author_email="contact@luzidos.com",
    description="Utils used for Luzidos agent project",   
)             