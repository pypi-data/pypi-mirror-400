import functools
import importlib.metadata
import platform

import requests


@functools.cache
def get_user_agent() -> str:
	parts: tuple[str, ...] = (
		'{}/{}'.format(__package__, importlib.metadata.version(__package__)),
		'Python {}'.format(platform.python_version()),
		'{} {}'.format(platform.system(), platform.release()),
		platform.machine(),
		'+https://codeberg.org/deadmaster/jerkup',
	)

	return '{} ({})'.format(parts[0], '; '.join(parts[1:]))


def create_session() -> requests.Session:
	session = requests.Session()
	session.headers['User-Agent'] = get_user_agent()
	session.stream = True
	return session
