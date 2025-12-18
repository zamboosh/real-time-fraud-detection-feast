# Fraud Detection Feast - Helm Chart

This Helm chart deploys the Real-Time Fraud Detection service with Feast to Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+

## Installation

### From GitHub Container Registry (Recommended)

Once published, install directly from GHCR:

```bash
# Install the latest version
helm install fraud-detection oci://ghcr.io/zamboosh/fraud-detection-feast

# Install a specific version
helm install fraud-detection oci://ghcr.io/zamboosh/fraud-detection-feast --version 0.1.0

# Install with custom values
helm install fraud-detection oci://ghcr.io/zamboosh/fraud-detection-feast \
  --set image.repository=zamboosh/fraud-detection-feast \
  --set replicaCount=3
```

### From Local Chart (Development)

```bash
# Install with default values
helm install fraud-detection .

# Install with custom values
helm install fraud-detection . \
  --set image.repository=your-username/fraud-detection-feast \
  --set replicaCount=3
```

### Using a Custom Values File

```bash
helm install fraud-detection . -f custom-values.yaml
```

## Configuration

See [values.yaml](./values.yaml) for all available configuration options.

### Common Configurations

#### Enable Ingress

```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: fraud-detection.example.com
      paths:
        - path: /
          pathType: Prefix
```

#### Enable Autoscaling

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

#### Adjust Resources

```yaml
resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 1000m
    memory: 1Gi
```

## Upgrading

```bash
helm upgrade fraud-detection .
```

## Uninstalling

```bash
helm uninstall fraud-detection
```

## Testing

```bash
# Lint the chart
helm lint .

# Dry run installation
helm install fraud-detection . --dry-run --debug

# Template rendering
helm template fraud-detection .
```
