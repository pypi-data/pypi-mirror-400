import functools
import os
import sys

import platformdirs

APPLICATION = 'JerkUp' if sys.platform in ('win32', 'darwin') else 'jerkup'
DIRECTORY = platformdirs.user_data_path(APPLICATION, False)

APIKEY_NAME = 'apikey.txt'
APIKEY_ENV = 'JERKUP_API_KEY'
APIKEY_PATH = DIRECTORY / APIKEY_NAME
APIKEY_ENCODING = 'utf-8'


def has_api_key() -> bool:
	return APIKEY_ENV in os.environ or APIKEY_PATH.is_file()


def load_api_key() -> str:
	value = os.environ.get(APIKEY_ENV)
	if value is not None:
		return value

	with APIKEY_PATH.open('r', encoding=APIKEY_ENCODING) as fp:
		value = fp.readline().rstrip('\n')
	return value


def save_api_key(api_key: str) -> None:
	DIRECTORY.mkdir(parents=True, exist_ok=True)

	opener = functools.partial(os.open, mode=0o660)
	with open(APIKEY_PATH, mode='w', encoding=APIKEY_ENCODING, opener=opener) as fp:
		fp.write(api_key)
