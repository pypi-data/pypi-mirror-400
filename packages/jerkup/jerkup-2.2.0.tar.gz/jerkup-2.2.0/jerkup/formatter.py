import dataclasses
import typing

from .uploader import Result

FORMAT_DIRECT_LINK = '{image}'
FORMAT_BBCODE_FULL = '[img]{image}[/img]'
FORMAT_BBCODE_FULL_LINKED = '[url={viewer}][img]{image}[/img][/url]'
FORMAT_BBCODE_MEDIUM = '[img]{medium}[/img]'
FORMAT_BBCODE_MEDIUM_LINKED = '[url={viewer}][img]{medium}[/img][/url]'
FORMAT_BBCODE_THUMBNAIL = '[img]{thumbnail}[/img]'
FORMAT_BBCODE_THUMBNAIL_LINKED = '[url={viewer}][img]{thumbnail}[/img][/url]'


def extract_format(result: Result) -> dict[str, object]:
	data = dataclasses.asdict(result)
	if result.medium is None:
		data.pop('medium')
	return data


def apply_format(result: Result, format: str) -> typing.Optional[str]:
	try:
		return format.format(**extract_format(result))
	except KeyError:
		return None
