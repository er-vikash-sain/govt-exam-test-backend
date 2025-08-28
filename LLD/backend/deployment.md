# Backend LLD - Deployment & DevOps
**Component:** Backend Deployment & Operations
**Technology:** Docker, Kubernetes, GitHub Actions, Monitoring
**Version:** 1.0

---

## 1. Deployment Overview

The backend system is designed for containerized deployment with automated CI/CD pipelines, monitoring, and scalability across different environments.

---

## 2. Environment Strategy

### 2.1 Environment Types
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Development   │    │     Staging     │    │   Production    │
│                 │    │                 │    │                 │
│ • Local Docker  │    │ • K8s Cluster   │    │ • K8s Cluster   │
│ • Hot Reload    │    │ • Test Data     │    │ • Live Data     │
│ • Debug Mode    │    │ • Integration   │    │ • Monitoring    │
│ • Single Node   │    │ • Load Testing  │    │ • Auto-scaling  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 Environment Configuration
- **Development**: Docker Compose with local services
- **Staging**: Kubernetes cluster with test data
- **Production**: Multi-zone Kubernetes cluster with production data

---

## 3. Containerization Strategy

### 3.1 Docker Configuration

#### `Dockerfile`
```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=app:app ./app ./app
COPY --chown=app:app ./alembic ./alembic
COPY --chown=app:app ./alembic.ini .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `docker-compose.yml` (Development)
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/exam_platform
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
    volumes:
      - ./app:/app/app
      - ./alembic:/app/alembic
    depends_on:
      - postgres
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=exam_platform
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery-worker:
    build: .
    command: celery -A app.workers.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/exam_platform
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  celery-beat:
    build: .
    command: celery -A app.workers.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/exam_platform
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

### 3.2 Container Optimization
- **Multi-stage builds** to reduce image size
- **Non-root user** for security
- **Health checks** for container monitoring
- **Layer caching** for faster builds

---

## 4. Kubernetes Deployment

### 4.1 Namespace Structure
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: exam-platform
  labels:
    name: exam-platform
    environment: production
```

### 4.2 ConfigMap for Environment Variables
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
  namespace: exam-platform
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: "https://examplatform.com,https://www.examplatform.com"
  DATABASE_POOL_SIZE: "20"
  REDIS_POOL_SIZE: "10"
```

### 4.3 Secret Management
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
  namespace: exam-platform
type: Opaque
data:
  DATABASE_URL: <base64-encoded-url>
  REDIS_URL: <base64-encoded-url>
  JWT_SECRET: <base64-encoded-secret>
  OPENAI_API_KEY: <base64-encoded-key>
  RAZORPAY_KEY_ID: <base64-encoded-key>
  RAZORPAY_KEY_SECRET: <base64-encoded-secret>
```

### 4.4 Deployment Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-api
  namespace: exam-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend-api
  template:
    metadata:
      labels:
        app: backend-api
    spec:
      containers:
      - name: backend-api
        image: examplatform/backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: backend-config
        - secretRef:
            name: backend-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: app-config
          mountPath: /app/config
      volumes:
      - name: app-config
        configMap:
          name: backend-config
```

### 4.5 Service Configuration
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: exam-platform
spec:
  selector:
    app: backend-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### 4.6 Ingress Configuration
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-ingress
  namespace: exam-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.examplatform.com
    secretName: backend-tls
  rules:
  - host: api.examplatform.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

---

## 5. CI/CD Pipeline

### 5.1 GitHub Actions Workflow

#### `.github/workflows/backend.yml`
```yaml
name: Backend CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/backend

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
        
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
      run: |
        pytest tests/ --cov=app --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha,prefix={{branch}}-
          
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add staging deployment commands
        
  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production environment"
        # Add production deployment commands
```

### 5.2 Deployment Strategies
- **Blue-Green Deployment**: Zero-downtime deployments
- **Rolling Updates**: Gradual rollout with health checks
- **Canary Deployment**: Traffic splitting for testing
- **Rollback Strategy**: Quick rollback on failures

---

## 6. Monitoring & Observability

### 6.1 Prometheus Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'backend-api'
      static_configs:
      - targets: ['backend-service:8000']
      metrics_path: /metrics
      scrape_interval: 10s
```

### 6.2 Grafana Dashboards
- **API Performance**: Response times, throughput, error rates
- **Database Metrics**: Connection pools, query performance
- **System Resources**: CPU, memory, disk usage
- **Business Metrics**: User registrations, quiz completions

### 6.3 Alerting Rules
```yaml
groups:
- name: backend-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: High error rate detected
      description: Error rate is {{ $value }} errors per second
      
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: High response time detected
      description: 95th percentile response time is {{ $value }} seconds
```

---

## 7. Database Deployment

### 7.1 PostgreSQL Deployment
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: exam-platform
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: exam_platform
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secrets
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secrets
              key: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

### 7.2 Redis Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: exam-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server", "--appendonly", "yes"]
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
```

---

## 8. Backup & Recovery

### 8.1 Database Backup Strategy
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: exam-platform
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16
            command:
            - /bin/bash
            - -c
            - |
              pg_dump $DATABASE_URL > /backup/backup-$(date +%Y%m%d-%H%M%S).sql
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-secrets
                  key: url
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### 8.2 Recovery Procedures
- **Point-in-time recovery** from backups
- **Automated failover** for high availability
- **Disaster recovery** runbooks
- **Regular recovery testing**

---

## 9. Security Configuration

### 9.1 Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: exam-platform
spec:
  podSelector:
    matchLabels:
      app: backend-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: exam-platform
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector:
        matchLabels:
          name: exam-platform
    ports:
    - protocol: TCP
      port: 6379
```

### 9.2 RBAC Configuration
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: exam-platform
  name: backend-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
```

---

## 10. Performance Optimization

### 10.1 Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: exam-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 10.2 Resource Management
- **CPU and memory limits** for all containers
- **Resource quotas** per namespace
- **Priority classes** for critical workloads
- **Node affinity** for optimal placement

---

## 11. Environment-Specific Configurations

### 11.1 Development Environment
- **Local Docker Compose** setup
- **Hot reload** for development
- **Debug mode** enabled
- **Local database** and Redis

### 11.2 Staging Environment
- **Kubernetes cluster** with test data
- **Integration testing** capabilities
- **Load testing** environment
- **Production-like** configuration

### 11.3 Production Environment
- **Multi-zone Kubernetes** cluster
- **Production data** and configurations
- **Monitoring and alerting** enabled
- **Auto-scaling** and load balancing

---

## 12. Next Steps

1. **Set up local development** environment with Docker Compose
2. **Configure Kubernetes** cluster for staging/production
3. **Implement CI/CD** pipeline with GitHub Actions
4. **Set up monitoring** with Prometheus and Grafana
5. **Configure backup** and recovery procedures

---

*This deployment guide provides the foundation for deploying the backend system across different environments with proper monitoring, security, and scalability.*
