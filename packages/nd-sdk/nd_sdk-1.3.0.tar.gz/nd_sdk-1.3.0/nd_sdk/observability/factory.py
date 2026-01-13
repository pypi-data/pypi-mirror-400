from ..utils.singleton import singleton

@singleton
def get_logger(provider):
    print(f"Provider: {provider}")
    if provider == "std":
        from .logging.std_logger import StdLogger
        return StdLogger()
    if provider == "azure_app_insights":
        from .logging.azure_app_insights_logger import AppInsightsLogger
        return AppInsightsLogger(name='PythonFrameworkLogger')
    if provider == "otel":
        from .logging.otel_logger import OTELLogger
        return OTELLogger()
    raise ValueError(f"Unknown logger provider: {provider}")

@singleton
def get_tracer(provider="otel"):
    from .tracing.otel_tracer import OTELTracer
    return OTELTracer.get_instance()

@singleton
def get_metrics(provider="otel"):
    from .metrics.otel_metrics import OTELMetrics
    return OTELMetrics.get_instance()
