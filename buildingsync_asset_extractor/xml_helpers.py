"""Typed accessors for elements of parsed BuildingSync documents."""

from lxml import etree

from buildingsync_asset_extractor.errors import BSyncProcessorError


def element_tag(element: etree._Element) -> str:
    """Return the element's tag, e.g. `{namespace}Name`

    Tags are always `str` in parsed documents (lxml only stores other types when a tag is set manually), while comments
    and processing instructions don't have a `str` tag, so they won't match a tag name.
    """
    return str(element.tag)


def element_text(element: etree._Element) -> str:
    """Return the element's text, raising if it has none"""
    if element.text is None:
        raise BSyncProcessorError(f"Element `{element_tag(element)}` has no text")
    return element.text


def find_element(element: etree._Element, path: str) -> etree._Element:
    """Return the first match of `path` (using the element's namespaces), raising if there isn't one"""
    found = element.find(path, element.nsmap)
    if found is None:
        raise BSyncProcessorError(f"`{path}` not found in element `{element_tag(element)}`")
    return found


def ancestor(element: etree._Element, levels: int = 1) -> etree._Element:
    """Return the element's parent, or a higher ancestor, raising if it doesn't exist"""
    for _ in range(levels):
        parent = element.getparent()
        if parent is None:
            raise BSyncProcessorError(f"Element `{element_tag(element)}` has no parent")
        element = parent
    return element
