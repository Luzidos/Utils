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
        "google-api-core",
        "google-api-python-client",
        "google-auth",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "googleapis-common-protos",
        "email",
        "os",
        "base64",
        "bs4",
    ],
    author="Luzidos",
    author_email="contact@luzidos.com",
    description="Utils used for Luzidos agent project",   
)             