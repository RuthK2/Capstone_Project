from setuptools import setup, find_packages

setup(
    name="expense-tracker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Django>=5.0,<6.0",
        "djangorestframework>=3.14.0",
        "gunicorn>=23.0.0",
    ],
)