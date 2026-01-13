default_config = {
    "global": {
        "timezone": "Asia/Shanghai",
        "holiday_keys": [],
        "year_start": 2025,
        "year_end": 2030,
        "days_max": 30000,
        "days_interval": 1000,
        "event_keys": [],
        "event_time": "10:00:00",
        "event_hours": 2,
        "reminders": [1, 3],
        "attendees": [],
    },
    "pastebin": {
        "enabled": False,
        "base_url": "https://komj.uk",
        "expiration": "",
        "manage_url": "",
    },
    "github_gist": {
        "enabled": False,
        "token": "",
        "gist_id": "",
        "description": "Lunar Birthday iCalendar",
        "public": False,
    },
    "events": [],
}

tests_config = {
    "events": [
        {
            "name": "张三",
            "start_date": "1989-06-03",
            "event_keys": ["lunar_birthday"],
        },
        {
            "name": "李四",
            "start_date": "2006-02-01",
            "event_keys": ["integer_days", "solar_birthday"],
        },
    ],
}

tests_config_overwride_global = {
    "global": {
        "timezone": "America/Los_Angeles",
    },
    "events": [
        {
            "name": "张三",
            "start_date": "1989-06-03",
            "event_keys": ["lunar_birthday"],
        },
        {
            "name": "李四",
            "start_date": "2006-02-01",
            "event_keys": ["integer_days", "solar_birthday"],
        },
    ],
}
