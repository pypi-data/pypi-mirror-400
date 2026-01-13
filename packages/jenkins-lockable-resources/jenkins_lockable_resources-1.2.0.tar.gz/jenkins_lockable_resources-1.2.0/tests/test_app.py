from unittest.mock import MagicMock

import requests

from jenkins_lockable_resources.app import api_method, LockableResourceApp


def _make_conn_error():
    return requests.exceptions.ConnectionError(request=requests.Request(url="URL"))


def test_api_method_connection_error():
    out = MagicMock()

    class C:
        def __init__(self, output):
            self.output = output

        @api_method
        def f(self):
            raise _make_conn_error()

    c = C(out)
    assert c.f() is None
    out.error.assert_called_once_with(
        "Failed to connect to URL. Check your connection and try again."
    )


def test_api_method_generic_exception():
    out = MagicMock()

    class C:
        def __init__(self, output):
            self.output = output

        @api_method
        def f(self):
            raise Exception("boom")

    c = C(out)
    assert c.f() is None
    out.error.assert_called_once_with("boom")


def resource_sampler(
    name, is_free=True, is_locked=False, is_reserved=False, reserved_by="", labels=None
):
    res = MagicMock()
    res.name = name
    res.is_free = is_free
    res.is_locked = is_locked
    res.is_reserved = is_reserved
    res.reserved_by = reserved_by
    res.labels = labels or []
    return res


def resource_manager_sampler(resources, owned_resources=None):
    class Mgr:
        def values(self, *a, **k):
            return iter(resources)

        def get_owned_resources(self, user=None):
            return owned_resources

    mgr = Mgr()

    return mgr


def test_reserve_success_single_free_resource():
    out = MagicMock()
    resource = resource_sampler("res1", is_free=True, is_reserved=False, reserved_by="")
    msgr = resource_manager_sampler([resource])

    app = LockableResourceApp(out, msgr)
    app.reserve()

    resource.reserve.assert_called_once()
    out.info.assert_any_call(f"Reserved {resource.name}")


def test_unreserve_calls_unreserve_on_reserved_resources():
    out = MagicMock()

    resource = resource_sampler(
        "res2",
        is_free=False,
        is_reserved=True,
        reserved_by="user1",
        labels=["l1"],
    )
    mgr = resource_manager_sampler([resource])

    app = LockableResourceApp(out, mgr)
    app.unreserve()

    resource.unreserve.assert_called_once()
    out.info.assert_any_call(f"Unreserved {resource.name}")


def test_info_outputs_state_and_labels():
    out = MagicMock()

    resource = resource_sampler(
        "host.example.com",
        is_free=False,
        is_locked=False,
        is_reserved=True,
        reserved_by="bob",
        labels=["l1", "l2"],
    )
    mgr = resource_manager_sampler([resource])

    app = LockableResourceApp(out, mgr)
    app.info()

    # resource name printed without newline first
    out.info.assert_any_call(resource.name, nl=False)
    # state printed with color
    out.info.assert_any_call(
        "",
    )
