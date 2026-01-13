"""Tools."""

import os
import typing

import yaml
from webtools import settings


def join(*folders):
    """Join multiple folders with os.path.join."""
    if len(folders) == 1:
        return folders[0]

    return join(os.path.join(*folders[:2]), *folders[2:])


def mkdir(path: str):
    """Make a directory."""
    if not os.path.isdir(path):
        os.mkdir(path)


def parse_metadata(content: str) -> typing.Tuple[typing.Dict[str, typing.Any], str]:
    """Parse metadata.

    Args:
        content: Raw data

    Returns:
        Parsed metadata and content without metadata
    """
    from webtools.markup import preprocess

    metadata: typing.Dict[str, typing.Any] = {"title": None}
    if content.startswith("--\n"):
        metadata_in, content = content[3:].split("\n--\n", 1)
        metadata.update(yaml.load(metadata_in, Loader=yaml.FullLoader))
    content = preprocess(content.strip())
    if metadata["title"] is None and content.startswith("# "):
        metadata["title"] = content[2:].split("\n", 1)[0].strip()
    return metadata, content


def html_local(path: str) -> str:
    """Get the local HTML path of a absolute path.

    Args:
        path: The absolute path

    Returns:
        Local HTML path
    """
    assert settings.html_path is not None
    assert path.startswith(settings.html_path)
    return path[len(settings.html_path) :]


def comma_and_join(ls: typing.List[str], oxford_comma: bool = True) -> str:
    """Join a list with commas and an and between the last two items."""
    if len(ls) == 1:
        return ls[0]
    if len(ls) == 2:
        return f"{ls[0]} and {ls[1]}"
    return ", ".join(ls[:-1]) + ("," if oxford_comma else "") + " and " + ls[-1]


def insert_author_info(content: str, authors: typing.List[str], url: str) -> str:
    """Insert author info into content.

    Args:
        content: The content
        authors: List of authors
        url: A URL

    Returns:
        Content with authrso inserted
    """
    assert content.startswith("# ")
    title, content = content.split("\n", 1)
    return f"{title}\n{{{{author-info::{';'.join(authors)}|{title[1:].strip()}|{url}}}}}\n{content}"
