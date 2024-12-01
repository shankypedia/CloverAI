# Governance Automation

## Overview

The `governance_automation` module enforces Kubernetes governance policies, ensuring the cluster adheres to defined security and compliance standards.

## Functions

### `enforce_policy(policy_yaml)`

- **Description**: Enforces the specified Kubernetes network policy.
- **Parameters**:
    - `policy_yaml` (str): Path to the YAML file containing the network policy.
- **Usage**:
    ```python
    from governance_automation import enforce_policy
    enforce_policy('config/network_policy.yaml')
    ```

## Example Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: secure-network-policy
    namespace: default
spec:
    podSelector:
        matchLabels:
            role: db
    policyTypes:
    - Ingress
    - Egress
    ingress:
    - from:
        - podSelector:
                matchLabels:
                    role: frontend
        ports:
        - protocol: TCP
            port: 3306
    egress:
    - to:
        - podSelector:
                matchLabels:
                    role: backend
        ports:
        - protocol: TCP
            port: 8080
```
