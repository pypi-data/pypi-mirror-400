#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools

setuptools.setup(
    name="story-python",
    version="0.1.2",
    author="Hive Solutions Lda.",
    author_email="development@hive.pt",
    description="Story Data System",
    license="Apache License, Version 2.0",
    keywords="story storage data engine web json",
    url="http://story.hive.pt",
    zip_safe=False,
    packages=[
        "story",
        "story.controllers",
        "story.controllers.api",
        "story.controllers.web",
        "story.models",
        "story.test",
    ],
    test_suite="story.test",
    package_dir={"": os.path.normpath("src")},
    install_requires=["appier", "appier-extras", "commons_py"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
