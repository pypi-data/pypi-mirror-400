"""HTML tools."""

import os
import typing

from webtools import settings
from webtools.markup import insert_dates


def make_html_page(
    content: str,
    pagetitle: typing.Optional[str] = None,
    extra_head: typing.Optional[str] = None,
) -> str:
    """Make a HTML page.

    Args:
        content: Page content
        pagetitle: Page title
        extra_head: Extra HTML to include in <head>

    Return:
        Formatted HTML page
    """
    assert settings.template_path is not None
    out = ""
    with open(os.path.join(settings.template_path, "intro.html")) as f:
        out += insert_dates(f.read())
    if extra_head is not None:
        a, b = out.split("<head>")
        out = f"{a}<head>\n{extra_head}\n{b}"
    if pagetitle is None:
        out = out.replace("{{: pagetitle}}", "")
        out = out.replace("{{pagetitle | }}", "")
    else:
        out = out.replace("{{: pagetitle}}", f": {pagetitle}")
        out = out.replace("{{pagetitle | }}", f"{pagetitle} | ")
    out += content
    with open(os.path.join(settings.template_path, "outro.html")) as f:
        out += insert_dates(f.read())
    if settings.local_prefix is not None:
        for q in ["'", '"']:
            out = out.replace(f"src={q}/", f"src={q}/{settings.local_prefix}/")
            out = out.replace(f"href={q}/", f"href={q}/{settings.local_prefix}/")
    return out


def make_html_forwarding_page(url: str) -> str:
    """Make a page that will redirect.

    Args:
        url: the URL to redirect to

    Return:
        Formatted HTML page
    """
    assert url[0] == "/"
    return make_html_page(
        content=(f"This page has moved to <a href='{url}'>{settings.url}{url}</a>"),
        extra_head=(f"<meta http-equiv='refresh' content='0; URL={url}' />"),
    )
