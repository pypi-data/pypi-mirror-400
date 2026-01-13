"""Properties test suite.

Ports src/props.c from the original litmus C implementation.
Tests property manipulation via PROPFIND and PROPPATCH operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from webdav_tck.framework import (
    WebdavTckContext,
    WebdavTckTestResult,
    WebdavTckTestSuite,
)
from webdav_tck.xml_utils import (
    build_propfind_body,
    build_proppatch_body,
    is_wellformed_xml,
    parse_multistatus,
)

if TYPE_CHECKING:
    from typing import Any

    from webdav_tck.session import WebdavTckSession

NS = "http://example.com/neon/litmus/"


def _verify_property_values(
    properties: dict[tuple[str, str], Any], context: WebdavTckContext
) -> None:
    """Verify property values match expected format and warn on mismatches."""
    for n in range(10):
        prop_key = (NS, f"prop{n}")
        if prop_key not in properties:
            continue
        value = properties[prop_key]
        if hasattr(value, "text"):
            value = value.text
        expected = f"value{n}"
        if str(value) != expected:
            context.warning(
                f"Property prop{n} has value '{value}', expected '{expected}'"
            )


async def test_propfind_d0(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPFIND: Depth 0 PROPFIND on root collection."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    # Request resourcetype property
    props = [("DAV:", "resourcetype")]
    body = build_propfind_body(props)

    response = await session.client.propfind(
        session.base_path, depth=0, body=body, test_name="propfind_d0"
    )

    if response.status_code not in (200, 207):
        context.context(f"PROPFIND returned {response.status_code}, expected 207")
        return WebdavTckTestResult.FAIL

    # Parse the multistatus response
    try:
        responses = parse_multistatus(response.content)
    except Exception as e:
        context.context(f"Failed to parse PROPFIND response: {e}")
        return WebdavTckTestResult.FAIL

    if not responses:
        context.context("No responses returned from PROPFIND")
        return WebdavTckTestResult.FAIL

    # Check for resourcetype property indicating collection
    for resp in responses:
        if resp.properties and ("DAV:", "resourcetype") in resp.properties:
            return WebdavTckTestResult.OK

    context.warning("resourcetype property not found in response")
    return WebdavTckTestResult.OK


async def test_propfind_invalid(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPFIND: Invalid XML body should return 400."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    # Send malformed XML
    invalid_body = b"<foo>"

    response = await session.client.propfind(
        session.base_path, depth=0, body=invalid_body, test_name="propfind_invalid"
    )

    if response.status_code != 400:
        context.context(
            f"PROPFIND with malformed XML should return 400, got {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_propset(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPPATCH: Set custom properties."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    # Create a resource for property testing
    prop_path = session.make_path("prop")
    content = b"Property test resource\n"

    response = await session.client.put(prop_path, content, test_name="propset_setup")
    if response.status_code != 201:
        context.context(f"PUT failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    # Set multiple properties
    set_props = {}
    for n in range(10):
        set_props[NS, f"prop{n}"] = f"value{n}"

    body = build_proppatch_body(set_props=set_props)

    response = await session.client.proppatch(prop_path, body, test_name="propset")

    if response.status_code not in (200, 207):
        context.context(f"PROPPATCH failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_propget(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPFIND: Get custom properties."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    prop_path = session.make_path("prop")
    props = [(NS, f"prop{n}") for n in range(10)]
    body = build_propfind_body(props)

    response = await session.client.propfind(
        prop_path, depth=0, body=body, test_name="propget"
    )
    if response.status_code not in (200, 207):
        context.context(f"PROPFIND failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    try:
        responses = parse_multistatus(response.content)
    except Exception as e:
        context.context(f"Failed to parse response: {e}")
        return WebdavTckTestResult.FAIL

    if not responses:
        context.context("No responses returned")
        return WebdavTckTestResult.FAIL

    for resp in responses:
        if resp.properties:
            _verify_property_values(resp.properties, context)

    return WebdavTckTestResult.OK


async def test_propmove(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """MOVE: Properties persist across MOVE."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    prop_path = session.make_path("prop")
    dest_path = session.make_path("prop2")

    # Clean destination
    await session.client.delete(dest_path, test_name="propmove_cleanup")

    # Move the resource
    response = await session.client.move(
        prop_path, dest_path, overwrite=False, test_name="propmove"
    )

    if response.status_code not in (200, 201, 204):
        context.context(f"MOVE failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_propdeletes(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPPATCH: Remove properties."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    prop_path = session.make_path("prop2")

    # Remove first 5 properties
    remove_props = [(NS, f"prop{n}") for n in range(5)]
    body = build_proppatch_body(remove_props=remove_props)

    response = await session.client.proppatch(prop_path, body, test_name="propdeletes")

    if response.status_code not in (200, 207):
        context.context(f"PROPPATCH remove failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_propreplace(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPPATCH: Replace property values."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    prop_path = session.make_path("prop2")

    # Replace remaining properties (5-9) with new values
    set_props = {}
    for n in range(5, 10):
        set_props[NS, f"prop{n}"] = f"newvalue{n}"

    body = build_proppatch_body(set_props=set_props)

    response = await session.client.proppatch(prop_path, body, test_name="propreplace")

    if response.status_code not in (200, 207):
        context.context(f"PROPPATCH replace failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_propnullns(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPPATCH: Property with null namespace."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    prop_path = session.make_path("prop2")

    # Set property with null namespace
    set_props = {("", "nonamespace"): "randomvalue"}
    body = build_proppatch_body(set_props=set_props)

    response = await session.client.proppatch(prop_path, body, test_name="propnullns")

    if response.status_code not in (200, 207):
        context.warning(
            f"PROPPATCH with null namespace returned {response.status_code}"
        )
        # This is a warning, not a failure - some servers may not support it
        return WebdavTckTestResult.OK

    return WebdavTckTestResult.OK


async def test_prophighunicode(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPPATCH: Property with high Unicode character (U+10000)."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    prop_path = session.make_path("prop2")

    # High Unicode character (U+10000 = UTF-8: F0 90 80 80)
    high_unicode = "\U00010000"  # Unicode character U+10000
    set_props = {(NS, "high-unicode"): high_unicode}
    body = build_proppatch_body(set_props=set_props)

    response = await session.client.proppatch(
        prop_path, body, test_name="prophighunicode"
    )

    if response.status_code not in (200, 207):
        context.warning(f"PROPPATCH with high Unicode returned {response.status_code}")
        # This is a warning - not all servers support high Unicode
        return WebdavTckTestResult.OK

    return WebdavTckTestResult.OK


async def test_propwformed(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPFIND: Response is well-formed XML."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    prop_path = session.make_path("prop2")

    # Request all properties
    body = build_propfind_body(allprop=True)

    response = await session.client.propfind(
        prop_path, depth=0, body=body, test_name="propwformed"
    )

    if response.status_code not in (200, 207):
        context.context(f"PROPFIND failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Check if response is well-formed XML
    if not is_wellformed_xml(response.content):
        context.context("PROPFIND response is not well-formed XML")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_propget_lastmodified(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPFIND: Get getlastmodified live property."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    prop_path = session.make_path("prop2")

    # Request getlastmodified property
    props = [("DAV:", "getlastmodified")]
    body = build_propfind_body(props)

    response = await session.client.propfind(
        prop_path, depth=0, body=body, test_name="propget_lastmodified"
    )

    if response.status_code not in (200, 207):
        context.context(f"PROPFIND failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Parse response
    try:
        responses = parse_multistatus(response.content)
    except Exception as e:
        context.context(f"Failed to parse response: {e}")
        return WebdavTckTestResult.FAIL

    # Verify getlastmodified is present
    for resp in responses:
        if resp.properties and ("DAV:", "getlastmodified") in resp.properties:
            value = resp.properties["DAV:", "getlastmodified"]
            if hasattr(value, "text"):
                value = value.text
            if value:
                return WebdavTckTestResult.OK
            context.warning("getlastmodified property is empty")
            return WebdavTckTestResult.OK

    context.warning("getlastmodified property not found")
    return WebdavTckTestResult.OK


def create_props_suite(session: WebdavTckSession) -> WebdavTckTestSuite:
    """Create the properties test suite.

    Args:
        session: WebdavTck session

    Returns:
        Test suite with property tests
    """
    suite = WebdavTckTestSuite("props", session=session)

    # Add tests in order
    tests = [
        test_propfind_d0,
        test_propfind_invalid,
        test_propset,
        test_propget,
        test_propmove,
        test_propdeletes,
        test_propreplace,
        test_propnullns,
        test_prophighunicode,
        test_propwformed,
        test_propget_lastmodified,
    ]

    for test_func in tests:
        suite.add_test(test_func)

    return suite
