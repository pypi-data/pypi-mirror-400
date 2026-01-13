import dataclasses
import datetime
import mimetypes
import os
import typing

import requests
import requests_toolbelt  # type: ignore[import-untyped]

from .iso8601 import format_duration
from .messages import DECODER


# https://v4-docs.chevereto.com/developer/api/api-v1.html
@dataclasses.dataclass(eq=False, frozen=True, kw_only=True)
class Settings:
	title: typing.Optional[str] = None
	description: typing.Optional[str] = None
	tags: typing.Optional[tuple[str, ...]] = None
	album_id: typing.Optional[str] = None
	category_id: typing.Optional[int] = None
	width: typing.Optional[int] = None
	expiration: typing.Union[datetime.timedelta, int, None] = None
	nsfw: typing.Optional[bool] = None
	use_file_date: typing.Optional[bool] = None


DEFAULT_SETTINGS = Settings()
DEFAULT_ENDPOINT = 'https://hamsterimg.net/api/1/upload'
DEFAULT_TIMEOUT = (10.0, 30.0)


@dataclasses.dataclass(eq=False, frozen=True, kw_only=True)
class Result:
	viewer: str
	image: str
	medium: typing.Optional[str] = None
	thumbnail: str


def upload(
	session: requests.Session,
	path: typing.Union[str, os.PathLike[str]],
	api_key: str,
	settings: Settings = DEFAULT_SETTINGS,
	endpoint: str = DEFAULT_ENDPOINT,
	timeout: typing.Union[float, tuple[float, float], tuple[float, None], None] = DEFAULT_TIMEOUT,
) -> Result:
	mimetypes.init()
	mime_type, _ = mimetypes.guess_type(path)
	if mime_type is None:
		raise ValueError('unknown file type')

	with open(path, 'rb') as fp:
		fields: dict[str, typing.Union[str, tuple[str, typing.BinaryIO, str]]] = {}
		fields['source'] = (os.path.basename(path), fp, mime_type)
		if settings.title is not None:
			fields['title'] = settings.title
		if settings.description is not None:
			fields['description'] = settings.description
		if settings.tags is not None:
			fields['tags'] = ','.join(settings.tags)
		if settings.album_id is not None:
			fields['album_id'] = settings.album_id
		if settings.category_id is not None:
			fields['category_id'] = str(settings.category_id)
		if settings.width is not None:
			fields['width'] = str(settings.width)
		if settings.expiration is not None:
			fields['expiration'] = format_duration(settings.expiration)
		if settings.nsfw is not None:
			fields['nsfw'] = str(int(settings.nsfw))
		fields['format'] = 'json'
		if settings.use_file_date is not None:
			fields['use_file_date'] = str(int(settings.use_file_date))

		encoder = requests_toolbelt.MultipartEncoder(fields)
		headers = {'X-API-Key': api_key, 'Content-Type': encoder.content_type}

		with session.post(
			endpoint, data=encoder, headers=headers, timeout=timeout, allow_redirects=False
		) as response:
			response.raise_for_status()
			data = DECODER.decode(response.content)

	return Result(
		viewer=data.image.url_viewer,
		image=data.image.image.url,
		medium=data.image.medium.url,
		thumbnail=data.image.thumb.url,
	)
