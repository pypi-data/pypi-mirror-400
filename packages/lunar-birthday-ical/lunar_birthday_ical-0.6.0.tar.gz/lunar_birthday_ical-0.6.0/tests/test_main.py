import sys
from pathlib import Path

import pytest
import yaml
from chaos_utils.dict_utils import deep_merge

from lunar_birthday_ical.config import default_config, tests_config
from lunar_birthday_ical.main import main


def test_main_no_args(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    with pytest.raises(SystemExit) as excinfo:
        main()
        assert excinfo.value.code == 0


def test_main_single_config_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    calendar_name = "test-calendar"
    config_file = tmp_path / f"{calendar_name}.yaml"
    config = deep_merge(default_config, tests_config)
    config_file.write_text(yaml.safe_dump(config))
    expected_output_file = config_file.with_suffix(".ics")

    monkeypatch.setattr(sys, "argv", ["main.py", str(config_file)])
    main()

    assert expected_output_file.exists()


def test_main_multiple_config_files(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    calendar_name = "test-calendar"
    config_file = tmp_path / f"{calendar_name}.yaml"
    config = deep_merge(default_config, tests_config)
    config_file.write_text(yaml.safe_dump(config))
    expected_output_file = config_file.with_suffix(".ics")

    monkeypatch.setattr(sys, "argv", ["main.py", str(config_file), str(config_file)])
    main()

    assert expected_output_file.exists()


def test_main_lunar_to_solar(monkeypatch: pytest.MonkeyPatch):
    lunar_date = (2020, 1, 1)
    monkeypatch.setattr(
        sys, "argv", ["main.py", "--lunar-to-solar", *(str(x) for x in lunar_date)]
    )

    with pytest.raises(SystemExit) as excinfo:
        main()
        assert excinfo.value.code == 0


def test_main_solar_to_lunar(monkeypatch: pytest.MonkeyPatch):
    solar_date = (2020, 1, 25)
    monkeypatch.setattr(
        sys, "argv", ["main.py", "--solar-to-lunar", *(str(x) for x in solar_date)]
    )

    with pytest.raises(SystemExit) as excinfo:
        main()
        assert excinfo.value.code == 0


def test_main_lunar_leap_month_to_solar(monkeypatch: pytest.MonkeyPatch):
    lunar_date = (2020, -4, 1)
    monkeypatch.setattr(
        sys, "argv", ["main.py", "--lunar-to-solar", *(str(x) for x in lunar_date)]
    )

    with pytest.raises(SystemExit) as excinfo:
        main()
        assert excinfo.value.code == 0
