# setups tracer for different agent frameworks

import base64
import os

from arize.otel import Endpoint, Transport
from arize.otel.otel import PROJECT_NAME
from arize.otel.otel import BatchSpanProcessor as ArizeBatchSpanProcessor
from arize.otel.otel import TracerProvider as ArizeTracerProvider
from dotenv import load_dotenv
from openinference.instrumentation.crewai import CrewAIInstrumentor
from opentelemetry import context as otel_context
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as GrpcSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

load_dotenv()


class SessionIDProcessor(SpanProcessor):
    def on_start(self, span, parent_context=None):
        ctx = parent_context or otel_context.get_current()
        sess = ctx.get("session.id")
        if sess:
            span.set_attribute("session.id", sess)


def _setup_langfuse_sink():
    lf_public = os.getenv("LANGFUSE_PUBLIC_KEY")
    lf_secret = os.getenv("LANGFUSE_SECRET_KEY")
    lf_base_url = os.getenv("LANGFUSE_HOST").rstrip("/")
    if not lf_public or not lf_secret or not lf_base_url:
        raise RuntimeError(
            "Langfuse credentials missing. Please set LANGFUSE_PUBLIC_KEY, "
            "LANGFUSE_SECRET_KEY and LANGFUSE_HOST in the environment."
        )

    OTEL_ENDPOINT = f"{lf_base_url}/api/public/otel/v1/traces"
    auth_bytes = f"{lf_public}:{lf_secret}".encode("utf-8")
    auth_b64 = base64.b64encode(auth_bytes).decode("ascii")
    HEADERS = {"Authorization": f"Basic {auth_b64}"}
    return OTEL_ENDPOINT, HEADERS


def setup_langgraph_tracer_arize(project_name: str):
    memory_exporter = InMemorySpanExporter()
    headers = {
        "authorization": os.environ["ARIZE_API_KEY"],
        "api_key": os.environ[
            "ARIZE_API_KEY"
        ],  # deprecated, will remove in future release
        "arize-space-id": os.environ["ARIZE_SPACE_ID"],
        "space_id": os.environ[
            "ARIZE_SPACE_ID"
        ],  # deprecated, will remove in future release
        "arize-interface": "otel",
    }
    grpc_span_exporter = GrpcSpanExporter(
        endpoint=Endpoint.ARIZE, insecure=False, headers=headers
    )

    resource = Resource.create({PROJECT_NAME: project_name})
    tracer_provider = ArizeTracerProvider(
        space_id=os.environ["ARIZE_SPACE_ID"],
        api_key=os.environ["ARIZE_API_KEY"],
        project_name=project_name,
        endpoint=Endpoint.ARIZE,
        transport=Transport.GRPC,
        resource=resource,
        verbose=False,
    )

    for exporter in [memory_exporter, grpc_span_exporter]:
        tracer_provider.add_span_processor(
            ArizeBatchSpanProcessor(
                space_id=os.environ["ARIZE_SPACE_ID"],
                api_key=os.environ["ARIZE_API_KEY"],
                endpoint=Endpoint.ARIZE,
                transport=Transport.GRPC,
                headers=None,
                span_exporter=exporter,
            )
        )

    return resource, memory_exporter, grpc_span_exporter, tracer_provider


def setup_langgraph_tracer():
    otel_endpoint, otel_headers = _setup_langfuse_sink()
    from phoenix.otel import register

    tracer_provider = register(
        endpoint=otel_endpoint, headers=otel_headers, auto_instrument=True
    )
    exporter = OTLPSpanExporter(endpoint=otel_endpoint, headers=otel_headers)
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    return tracer_provider


def setup_wxo_tracer():
    return setup_langgraph_tracer()


def setup_langflow_tracer():
    """Langflow starts a tracer on its own"""
    return None


def setup_pydantic_ai_tracer():
    otel_endpoint, otel_headers = _setup_langfuse_sink()
    from openinference.instrumentation.pydantic_ai import (
        OpenInferenceSpanProcessor,
    )

    tracer_provider = TracerProvider()
    exporter = OTLPSpanExporter(endpoint=otel_endpoint, headers=otel_headers)
    tracer_provider.add_span_processor(
        span_processor=OpenInferenceSpanProcessor()
    )
    tracer_provider.add_span_processor(span_processor=SessionIDProcessor())
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(tracer_provider)
    return tracer_provider


def setup_crewai_tracer():
    from openinference.instrumentation.crewai import CrewAIInstrumentor

    otel_endpoint, otel_headers = _setup_langfuse_sink()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(
            OTLPSpanExporter(endpoint=otel_endpoint, headers=otel_headers)
        )
    )

    CrewAIInstrumentor().instrument(tracer_provider=tracer_provider)
    return tracer_provider


def setup_claude_agent_tracer():
    otel_endpoint, otel_headers = _setup_langfuse_sink()
    from dotenv import load_dotenv

    load_dotenv()

    # Set environment variables for LangChain
    os.environ["LANGSMITH_OTEL_ENABLED"] = "true"
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_OTEL_ONLY"] = "true"

    # Custom span processor to map session id to langfuse
    class LangsmithSessionToLangfuseProcessor(SpanProcessor):
        def on_start(self, span, parent_context=None):
            ctx = parent_context or otel_context.get_current()
            sess = ctx.get("session.id")
            # sess = "test"
            if sess:
                span.set_attribute("session.id", sess)

    # Configure the OTLP exporter for your custom endpoint
    provider = TracerProvider()
    otlp_exporter = OTLPSpanExporter(
        endpoint=otel_endpoint, headers=otel_headers
    )
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(LangsmithSessionToLangfuseProcessor())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    from langsmith.integrations.claude_agent_sdk import (
        configure_claude_agent_sdk,
    )

    configure_claude_agent_sdk()

    return provider
