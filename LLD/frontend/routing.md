# Frontend Routing LLD
**Component:** Student Portal Routing & Navigation
**Technology:** Next.js 14 App Router, React 18, TypeScript
**Version:** 1.0

---

## 1. Routing Architecture Overview

### 1.1 Next.js App Router Structure
The frontend uses Next.js 14 App Router with file-based routing, providing:
- **Server Components**: Default server-side rendering
- **Client Components**: Interactive client-side components
- **Route Groups**: Logical grouping of related routes
- **Dynamic Routes**: Parameterized route segments
- **Parallel Routes**: Simultaneous route rendering

### 1.2 Route Organization
```
app/
├── (auth)/                    # Authentication route group
├── (dashboard)/               # Dashboard route group
├── (exam)/                    # Exam-related route group
├── (public)/                  # Public route group
├── api/                       # API routes
├── globals.css                # Global styles
├── layout.tsx                 # Root layout
└── page.tsx                   # Home page
```

---

## 2. Route Groups & Organization

### 2.1 Authentication Routes `(auth)/`
**Purpose**: User authentication and account management
**Routes**:
```
(auth)/
├── login/
│   ├── page.tsx              # Login page
│   ├── loading.tsx           # Loading state
│   └── error.tsx             # Error handling
├── register/
│   ├── page.tsx              # Registration page
│   └── verify/
│       └── page.tsx          # Email verification
├── forgot-password/
│   ├── page.tsx              # Password reset request
│   └── reset/
│       └── [token]/
│           └── page.tsx      # Password reset form
└── layout.tsx                # Auth layout wrapper
```

**Auth Layout Features**:
- Minimal header and footer
- Authentication state management
- Redirect logic for authenticated users
- Error boundary for auth failures

### 2.2 Dashboard Routes `(dashboard)/`
**Purpose**: Main user dashboard and profile management
**Routes**:
```
(dashboard)/
├── dashboard/
│   ├── page.tsx              # Dashboard home
│   ├── loading.tsx           # Loading state
│   └── error.tsx             # Error handling
├── profile/
│   ├── page.tsx              # User profile
│   ├── edit/
│   │   └── page.tsx          # Profile editing
│   └── settings/
│       └── page.tsx          # User preferences
├── progress/
│   ├── page.tsx              # Progress overview
│   ├── topics/
│   │   └── [topicId]/
│   │       └── page.tsx      # Topic progress details
│   └── achievements/
│       └── page.tsx          # Achievement tracking
└── layout.tsx                # Dashboard layout wrapper
```

**Dashboard Layout Features**:
- Full application header and navigation
- Sidebar navigation for dashboard sections
- User authentication verification
- Breadcrumb navigation

### 2.3 Exam Routes `(exam)/`
**Purpose**: Exam discovery, taking, and results
**Routes**:
```
(exam)/
├── exams/
│   ├── page.tsx              # Exam list/browser
│   ├── [examId]/
│   │   ├── page.tsx          # Exam details
│   │   ├── preview/
│   │   │   └── page.tsx      # Exam preview
│   │   └── quiz/
│   │       ├── page.tsx      # Quiz interface
│   │       ├── [questionId]/
│   │       │   └── page.tsx  # Individual question
│   │       └── review/
│   │           └── page.tsx  # Quiz review
│   └── generate/
│       └── page.tsx          # AI quiz generation
├── results/
│   ├── page.tsx              # Results list
│   ├── [resultId]/
│   │   ├── page.tsx          # Result details
│   │   ├── analysis/
│   │   │   └── page.tsx      # Detailed analysis
│   │   └── pdf/
│   │       └── page.tsx      # PDF download
│   └── compare/
│       └── page.tsx          # Result comparison
├── study-plan/
│   ├── page.tsx              # Study plan overview
│   ├── create/
│   │   └── page.tsx          # Plan creation
│   └── [planId]/
│       ├── page.tsx          # Plan details
│       └── edit/
│           └── page.tsx      # Plan editing
└── layout.tsx                # Exam layout wrapper
```

**Exam Layout Features**:
- Exam-specific navigation
- Progress tracking during quizzes
- Timer and navigation controls
- Results and analysis tools

### 2.4 Public Routes `(public)/`
**Purpose**: Publicly accessible content and marketing
**Routes**:
```
(public)/
├── about/
│   └── page.tsx              # About page
├── features/
│   └── page.tsx              # Feature overview
├── pricing/
│   └── page.tsx              # Pricing plans
├── contact/
│   └── page.tsx              # Contact information
├── help/
│   ├── page.tsx              # Help center
│   ├── faq/
│   │   └── page.tsx          # Frequently asked questions
│   └── tutorials/
│       └── page.tsx          # User tutorials
└── layout.tsx                # Public layout wrapper
```

**Public Layout Features**:
- Marketing-focused header
- Call-to-action elements
- SEO optimization
- Social media integration

---

## 3. Dynamic Routes & Parameters

### 3.1 Route Parameters
**Dynamic Segments**:
```typescript
// [examId] - Dynamic exam identifier
interface ExamParams {
  examId: string;
}

// [questionId] - Dynamic question identifier
interface QuestionParams {
  examId: string;
  questionId: string;
}

// [resultId] - Dynamic result identifier
interface ResultParams {
  resultId: string;
}
```

**Parameter Validation**:
```typescript
// app/exams/[examId]/page.tsx
interface ExamPageProps {
  params: Promise<ExamParams>;
  searchParams: Promise<SearchParams>;
}

export default async function ExamPage({ params, searchParams }: ExamPageProps) {
  const { examId } = await params;
  
  // Validate examId format
  if (!isValidExamId(examId)) {
    notFound();
  }
  
  // Fetch exam data
  const exam = await getExam(examId);
  
  if (!exam) {
    notFound();
  }
  
  return <ExamDetails exam={exam} />;
}
```

### 3.2 Search Parameters
**Query String Handling**:
```typescript
// app/exams/page.tsx
interface ExamsPageProps {
  searchParams: Promise<{
    category?: string;
    difficulty?: string;
    search?: string;
    page?: string;
    sort?: string;
  }>;
}

export default async function ExamsPage({ searchParams }: ExamsPageProps) {
  const { category, difficulty, search, page, sort } = await searchParams;
  
  // Build filter object
  const filters = {
    category: category || undefined,
    difficulty: difficulty || undefined,
    search: search || undefined,
    page: parseInt(page || '1'),
    sort: sort || 'popular'
  };
  
  // Fetch filtered exams
  const exams = await getExams(filters);
  
  return <ExamBrowser exams={exams} filters={filters} />;
}
```

---

## 4. Route Protection & Authentication

### 4.1 Authentication Guards
**Route Protection**:
```typescript
// app/(dashboard)/layout.tsx
import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();
  
  if (!user) {
    redirect('/login');
  }
  
  if (!user.isVerified) {
    redirect('/verify-email');
  }
  
  return (
    <DashboardLayoutWrapper>
      {children}
    </DashboardLayoutWrapper>
  );
}
```

**Role-Based Access**:
```typescript
// app/admin/layout.tsx
import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();
  
  if (!user || user.role !== 'admin') {
    redirect('/dashboard');
  }
  
  return (
    <AdminLayoutWrapper>
      {children}
    </AdminLayoutWrapper>
  );
}
```

### 4.2 Middleware Protection
**Global Middleware**:
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('auth-token');
  
  // Protected routes
  if (pathname.startsWith('/dashboard') || pathname.startsWith('/exam')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }
  
  // Admin routes
  if (pathname.startsWith('/admin')) {
    if (!token || !isAdmin(token)) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/exam/:path*',
    '/admin/:path*',
    '/profile/:path*'
  ],
};
```

---

## 5. Navigation & Routing Patterns

### 5.1 Programmatic Navigation
**Client-Side Navigation**:
```typescript
'use client';

import { useRouter, useSearchParams } from 'next/navigation';

export function ExamFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const updateFilters = (newFilters: Partial<FilterState>) => {
    const params = new URLSearchParams(searchParams);
    
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    });
    
    router.push(`/exams?${params.toString()}`);
  };
  
  return (
    <FilterControls onFilterChange={updateFilters} />
  );
}
```

**Server-Side Redirects**:
```typescript
// app/exam/[examId]/quiz/page.tsx
import { redirect } from 'next/navigation';
import { getExamSession } from '@/lib/exam';

export default async function QuizPage({ params }: { params: Promise<{ examId: string }> }) {
  const { examId } = await params;
  const session = await getExamSession(examId);
  
  if (!session) {
    redirect(`/exams/${examId}`);
  }
  
  if (session.status === 'completed') {
    redirect(`/results/${session.resultId}`);
  }
  
  return <QuizInterface examId={examId} session={session} />;
}
```

### 5.2 Breadcrumb Navigation
**Dynamic Breadcrumbs**:
```typescript
// components/navigation/Breadcrumbs.tsx
interface BreadcrumbItem {
  label: string;
  href?: string;
  current?: boolean;
}

export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav className="flex" aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-center">
            {index > 0 && <ChevronRightIcon className="h-4 w-4 text-gray-400" />}
            {item.current ? (
              <span className="text-gray-500">{item.label}</span>
            ) : (
              <Link href={item.href!} className="text-blue-600 hover:text-blue-800">
                {item.label}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
```

---

## 6. Error Handling & Loading States

### 6.1 Error Boundaries
**Route Error Handling**:
```typescript
// app/exam/[examId]/error.tsx
'use client';

export default function ExamError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <h2 className="text-xl font-semibold text-red-600">
        Something went wrong loading this exam
      </h2>
      <p className="text-gray-600 mt-2">
        {error.message}
      </p>
      <button
        onClick={reset}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Try again
      </button>
    </div>
  );
}
```

**Global Error Handling**:
```typescript
// app/global-error.tsx
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <div className="flex flex-col items-center justify-center min-h-screen">
          <h2 className="text-2xl font-bold text-red-600">
            Something went wrong
          </h2>
          <button
            onClick={reset}
            className="mt-4 px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
```

### 6.2 Loading States
**Route Loading**:
```typescript
// app/exam/[examId]/loading.tsx
export default function ExamLoading() {
  return (
    <div className="flex flex-col space-y-4 p-6">
      <div className="h-8 bg-gray-200 rounded animate-pulse" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
      <div className="h-32 bg-gray-200 rounded animate-pulse" />
    </div>
  );
}
```

**Suspense Boundaries**:
```typescript
// app/exam/[examId]/page.tsx
import { Suspense } from 'react';
import { ExamDetails } from '@/components/exam/ExamDetails';
import { ExamLoading } from '@/components/exam/ExamLoading';

export default function ExamPage({ params }: { params: Promise<{ examId: string }> }) {
  return (
    <Suspense fallback={<ExamLoading />}>
      <ExamDetails params={params} />
    </Suspense>
  );
}
```

---

## 7. SEO & Meta Tags

### 7.1 Dynamic Meta Tags
**Page Metadata**:
```typescript
// app/exam/[examId]/page.tsx
import { Metadata } from 'next';

interface ExamPageProps {
  params: Promise<{ examId: string }>;
}

export async function generateMetadata({ params }: ExamPageProps): Promise<Metadata> {
  const { examId } = await params;
  const exam = await getExam(examId);
  
  if (!exam) {
    return {
      title: 'Exam Not Found',
      description: 'The requested exam could not be found.'
    };
  }
  
  return {
    title: `${exam.title} - Practice Test`,
    description: exam.description,
    keywords: exam.topics.join(', '),
    openGraph: {
      title: exam.title,
      description: exam.description,
      type: 'website',
    },
  };
}
```

**Structured Data**:
```typescript
// app/exam/[examId]/page.tsx
export default async function ExamPage({ params }: ExamPageProps) {
  const { examId } = await params;
  const exam = await getExam(examId);
  
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "Quiz",
    "name": exam.title,
    "description": exam.description,
    "educationalLevel": exam.level,
    "learningResourceType": "Practice Test",
    "subject": exam.topics,
  };
  
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      <ExamDetails exam={exam} />
    </>
  );
}
```

---

## 8. Performance Optimization

### 8.1 Route Prefetching
**Automatic Prefetching**:
```typescript
// components/navigation/Navigation.tsx
import Link from 'next/link';

export function Navigation() {
  return (
    <nav>
      <Link href="/dashboard" prefetch={true}>
        Dashboard
      </Link>
      <Link href="/exams" prefetch={true}>
        Exams
      </Link>
      <Link href="/results" prefetch={false}>
        Results
      </Link>
    </nav>
  );
}
```

**Conditional Prefetching**:
```typescript
// components/exam/ExamCard.tsx
'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export function ExamCard({ exam }: { exam: Exam }) {
  const router = useRouter();
  
  useEffect(() => {
    // Prefetch exam details on hover
    const prefetchExam = () => {
      router.prefetch(`/exam/${exam.id}`);
    };
    
    const card = document.getElementById(`exam-${exam.id}`);
    card?.addEventListener('mouseenter', prefetchExam);
    
    return () => {
      card?.removeEventListener('mouseenter', prefetchExam);
    };
  }, [exam.id, router]);
  
  return (
    <div id={`exam-${exam.id}`} className="exam-card">
      {/* Exam card content */}
    </div>
  );
}
```

### 8.2 Route Optimization
**Parallel Routes**:
```typescript
// app/exam/[examId]/layout.tsx
export default function ExamLayout({
  children,
  sidebar,
  analytics,
}: {
  children: React.ReactNode;
  sidebar: React.ReactNode;
  analytics: React.ReactNode;
}) {
  return (
    <div className="flex">
      <main className="flex-1">{children}</main>
      <aside className="w-80">{sidebar}</aside>
      <div className="w-64">{analytics}</div>
    </div>
  );
}
```

---

*This routing document provides the foundation for implementing the frontend navigation and routing system. Each route should be implemented following the established patterns and include proper error handling, loading states, and SEO optimization.*
