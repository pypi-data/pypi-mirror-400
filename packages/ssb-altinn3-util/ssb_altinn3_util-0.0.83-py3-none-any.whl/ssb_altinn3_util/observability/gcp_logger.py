import logging.config
from logging import Logger

from opentelemetry.instrumentation.logging import LoggingInstrumentor  # type: ignore
from pythonjsonlogger import jsonlogger


class GcpLogger:
    """Class to create a logger to use for log collection in GCP. Configures correct names, and
    will also connect the log to tracing
    @:param tracing_gcp_project_id The project id where the attached tracing info is stored
            use blank if NA"""

    tracing_gcp_project_id: str

    def __init__(self, tracing_gcp_project_id: str):
        self.tracing_gcp_project_id = tracing_gcp_project_id

    def create_logger(self) -> Logger:
        """Creates a correctly formatted json-logger"""

        LoggingInstrumentor().instrument(set_logging_format=True)
        logger = logging.getLogger()

        # Format the json-payload for GCP-logging, and also connect to tracing
        # According to https://cloud.google.com/logging/docs/agent/logging/configuration the trace field should
        # probably be formatted as projects/<my-projectid>/traces/<traceId>". It might alseo be possible that
        # spanId should be span_id. Not testet from Kubernetes yet
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(threadName) %(module) %(funcName)s %(lineno)d  %(message)s %(otelSpanID) %(otelTraceID)s ",
            rename_fields={
                "levelname": "severity",
                "otelSpanID": "spanId",
                "otelTraceID": "trace",
            },
        )
        logger.handlers[0].setFormatter(formatter)
        return logger
