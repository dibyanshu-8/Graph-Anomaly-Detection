# src/utils/monitoring.py

import prometheus_client
from prometheus_client import generate_latest, REGISTRY

class MetricsCollector:
    """
    A central class to manage and expose Prometheus metrics.
    """
    def __init__(self):
        # Using a dictionary to dynamically create metrics
        self._metrics = {
            'analysis_requests': prometheus_client.Counter(
                'analysis_requests_total', 'Total analysis requests', ['domain']
            ),
            'successful_analyses': prometheus_client.Counter(
                'successful_analyses_total', 'Total successful analyses', ['domain']
            ),
            'analysis_errors': prometheus_client.Counter(
                'analysis_errors_total', 'Total analysis errors', ['domain']
            ),
            'anomalies_detected': prometheus_client.Gauge(
                'anomalies_detected_current', 'Current number of anomalies detected', ['domain']
            )
        }

    def increment(self, metric_name: str, domain: str = "unknown"):
        """Increments a counter metric."""
        if metric_name in self._metrics and isinstance(self._metrics[metric_name], prometheus_client.Counter):
            self._metrics[metric_name].labels(domain=domain).inc()

    def set_gauge(self, metric_name: str, value: float, domain: str = "unknown"):
        """Sets a gauge metric to a specific value."""
        if metric_name in self._metrics and isinstance(self._metrics[metric_name], prometheus_client.Gauge):
            self._metrics[metric_name].labels(domain=domain).set(value)

    def generate_prometheus(self):
        """Generate Prometheus metrics text format."""
        return generate_latest(REGISTRY)

    def start_server(self, port=8001): # Changed port to avoid conflict with API
        """Starts the Prometheus metrics server."""
        prometheus_client.start_http_server(port)
        print(f"Prometheus metrics server started on port {port}")


# --- Singleton Instance ---
metrics_collector = MetricsCollector()