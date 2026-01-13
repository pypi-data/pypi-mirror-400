"""Citations."""

import re
import typing

from webtools.tools import comma_and_join


def markup_authors(a: typing.Union[str, typing.List[str]], format: str = "HTML") -> str:
    """Markup authors.

    Args:
        a: Authors
        format: Format (HTML or txt)

    Returns:
        Formatted list of authors
    """
    if format not in ["HTML", "txt"]:
        raise ValueError(f"Unsupported format: {format}")
    if isinstance(a, str):
        return a
    else:
        return comma_and_join(a)


def markup_citation(r: typing.Dict[str, typing.Any], format: str = "HTML") -> str:
    """Markup citations.

    Args:
        r: Citation
        format: Format (HTML or txt)

    Returns:
        Formatted citation
    """
    if format not in ["HTML", "txt"]:
        raise ValueError(f"Unsupported format: {format}")
    out = ""
    if "author" in r:
        out += markup_authors(r["author"], format)
    else:
        if format == "HTML":
            out += "<i>(unknown author)</i>"
        elif format == "txt":
            out += "(unknown author)"
    if out[-1] != ".":
        out += "."
    out += f" {r['title']}"
    if "journal" in r:
        if format == "HTML":
            out += f", <em>{r['journal']}</em>"
        elif format == "txt":
            out += f", {r['journal']}"
        if "volume" in r:
            out += f" {r['volume']}"
            if "issue" in r:
                out += f"({r['issue']})"
        if "pagestart" in r and "pageend" in r:
            if format == "HTML":
                out += f", {r['pagestart']}&ndash;{r['pageend']}"
            elif format == "txt":
                out += f", {r['pagestart']}-{r['pageend']}"
    elif "publisher" in r:
        out += f", {r['publisher']}"
        if "address" in r:
            out += f", {r['address']}"
    elif "howpublished" in r:
        if format == "HTML":
            out += f", <em>{r['howpublished']}</em>"
        elif format == "txt":
            out += f", {r['howpublished']}"
    elif "arxiv" in r:
        if format == "HTML":
            out += f", ar&Chi;iv: <a href='https://arxiv.org/abs/{r['arxiv']}'>{r['arxiv']}</a>"
        elif format == "txt":
            out += f", https://arxiv.org/abs/{r['arxiv']}"
    elif "thesis-institution" in r:
        out += f" (PhD thesis, {r['thesis-institution']})"
    if "booktitle" in r:
        out += ","
        if "chapter" in r:
            out += f" chapter {r['chapter']}"
        if format == "HTML":
            out += f" in <em>{r['booktitle']}</em>"
        elif format == "txt":
            out += f" in {r['booktitle']}"
        if "editor" in r:
            out += f" (eds: {markup_authors(r['editor'], format)})"
        if "pagestart" in r and "pageend" in r:
            if format == "HTML":
                out += f", {r['pagestart']}&ndash;{r['pageend']}"
            elif format == "txt":
                out += f", {r['pagestart']}-{r['pageend']}"
    if "year" in r:
        out += f", {r['year']}"
    out += "."
    if "doi" in r:
        if format == "HTML":
            out += f" [DOI:&nbsp;<a href='https://doi.org/{r['doi']}'>{r['doi']}</a>]"
        elif format == "txt":
            out += f" [https://doi.org/{r['doi']}]"
    if "url" in r:
        if format == "HTML":
            out += f" [<a href='{r['url']}'>{r['url'].split('://')[1]}</a>]"
        elif format == "txt":
            out += f" [{r['url']}]"
    if "note" in r:
        out += f" [{r['note']}]"
    return out


def wrap_caps(txt: str) -> str:
    """Wrap capitials in curly braces.

    Args:
        txt: Input string

    Returns:
        String with capitals wrapped in curly braces
    """
    out = ""
    for word in txt.split():
        if out != "":
            out += " "
        if re.match(r".[A-Z]", word) or (out != "" and re.match(r"[A-Z]", word)):
            out += f"{{{word}}}"
        else:
            out += word
    return out


def html_to_tex(txt: str) -> str:
    """Convert html to TeX.

    Args:
        txt: HTML

    Returns:
        TeX
    """
    txt = re.sub(r"&([A-Za-z])acute;", r"\\'\1", txt)
    txt = re.sub(r"&([A-Za-z])grave;", r"\\`\1", txt)
    txt = re.sub(r"&([A-Za-z])caron;", r"\v{\1}", txt)
    txt = re.sub(r"&([A-Za-z])uml;", r'\\"\1', txt)
    txt = re.sub(r"&([A-Za-z])cedil;", r"\\c{\1}", txt)
    txt = re.sub(r"&([A-Za-z])circ;", r"\\^\1", txt)
    txt = re.sub(r"&([A-Za-z])tilde;", r"\\~\1", txt)
    txt = txt.replace("&oslash;", "{\\o}")
    txt = txt.replace("&ndash;", "--")
    txt = txt.replace("&mdash;", "---")
    return txt


def make_bibtex(id: str, r: typing.Dict[str, typing.Any]) -> str:
    """Make BibTex.

    Args:
        id: Unique identifier
        r: A citation

    Returns:
        The citation in BibTeX format
    """
    if "type" not in r:
        r["type"] = "article"
    out = f"@{r['type']}{{{id},\n"

    # Author-type fields
    for i, j in [("AUTHOR", "author"), ("EDITOR", "editor")]:
        if j in r:
            out += " " * (10 - len(i)) + f"{i} = {{"
            if isinstance(r[j], str):
                out += html_to_tex(r[j])
            else:
                out += " and ".join([html_to_tex(k) for k in r[j]])
            out += "},\n"

    # Fields with caps that need wrapping
    for i, j in [
        ("TITLE", "title"),
        ("BOOKTITLE", "booktitle"),
        ("SCHOOL", "thesis-institution"),
        ("PUBLISHER", "publisher"),
        ("ADDRESS", "address"),
    ]:
        if j in r:
            out += " " * (10 - len(i)) + f"{i} = {{{wrap_caps(html_to_tex(r[j]))}}},\n"

    # Text fields
    for i, j in [("JOURNAL", "journal"), ("HOWPUBLISHED", "howpublished"), ["NOTE", "note"]]:
        if j in r:
            out += " " * (10 - len(i)) + f"{i} = {{{html_to_tex(r[j])}}},\n"

    # Numerical fields
    for i, j in [
        ("VOLUME", "volume"),
        ("NUMBER", "issue"),
        ("YEAR", "year"),
        ("DOI", "doi"),
        ("CHAPTER", "chapter"),
    ]:
        if j in r:
            out += " " * (10 - len(i)) + f"{i} = {{{r[j]}}},\n"

    # Page numbers
    if "pagestart" in r:
        if "pageend" not in r or r["pagestart"] == r["pageend"]:
            out += f"     PAGES = {{{{{r['pagestart']}}}}},\n"
        else:
            out += f"     PAGES = {{{{{r['pagestart']}--{r['pageend']}}}}},\n"
    out += "}"
    return out


template = {
    "type": None,
    "author": None,
    "title": "REQUIRED",
    "journal": None,
    "volume": None,
    "issue": None,
    "pagestart": None,
    "pageend": None,
    "publisher": None,
    "address": None,
    "howpublished": None,
    "arxiv": None,
    "thesis-institution": None,
    "booktitle": None,
    "chapter": None,
    "editor": None,
    "year": None,
    "doi": None,
    "url": None,
    "note": None,
}
