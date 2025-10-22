# src/utils/monitoring.py

import prometheus_client

class MetricsCollector:
    """
    A central class to manage and expose Prometheus metrics.
    This follows a singleton pattern by creating one instance for the app.
    """
    def __init__(self):
        """
        The constructor. This is called when we create an object from this class.
        All metrics are defined here.
        """
        # Metric for total transactions processed
        self.transactions_processed = prometheus_client.Counter(
            'transactions_processed_total',
            'Total number of transactions processed'
        )

        # Metric for anomalies, with a 'domain' label (e.g., fraud, social)
        self.anomalies_detected = prometheus_client.Counter(
            'anomalies_detected_total',
            'Total number of anomalies detected',
            ['domain']
        )

        # Metric to track the time it takes to update the graph
        self.graph_update_latency = prometheus_client.Histogram(
            'graph_update_latency_seconds',
            'Latency of graph update operations'
        )

    def start_server(self, port=8000):
        """Starts the Prometheus metrics server in a separate thread."""
        prometheus_client.start_http_server(port)
        print(f"Prometheus metrics server started on port {port}")


# --- Singleton Instance ---
# Create one single instance of the collector that the entire application can share.
# We import this instance, not the class itself.
metrics_collector = MetricsCollector()