"""
This packages insulates us from actually having to *load* OpenTelemetry,
and also allows any of the Spans, Tracers, etc., to be None with no ill
effect.

* OSpan is an *optional* `opentelemetry.span.Span`
* OTracer is an *optional* `opentelemetry.tracer.Tracer`
* OAttributes is a dict of values allowed by opentelemetry
* OContextManager *could* be the context manager returned by
  `Tracer.start_as_current_span` whose `__enter__` returns a `span`,
  but it could also be a `contextlib.nullcontext` whose `__enter__` returns None.

`OContextManager` is returned by `tracer_span`, and you use it as:
    ```
    with tracer_span(tracer, 'name', ...) as span:
        span_set_attributes(span, ...)
        ...
    ```

When given a `tracer` is None, `span` will be None, otherwise it is
equivalent to `tracer.start_as_current_span(...)`.

The functions `span_set_attributes` etc. are the None-safe versions of
the ordinary methods on spans.
"""

from contextlib import AbstractContextManager, nullcontext
from typing import TYPE_CHECKING, Literal

__all__ = [
    'OSpan',
    'OTracer',
    'OContext',
    'OContextManager',
    'OAttributeValue',
    'OAttributes',
    'get_tracer',
    'span_set_context',
    'span_set_attributes',
    'span_set_attribute',
    'span_set_attributes',
    'span_set_error',
    'span_set_ok',
    'span_start',
    'span_finish',
    'span_end',
    'span_context_manager',
    'span_inject',
]

###############################################################################

if TYPE_CHECKING:
    from opentelemetry import trace
    from opentelemetry.util import types

###############################################################################

type OTracer = trace.Tracer | None
type OSpan = trace.Span | None
type OContext = trace.Context | None
type OAttributeValue = types.AttributeValue
type OAttributes = types.Attributes
type OContextManager = AbstractContextManager[OSpan]
type SpanKind = Literal['INTERNAL', 'SERVER', 'CLIENT', 'PRODUCER', 'CONSUMER']

###############################################################################


def get_tracer(name: str, enabled: bool) -> OTracer:
    if enabled and name:
        from opentelemetry.trace import get_tracer

        return get_tracer(name)
    return None


###############################################################################


def span_context_manager(tracer: OTracer, name: str, *args, **kwargs) -> OContextManager:
    if tracer is not None:
        return tracer.start_as_current_span(name, *args, **kwargs)
    return nullcontext()


def span_start(
    tracer: OTracer,
    name: str,
    context_span: OSpan = None,
    context: OContext = None,
    attributes: OAttributes = None,
    kind: SpanKind = 'INTERNAL',
) -> OSpan:
    if tracer is not None:
        from opentelemetry.trace import SpanKind, set_span_in_context

        span_kind = SpanKind[kind]
        if context_span is not None:
            context = set_span_in_context(context_span)
        return tracer.start_span(name, kind=span_kind, context=context, attributes=attributes)
    return None


def span_inject(span: OSpan, dct: dict) -> None:
    # Inject trace context into WebSocket headers for distributed tracing
    # This must happen AFTER setting the connection_span as the active span
    # so the correct trace context is propagated to the server
    if span is not None:
        from opentelemetry.propagate import inject
        from opentelemetry.trace import set_span_in_context

        context = set_span_in_context(span)
        inject(dct, context=context)


def span_finish(span: OSpan, error: BaseException | str | None = None) -> None:
    if span is not None:
        if error is not None:
            span_set_error(span, error)
        else:
            span_set_ok(span)
        span.end()


def span_end(span: OSpan) -> None:
    if span is not None:
        span.end()


################################################################################


def span_set_context(span: OSpan) -> OContext:
    if span is not None:
        from opentelemetry.trace import set_span_in_context

        return set_span_in_context(span)
    return None


def span_set_attribute(span: OSpan, name: str, value: OAttributeValue) -> None:
    if span is not None:
        span.set_attribute(name, value)


def span_set_attributes(span: OSpan, attributes: OAttributes) -> None:
    if span is not None and attributes:
        span.set_attributes(attributes)


def span_set_error(span: OSpan, error: BaseException | str | None = None) -> None:
    if span is not None:
        from opentelemetry.trace import Status, StatusCode

        if isinstance(error, BaseException):
            span.record_exception(error)
            error = str(error)
        elif type(error) is not str:
            error = None
        span.set_status(Status(StatusCode.ERROR, error))


def span_set_ok(span: OSpan) -> None:
    if span is not None:
        from opentelemetry.trace import Status, StatusCode

        span.set_status(Status(StatusCode.OK))


def span_add_link(span: OSpan, link: OSpan) -> None:
    if span is not None and link is not None:
        span.add_link(link.get_span_context())
