"""
URL functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def protocol(url: Union[Column, str]) -> Function:
    """Extracts protocol."""
    return Function("protocol", url)


def domain(url: Union[Column, str]) -> Function:
    """Extracts domain."""
    return Function("domain", url)


def domainWithoutWWW(url: Union[Column, str]) -> Function:
    """Extracts domain without www."""
    return Function("domainWithoutWWW", url)


def topLevelDomain(url: Union[Column, str]) -> Function:
    """Extracts top-level domain."""
    return Function("topLevelDomain", url)


def firstSignificantSubdomain(url: Union[Column, str]) -> Function:
    """First significant subdomain."""
    return Function("firstSignificantSubdomain", url)


def cutToFirstSignificantSubdomain(url: Union[Column, str]) -> Function:
    """Cuts to first significant subdomain."""
    return Function("cutToFirstSignificantSubdomain", url)


def path(url: Union[Column, str]) -> Function:
    """Extracts path."""
    return Function("path", url)


def pathFull(url: Union[Column, str]) -> Function:
    """Extracts full path."""
    return Function("pathFull", url)


def queryString(url: Union[Column, str]) -> Function:
    """Extracts query string."""
    return Function("queryString", url)


def fragment(url: Union[Column, str]) -> Function:
    """Extracts fragment."""
    return Function("fragment", url)


def queryStringAndFragment(url: Union[Column, str]) -> Function:
    """Extracts query and fragment."""
    return Function("queryStringAndFragment", url)


def extractURLParameter(url: Union[Column, str], name: str) -> Function:
    """Extracts URL parameter."""
    return Function("extractURLParameter", url, name)


def extractURLParameters(url: Union[Column, str]) -> Function:
    """Extracts all URL parameters."""
    return Function("extractURLParameters", url)


def extractURLParameterNames(url: Union[Column, str]) -> Function:
    """Extracts URL parameter names."""
    return Function("extractURLParameterNames", url)


def cutURLParameter(url: Union[Column, str], name: str) -> Function:
    """Removes URL parameter."""
    return Function("cutURLParameter", url, name)


def cutWWW(url: Union[Column, str]) -> Function:
    """Removes www."""
    return Function("cutWWW", url)


def cutQueryString(url: Union[Column, str]) -> Function:
    """Removes query string."""
    return Function("cutQueryString", url)


def cutFragment(url: Union[Column, str]) -> Function:
    """Removes fragment."""
    return Function("cutFragment", url)


def cutQueryStringAndFragment(url: Union[Column, str]) -> Function:
    """Removes query and fragment."""
    return Function("cutQueryStringAndFragment", url)


def decodeURLComponent(url: Union[Column, str]) -> Function:
    """Decodes URL component."""
    return Function("decodeURLComponent", url)


def encodeURLComponent(url: Union[Column, str]) -> Function:
    """Encodes URL component."""
    return Function("encodeURLComponent", url)

