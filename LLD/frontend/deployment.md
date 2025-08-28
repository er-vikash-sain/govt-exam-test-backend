# Frontend Deployment LLD
**Component:** Student Portal Frontend Deployment
**Technology:** Next.js 14, React 18, TypeScript, Tailwind CSS
**Version:** 1.0

---

## 1. Deployment Strategy Overview

### 1.1 Deployment Environments
- **Development**: Local development environment
- **Staging**: Pre-production testing environment
- **Production**: Live production environment
- **Preview**: Feature branch preview deployments

### 1.2 Deployment Models
- **Static Export**: Pre-built static files for CDN deployment
- **Server-Side Rendering**: Next.js SSR for dynamic content
- **Edge Runtime**: Vercel Edge Functions for global distribution
- **Hybrid Approach**: Static + dynamic content optimization

---

## 2. Build Configuration

### 2.1 Next.js Configuration
**next.config.js**:
```typescript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Build optimization
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['@heroicons/react', 'lucide-react'],
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
  },
  
  // Image optimization
  images: {
    domains: ['s3.amazonaws.com', 'cdn.examplatform.com'],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  
  // Performance optimization
  compress: true,
  poweredByHeader: false,
  generateEtags: false,
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
  
  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // Webpack configuration
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Custom webpack configuration
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    
    return config;
  },
};

module.exports = nextConfig;
```

### 2.2 Environment Configuration
**Environment Files**:
```bash
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_SENTRY_DSN=
NEXT_PUBLIC_ANALYTICS_ID=

# .env.production
NEXT_PUBLIC_API_URL=https://api.examplatform.com
NEXT_PUBLIC_APP_URL=https://examplatform.com
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_SENTRY_DSN=https://sentry.io/project
NEXT_PUBLIC_ANALYTICS_ID=G-XXXXXXXXXX

# .env.staging
NEXT_PUBLIC_API_URL=https://api-staging.examplatform.com
NEXT_PUBLIC_APP_URL=https://staging.examplatform.com
NEXT_PUBLIC_ENVIRONMENT=staging
NEXT_PUBLIC_SENTRY_DSN=https://sentry.io/project
NEXT_PUBLIC_ANALYTICS_ID=G-XXXXXXXXXX
```

### 2.3 TypeScript Configuration
**tsconfig.json**:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/hooks/*": ["./src/hooks/*"],
      "@/stores/*": ["./src/stores/*"],
      "@/types/*": ["./src/types/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## 3. Build Optimization

### 3.1 Bundle Analysis
**Bundle Analyzer Configuration**:
```typescript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer(nextConfig);
```

**Bundle Analysis Scripts**:
```json
{
  "scripts": {
    "analyze": "ANALYZE=true npm run build",
    "analyze:server": "ANALYZE=true npm run build && npm run start",
    "build:analyze": "npm run build && npm run analyze"
  }
}
```

### 3.2 Code Splitting
**Dynamic Imports**:
```typescript
// components/Charts/ChartContainer.tsx
import dynamic from 'next/dynamic';

const LineChart = dynamic(() => import('./LineChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false,
});

const BarChart = dynamic(() => import('./BarChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false,
});

export function ChartContainer({ type, data }: ChartContainerProps) {
  if (type === 'line') {
    return <LineChart data={data} />;
  }
  
  if (type === 'bar') {
    return <BarChart data={data} />;
  }
  
  return <div>Unsupported chart type</div>;
}
```

**Route-based Code Splitting**:
```typescript
// app/dashboard/page.tsx
import dynamic from 'next/dynamic';

const DashboardContent = dynamic(() => import('@/components/Dashboard/DashboardContent'), {
  loading: () => <DashboardSkeleton />,
  ssr: true,
});

export default function DashboardPage() {
  return <DashboardContent />;
}
```

### 3.3 Tree Shaking
**Package Optimization**:
```typescript
// next.config.js
const nextConfig = {
  experimental: {
    optimizePackageImports: [
      '@heroicons/react',
      'lucide-react',
      '@radix-ui/react-icons',
      'framer-motion',
    ],
  },
};
```

**Import Optimization**:
```typescript
// Good: Tree-shakeable imports
import { useState, useEffect } from 'react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

// Avoid: Non-tree-shakeable imports
import * as React from 'react';
import * as Icons from '@heroicons/react/24/outline';
```

---

## 4. Performance Optimization

### 4.1 Core Web Vitals
**Performance Monitoring**:
```typescript
// lib/performance.ts
export function reportWebVitals(metric: any) {
  if (metric.label === 'web-vital') {
    // Send to analytics
    gtag('event', metric.name, {
      event_category: 'Web Vitals',
      event_label: metric.id,
      value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
      non_interaction: true,
    });
  }
}

// app/layout.tsx
import { reportWebVitals } from '@/lib/performance';

export function reportWebVitals(reportWebVitals);
```

**Image Optimization**:
```typescript
// components/optimized/Image.tsx
import NextImage from 'next/image';
import { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  priority?: boolean;
  className?: string;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  className,
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <NextImage
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        className={`
          duration-700 ease-in-out
          ${isLoading ? 'scale-110 blur-2xl grayscale' : 'scale-100 blur-0 grayscale-0'}
        `}
        onLoadingComplete={() => setIsLoading(false)}
      />
    </div>
  );
}
```

### 4.2 Caching Strategy
**Static Asset Caching**:
```typescript
// next.config.js
const nextConfig = {
  async headers() {
    return [
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};
```

**Service Worker Caching**:
```typescript
// public/sw.js
const CACHE_NAME = 'exam-platform-v1';
const urlsToCache = [
  '/',
  '/static/js/main.bundle.js',
  '/static/css/main.css',
  '/offline.html',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});
```

---

## 5. CI/CD Pipeline

### 5.1 GitHub Actions Workflow
**Frontend Deployment Workflow**:
```yaml
# .github/workflows/frontend-deploy.yml
name: Frontend Deployment

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linting
      run: npm run lint
    
    - name: Run type checking
      run: npm run type-check
    
    - name: Run tests
      run: npm run test:ci
    
    - name: Build application
      run: npm run build
    
    - name: Run bundle analysis
      run: npm run analyze
      if: github.ref == 'refs/heads/main'

  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build application
      run: npm run build:staging
      env:
        NEXT_PUBLIC_ENVIRONMENT: staging
        NEXT_PUBLIC_API_URL: ${{ secrets.STAGING_API_URL }}
    
    - name: Deploy to staging
      run: |
        # Deploy to staging environment
        echo "Deploying to staging..."

  deploy-production:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build application
      run: npm run build:production
      env:
        NEXT_PUBLIC_ENVIRONMENT: production
        NEXT_PUBLIC_API_URL: ${{ secrets.PRODUCTION_API_URL }}
    
    - name: Deploy to production
      run: |
        # Deploy to production environment
        echo "Deploying to production..."
```

### 5.2 Build Scripts
**Package.json Scripts**:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "build:staging": "NODE_ENV=staging next build",
    "build:production": "NODE_ENV=production next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:ci": "jest --ci --coverage",
    "test:watch": "jest --watch",
    "analyze": "ANALYZE=true npm run build",
    "clean": "rm -rf .next out",
    "export": "next build && next export",
    "preview": "npm run build && npm run start"
  }
}
```

---

## 6. Deployment Platforms

### 6.1 Vercel Deployment
**Vercel Configuration**:
```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url",
    "NEXT_PUBLIC_APP_URL": "@app-url"
  },
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    }
  }
}
```

**Environment Variables**:
```bash
# Vercel environment variables
NEXT_PUBLIC_API_URL=https://api.examplatform.com
NEXT_PUBLIC_APP_URL=https://examplatform.com
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_SENTRY_DSN=https://sentry.io/project
NEXT_PUBLIC_ANALYTICS_ID=G-XXXXXXXXXX
```

### 6.2 AWS S3 + CloudFront
**S3 Deployment Script**:
```bash
#!/bin/bash
# deploy-s3.sh

# Build the application
npm run build

# Sync with S3
aws s3 sync out/ s3://exam-platform-frontend --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"

echo "Deployment completed successfully!"
```

**CloudFront Configuration**:
```yaml
# cloudformation/cloudfront.yml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: S3Origin
            DomainName: !GetAtt S3Bucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub 'origin-access-identity/cloudfront/${CloudFrontOAI}'
        
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6 # CachingOptimized
          
        PriceClass: PriceClass_100
        Enabled: true
        DefaultRootObject: index.html
        ErrorPages:
          - ErrorCode: 404
            ResponseCode: 200
            ResponsePagePath: /index.html
```

### 6.3 Docker Deployment
**Dockerfile**:
```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

**Docker Compose**:
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    image: exam-platform-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/exam_platform
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=exam_platform
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## 7. Monitoring & Analytics

### 7.1 Performance Monitoring
**Sentry Integration**:
```typescript
// lib/sentry.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
  tracesSampleRate: 1.0,
  integrations: [
    new Sentry.BrowserTracing({
      tracePropagationTargets: ['localhost', 'examplatform.com'],
    }),
    new Sentry.Replay({
      maskAllText: false,
      blockAllMedia: false,
    }),
  ],
  beforeSend(event) {
    // Filter out sensitive data
    if (event.request?.url) {
      delete event.request.url;
    }
    return event;
  },
});
```

**Google Analytics**:
```typescript
// lib/analytics.ts
export const GA_TRACKING_ID = process.env.NEXT_PUBLIC_ANALYTICS_ID;

export const pageview = (url: string) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('config', GA_TRACKING_ID, {
      page_location: url,
    });
  }
};

export const event = ({ action, category, label, value }: {
  action: string;
  category: string;
  label: string;
  value?: number;
}) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value,
    });
  }
};
```

### 7.2 Error Tracking
**Error Boundary**:
```typescript
// components/ErrorBoundary.tsx
'use client';

import { Component, ErrorInfo, ReactNode } from 'react';
import * as Sentry from '@sentry/nextjs';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    Sentry.captureException(error, { contexts: { react: errorInfo } });
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## 8. Security Configuration

### 8.1 Security Headers
**Next.js Security Headers**:
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'origin-when-cross-origin',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()',
  },
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;",
  },
];

const nextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },
};
```

### 8.2 Environment Security
**Environment Variable Validation**:
```typescript
// lib/env.ts
const requiredEnvVars = [
  'NEXT_PUBLIC_API_URL',
  'NEXT_PUBLIC_APP_URL',
  'NEXT_PUBLIC_ENVIRONMENT',
] as const;

export function validateEnv() {
  const missing = requiredEnvVars.filter(
    (envVar) => !process.env[envVar]
  );
  
  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}`
    );
  }
}

export const env = {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL!,
  NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL!,
  NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT!,
  NEXT_PUBLIC_SENTRY_DSN: process.env.NEXT_PUBLIC_SENTRY_DSN,
  NEXT_PUBLIC_ANALYTICS_ID: process.env.NEXT_PUBLIC_ANALYTICS_ID,
} as const;
```

---

## 9. Testing & Quality Assurance

### 9.1 Testing Configuration
**Jest Configuration**:
```typescript
// jest.config.js
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

module.exports = createJestConfig(customJestConfig);
```

**Playwright E2E Testing**:
```typescript
// tests/e2e/exam-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Exam Flow', () => {
  test('user can complete an exam', async ({ page }) => {
    await page.goto('/exams');
    
    // Select an exam
    await page.click('[data-testid="exam-card"]');
    
    // Start the exam
    await page.click('[data-testid="start-exam"]');
    
    // Answer questions
    await page.click('[data-testid="answer-option"]');
    await page.click('[data-testid="next-question"]');
    
    // Submit exam
    await page.click('[data-testid="submit-exam"]');
    
    // Verify results page
    await expect(page.locator('[data-testid="results-page"]')).toBeVisible();
  });
});
```

---

## 10. Deployment Checklist

### 10.1 Pre-Deployment
- [ ] All tests passing
- [ ] Code linting clean
- [ ] Type checking successful
- [ ] Bundle analysis completed
- [ ] Environment variables configured
- [ ] Security headers configured
- [ ] Performance metrics baseline established

### 10.2 Deployment
- [ ] Staging deployment successful
- [ ] Smoke tests passed
- [ ] Performance metrics acceptable
- [ ] Production deployment initiated
- [ ] Health checks monitoring
- [ ] Error tracking active

### 10.3 Post-Deployment
- [ ] Production deployment verified
- [ ] Performance metrics normal
- [ ] Error rates acceptable
- [ ] User feedback positive
- [ ] Monitoring alerts configured
- [ ] Rollback plan ready

---

*This deployment document provides the operational foundation for frontend deployment and management. Each deployment should follow the established procedures and include proper testing and validation.*
