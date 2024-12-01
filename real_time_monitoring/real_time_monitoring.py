from prometheus_client import start_http_server, Gauge, Counter, Histogram
import random
import time
import logging
from typing import Optional
import threading
from contextlib import contextmanager

class MonitoringError(Exception):
    """Custom exception for monitoring errors."""
    pass

class MetricsMonitor:
    """Class to handle real-time metrics monitoring."""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.logger = logging.getLogger(__name__)
        self._setup_metrics()
        self._server_started = False
        self._lock = threading.Lock()
        
    def _setup_metrics(self):
        """Initialize Prometheus metrics."""
        self.compliance_gauge = Gauge(
            'ai_model_compliance',
            'Compliance of AI models'
        )
        self.request_counter = Counter(
            'ai_model_requests',
            'Number of requests to the AI model'
        )
        self.latency_histogram = Histogram(
            'ai_model_latency',
            'Latency of AI model requests',
            buckets=[0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
        )
        
    def start_server(self):
        """Start the Prometheus metrics server."""
        with self._lock:
            if not self._server_started:
                try:
                    start_http_server(self.port)
                    self._server_started = True
                    self.logger.info(f"Metrics server started on port {self.port}")
                except Exception as e:
                    self.logger.error(f"Failed to start metrics server: {e}")
                    raise MonitoringError(f"Server startup failed: {str(e)}")
                
    def update_metrics(self):
        """Update monitoring metrics with new values."""
        try:
            self.compliance_gauge.set(random.uniform(0, 1))
            self.request_counter.inc(random.randint(1, 10))
            self.latency_histogram.observe(random.uniform(0.1, 1.0))
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
            raise MonitoringError(f"Metric update failed: {str(e)}")
            
    @contextmanager
    def monitor_session(self, duration: float):
        """Context manager for monitoring session."""
        try:
            self.start_server()
            yield self
        finally:
            self.logger.info("Monitoring session completed")

def monitor_metrics(duration: float = 10):
    """
    Monitor metrics for a specified duration.
    
    Args:
        duration: Time in seconds to run monitoring
    
    Raises:
        MonitoringError: If monitoring fails
    """
    monitor = MetricsMonitor()
    
    with monitor.monitor_session(duration):
        end_time = time.time() + duration
        while time.time() < end_time:
            try:
                monitor.update_metrics()
                time.sleep(1)
            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                # Continue monitoring despite errors
                continue

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start monitoring
    monitor_metrics()
    