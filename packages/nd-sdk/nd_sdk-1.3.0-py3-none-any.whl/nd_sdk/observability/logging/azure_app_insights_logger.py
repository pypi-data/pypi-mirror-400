import os
import logging
from typing import Dict, Optional

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry._logs import set_logger_provider

from .base import BaseLogger


class AppInsightsLogger(BaseLogger):
    """
    Application Insights logger compatible with StdLogger interface
    """

    _configured = False

    def __init__(self, name: str = "nd_sdk"):
        connection_string = os.getenv("AZURE_APPLICATIONINSIGHTS_CONNECTION_STRING")

        if not connection_string:
            raise EnvironmentError(
                "AZURE_APPLICATIONINSIGHTS_CONNECTION_STRING is not set"
            )

        # Configure Azure Monitor only once
        if not AppInsightsLogger._configured:
            configure_azure_monitor(
                connection_string=connection_string
            )

            provider = LoggerProvider()
            set_logger_provider(provider)

            AppInsightsLogger._configured = True

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        # OpenTelemetry → Azure App Insights handler
        otel_handler = LoggingHandler(level=logging.INFO)
        otel_handler.setFormatter(formatter)
        self.logger.addHandler(otel_handler)

        # Optional console logging (can be removed if not needed)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.logger.propagate = False
        self.tracer = trace.get_tracer(name)

    # ---------------------------
    # StdLogger-compatible APIs
    # ---------------------------

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)

    # ---------------------------
    # App Insights extensions
    # ---------------------------

    def track_event(self, event_name: str, properties: Optional[Dict] = None):
        with self.tracer.start_as_current_span(event_name) as span:
            if properties:
                for key, value in properties.items():
                    span.set_attribute(key, value)

    def track_exception(self, exception: Exception):
        self.logger.exception(str(exception))
