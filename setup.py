#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="django-url-tracker-fork",
    version='0.2.0',
    url="https://github.com/saulshanabrook/django-url-tracker",
    author="Sebastian Vetter",
    author_email="sebastian.vetter@tangentone.com.au",
    description=("A little app that trackes URL changes in a database table "
                 "to provide HTTP 301 & 410 on request."),
    long_description = open('README.rst').read(),
    license = "BSD",
    packages = find_packages(exclude=["docs*", "tests*"]),
    include_package_data = True,
    install_requires=[
        'django>=1.3.1,<1.10',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development"
    ],
    keywords = "seo, django, framework",
)
