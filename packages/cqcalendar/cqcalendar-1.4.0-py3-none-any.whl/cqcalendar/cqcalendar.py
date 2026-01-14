__version__ = "1.4.0"

import json
import os
import math

class CQCalendar:
	def __init__(
		self,
		hour=9,
		minute=0,
		is_pm=False,
		minutes_per_tick=1,
		day=1,
		month=1,
		year=1,
		weekday=0,
		moon_age_days=0.0,
		moon_phase=None,
		debug_callbacks=False,
		months=None,
		weekdays=None,
		synodic_month_days=29.530588,
		use_gregorian_leap_years=True,
		moon_phases=None,
	):
		self.minutes_per_tick = max(1, int(minutes_per_tick))

		self.use_gregorian_leap_years = bool(use_gregorian_leap_years)

		# Months (customizable)
		if months is None:
			self.months = [
				("January", 31),
				("February", 28),
				("March", 31),
				("April", 30),
				("May", 31),
				("June", 30),
				("July", 31),
				("August", 31),
				("September", 30),
				("October", 31),
				("November", 30),
				("December", 31),
			]
		else:
			normalized = []
			for m in months:
				if isinstance(m, dict):
					name = str(m["name"])
					days = int(m["days"])
					normalized.append((name, days))
				else:
					name, days = m
					normalized.append((str(name), int(days)))
			self.months = normalized

		# Weekdays (customizable)
		if weekdays is None:
			self.weekdays = [
				"Monday",
				"Tuesday",
				"Wednesday",
				"Thursday",
				"Friday",
				"Saturday",
				"Sunday",
			]
		else:
			self.weekdays = [str(w) for w in weekdays]

		# Callbacks
		self._on_hour = []
		self._on_day = []
		self._on_month = []
		self._on_year = []

		# Moon system (customizable)
		self.synodic_month_days = float(synodic_month_days)
		if self.synodic_month_days <= 0:
			raise ValueError("synodic_month_days must be > 0")

		self.moon_age_days = float(moon_age_days) % self.synodic_month_days

		if moon_phases is None:
			self.moon_phases = self._default_moon_phases()
		else:
			self.moon_phases = self._normalize_moon_phases(moon_phases)

		# Apply initial time/date/weekday
		self.set_time(hour=hour, minute=minute, is_pm=is_pm)
		self.set_date(day=day, month=month, year=year)
		self.set_weekday(weekday)

		self.debug_callbacks = bool(debug_callbacks)

		# Backward-compatible: allow setting a moon phase by name/index on init
		if moon_phase is not None:
			self.set_moon_phase(moon_phase)

	def __repr__(self):
		return f"<CQCalendar {self.date_string()} {self.time_string()}>"

	def on_hour(self, callback):
		self._on_hour.append(callback)
		return callback

	def on_day(self, callback):
		self._on_day.append(callback)
		return callback

	def on_month(self, callback):
		self._on_month.append(callback)
		return callback

	def on_year(self, callback):
		self._on_year.append(callback)
		return callback

	def off_hour(self, callback):
		if callback in self._on_hour:
			self._on_hour.remove(callback)

	def off_day(self, callback):
		if callback in self._on_day:
			self._on_day.remove(callback)

	def off_month(self, callback):
		if callback in self._on_month:
			self._on_month.remove(callback)

	def off_year(self, callback):
		if callback in self._on_year:
			self._on_year.remove(callback)

	def _emit(self, callbacks):
		for cb in list(callbacks):
			try:
				cb(self)
			except Exception:
				if self.debug_callbacks:
					raise
					
	def set_time(self, hour=9, minute=0, is_pm=False):
		hour = int(hour)
		minute = int(minute)

		if hour < 1: hour = 1
		if hour > 12: hour = 12

		if minute < 0: minute = 0
		if minute > 59: minute = 59

		self.hour = hour
		self.minute = minute
		self.is_pm = bool(is_pm)

	def set_date(self, day=1, month=1, year=1):
		month = int(month)
		day = int(day)
		year = int(year)

		month = max(1, min(month, len(self.months)))
		year = max(1, year)

		days_in_month = self.days_in_month(month, year)
		day = max(1, min(day, days_in_month))

		self.day = day
		self.month = month
		self.year = year

	def set_weekday(self, weekday=0):
		if weekday is None:
			weekday = 0
		self.weekday = int(weekday) % len(self.weekdays)

	def update(self, ticks=1):
		self.add_minutes(int(ticks) * self.minutes_per_tick)

	def add_minutes(self, minutes: int):
		minutes = int(minutes)

		if minutes == 0:
			return

		if minutes < 0:
			raise ValueError("add_minutes does not support negative values.")

		# Moon progression by real elapsed minutes
		self.advance_moon_by_minutes(minutes)

		self.minute += minutes

		while self.minute >= 60:
			self.minute -= 60
			self.advance_hour()

	def add_hours(self, hours: int):
		hours = int(hours)

		if hours == 0:
			return

		if hours < 0:
			raise ValueError("add_hours does not support negative values.")

		self.add_minutes(hours * 60)

	def add_days(self, days: int):
		days = int(days)

		if days == 0:
			return

		if days < 0:
			raise ValueError("add_days does not support negative values.")

		# Moon progression by real elapsed minutes
		self.advance_moon_by_minutes(days * 24 * 60)

		for _ in range(days):
			self.advance_day()

	def add_months(self, months: int):
		months = int(months)

		if months == 0:
			return

		if months < 0:
			raise ValueError("add_months does not support negative values.")

		for _ in range(months):
			self.advance_month()

		self.clamp_day_to_month()

	def add_years(self, years: int):
		years = int(years)

		if years == 0:
			return

		if years < 0:
			raise ValueError("add_years does not support negative values.")

		self.year += years
		self.clamp_day_to_month()

	def add(self, minutes=0, hours=0, days=0, months=0, years=0):
		if years: self.add_years(years)
		if months: self.add_months(months)
		if days: self.add_days(days)
		if hours: self.add_hours(hours)
		if minutes: self.add_minutes(minutes)

	def advance_hour(self):
		if self.hour == 11:
			self.hour = 12
			self.is_pm = not self.is_pm

			# 11AM -> 12PM (no day change)
			# 11PM -> 12AM (day change)
			if not self.is_pm:
				self.advance_day()

		elif self.hour == 12:
			self.hour = 1
		else:
			self.hour += 1

		self._emit(self._on_hour)

	def advance_day(self):
		days_in_month = self.days_in_month(self.month, self.year)

		self.day += 1

		if self.day > days_in_month:
			self.day = 1
			self.advance_month()

		self.weekday = (self.weekday + 1) % len(self.weekdays)

		self._emit(self._on_day)

	def advance_month(self):
		self.month += 1

		if self.month > len(self.months):
			self.month = 1
			self.advance_year()

		self.clamp_day_to_month()

		self._emit(self._on_month)

	def advance_year(self):
		self.year += 1
		self._emit(self._on_year)

	def advance_moon_by_minutes(self, minutes: int):
		days = minutes / (60.0 * 24.0)
		self.moon_age_days = (self.moon_age_days + days) % self.synodic_month_days

	def set_moon_phase_fraction(self, frac: float):
		frac = float(frac) % 1.0
		self.moon_age_days = frac * self.synodic_month_days

	def moon_phase_info(self):
		if not self.moon_phases:
			self.moon_phases = self._default_moon_phases()

		frac = self.moon_age_days / self.synodic_month_days

		for phase in self.moon_phases:
			start = phase.get("start", 0.0)
			end = phase.get("end", 1.0)

			# Normal range
			if start <= end:
				if start <= frac < end:
					return phase
			# Wrap-around range
			else:
				if frac >= start or frac < end:
					return phase

		return self.moon_phases[0]

	def moon_phase_name(self):
		info = self.moon_phase_info()
		return info.get("name", "")

	def moon_color_hex(self):
		info = self.moon_phase_info()
		return info.get("color_hex", "#ffffff")

	def moon_color_rgb(self):
		info = self.moon_phase_info()
		return info.get("color_rgb", (255, 255, 255))

	def moon_illumination(self):
		phase_angle = (self.moon_age_days / self.synodic_month_days) * 2.0 * math.pi
		return 0.5 * (1.0 - math.cos(phase_angle))

	def set_moon_phase(self, phase_name_or_index):
		# Backward-compatible behavior:
		# - if string: match a phase "name"
		# - else: treat as index into moon_phases list
		if not self.moon_phases:
			self.moon_phases = self._default_moon_phases()

		if isinstance(phase_name_or_index, str):
			target = phase_name_or_index.strip()
			names = [p.get("name", "") for p in self.moon_phases]

			# Try exact match first
			if target in names:
				idx = names.index(target)
			else:
				# Try case-insensitive match
				lower_names = [n.lower() for n in names]
				if target.lower() not in lower_names:
					raise ValueError(f"Invalid phase name: {phase_name_or_index}")
				idx = lower_names.index(target.lower())
		else:
			idx = int(phase_name_or_index) % len(self.moon_phases)

		# Set to the midpoint of that phase range
		phase = self.moon_phases[idx]
		start = float(phase.get("start", 0.0))
		end = float(phase.get("end", 1.0))

		if start <= end:
			mid = (start + end) / 2.0
		else:
			# Wrap-around: treat as two segments [start,1) U [0,end)
			span = (1.0 - start) + end
			mid = (start + (span / 2.0)) % 1.0

		self.set_moon_phase_fraction(mid)
		return self.moon_age_days

	def _default_moon_phases(self):
		return [
			{"name": "New Moon", "start": 0.00, "end": 0.0625, "color_hex": "#000000", "color_rgb": (0, 0, 0)},
			{"name": "Waxing Crescent", "start": 0.0625, "end": 0.1875, "color_hex": "#ffffff", "color_rgb": (255, 255, 255)},
			{"name": "First Quarter", "start": 0.1875, "end": 0.3125, "color_hex": "#ffffff", "color_rgb": (255, 255, 255)},
			{"name": "Waxing Gibbous", "start": 0.3125, "end": 0.4375, "color_hex": "#ffffff", "color_rgb": (255, 255, 255)},
			{"name": "Full Moon", "start": 0.4375, "end": 0.5625, "color_hex": "#ffffff", "color_rgb": (255, 255, 255)},
			{"name": "Waning Gibbous", "start": 0.5625, "end": 0.6875, "color_hex": "#ffffff", "color_rgb": (255, 255, 255)},
			{"name": "Last Quarter", "start": 0.6875, "end": 0.8125, "color_hex": "#ffffff", "color_rgb": (255, 255, 255)},
			{"name": "Waning Crescent", "start": 0.8125, "end": 1.00, "color_hex": "#ffffff", "color_rgb": (255, 255, 255)},
		]

	def _normalize_moon_phases(self, phases):
		normalized = []

		for p in phases:
			if not isinstance(p, dict):
				continue

			name = str(p.get("name", ""))

			start = float(p.get("start", 0.0))
			end = float(p.get("end", 1.0))

			if start < 0.0: start = 0.0
			if start >= 1.0: start = start % 1.0

			if end <= 0.0: end = 0.0
			if end > 1.0: end = 1.0

			color_hex = p.get("color_hex", "#ffffff")
			color_rgb = p.get("color_rgb", (255, 255, 255))
			
			if isinstance(color_rgb, list):
				color_rgb = tuple(color_rgb)

			normalized.append({
				"name": name,
				"start": start,
				"end": end,
				"color_hex": color_hex,
				"color_rgb": color_rgb,
			})

		if not normalized:
			return self._default_moon_phases()

		return normalized
		
	def export_settings_json(self, path_or_none=None, indent=2):
		"""
		Exports the full calendar configuration (time, date, calendar, lunar)
		to a single JSON preset.

		Schema:
		{
			"schema": "cqcalendar.settings",
			"schema_version": 1,
			...
		}
		"""
		
		phases = list(self.moon_phases) if self.moon_phases else self._default_moon_phases()
		for p in phases:
			if isinstance(p, dict) and isinstance(p.get("color_rgb"), tuple):
				p["color_rgb"] = list(p["color_rgb"])
		
		payload = {
			"schema": "cqcalendar.settings",
			"schema_version": 1,
			"version": __version__,

			"time": {
				"hour": self.hour,
				"minute": self.minute,
				"is_pm": self.is_pm,
				"minutes_per_tick": self.minutes_per_tick,
			},

			"date": {
				"day": self.day,
				"month": self.month,
				"year": self.year,
				"weekday": self.weekday,
			},

			"calendar": {
				"months": [
					{"name": name, "days": days}
					for name, days in self.months
				],
				"weekdays": list(self.weekdays),
				"use_gregorian_leap_years": self.use_gregorian_leap_years,
			},

			"lunar": {
				"synodic_month_days": float(self.synodic_month_days),
				"moon_age_days": float(self.moon_age_days),
				"moon_phases": phases,
			},
		}

		text = json.dumps(payload, indent=indent)

		if path_or_none:
			with open(str(path_or_none), "w", encoding="utf-8") as f:
				f.write(text)

		return text
		
	def import_settings_json(self, path_or_json_text):
		"""
		Imports a full calendar preset from:
		- a file path, OR
		- a JSON string
		"""
		src = str(path_or_json_text)

		if os.path.exists(src) and os.path.isfile(src):
			with open(src, "r", encoding="utf-8") as f:
				payload = json.load(f)
		else:
			payload = json.loads(src)

		if not isinstance(payload, dict):
			raise ValueError("Invalid CQCalendar preset JSON")

		if payload.get("schema") != "cqcalendar.settings":
			raise ValueError("Invalid preset schema")

		# --- Time ---
		time = payload.get("time", {})
		self.minutes_per_tick = max(1, int(time.get("minutes_per_tick", self.minutes_per_tick)))
		self.set_time(
			hour=time.get("hour", self.hour),
			minute=time.get("minute", self.minute),
			is_pm=time.get("is_pm", self.is_pm),
		)

		# --- Date ---
		date = payload.get("date", {})
		self.set_date(
			day=date.get("day", self.day),
			month=date.get("month", self.month),
			year=date.get("year", self.year),
		)
		self.set_weekday(date.get("weekday", self.weekday))

		# --- Calendar ---
		cal = payload.get("calendar", {})
		if "months" in cal:
			self.months = [
				(str(m["name"]), int(m["days"]))
				for m in cal.get("months", [])
			]

		if "weekdays" in cal:
			self.weekdays = [str(w) for w in cal.get("weekdays", [])]

		self.use_gregorian_leap_years = bool(
			cal.get("use_gregorian_leap_years", self.use_gregorian_leap_years)
		)

		# --- Lunar ---
		lunar = payload.get("lunar", {})
		if "synodic_month_days" in lunar:
			self.synodic_month_days = float(lunar["synodic_month_days"])

		if "moon_phases" in lunar:
			self.moon_phases = self._normalize_moon_phases(lunar["moon_phases"])

		if "moon_age_days" in lunar:
			self.moon_age_days = float(lunar["moon_age_days"]) % self.synodic_month_days

		return self



	def export_lunar_phases_json(self, path_or_none=None, indent=2):
		"""
		Exports lunar phase data to a JSON string, or writes to a file if a path is provided.

		Schema:
		{
			"schema": "cqcalendar.lunar_phases",
			"schema_version": 1,
			"synodic_month_days": 29.530588,
			"moon_phases": [ ... ]
		}
		"""
		phases = list(self.moon_phases) if self.moon_phases else self._default_moon_phases()
		
		for p in phases:
			if isinstance(p, dict) and isinstance(p.get("color_rgb"), tuple):
				p["color_rgb"] = list(p["color_rgb"])
		
		payload = {
			"schema": "cqcalendar.lunar_phases",
			"schema_version": 1,
			"synodic_month_days": float(self.synodic_month_days),
			"moon_phases": phases,
		}

		text = json.dumps(payload, indent=indent)

		if path_or_none:
			with open(str(path_or_none), "w", encoding="utf-8") as f:
				f.write(text)

		return text

	def import_lunar_phases_json(self, path_or_json_text):
		"""
		Imports lunar phase data from either:
		- a file path, if the string points to an existing file, OR
		- a JSON string containing the payload.

		Updates:
		- self.synodic_month_days (if present)
		- self.moon_phases (normalized)
		"""
		if path_or_json_text is None:
			raise ValueError("path_or_json_text cannot be None")

		src = str(path_or_json_text)

		# If it's a real file path, read it; otherwise treat as JSON text
		if os.path.exists(src) and os.path.isfile(src):
			with open(src, "r", encoding="utf-8") as f:
				payload = json.load(f)
		else:
			payload = json.loads(src)

		if not isinstance(payload, dict):
			raise ValueError("Invalid lunar phases JSON: root must be an object.")

		# Support the preferred schema, plus a couple of simple fallback shapes
		if "moon_phases" in payload:
			phases = payload.get("moon_phases", None)
			syn = payload.get("synodic_month_days", None)

		# Fallback: {"lunar_cycle":{"phases":[...]}, "synodic_month_days": ...}
		elif isinstance(payload.get("lunar_cycle", None), dict) and "phases" in payload["lunar_cycle"]:
			phases = payload["lunar_cycle"].get("phases", None)
			syn = payload.get("synodic_month_days", None)

		# Fallback: {"phases":[...]}
		elif "phases" in payload:
			phases = payload.get("phases", None)
			syn = payload.get("synodic_month_days", None)

		else:
			raise ValueError("Invalid lunar phases JSON: missing 'moon_phases' (or fallback keys).")

		if syn is not None:
			syn = float(syn)
			if syn <= 0:
				raise ValueError("synodic_month_days must be > 0")
			self.synodic_month_days = syn
			self.moon_age_days = float(self.moon_age_days) % self.synodic_month_days

		# Normalize phases
		if phases is None:
			raise ValueError("Invalid lunar phases JSON: phases were null/None.")
		if not isinstance(phases, list):
			raise ValueError("Invalid lunar phases JSON: phases must be a list.")

		self.moon_phases = self._normalize_moon_phases(phases)
		return self.moon_phases

	def is_leap_year(self, year=None) -> bool:
		if year is None:
			year = self.year

		year = int(year)

		if year % 400 == 0:
			return True
		if year % 100 == 0:
			return False
		return year % 4 == 0

	def days_in_month(self, month=None, year=None) -> int:
		if month is None:
			month = self.month
		if year is None:
			year = self.year

		month = int(month)
		year = int(year)

		if self.use_gregorian_leap_years and month == 2:
			return 29 if self.is_leap_year(year) else 28

		_, base_days = self.months[month - 1]
		return base_days

	def clamp_day_to_month(self):
		dim = self.days_in_month(self.month, self.year)
		if self.day > dim:
			self.day = dim

	def weekday_name(self):
		return self.weekdays[self.weekday]

	def time_string(self):
		return f"{self.hour}:{self.minute:02d} {'PM' if self.is_pm else 'AM'}"

	def date_string(self):
		month_name, _ = self.months[self.month - 1]
		return f"{self.weekday_name()}, {month_name} {self.day}, Year {self.year}"

	def datetime_string(self):
		return f"{self.date_string()} at {self.time_string()}"
		
	def _time_to_minutes(self, hour, minute, is_pm):
		hour = int(hour)
		minute = int(minute)

		hour = max(1, min(hour, 12))
		minute = max(0, min(minute, 59))

		# Convert to 24-hour minutes
		# 12AM -> 0, 12PM -> 12
		if bool(is_pm):
			h24 = 12 if hour == 12 else hour + 12
		else:
			h24 = 0 if hour == 12 else hour

		return h24 * 60 + minute

	def is_night(
		self,
		night_start_hour=7,
		night_start_is_pm=True,
		night_end_hour=6,
		night_end_is_pm=False,
	):
		"""
		Returns True if the current time is within the night window.

		Default: 7:00 PM -> 6:00 AM
		Works with wrap-around ranges (PM -> AM).
		"""
		now = self._time_to_minutes(self.hour, self.minute, self.is_pm)

		start = self._time_to_minutes(night_start_hour, 0, night_start_is_pm)
		end = self._time_to_minutes(night_end_hour, 0, night_end_is_pm)

		# Normal range (ex: 8PM -> 11PM)
		if start < end:
			return start <= now < end

		# Wrap-around range (ex: 7PM -> 6AM)
		return now >= start or now < end

	def is_day(
		self,
		night_start_hour=7,
		night_start_is_pm=True,
		night_end_hour=6,
		night_end_is_pm=False,
	):
		return not self.is_night(
			night_start_hour=night_start_hour,
			night_start_is_pm=night_start_is_pm,
			night_end_hour=night_end_hour,
			night_end_is_pm=night_end_is_pm,
		)
