import os
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-xladmin-enhanced",
    version="1.0.6",
    author="Enhanced Team",
    author_email="your_email@example.com",
    description="Enhanced Django xAdmin - A modern admin interface for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/django-xladmin-enhanced",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
    ],
    python_requires='>=3.8',
    install_requires=[
        "Django>=3.2",
        "django-crispy-forms",
        "crispy-bootstrap3",
        "django-import-export",
        "django-reversion",
        "Pillow",
        "future",
        "six",
        "xlsxwriter",
        "xlwt",
        "httplib2",
    ],
)
