"""
SKU Template Client SDK

A Python SDK for managing AppID resources with support for concurrent access and product isolation.
Includes SKU query framework, HTML report generation, and AppID management service.
"""

from .client import AppIdClient
from .sku_query_framework import SkuQueryFactory
from .html_report_generator import HTMLReportGenerator, ComparisonConfig, ComparisonItem, load_report_config_from_business

__version__ = "1.0.3"
__author__ = "ouyangrunli"
__email__ = "ouyangrunli@agora.com"

__all__ = [
    "AppIdClient",
    "SkuQueryFactory",
    "HTMLReportGenerator",
    "ComparisonConfig",
    "ComparisonItem",
    "load_report_config_from_business",
]
