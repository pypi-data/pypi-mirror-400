import datetime
import json
import logging
import uuid
import zoneinfo
from pathlib import Path
from typing import Any

import icalendar
import yaml
from chaos_utils.dict_utils import deep_merge
from lunar_python import Solar

from lunar_birthday_ical.config import default_config
from lunar_birthday_ical.holidays import HOLIDAYS
from lunar_birthday_ical.uploader import GitHubGistUploader, PastebinWorkerUploader
from lunar_birthday_ical.utils import (
    get_future_solar_datetime,
    get_local_datetime,
    local_datetime_to_utc_datetime,
)

logger = logging.getLogger(__name__)


class SafeDict(dict):
    """Dictionary that returns the key itself when missing."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


class LunarCalendarApp:
    """Generates iCalendar files from configuration."""

    def __init__(self, config_path: Path) -> None:
        """Initialize the generator with a configuration file.

        Args:
            config_path: Path to the YAML configuration file.
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.calendar = icalendar.Calendar()
        self._init_calendar()

    def generate(self) -> None:
        """Generate calendar events based on configuration."""
        global_config = self.config.get("global", {})

        for item in self.config.get("events", []):
            item_config = deep_merge(global_config, item)
            event_keys = item_config.get("event_keys", [])

            if "integer_days" in event_keys:
                self._add_integer_days_event(item_config)

            self._add_birthday_event(item_config)

        self._add_holiday_event(global_config)

    def save(self) -> Path:
        """Save the generated calendar to a file.

        Returns:
            Path to the saved .ics file.
        """
        calendar_data = self.calendar.to_ical()
        output = self.config_path.with_suffix(".ics")
        with output.open("wb") as f:
            f.write(calendar_data)
        logger.info("iCal saved to %s", output)
        return output

    def upload(self, file_path: Path) -> None:
        """Upload the calendar file to configured services.

        Args:
            file_path: Path to the calendar file to upload.
        """
        self._upload_to_pastebin(file_path)
        self._upload_to_github_gist(file_path)

    def _upload_to_pastebin(self, file_path: Path) -> None:
        """Upload to Pastebin if enabled."""
        pastebin_config = self.config.get("pastebin", {})
        if pastebin_config.get("enabled", False):
            try:
                uploader = PastebinWorkerUploader(pastebin_config)
                result = uploader.upload(file_path)
                if "manageUrl" in result:
                    logger.info(
                        "Add 'manage_url: %s' to your config file to update this paste in the future",
                        result["manageUrl"],
                    )
            except Exception as e:
                logger.error("Failed to upload to pastebin: %s", e)

    def _upload_to_github_gist(self, file_path: Path) -> None:
        """Upload to GitHub Gist if enabled."""
        gist_config = self.config.get("github_gist", {})
        if gist_config.get("enabled", False):
            try:
                uploader = GitHubGistUploader(gist_config)
                result = uploader.upload(file_path)
                # Log the gist_id for future updates
                if "id" in result:
                    logger.info(
                        "Add 'gist_id: %s' to your config file to update this gist in the future",
                        result["id"],
                    )
            except Exception as e:
                logger.error("Failed to upload to GitHub Gist: %s", e)

    def _load_config(self) -> dict:
        """Load and merge configuration."""
        with open(self.config_path, "r") as f:
            yaml_config = yaml.safe_load(f)
            merged_config = deep_merge(default_config, yaml_config)
            logger.debug(
                "merged_config=%s",
                json.dumps(merged_config, ensure_ascii=False, default=str),
            )
        return merged_config

    def _init_calendar(self) -> None:
        """Initialize the calendar object with metadata."""
        global_config = self.config.get("global", {})
        calendar_name = self.config_path.stem
        timezone = zoneinfo.ZoneInfo(global_config.get("timezone"))

        self.calendar.add("PRODID", "-//ak1ra-lab//lunar-birthday-ical//EN")
        self.calendar.add("VERSION", "2.0")
        self.calendar.add("CALSCALE", "GREGORIAN")
        self.calendar.add("X-WR-CALNAME", calendar_name)
        self.calendar.add("X-WR-TIMEZONE", timezone)

    def _add_event(
        self,
        dtstart: datetime.datetime,
        dtend: datetime.datetime,
        summary: str,
        description: str,
        reminders: list[int | datetime.datetime],
        attendees: list[str],
    ) -> None:
        """Add a single event to the calendar."""
        event = icalendar.Event()
        event.add("uid", uuid.uuid4())
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        event.add("dtstamp", icalendar.vDatetime(now_utc))
        event.add("dtstart", icalendar.vDatetime(dtstart))
        event.add("dtend", icalendar.vDatetime(dtend))
        event.add("summary", summary)
        event.add("description", description)

        self._add_reminders_to_event(event, reminders, summary)
        self._add_attendees_to_event(event, attendees)

        self.calendar.add_component(event)

    def _add_reminders_to_event(
        self,
        event: icalendar.Event,
        reminders: list[int | datetime.datetime],
        summary: str,
    ) -> None:
        # 添加提醒
        for reminder_days in reminders:
            if isinstance(reminder_days, datetime.datetime):
                trigger_time = reminder_days
            elif isinstance(reminder_days, int):
                trigger_time = datetime.timedelta(days=-reminder_days)
            else:
                continue
            alarm = icalendar.Alarm()
            alarm.add("uid", uuid.uuid4())
            alarm.add("action", "DISPLAY")
            alarm.add("description", f"Reminder: {summary}")
            alarm.add("trigger", trigger_time)
            event.add_component(alarm)

    def _add_attendees_to_event(
        self, event: icalendar.Event, attendees: list[str]
    ) -> None:
        # 添加与会者
        for attendee_email in attendees:
            attendee = icalendar.vCalAddress(f"mailto:{attendee_email}")
            attendee.params["cn"] = icalendar.vText(attendee_email.split("@")[0])
            attendee.params["role"] = icalendar.vText("REQ-PARTICIPANT")
            event.add("attendee", attendee)

    def _add_integer_days_event(self, item_config: dict) -> None:
        """Add integer days events (e.g. 10000 days old)."""
        timezone = zoneinfo.ZoneInfo(item_config.get("timezone"))
        start_date = item_config.get("start_date")
        event_time = item_config.get("event_time")
        start_datetime = get_local_datetime(start_date, event_time, timezone)
        event_hours = datetime.timedelta(hours=item_config.get("event_hours"))

        name = item_config.get("name")
        year_start = item_config.get("year_start") or datetime.date.today().year
        year_end = item_config.get("year_end")

        days_max = item_config.get("days_max")
        days_interval = item_config.get("days_interval")

        integer_days_summary = "{name} 降临地球🌏已经 {days} 天啦!"
        integer_days_description = (
            "{name} 降临地球🌏已经 {days} 天啦! (age: {age}, birthday: {birthday})"
        )
        summary = item_config.get("summary") or integer_days_summary
        description = item_config.get("description") or integer_days_description

        for days in range(days_interval, days_max + 1, days_interval):
            event_datetime = start_datetime + datetime.timedelta(days=days)
            if event_datetime.year < year_start or event_datetime.year > year_end:
                continue

            dtstart = local_datetime_to_utc_datetime(event_datetime)
            dtend = dtstart + event_hours
            year_average = 365.25
            age = round(days / year_average, 2)

            reminders_datetime = [
                dtstart - datetime.timedelta(days=d)
                for d in item_config.get("reminders")
            ]
            self._add_event(
                dtstart=dtstart,
                dtend=dtend,
                summary=self._safe_format(summary, name=name, days=days),
                description=self._safe_format(
                    description, name=name, days=days, age=age, birthday=start_date
                ),
                reminders=reminders_datetime,
                attendees=item_config.get("attendees"),
            )

    def _add_birthday_event(self, item_config: dict) -> None:
        """Add birthday events (solar and lunar)."""
        timezone = zoneinfo.ZoneInfo(item_config.get("timezone"))
        start_date = item_config.get("start_date")
        event_time = item_config.get("event_time")
        start_datetime = get_local_datetime(start_date, event_time, timezone)
        start_datetime_in_lunar = Solar.fromDate(start_datetime).getLunar()
        event_hours = datetime.timedelta(hours=item_config.get("event_hours"))

        name = item_config.get("name")
        year_start = item_config.get("year_start") or datetime.date.today().year
        year_end = item_config.get("year_end")

        for event_key in item_config.get("event_keys") or []:
            if event_key not in ["solar_birthday", "lunar_birthday"]:
                continue

            if event_key == "solar_birthday":
                birthday = start_date
                birthday_summary = "{name} {year} 年生日🎂快乐!"
                birthday_description = (
                    "{name} {year} 年生日🎂快乐! (age: {age}, birthday: {birthday})"
                )
            elif event_key == "lunar_birthday":
                birthday = start_datetime_in_lunar
                birthday_summary = "{name} {year} 年农历生日🎂快乐!"
                birthday_description = (
                    "{name} {year} 年农历生日🎂快乐! (age: {age}, birthday: {birthday})"
                )

            summary = item_config.get("summary") or birthday_summary
            description = item_config.get("description") or birthday_description

            for year in range(year_start, year_end + 1):
                age = year - start_datetime.year
                if event_key == "solar_birthday":
                    event_datetime = start_datetime.replace(year=year)
                elif event_key == "lunar_birthday":
                    event_datetime = get_future_solar_datetime(start_datetime, year)

                dtstart = local_datetime_to_utc_datetime(event_datetime)
                dtend = dtstart + event_hours
                reminders_datetime = [
                    dtstart - datetime.timedelta(days=d)
                    for d in item_config.get("reminders")
                ]
                self._add_event(
                    dtstart=dtstart,
                    dtend=dtend,
                    summary=self._safe_format(
                        summary,
                        name=name,
                        year=year,
                    ),
                    description=self._safe_format(
                        description,
                        name=name,
                        year=year,
                        age=age,
                        birthday=birthday,
                    ),
                    reminders=reminders_datetime,
                    attendees=item_config.get("attendees"),
                )

    def _add_holiday_event(self, global_config: dict) -> None:
        """Add public holiday events."""
        timezone = zoneinfo.ZoneInfo(global_config.get("timezone"))
        event_time = global_config.get("event_time")
        event_hours = datetime.timedelta(hours=global_config.get("event_hours"))

        year_start = global_config.get("year_start")
        year_end = global_config.get("year_end")

        for holiday_key, holiday in HOLIDAYS.items():
            if holiday_key not in global_config.get("holiday_keys") or []:
                continue

            for year in range(year_start, year_end + 1):
                event_date = holiday.get_date(year)
                event_datetime = get_local_datetime(event_date, event_time, timezone)
                dtstart = local_datetime_to_utc_datetime(event_datetime)
                dtend = dtstart + event_hours
                reminders_datetime = [
                    dtstart - datetime.timedelta(days=d)
                    for d in global_config.get("reminders")
                ]
                self._add_event(
                    dtstart=dtstart,
                    dtend=dtend,
                    summary=holiday.summary,
                    description=holiday.description,
                    reminders=reminders_datetime,
                    attendees=global_config.get("attendees"),
                )

    def _safe_format(self, template: str, **kwargs: Any) -> str:
        """Safely format a string with given arguments.

        Missing keys in the template will be preserved as is.
        """
        return template.format_map(SafeDict(**kwargs))
