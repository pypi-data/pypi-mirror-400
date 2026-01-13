from unittest.mock import MagicMock, patch, ANY

import click

from jenkins_lockable_resources.main import AppFactory, ClickStreamer, default_streamer


def test_appfactory_create_and_cache():
    # use a MagicMock to verify constructor is called with provided args
    ctor = MagicMock(return_value={"a": 1, "b": 2})

    f = AppFactory(ctor, 1, 2)
    # create app
    app1 = f.app
    app2 = f.app
    assert app1 is app2
    ctor.assert_called_once_with(1, 2)


def test_clickstreamer_calls_secho(mocker):
    secho = MagicMock()

    with patch("click.secho", secho):

        s = ClickStreamer()
        s.info("hello")
        s.warn("problem")
        s.error("bad")
        s.highlight("hi")

    # verify that secho was called and formatted messages exist
    secho.assert_any_call("hello", fg=ANY)
    secho.assert_any_call("WARN: problem", fg=ANY)
    secho.assert_any_call("ERROR: bad", fg=ANY)
    secho.assert_any_call("hi", fg=ANY)

    # default_streamer should be an instance of ClickStreamer
    assert isinstance(default_streamer, ClickStreamer)
