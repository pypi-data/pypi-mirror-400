from pathlib import Path

import yaml
from chaos_utils.dict_utils import deep_merge
from icalendar import Calendar, Event, vCalAddress, vText

from lunar_birthday_ical.calendar import LunarCalendarApp
from lunar_birthday_ical.config import (
    default_config,
    tests_config,
    tests_config_overwride_global,
)


def test_add_reminders_to_event():
    event = Event()
    reminders = [1, 2]
    summary = "Test Event"
    LunarCalendarApp._add_reminders_to_event(None, event, reminders, summary)
    assert len(event.subcomponents) == 2


def test_add_attendees_to_event_one():
    event = Event()
    attendees = ["test@example.com"]
    LunarCalendarApp._add_attendees_to_event(None, event, attendees)
    assert (
        len(
            [event.get("ATTENDEE")]
            if isinstance(event.get("ATTENDEE"), vCalAddress)
            else event.get("ATTENDEE")
        )
        == 1
    )


def test_add_attendees_to_event_multi():
    event = Event()
    attendees = ["test@example.com", "test@example.net"]
    LunarCalendarApp._add_attendees_to_event(None, event, attendees)
    assert (
        len(
            [event.get("ATTENDEE")]
            if isinstance(event.get("ATTENDEE"), vCalAddress)
            else event.get("ATTENDEE")
        )
        == 2
    )


def test_create_calendar(tmp_path: Path):
    calendar_name = "test-calendar"
    config_file = tmp_path / f"{calendar_name}.yaml"

    config = deep_merge(default_config, tests_config)
    config_file.write_text(yaml.safe_dump(config))
    expected_output_file = config_file.with_suffix(".ics")

    app = LunarCalendarApp(config_file)
    app.generate()
    app.save()

    assert expected_output_file.exists()
    assert expected_output_file.exists()

    with expected_output_file.open("rb") as f:
        calendar_data = f.read()
    calendar = Calendar.from_ical(calendar_data)
    assert len(calendar.subcomponents) > 0
    assert calendar.get("X-WR-CALNAME") == calendar_name


def test_create_calendar_with_override_timezone(tmp_path: Path):
    calendar_name = "test-calendar-override-global"
    config_file = tmp_path / f"{calendar_name}.yaml"

    config = deep_merge(default_config, tests_config_overwride_global)
    config_file.write_text(yaml.safe_dump(config))
    expected_output_file = config_file.with_suffix(".ics")

    app = LunarCalendarApp(config_file)
    app.generate()
    app.save()

    assert expected_output_file.exists()

    with expected_output_file.open("rb") as f:
        calendar_data = f.read()
    calendar = Calendar.from_ical(calendar_data)

    assert len(calendar.subcomponents) > 0
    assert calendar.get("X-WR-CALNAME") == calendar_name
    assert calendar.get("X-WR-TIMEZONE") == vText(b"America/Los_Angeles")
