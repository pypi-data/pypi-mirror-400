#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lockable Resources management application
"""
import logging
import functools

import requests.exceptions
from jenkinsapi.jenkins import Jenkins

from .model import LockableResources

INFO_STATE_COLORS = {"FREE": "green", "RESERVED": "yellow", "LOCKED": "red"}


def api_method(func):
    log = logging.getLogger(func.__name__)

    @functools.wraps(func)
    def wrapped(api, *args, **kwargs):
        try:
            return func(api, *args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            api.output.error(
                f"Failed to connect to {e.request.url}. Check your connection and try again."
            )
            log.error(e)
        except Exception as e:  # pylint: disable=broad-except
            api.output.error(f"{e}")
            log.exception(e)
        return None

    return wrapped


class NoResourceError(Exception):
    """
    No resource found exception
    """


class Application:
    """
    Base Application context class for accessing.
    """

    def __init__(self, output, obj, interactive=False):
        """
        Instantiate the application

        Args:
            output: The outputer object
            obj: A backend object
            interactive: Set interactive to let prompt for user input
        """
        self.output = output
        self.interactive = interactive
        self.obj = obj


class LockableResourceApp(Application):
    """
    Application context class for accessing lockable resources in jenkins.
    """

    @staticmethod
    def from_default(
        *,
        output,
        jenkins_url,
        jenkins_user,
        jenkins_token,
        filter_expr=None,
        interactive=False,
    ):
        """
        Default app creator using dependency injections
        - Instantiate Jenkins object
        - Instantiate LockableResources
        - Instantiate LockableResourceApp

        Args:
            output: The outputer object.
            jenkins_url: The url to jenkins instance
            jenkins_user: The user to authenticate to jenkins
            jenkins_token: The user token to use for authentication
            filter_expr: A filter expression to include only matching patterns of resources
            interactive: Set interactive to let prompt for user input

        Return:
            LockableResourceApp object
        """
        # Instantiate jenkins object
        jenkins = Jenkins(jenkins_url, jenkins_user, jenkins_token, lazy=True)
        mgr = LockableResources(jenkins, res_filter=filter_expr)

        return LockableResourceApp(output, mgr, interactive)

    @api_method
    def reserve(self, name=None, labels=None, force=None):
        """
        Reserve a resource

        Args:
            name: Resource name to match (regex string)
            labels: Resource labels to match (regex string)
            force: Force reserve if already one or more resources owned
        """
        # Issue a warning if you already have one resource owned
        owned = self.obj.get_owned_resources()
        if owned:
            self.output.warn("You already have one resource owned.")
            if force is None:
                if not self.output.confirm("Force reserving?"):
                    return
            elif not force:
                return

        # Find free resources in list
        reslist = self._get_matching_free_resources(name, labels)
        if reslist and not name:
            reslist = reslist[:1]

        if not reslist:
            self.output.warn("Sorry, no free resources at the moment. Try again later.")
            return

        for res in reslist:
            res.reserve()
            self.output.info(f"Reserved {res.name}")

    @api_method
    def unreserve(self, name=None, labels=None):
        """
        Unreserve a resource

        Args:
            name: Resource name to match (regex string)
            labels: Resource labels to match (regex string)
        """
        # Name provided: Find matching resources
        reslist = self._get_matching_resources(name, labels)

        # Find owned resources in list
        reslist = [r for r in reslist if r.is_reserved]

        if not reslist:
            self.output.warn("No resources to release")
            return

        for res in reslist:
            res.unreserve()
            self.output.info(f"Unreserved {res.name}")

    @api_method
    def list(self, name=None, labels=None, state=None, short_name=False):
        """
        List resources

        Args:
            name: Resource name to match (regex string)
            labels: Resource labels to match (regex string)
            state: Match state given (case insensitive)
            short_name: Output to the short name version instead of full hostname
        """
        if state is None:
            is_locked = None
            is_reserved = None
        else:
            is_reserved = state.lower() == "reserved"
            is_locked = state.lower() == "locked"

        for res in self.obj.values(
            name, labels, is_locked=is_locked, is_reserved=is_reserved
        ):
            name = res.name
            if short_name:
                name = name.split(".")[0]
            self.output.info(name)

    @api_method
    def info(self, name=None, labels=None, state=None, reserved_by=None):
        """
        Show info of resources

        Args:
            name: Resource name to match (regex string)
            labels: Resource labels to match (regex string)
            locked: Match state given (case insensitive)
            reserved: Match state given (case insensitive)
            reserved_by: Match owner of resource (string)
        """
        if state is None:
            is_locked = None
            is_reserved = None
        else:
            is_reserved = state.lower() == "reserved"
            is_locked = state.lower() == "locked"

        for res in self.obj.values(
            name=name,
            labels=labels,
            is_locked=is_locked,
            is_reserved=is_reserved,
            reserved_by=reserved_by,
        ):
            state = (
                "LOCKED" if res.is_locked else "RESERVED" if res.is_reserved else "FREE"
            )
            self.output.info(f"{res.name}", nl=False)
            if res.labels:
                labels = ",".join(res.labels)
                self.output.info(f" [{labels}]", nl=False)
            self.output.info(": ", nl=False)
            self.output.info(f"{state}", fg=INFO_STATE_COLORS[state], nl=False)
            if not res.is_free:
                self.output.info(f" by {res.reserved_by}", nl=False)
            self.output.info("")

    @api_method
    def owned(
        self,
        user=None,
        short_name=False,
        count=None,
        index=None,
    ):
        """
        List owned resources

        Args:
            user: Owner of resource
            short_name: Output to the short name version instead of full hostname
            count: the max number of owned resources to return
            index: the owned resource list position to select
        """
        owned = self.obj.get_owned_resources(user)
        count = count or len(owned)
        if index is None:
            index = 0
        else:
            count = 1
        end = index + count

        for res in owned[index:end]:
            name = res.name
            if short_name:
                name = name.split(".")[0]
            self.output.info(name)

    def _get_matching_resources(self, name=r".*", labels=None):
        # Find matchingn resources
        reslist = list(self.obj.values(name, labels))
        if not reslist:
            exprs = []
            if name:
                exprs.append(f"name~=/{name}/")
            if labels:
                exprs.append(f"labels~=/{labels}/")
            raise NoResourceError("No resources matching " + " or ".join(exprs))
        return reslist

    def _get_matching_free_resources(self, name=r".*", labels=None):
        # Find matchingn resources
        reslist = self._get_matching_resources(name, labels)
        # Find free resources in list
        return [r for r in reslist if r.is_free]
