# NFO Helm Chart

Network Function Orchestration microservice Helm chart.

## Install

```bash
helm install nfo ./helm-chart
```

## Install with custom values

```bash
helm install nfo ./helm-chart \
  --set image.tag=v1.0.0 \
  --set config.secretKey="your-secret-key" \
  --set config.debug=false
```

## Upgrade

```bash
kubectl create namespace o2
helm upgrade nfo . --namespace o2
```

## Uninstall

```bash
helm uninstall nfo
```

## Configuration

| Parameter             | Description        | Default                  |
| -----------           | -------------      | ---------                |
| `replicaCount`        | Number of replicas | `1`                      |
| `image.repository`    | Image repository   | `nfo`                    |
| `image.tag`           | Image tag          | `latest`                 |
| `service.type`        | Service type       | `ClusterIP`              |
| `service.port`        | Service port       | `8000`                   |
| `ingress.enabled`     | Enable ingress     | `false`                  |
| `persistence.enabled` | Enable persistence | `true`                   |
| `persistence.size`    | PVC size           | `1Gi`                    |
| `config.secretKey`    | Django secret key  | `changeme-in-production` |
| `config.debug`        | Debug mode         | `true`                   |
| `config.allowedHosts` | Allowed hosts      | `*`                      |

## Build and Push Image

```bash
docker build -t nfo:latest .
docker tag nfo:latest your-registry/nfo:latest
docker push your-registry/nfo:latest
```

Update `values.yaml` with your registry:

```yaml
image:
  repository: your-registry/nfo
  tag: latest
```
