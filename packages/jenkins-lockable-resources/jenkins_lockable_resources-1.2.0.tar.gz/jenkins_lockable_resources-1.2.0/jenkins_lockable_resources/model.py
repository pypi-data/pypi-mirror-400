#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

"""
Jenkins Lockable Resources plugin API

This library aims to query Jenkins Lockable Resources plugin to retieve information or control resources.
"""

import json
import re

from jenkinsapi.jenkinsbase import JenkinsBase


PLUGIN_NAME = "lockable-resources"


def check_request(f):
    def wrapper(*args, **kwargs):
        response = f(*args, **kwargs)
        if not response.ok:
            response.raise_for_status()

    return wrapper


class Resource:
    def __init__(
        self,
        jenkins_obj,
        name,
        *,
        is_locked=False,
        is_reserved=False,
        reserved_by=None,
        labels=None,
        is_queued=False,
        description=None,
        timestamp=None,
    ):
        self.jenkins = jenkins_obj.get_jenkins_obj()
        self.name = name
        self.is_locked = is_locked
        self.is_reserved = is_reserved
        self.reserved_by = reserved_by
        self.labels = labels
        self.baseurl = jenkins_obj.baseurl
        self.is_queued = is_queued
        self.description = description
        self.timestamp = timestamp

    @property
    def is_free(self):
        """
        Check if resource is free
        """
        return not self.is_reserved and not self.is_locked

    @property
    def is_owned(self):
        """
        Check if resource is owned by current user
        """
        return self.reserved_by == self.jenkins.username

    @check_request
    def reserve(self):
        """
        Reserve the resource
        """
        url = f"{self.baseurl}/reserve?resource={self.name}"
        return self.jenkins.requester.post_url(url)

    @check_request
    def unreserve(self):
        """
        Unreserve the resource
        """
        url = f"{self.baseurl}/unreserve?resource={self.name}"
        return self.jenkins.requester.post_url(url)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(
            {
                "name": self.name,
                "is_locked": self.is_locked,
                "is_reserved": self.is_reserved,
                "reserved_by": self.reserved_by,
                "labels": self.labels,
                "is_queued": self.is_queued,
                "description": self.description,
                "timestamp": self.timestamp,
            }
        )


GROOVY_LIST_SCRIPT = """
import org.jenkins.plugins.lockableresources.LockableResourcesManager
import groovy.json.JsonBuilder

def manager = LockableResourcesManager.get()
def resources = manager.getResources()

def resourceData = resources.collect { r ->
    return [
        name: r.getName(),
        is_locked: r.isLocked(),
        is_reserved: r.isReserved(),
        is_queued: r.isQueued(),
        reserved_by: r.getReservedBy() ?: "",
        labels: r.getLabelsAsList(),
        timestamp: r.getReservedTimestamp() ?: 0,
        description: r.getDescription() ?: "",
    ]
}

new JsonBuilder(resourceData)
"""


class LockableResources(JenkinsBase):
    """
    Class to hold information on lockable resources
    """

    def __init__(
        self,
        jenkins_obj,
        baseurl=None,
        poll=True,
        res_filter=None,
    ):
        """
        Init a lockable resource object

        Args:
            jenkins_obj (Jenkins): ref to the jenkins obj
            baseurl (str): basic url for querying information on a node
                If url is not set - object will construct it itself. This is
                useful when node is being created and not exists in Jenkins yet
            poll (bool): set to False if node does not exist or automatic
                refresh from Jenkins is not required. Default is True.
                If baseurl parameter is set to None - poll parameter will be
                set to False
            res_filter (str): Regex expression to filter resources (default '.*')
        """

        self.jenkins = jenkins_obj
        self.plugin = self.get_plugin()
        if not baseurl:
            poll = False
            baseurl = f"{self.jenkins.baseurl}/{PLUGIN_NAME}/"

        self._filter = re.compile(res_filter) if res_filter else re.compile(".*")
        self._cache_data = {}
        self._data = None

        JenkinsBase.__init__(self, baseurl, poll=poll)

    def get_plugin(self):
        # Check plugin availablility and version
        plugins = self.get_jenkins_obj().plugins
        return plugins[PLUGIN_NAME]

    def get_jenkins_obj(self):
        return self.jenkins

    def get_data(self, url, params=None, tree=None):
        """
        Retrieve data of lockable-resources
        """
        requester = self.get_jenkins_obj().requester
        response = requester.post_url(
            url=f"{self.jenkins.baseurl}/scriptText",
            data={"script": GROOVY_LIST_SCRIPT},
            verify=True,
        )
        response.raise_for_status()

        res = response.text.replace("Result: ", "").strip()
        return json.loads(res)

    @property
    def data(self):
        if self._data is None:
            self._data = self.poll()
        return self._data

    def list_resources(self) -> list:
        """
        Lists resources names
        """
        return list(self.keys())

    def get_resources(self) -> list:
        """
        Get resources
        """
        return list(self.values())

    def is_reserved(self, name) -> bool:
        """
        Check if a resource is reserved

        Args:
            name (str): The resource name
        """
        return self[name].is_reserved

    def is_locked(self, name) -> bool:
        """
        Check if a resource is locked

        Args:
            name (str): The resource name
        """
        return self[name].is_locked

    def is_free(self, name) -> bool:
        """
        Check if resource is free
        """
        return self[name].is_free

    def get_owner(self, name) -> str:
        """
        Get resource owner

        Args:
            name (str): The resource name
        """
        return self[name].reserved_by

    def get_owned_resources(self, user=None) -> list:
        """
        Get resources owned by user

        Args:
            user (str): The owner name. Default to the current jenkins user.
        """
        if user is None:
            user = self.jenkins.username

        return [
            res
            for res in self.values(reserved_by=user)
            if res.is_reserved or res.is_locked
        ]

    def get_free_resources(self) -> list:
        """
        Find a free resource
        """
        return list(self.values(is_locked=False, is_reserved=False))

    def reserve(self, name):
        """
        Reserve a resource
        """
        self[name].reserve()

    def unreserve(self, name):
        """
        Unreserve a resource
        """
        self[name].unreserve()

    def items(self):
        """
        Iterate over the names & objects for all resources
        """
        for resource in self.values():
            yield resource.name, resource

    def keys(self):
        """
        Iterate over the names of all available resources
        """
        for row in self.data:
            yield row["name"]

    def values(
        self,
        *,
        name=None,
        labels=None,
        is_locked=None,
        is_reserved=None,
        reserved_by=None,
    ):
        """
        Iterate over all available resources

        Args:
            name (str): a regex match string for resource name
            labels (str): a regex match string for resource labels
            locked (bool): if locked
            reserved (bool): if reserved
        """
        data = self.data
        if name is not None:
            if isinstance(name, str):
                name = re.compile(name)
            data = filter(lambda x: name.match(x["name"]), data)
        if labels is not None:
            if isinstance(labels, str):
                labels = re.compile(labels)
            data = filter(lambda x: labels.match(",".join(x["labels"])), data)
        if is_locked is not None:
            data = filter(lambda x: x["is_locked"] == is_locked, data)
        if is_reserved is not None:
            data = filter(lambda x: x["is_reserved"] == is_reserved, data)
        if reserved_by is not None:
            data = filter(lambda x: x["reserved_by"] == reserved_by, data)

        for attrs in data:
            yield self._make_resource(attrs)

    def _make_resource(self, attrs):
        return Resource(self, **attrs)

    def __contains__(self, resource):
        """
        True if resource exists in Jenkins
        """
        return resource in self.keys()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        # Regex key search
        pattern = re.compile(key)
        for attrs in self.data:
            if pattern.match(attrs["name"]):
                return self._make_resource(attrs)
        raise KeyError(key)

    def __str__(self):
        return self.baseurl
