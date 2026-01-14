import logging

from opentelemetry import propagate, trace  # type: ignore
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter  # type: ignore
from opentelemetry.propagators.cloud_trace_propagator import CloudTraceFormatPropagator  # type: ignore
from opentelemetry.sdk.trace import TracerProvider, Tracer  # type: ignore
from opentelemetry.sdk.trace.export import SimpleSpanProcessor  # type: ignore


class GcpTracer:
    """Class to create a tracer to use for trace collection in GCP.
    @:param tracing_gcp_project_id The project id where the traces should be stored"""

    tracing_gcp_project_id: str

    def __init__(self, tracing_gcp_project_id: str):
        self.tracing_gcp_project_id = tracing_gcp_project_id

    def create_tracer(self) -> Tracer:
        """Create tracer.
        Usage: annotage a method ->@tracer.start_as_current_span(f"{appname}/startup")
        """
        logger = logging.getLogger()
        logger.info(f"Initializing tracer on project {self.tracing_gcp_project_id}")
        trace.set_tracer_provider(TracerProvider())
        cloud_trace_exporter = CloudTraceSpanExporter(self.tracing_gcp_project_id)
        trace.get_tracer_provider().add_span_processor(
            SimpleSpanProcessor(cloud_trace_exporter)
        )
        propagate.set_global_textmap(CloudTraceFormatPropagator())
        tracer: Tracer = trace.get_tracer(__name__)
        logger.info(f"Tracer init done!")
        return tracer
