"""
Wedata MLflow Header Plugin

A plugin that adds custom headers to MLflow requests.
"""

__version__ = "0.1.0"

from wedata_mlflow_header_plugin.plugin import WedataRequestHeaderProvider

__all__ = ["WedataRequestHeaderProvider"]

