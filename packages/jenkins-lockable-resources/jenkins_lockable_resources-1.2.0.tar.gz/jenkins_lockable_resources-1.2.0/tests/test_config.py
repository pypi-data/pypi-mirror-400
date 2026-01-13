import yaml

from jenkins_lockable_resources.config import Config, ConfigLoader


def test_config_update_merge_dicts():
    c = Config({"a": {"x": 1}, "b": [1, 2]}, policy="overwrite")
    c.update({"a": {"y": 2}, "b": [3], "c": 4})
    assert c["a"]["x"] == 1
    assert c["a"]["y"] == 2
    assert c["b"] == [3]
    assert c["c"] == 4


def test_config_update_type_mismatch_strict():
    c = Config({"a": 1}, policy="strict")
    try:
        c.update({"a": {"x": 1}})
        assert False, "should have raised TypeError"
    except TypeError:
        pass


def test_config_loader_reads_files(tmp_path, monkeypatch):
    # create two temp yaml files
    f1 = tmp_path / "one.yml"
    f2 = tmp_path / "two.yml"
    f1.write_text(yaml.safe_dump({"cmd": {"param1": "v1"}}))
    f2.write_text(yaml.safe_dump({"cmd": {"param2": "v2"}}))

    loader = ConfigLoader([str(f1), str(f2)])
    conf = loader.conf
    assert "cmd" in conf
    assert conf["cmd"]["param1"] == "v1"
    assert conf["cmd"]["param2"] == "v2"

    # click_settings should return a dict containing default_map
    cs = loader.click_settings
    assert isinstance(cs, dict)
    assert "default_map" in cs
