import datetime
import typing


# https://en.wikipedia.org/wiki/ISO_8601#Durations
def format_duration(duration: typing.Union[datetime.timedelta, int]) -> str:
	if isinstance(duration, datetime.timedelta):
		duration = duration.days * 86400 + duration.seconds

	parts: list[typing.Union[str, int]] = []
	seconds = duration

	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)

	if seconds or not (minutes or hours or days):
		parts.append('S')
		parts.append(seconds)

	if minutes:
		parts.append('M')
		parts.append(minutes)

	if hours:
		parts.append('H')
		parts.append(hours)

	if parts:
		parts.append('T')

	if days:
		parts.append('D')
		parts.append(days)

	parts.append('P')
	parts.reverse()

	return ''.join(map(str, parts))
