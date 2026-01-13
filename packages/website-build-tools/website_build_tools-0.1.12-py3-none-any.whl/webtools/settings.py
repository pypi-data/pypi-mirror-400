"""Settings."""

import typing as _typing

dir_path: _typing.Optional[str] = None
html_path: _typing.Optional[str] = None
template_path: _typing.Optional[str] = None
github_token: _typing.Optional[str] = None

owners: _typing.List[str] = []
editors: _typing.List[str] = []
contributors: _typing.List[_typing.Dict[str, str]] = []
url: _typing.Optional[str] = None
website_name: _typing.List[_typing.Optional[str]] = [None, None]
local_prefix: _typing.Optional[str] = None
repo: _typing.Optional[str] = None

re_extras: _typing.List[_typing.Tuple[str, _typing.Callable]] = []
str_extras: _typing.List[_typing.Tuple[str, str]] = []
insert_links: _typing.Optional[_typing.Callable] = None
