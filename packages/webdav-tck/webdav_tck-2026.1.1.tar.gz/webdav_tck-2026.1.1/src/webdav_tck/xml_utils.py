"""XML utilities for WebDAV protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from lxml import etree

if TYPE_CHECKING:
    from lxml.etree import _Element

# WebDAV namespaces
NS_DAV = "DAV:"
NS_MAP = {"D": NS_DAV}


@dataclass
class PropValue:
    """A property value with namespace."""

    namespace: str
    name: str
    value: Any


@dataclass
class MultiStatusResponse:
    """Response element from multistatus."""

    href: str
    status: int | None = None
    properties: dict[tuple[str, str], Any] | None = None  # (namespace, name) -> value
    error: str | None = None


@dataclass
class LockInfo:
    """Information about a lock."""

    token: str
    timeout: str | None = None
    owner: str | None = None
    scope: str = "exclusive"  # exclusive or shared
    depth: str = "0"


def build_propfind_body(
    props: list[tuple[str, str]] | None = None,
    allprop: bool = False,
    propname: bool = False,
) -> bytes:
    """Build PROPFIND XML request body.

    Args:
        props: List of (namespace, name) tuples for specific properties
        allprop: Request all properties
        propname: Request only property names

    Returns:
        XML as bytes
    """
    root = etree.Element("{DAV:}propfind", nsmap=NS_MAP)

    if allprop:
        etree.SubElement(root, "{DAV:}allprop")
    elif propname:
        etree.SubElement(root, "{DAV:}propname")
    elif props:
        prop = etree.SubElement(root, "{DAV:}prop")
        for namespace, name in props:
            etree.SubElement(prop, f"{{{namespace}}}{name}")
    else:
        # Default: allprop
        etree.SubElement(root, "{DAV:}allprop")

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")


def build_proppatch_body(
    set_props: dict[tuple[str, str], str | _Element] | None = None,
    remove_props: list[tuple[str, str]] | None = None,
) -> bytes:
    """Build PROPPATCH XML request body.

    Args:
        set_props: Properties to set as {(namespace, name): value}
        remove_props: Properties to remove as [(namespace, name)]

    Returns:
        XML as bytes
    """
    root = etree.Element("{DAV:}propertyupdate", nsmap=NS_MAP)

    # Add set operations
    if set_props:
        set_elem = etree.SubElement(root, "{DAV:}set")
        prop = etree.SubElement(set_elem, "{DAV:}prop")

        for (namespace, name), value in set_props.items():
            prop_elem = etree.SubElement(prop, f"{{{namespace}}}{name}")
            if isinstance(value, etree._Element):
                prop_elem.append(value)
            else:
                prop_elem.text = str(value)

    # Add remove operations
    if remove_props:
        remove_elem = etree.SubElement(root, "{DAV:}remove")
        prop = etree.SubElement(remove_elem, "{DAV:}prop")

        for namespace, name in remove_props:
            etree.SubElement(prop, f"{{{namespace}}}{name}")

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")


def build_lock_body(
    owner: str, scope: str = "exclusive", lock_type: str = "write"
) -> bytes:
    """Build LOCK XML request body.

    Args:
        owner: Lock owner identifier (URL or text)
        scope: Lock scope (exclusive or shared)
        lock_type: Lock type (write)

    Returns:
        XML as bytes
    """
    root = etree.Element("{DAV:}lockinfo", nsmap=NS_MAP)

    # Lock scope
    lockscope = etree.SubElement(root, "{DAV:}lockscope")
    etree.SubElement(lockscope, f"{{DAV:}}{scope}")

    # Lock type
    locktype_elem = etree.SubElement(root, "{DAV:}locktype")
    etree.SubElement(locktype_elem, f"{{DAV:}}{lock_type}")

    # Owner
    owner_elem = etree.SubElement(root, "{DAV:}owner")
    if owner.startswith(("http://", "https://")):
        href = etree.SubElement(owner_elem, "{DAV:}href")
        href.text = owner
    else:
        owner_elem.text = owner

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")


def _parse_http_status(status_text: str | None) -> int | None:
    """Parse HTTP status from 'HTTP/1.1 200 OK' format."""
    if not status_text:
        return None
    parts = status_text.split()
    if len(parts) >= 2:
        try:
            return int(parts[1])
        except ValueError:
            pass
    return None


def _parse_tag_namespace(tag: str | bytes | bytearray | etree.QName) -> tuple[str, str]:
    """Parse namespace and name from '{namespace}name' format."""
    tag_str = str(tag)
    if "}" in tag_str:
        namespace = tag_str.split("}", maxsplit=1)[0][1:]
        name = tag_str.split("}")[1]
    else:
        namespace = ""
        name = tag_str
    return namespace, name


def _extract_propstat_properties(
    response_elem: _Element,
) -> dict[tuple[str, str], Any]:
    """Extract properties from propstat elements."""
    properties: dict[tuple[str, str], Any] = {}

    for propstat in response_elem.findall("{DAV:}propstat"):
        status_elem = propstat.find("{DAV:}status")
        status = _parse_http_status(
            status_elem.text if status_elem is not None else None
        )

        if status is None or not (200 <= status < 300):
            continue

        prop_elem = propstat.find("{DAV:}prop")
        if prop_elem is None:
            continue

        for prop in prop_elem:
            namespace, name = _parse_tag_namespace(prop.tag)
            properties[namespace, name] = _extract_prop_value(prop)

    return properties


def parse_multistatus(xml_data: bytes) -> list[MultiStatusResponse]:
    """Parse WebDAV multistatus XML response."""
    try:
        root = etree.fromstring(xml_data)
    except etree.XMLSyntaxError as e:
        msg = f"Invalid XML: {e}"
        raise ValueError(msg) from e

    responses: list[MultiStatusResponse] = []

    for response_elem in root.findall(".//{DAV:}response"):
        href_elem = response_elem.find("{DAV:}href")
        if href_elem is None or href_elem.text is None:
            continue

        status_elem = response_elem.find("{DAV:}status")
        status = _parse_http_status(
            status_elem.text if status_elem is not None else None
        )
        properties = _extract_propstat_properties(response_elem)

        responses.append(
            MultiStatusResponse(
                href=href_elem.text, status=status, properties=properties, error=None
            )
        )

    return responses


def _extract_prop_value(prop_elem: _Element) -> _Element | str:
    """Extract value from property element.

    Args:
        prop_elem: Property element

    Returns:
        Property value (string or element)
    """
    # If property has children, return the element itself
    if len(prop_elem) > 0:
        return prop_elem

    # Otherwise return text content
    return prop_elem.text or ""


def extract_dav_header(dav_header: str) -> dict[str, bool]:
    """Parse DAV header to extract capabilities.

    Args:
        dav_header: Value of DAV header

    Returns:
        Dictionary of capabilities (e.g., {"1": True, "2": True})
    """
    capabilities = {}
    for part in dav_header.split(","):
        part = part.strip()
        if part:
            capabilities[part] = True
    return capabilities


def build_if_header(
    lock_token: str | list[tuple[str | None, list[str]]], etag: str | None = None
) -> str:
    """Build If header for conditional requests.

    Args:
        lock_token: Either a simple lock token string, or a list of (resource, [tokens/etags]) tuples
                   for complex conditions
        etag: Optional ETag for simple case

    Returns:
        If header value

    Examples:
        ("token1",) -> "(<token1>)"
        ("token1", "etag1") -> "(<token1> [etag1])"
        [("path1", ["token1"]), ("path2", ["token2"])] -> "<path1> (<token1>) <path2> (<token2>)"
    """
    # Simple case: single lock token with optional etag
    if isinstance(lock_token, str):
        if etag:
            return f"(<{lock_token}> [{etag}])"
        return f"(<{lock_token}>)"

    # Complex case: list of conditions
    parts: list[str] = []
    for resource, tokens in lock_token:
        if resource:
            parts.append(f"<{resource}>")

        token_parts: list[str] = []
        for token in tokens:
            if token.startswith('"'):
                # ETag
                token_parts.append(f"[{token}]")
            else:
                # Lock token
                token_parts.append(f"<{token}>")

        parts.append(f"({' '.join(token_parts)})")

    return " ".join(parts)


def parse_lock_response(xml_data: bytes) -> tuple[str | None, str]:
    """Parse LOCK response to extract lock token and scope.

    Args:
        xml_data: XML response body from LOCK request

    Returns:
        Tuple of (lock_token, scope) where scope is "exclusive" or "shared"
    """
    try:
        root = etree.fromstring(xml_data)
    except etree.XMLSyntaxError:
        return None, "exclusive"

    # Find lock token - typically in activelock/locktoken/href
    token_elem = root.find(".//{DAV:}locktoken/{DAV:}href")
    if token_elem is None:
        # Try alternative path
        token_elem = root.find(".//{DAV:}activelock/{DAV:}locktoken/{DAV:}href")

    token = None
    if token_elem is not None and token_elem.text:
        token = token_elem.text.strip()

    # Find scope
    scope = "exclusive"
    if root.find(".//{DAV:}lockscope/{DAV:}shared") is not None:
        scope = "shared"

    return token, scope


def is_wellformed_xml(xml_data: bytes) -> bool:
    """Check if XML is well-formed.

    Args:
        xml_data: XML data to check

    Returns:
        True if well-formed, False otherwise
    """
    try:
        etree.fromstring(xml_data)
        return True
    except etree.XMLSyntaxError:
        return False
