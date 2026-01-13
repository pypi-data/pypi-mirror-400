#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Setup config for installing the package."""

from setuptools import setup


def get_long_description():
    desc = open('README.md').read()
    try:
        changelog = open('CHANGELOG').read()
        desc += '\n\n'
        desc += "## CHANGELOG: "
        desc += '\n```\n'
        desc += changelog
        desc += '\n```\n'
    except FileNotFoundError:
        try:
            from owega.changelog import OwegaChangelog as oc
            changelog = oc.log
            desc += '\n\n'
            desc += "## CHANGELOG: "
            desc += '\n```\n'
            desc += changelog
            desc += '\n```\n'
        except ModuleNotFoundError:
            pass
    return desc


setup()
