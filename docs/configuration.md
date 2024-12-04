# Configuration Guide

## Bias Detection Configuration

- **Thresholds and Protected Attributes**: Configure bias detection thresholds and protected attributes in the `config` directory.

Example configuration:
```yaml
bias_detection:
  thresholds:
    demographic_parity: 0.1
    equal_opportunity: 0.1
  protected_attributes:
    - race
    - gender
```

## Privacy Protection Configuration

- **Encryption Settings**: Configure encryption settings and sensitive fields in the `config` directory.

Example configuration:
```yaml
privacy_protection:
  encryption:
    method: AES-GCM
  sensitive_fields:
    - ssn
    - email
    - phone
```

## Governance Policies

- **Policy Files**: Define governance policies in YAML files located in the `config` directory.

Example network policy:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: cloverai-network-policy
spec:
  podSelector:
    matchLabels:
      app: cloverai
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: cloverai
          role: frontend
    ports:
    - protocol: TCP
      port: 3306
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: cloverai
          role: backend
    ports:
    - protocol: TCP
      port: 8080
```

## Monitoring Configuration

- **Prometheus Configuration**: Configure Prometheus metrics and alerting rules in the `config/prometheus.yml` file.

Example configuration:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'cloverai-model-metrics'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - 'alertmanager:9093'
```