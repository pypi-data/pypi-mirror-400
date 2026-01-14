# -*- coding: utf-8 -*-
from __future__ import annotations

from setuptools import find_packages
from setuptools import setup


setup(
    name="pioreactor-relay-plugin",
    version="0.7.1",
    license="MIT",
    description="Turn the PWM channels into a simple on/off relay for additional hardware.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author_email="cam@pioreactor.com",
    author="Kelly Tran, Pioreactor",
    url="https://github.com/CamDavidsonPilon/pioreactor-relay-plugin",
    packages=find_packages(),
    include_package_data=True,
    entry_points={"pioreactor.plugins": "pioreactor_relay_plugin = pioreactor_relay_plugin"},
)
