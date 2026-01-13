#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from setuptools import setup

from jenkins_lockable_resources import VERSION


def get_version():
    CI_COMMIT_TAG = os.environ.get("CI_COMMIT_TAG", None)
    if not CI_COMMIT_TAG:
        return VERSION

    # Fixup extra release tag
    if VERSION not in CI_COMMIT_TAG:
        raise Exception(
            "Commit tag {} does not match version {}".format(CI_COMMIT_TAG, VERSION)
        )

    # Tag postfix
    postfix = CI_COMMIT_TAG.replace(VERSION, "")
    return VERSION + postfix


setup(version=get_version())
