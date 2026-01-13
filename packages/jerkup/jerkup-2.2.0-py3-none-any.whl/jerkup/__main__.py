import argparse
import contextlib
import json
import os
import sys
import time
import traceback
import typing

import requests

from .configuration import has_api_key, load_api_key, save_api_key
from .formatter import (
	FORMAT_BBCODE_FULL,
	FORMAT_BBCODE_FULL_LINKED,
	FORMAT_BBCODE_MEDIUM,
	FORMAT_BBCODE_MEDIUM_LINKED,
	FORMAT_BBCODE_THUMBNAIL,
	FORMAT_BBCODE_THUMBNAIL_LINKED,
	FORMAT_DIRECT_LINK,
	apply_format,
	extract_format,
)
from .session import create_session
from .uploader import DEFAULT_SETTINGS, Result, Settings, upload

FORMAT_MAP: dict[str, str] = {
	'direct-link': FORMAT_DIRECT_LINK,
	'bbcode-full': FORMAT_BBCODE_FULL,
	'bbcode-full-linked': FORMAT_BBCODE_FULL_LINKED,
	'bbcode-medium': FORMAT_BBCODE_MEDIUM,
	'bbcode-medium-linked': FORMAT_BBCODE_MEDIUM_LINKED,
	'bbcode-thumbnail': FORMAT_BBCODE_THUMBNAIL,
	'bbcode-thumbnail-linked': FORMAT_BBCODE_THUMBNAIL_LINKED,
}


def parse_tags(tags: str) -> tuple[str, ...]:
	if not tags:
		return ()
	return tuple(map(str.strip, tags.split(',')))


def create_parser(require_api_key: bool) -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser()
	parser.description = 'hamster uploader'

	parser.add_argument('image', type=str, nargs='+', help='path to image file')

	parser.add_argument('--api-key', type=str, required=require_api_key, help='hamster api key')

	parser.add_argument('--title', type=str, help='image title')
	parser.add_argument('--description', type=str, help='image description')
	parser.add_argument('--tags', type=parse_tags, help='comma-separated image tags')
	parser.add_argument('--album', type=str, help='add to album with id')
	parser.add_argument('--category', type=int, help='assign category id')
	parser.add_argument('--width', type=int, help='target resize width')
	parser.add_argument('--expiration', type=int, help='expiration, in seconds')
	parser.add_argument('--nsfw', action='store_true', help='flag as nsfw')
	parser.add_argument(
		'--use-file-date',
		action='store_true',
		help='use exif date instead of upload date (admin only)',
	)

	parser.add_argument('--retry-count', type=int, default=3, help='number of retries on failure')
	parser.add_argument('--retry-delay', type=float, default=2.0, help='delay between retries')

	parser.add_argument('--output', '-o', type=str, help='output file')
	parser.add_argument(
		'--format',
		'-f',
		type=str,
		default='direct-link',
		choices=('json',) + tuple(FORMAT_MAP.keys()),
		help='output format',
	)

	sub = parser.add_mutually_exclusive_group()
	sub.add_argument(
		'--multiline', dest='multiline', default=None, action='store_true', help='multiline output'
	)
	sub.add_argument('--single', dest='multiline', action='store_false', help='single line output')

	return parser


def safe_upload(
	session: requests.Session,
	path: typing.Union[str, os.PathLike[str]],
	api_key: str,
	retry: tuple[int, float],
	output: typing.TextIO,
	settings: Settings = DEFAULT_SETTINGS,
) -> typing.Optional[Result]:
	for index in range(retry[0]):
		if index:
			time.sleep(retry[1])
			output.write('{} ({}/{})\n'.format(os.path.basename(path), index + 1, retry[0]))
		else:
			output.write('{}\n'.format(os.path.basename(path)))

		try:
			return upload(session, path, api_key, settings)
		except Exception:
			traceback.print_exc(file=output)
			output.write('\n')

	return None


def dump(
	results: list[Result],
	output: typing.TextIO,
	format: typing.Optional[str],
	multiline: typing.Optional[bool],
) -> None:
	if multiline is None:
		multiline = output.isatty() or format == FORMAT_DIRECT_LINK

	if format is None:
		data = list(map(extract_format, results))
		indent = 2 if multiline else None

		json.dump(data, fp=output, indent=indent)
		output.write('\n')

		return

	count = 0
	for result in results:
		value = apply_format(result, format)
		if value is None:
			continue

		if count and not multiline:
			output.write(' ')

		output.write(value)
		if multiline:
			output.write('\n')

		count += 1

	if count and not multiline:
		output.write('\n')


def execute(
	images: typing.Iterable[typing.Union[str, os.PathLike[str]]],
	api_key: str,
	settings: Settings,
	retry: tuple[int, float],
	output_data: typing.TextIO,
	output_text: typing.TextIO,
	format: typing.Optional[str],
	multiline: typing.Optional[bool],
) -> None:
	results: list[Result] = []

	with create_session() as session:
		for image in images:
			result = safe_upload(session, image, api_key, retry, output_text, settings)

			if result is not None:
				results.append(result)

	dump(results, output_data, format, multiline)


def open_output(path: typing.Optional[str]) -> contextlib.AbstractContextManager[typing.TextIO]:
	if path and path != '-':
		return open(path, 'w', encoding='utf-8')
	else:
		return contextlib.nullcontext(sys.stdout)


def main() -> None:
	parser = create_parser(not has_api_key())
	options = parser.parse_args()

	images: list[str] = options.image
	api_key: typing.Optional[str] = options.api_key
	title: typing.Optional[str] = options.title
	description: typing.Optional[str] = options.description
	tags: typing.Optional[tuple[str, ...]] = options.tags
	album_id: typing.Optional[str] = options.album
	category_id: typing.Optional[int] = options.category
	width: typing.Optional[int] = options.width
	expiration: typing.Optional[int] = options.expiration
	nsfw: bool = options.nsfw
	use_file_date: bool = options.use_file_date
	retry_count: int = options.retry_count
	retry_delay: float = options.retry_delay
	output: typing.Optional[str] = options.output
	format: str = options.format
	multiline: typing.Optional[bool] = options.multiline

	if api_key is None:
		api_key = load_api_key()
	else:
		save_api_key(api_key)

	settings = Settings(
		title=title,
		description=description,
		tags=tags,
		album_id=album_id,
		category_id=category_id,
		width=width,
		expiration=expiration,
		nsfw=nsfw,
		use_file_date=use_file_date,
	)

	retry = (retry_count, retry_delay)

	with open_output(output) as fp:
		execute(images, api_key, settings, retry, fp, sys.stderr, FORMAT_MAP.get(format), multiline)


if __name__ == '__main__':
	main()
