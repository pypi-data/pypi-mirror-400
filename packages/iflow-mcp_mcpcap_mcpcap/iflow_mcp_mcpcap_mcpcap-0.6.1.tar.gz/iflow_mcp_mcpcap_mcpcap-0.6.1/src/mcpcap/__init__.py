"""mcpcap - A modular Python MCP Server for analyzing PCAP files.

mcpcap provides a comprehensive solution for analyzing network packet captures (PCAP files)
through the Model Context Protocol (MCP). It enables LLMs to perform network traffic analysis
with support for DNS protocol analysis and extensible architecture for additional protocols.

Key Features:
    - Modular architecture for easy protocol extension
    - Robust DNS packet analysis with error handling
    - MCP integration for seamless LLM interaction
    - Security-focused analysis prompts and indicators
    - Support for both .pcap and .pcapng file formats

Example:
    Start the MCP server with a directory containing PCAP files::

        $ mcpcap --pcap-path /path/to/pcap/files

    Then connect with an MCP client to analyze DNS traffic.
"""

# Dynamic version detection
try:
    # First try to import from _version.py (created by setuptools-scm in built packages)
    from ._version import version as __version__
except ImportError:
    try:
        # Fall back to setuptools_scm for development environments
        from setuptools_scm import get_version

        __version__ = get_version(root="..", relative_to=__file__)
    except (ImportError, LookupError):
        # Final fallback for cases where setuptools_scm isn't available
        __version__ = "dev-unknown"

from .cli import main

__all__ = ["main", "__version__"]
