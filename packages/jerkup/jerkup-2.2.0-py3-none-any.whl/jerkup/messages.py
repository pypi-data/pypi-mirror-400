import typing

import msgspec

TStr = typing.TypeVar('TStr', str, typing.Optional[str])


class Status(msgspec.Struct):
	message: str
	code: typing.Union[int, str]


class Image(typing.Generic[TStr], msgspec.Struct):
	url: TStr


class Body(msgspec.Struct):
	url_viewer: str
	image: Image[str]
	thumb: Image[str]
	medium: Image[typing.Optional[str]]


class Response(msgspec.Struct):
	status_code: int
	success: Status
	image: Body
	status_txt: str


DECODER = msgspec.json.Decoder(Response)
