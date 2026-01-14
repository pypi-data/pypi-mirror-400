# CQCalendar v1.4.0
CQCalendar is a customizable, tick-based time and calendar system for Python games and simulations.

It is designed for RPGs, sandbox sims, and systemic games, where time drives world behavior rather than just displaying a UI clock.

CQCalendar supports custom calendars, custom lunar cycles, and advanced moon phase configuration, making it suitable for fantasy, sci-fi, and procedural worlds.

***
## Features
* Tick-based and absolute time progression
* Fully custom calendar support
* Custom month names & day counts
* Custom weekday names
* Optional Gregorian leap year logic
* Custom synodic lunar cycle (length of moon cycle)
* Custom moon phases (names, ranges, & colors)
* Moon illumination calculation
* Full calendar preset JSON import/export
* Lunar phase-only JSON import/export
* Day/Night helper functions (is_night / is_day)
* Event callbacks for hour/day/month/year changes
* Designed for decoupled, systemic game logic
* No external dependencies

***
## Installation
You can install CQCalendar using [pip](https://pypi.org/project/cqcalendar/).

```
pip install cqcalendar
```
***

## How to Create a Calendar for Your Game
```
import cqcalendar

calendar = cqcalendar.CQCalendar(
	hour=9,
	minute=0,
	is_pm=False,
	minutes_per_tick=1,
	day=1,
	month=1,
	year=1,
	weekday=0,
	months=[
		{"name": "Frostwane", "days": 31},
		{"name": "Emberfall", "days": 28},
		{"name": "Stonewake", "days": 31},
	],
	weekdays=["Firstday", "Secondday", "Thirdday", "Fourthday"],
	synodic_month_days=20.0,
	use_gregorian_leap_years=False,
)
```

***
## Time

### How to Display Current Time
```
print(calendar.time_string())
```

### How to Change Time
```
calendar.set_time(hour=12, minute=0, is_pm=True)
```

### How to Increment Time
```
calendar.update(ticks=10)
```

***
## Date

### How to Display Current Date
```
print(calendar.date_string())
```

### How to Change Date
```
calendar.set_date(day=31, month=12, year=1)
```
***

## Absolute Time Advancement
You can advance time directly without ticks.

```
calendar.add_minutes(30)
calendar.add_hours(6)
calendar.add_days(1)
calendar.add_months(1)
calendar.add_years(1)
```

Or you can do it in a single method.

```
calendar.add(days=3, hours=4)
```

***
## Weekdays
Weekdays are zero-indexed (0 = Monday, 6 = Sunday).

### How to Display Weekday
```
print(calendar.weekday_name())
```

### How to Change Weekday
```
calendar.set_weekday(weekday=1)
```

***
## Lunar Cycle
CQCalendar includes a synodic lunar cycle (approximately 29.53 days)

### How to Display Moon Phase
```
print(calendar.moon_phase_name())
```

### How to Set Moon Phase
```
calendar.set_moon_phase("Waning Crescent")
```

The above is an alternative to using ```moon_age_days```:
```
# Precise numeric control still supported
calendar = CQCalendar(moon_age_days=14.77) # Full Moon
```

If both ```moon_phase``` and ```moon_age_days``` are provided, ```moon_phase``` takes priority.

### How to Get Moon Illumination
```
print(calendar.moon_illumination())
```

Useful for:
* werewolf systems
* rituals
* night visibility
* tides or magic strength

### Custom Moon Phases
```
moon_phases = [
	{"name": "New Moon", "start": 0.00, "end": 0.10, "color_hex": "#000000"},
	{"name": "Waxing Crescent", "start": 0.10, "end": 0.25, "color_hex": "#aaaaaa"},
	{"name": "Blood Moon", "start": 0.45, "end": 0.55, "color_hex": "#ff0000"},
]

calendar = cqcalendar.CQCalendar(
	moon_phases=moon_phases,
	synodic_month_days=20.0,
)
```
### Get Moon Color
```
print(calendar.moon_color_hex())
print(calendar.moon_color_rgb())

```

### Lunar Phase JSON Import / Export
CQCalendar supports importing and exporting lunar phase definitions via JSON.

```
calendar.export_lunar_phases_json("lunar_phases.json")
```

```
calendar.import_lunar_phases_json("lunar_phases.json")
```
This allows CQCalendar to interoperate cleanly with tools such as [MoonTex](https://github.com/BriannaLadson/MoonTex) and future editors.

***
## Day / Night Helpers
CQCalendar includes helper functions to determine whether the current time is within a night window.

This is useful for day/night cycles and showing moon textures (e.g. when using CQCalendar with MoonTex).

### Check If It's Night
Default night window: 7:00 PM → 6:00 AM

```
print(calendar.is_night())

```

### Use a Custom Night Window
Example: 8:00 PM → 5:00 AM
```
print(calendar.is_night(
	night_start_hour=8,
	night_start_is_pm=True,
	night_end_hour=5,
	night_end_is_pm=False,
))

```

### Check If It's Day
```
print(calendar.is_day())
```


***
## Callbacks (Events)
CQCalendar allows systems to react to time changes using callbacks.

Callbacks are triggered when time crosses a boundary (hour/day/month/year), not continuously.

### Hourly Event
```
def restock_shops(calendar):
  if calendar.hour == 6 and not calendar.is_pm:
    print("Shops restocked!")

calendar.on_hour(restock_shops)
```

### Daily Event
```
def payday(calendar):
  if calendar.day == 1:
    print("Rent is due!")

calendar.on_day(payday)
```

Available callbacks:
* on_hour
* on_day
* on_month
* on_year

***
## Full Calendar Preset
CQCalendar can export all settings - time, date, calendar, and lunar - to one JSON file.

### Export Full Preset
```
calendar.export_settings_json("my_calendar.json")
```

### Import Full Preset
```
calendar.import_settings_json("my_calendar.json")
```

***
## Misc.

### How to Display Current Date and Time
```
print(calendar.datetime_string())
```

### Check Leap Year
```
print(calendar.is_leap_year())
```

### Internal Representation
```
print(repr(calendar))
```

***
## Related Tools
* CQCalendar Studio: Visual calendar editor (coming soon)

***
## Related Libraries
* [TerraForge](https://github.com/BriannaLadson/TerraForge): A versatile Python toolset for procedural map generation.
* [MoonTex](https://github.com/BriannaLadson/MoonTex): A noise-based texture generator that creates realistic grayscale moon phase images.
