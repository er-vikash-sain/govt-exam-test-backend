# Frontend LLD - Architecture & Design
**Component:** Frontend System Architecture
**Technology:** Next.js 14, React 18, TypeScript
**Version:** 1.0

---

## 1. Frontend Architecture Overview

The frontend follows a modern, component-based architecture with Next.js 14 App Router, React 18 Server Components, and a clean separation of concerns for maintainability and scalability.

---

## 2. High-Level Architecture

### 2.1 System Components
```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Header    │ │   Sidebar   │ │   Main      │ │   Footer    │ │
│  │  Component  │ │  Component  │ │  Content    │ │  Component  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Pages     │ │ Components  │ │   Hooks     │ │   Utils     │ │
│  │  (Routes)   │ │  (UI/Logic) │ │  (Custom)   │ │ (Helpers)   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      State Management                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ TanStack    │ │   Zustand   │ │   Context   │ │ Local      │ │
│  │   Query     │ │  (Client)   │ │  (Global)   │ │ Storage    │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   API       │ │   Cache     │ │   WebSocket │ │   PWA       │ │
│  │  Client     │ │  (Redis)    │ │  (Real-time)│ │ (Offline)   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Architecture
```
User Action → Component → Hook → State Management → API Call → Backend
     ↑                                                              │
     └────────────────── Response ← Cache ← Database ←──────────────┘
```

---

## 3. Next.js App Router Structure

### 3.1 Directory Structure
```
app/
├── (auth)/                    # Authentication routes
│   ├── login/
│   │   ├── page.tsx          # Login page
│   │   └── layout.tsx        # Auth layout
│   ├── register/
│   │   └── page.tsx          # Registration page
│   └── forgot-password/
│       └── page.tsx          # Password reset page
├── (dashboard)/               # Dashboard routes
│   ├── dashboard/
│   │   ├── page.tsx          # Dashboard home
│   │   └── loading.tsx       # Loading state
│   ├── profile/
│   │   └── page.tsx          # User profile
│   └── settings/
│       └── page.tsx          # User settings
├── (exam)/                    # Exam-related routes
│   ├── exams/
│   │   ├── page.tsx          # Exam list
│   │   ├── [id]/
│   │   │   ├── page.tsx      # Exam details
│   │   │   └── quiz/
│   │   │       └── page.tsx  # Quiz interface
│   │   └── generate/
│   │       └── page.tsx      # AI quiz generation
│   ├── results/
│   │   ├── page.tsx          # Results list
│   │   └── [id]/
│   │       └── page.tsx      # Result details
│   └── study-plan/
│       └── page.tsx          # Study planning
├── api/                       # API routes
│   ├── auth/
│   │   ├── login/
│   │   │   └── route.ts      # Login API
│   │   └── register/
│   │       └── route.ts      # Registration API
│   └── webhooks/
│       └── payment/
│           └── route.ts      # Payment webhook
├── globals.css                # Global styles
├── layout.tsx                 # Root layout
├── page.tsx                   # Home page
├── loading.tsx                # Global loading
├── error.tsx                  # Global error
└── not-found.tsx              # 404 page
```

### 3.2 Route Groups
- **`(auth)`**: Authentication-related pages with shared layout
- **`(dashboard)`**: Protected dashboard pages
- **`(exam)`**: Exam and quiz functionality
- **`api`**: Backend API endpoints

---

## 4. Component Architecture

### 4.1 Component Hierarchy
```
App Layout
├── Header
│   ├── Logo
│   ├── Navigation
│   ├── User Menu
│   └── Notifications
├── Sidebar (Dashboard)
│   ├── User Profile
│   ├── Navigation Menu
│   ├── Quick Actions
│   └── Progress Summary
├── Main Content
│   ├── Page Header
│   ├── Content Area
│   └── Page Footer
└── Footer
    ├── Links
    ├── Social Media
    └── Copyright
```

### 4.2 Component Categories

#### Layout Components
```typescript
// app/components/layout/Header.tsx
export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Logo />
          <Navigation />
          <UserMenu />
        </div>
      </div>
    </header>
  );
}

// app/components/layout/Sidebar.tsx
export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-50 border-r">
      <UserProfile />
      <NavigationMenu />
      <QuickActions />
      <ProgressSummary />
    </aside>
  );
}
```

#### Feature Components
```typescript
// app/components/features/exam/ExamCard.tsx
interface ExamCardProps {
  exam: Exam;
  onStart: (examId: string) => void;
  onViewDetails: (examId: string) => void;
}

export default function ExamCard({ exam, onStart, onViewDetails }: ExamCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900">{exam.title}</h3>
      <p className="text-gray-600 mt-2">{exam.description}</p>
      <div className="mt-4 flex justify-between items-center">
        <ExamStats exam={exam} />
        <div className="flex space-x-2">
          <Button onClick={() => onViewDetails(exam.id)} variant="outline">
            View Details
          </Button>
          <Button onClick={() => onStart(exam.id)} variant="primary">
            Start Exam
          </Button>
        </div>
      </div>
    </div>
  );
}
```

#### UI Components
```typescript
// app/components/ui/Button.tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export default function Button({ 
  variant = 'primary', 
  size = 'md', 
  loading = false,
  children,
  ...props 
}: ButtonProps) {
  const baseClasses = "inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  
  const variantClasses = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500",
    outline: "border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-blue-500",
    danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500"
  };
  
  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base"
  };
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}
      disabled={loading}
      {...props}
    >
      {loading && <Spinner className="mr-2" />}
      {children}
    </button>
  );
}
```

---

## 5. State Management Architecture

### 5.1 State Management Strategy
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Server State  │    │   Client State  │    │   Global State  │
│   (TanStack     │    │   (Zustand)     │    │   (Context)     │
│    Query)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Data      │    │   UI State      │    │   Theme/Auth    │
│   Caching       │    │   Forms         │    │   Settings      │
│   Synchronization│   │   Modals        │    │   Preferences   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 5.2 TanStack Query (Server State)
```typescript
// app/hooks/useExams.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { examApi } from '@/lib/api/exam';

export function useExams(filters?: ExamFilters) {
  return useQuery({
    queryKey: ['exams', filters],
    queryFn: () => examApi.getExams(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useExam(id: string) {
  return useQuery({
    queryKey: ['exam', id],
    queryFn: () => examApi.getExam(id),
    enabled: !!id,
  });
}

export function useCreateExam() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: examApi.createExam,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exams'] });
    },
  });
}
```

### 5.3 Zustand (Client State)
```typescript
// app/stores/examStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface ExamState {
  currentExam: Exam | null;
  currentQuestion: number;
  answers: Record<string, string>;
  timeRemaining: number;
  isPaused: boolean;
  
  // Actions
  setCurrentExam: (exam: Exam) => void;
  setCurrentQuestion: (questionNumber: number) => void;
  setAnswer: (questionId: string, answer: string) => void;
  setTimeRemaining: (time: number) => void;
  pauseExam: () => void;
  resumeExam: () => void;
  resetExam: () => void;
}

export const useExamStore = create<ExamState>()(
  devtools(
    (set) => ({
      currentExam: null,
      currentQuestion: 0,
      answers: {},
      timeRemaining: 0,
      isPaused: false,
      
      setCurrentExam: (exam) => set({ currentExam: exam }),
      setCurrentQuestion: (questionNumber) => set({ currentQuestion: questionNumber }),
      setAnswer: (questionId, answer) => 
        set((state) => ({
          answers: { ...state.answers, [questionId]: answer }
        })),
      setTimeRemaining: (time) => set({ timeRemaining: time }),
      pauseExam: () => set({ isPaused: true }),
      resumeExam: () => set({ isPaused: false }),
      resetExam: () => set({
        currentExam: null,
        currentQuestion: 0,
        answers: {},
        timeRemaining: 0,
        isPaused: false
      }),
    }),
    { name: 'exam-store' }
  )
);
```

### 5.4 React Context (Global State)
```typescript
// app/contexts/AuthContext.tsx
import { createContext, useContext, useReducer, ReactNode } from 'react';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' };

const AuthContext = createContext<{
  state: AuthState;
  dispatch: React.Dispatch<AuthAction>;
} | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  
  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

---

## 6. Data Fetching & API Integration

### 6.1 API Client Structure
```typescript
// app/lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or logout
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 6.2 API Service Layer
```typescript
// app/lib/api/exam.ts
import apiClient from './client';
import { Exam, ExamFilters, CreateExamRequest } from '@/types/exam';

export const examApi = {
  // Get exams with filters
  async getExams(filters?: ExamFilters): Promise<Exam[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    
    const response = await apiClient.get(`/exams?${params.toString()}`);
    return response.data.data;
  },
  
  // Get single exam
  async getExam(id: string): Promise<Exam> {
    const response = await apiClient.get(`/exams/${id}`);
    return response.data.data;
  },
  
  // Create new exam
  async createExam(data: CreateExamRequest): Promise<Exam> {
    const response = await apiClient.post('/exams', data);
    return response.data.data;
  },
  
  // Start exam attempt
  async startAttempt(examId: string): Promise<Attempt> {
    const response = await apiClient.post(`/exams/${examId}/attempts`);
    return response.data.data;
  },
  
  // Submit exam answer
  async submitAnswer(attemptId: string, questionId: string, answer: string): Promise<void> {
    await apiClient.post(`/attempts/${attemptId}/answer`, {
      question_id: questionId,
      selected_option_ids: [answer],
    });
  },
  
  // Finish exam attempt
  async finishAttempt(attemptId: string): Promise<AttemptResult> {
    const response = await apiClient.post(`/attempts/${attemptId}/finish`);
    return response.data.data;
  },
};
```

---

## 7. Performance Optimization

### 7.1 Code Splitting & Lazy Loading
```typescript
// app/components/features/exam/QuizInterface.tsx
import dynamic from 'next/dynamic';

// Lazy load heavy components
const MathJaxRenderer = dynamic(() => import('@/components/ui/MathJaxRenderer'), {
  loading: () => <div>Loading math renderer...</div>,
  ssr: false,
});

const ChartComponent = dynamic(() => import('@/components/ui/ChartComponent'), {
  loading: () => <div>Loading chart...</div>,
  ssr: false,
});

export default function QuizInterface() {
  return (
    <div>
      <QuestionDisplay />
      <MathJaxRenderer />
      <ChartComponent />
    </div>
  );
}
```

### 7.2 Image Optimization
```typescript
// app/components/ui/OptimizedImage.tsx
import Image from 'next/image';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  priority?: boolean;
}

export default function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
}: OptimizedImageProps) {
  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      priority={priority}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
      className="object-cover"
    />
  );
}
```

### 7.3 Caching Strategy
```typescript
// app/hooks/useExams.ts
export function useExams(filters?: ExamFilters) {
  return useQuery({
    queryKey: ['exams', filters],
    queryFn: () => examApi.getExams(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  });
}

// Prefetch exams for better UX
export function usePrefetchExams() {
  const queryClient = useQueryClient();
  
  return useCallback(
    (filters?: ExamFilters) => {
      queryClient.prefetchQuery({
        queryKey: ['exams', filters],
        queryFn: () => examApi.getExams(filters),
        staleTime: 5 * 60 * 1000,
      });
    },
    [queryClient]
  );
}
```

---

## 8. Accessibility & Internationalization

### 8.1 Accessibility Features
```typescript
// app/components/ui/AccessibleButton.tsx
interface AccessibleButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  ariaLabel?: string;
  ariaDescribedBy?: string;
}

export default function AccessibleButton({
  children,
  ariaLabel,
  ariaDescribedBy,
  ...props
}: AccessibleButtonProps) {
  return (
    <button
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      {...props}
    >
      {children}
    </button>
  );
}

// app/components/features/exam/QuestionNavigator.tsx
export default function QuestionNavigator({ 
  currentQuestion, 
  totalQuestions, 
  onNavigate 
}: QuestionNavigatorProps) {
  return (
    <nav aria-label="Question navigation">
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onNavigate(currentQuestion - 1)}
          disabled={currentQuestion <= 1}
          aria-label={`Go to question ${currentQuestion - 1}`}
          className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 disabled:opacity-50"
        >
          <ChevronLeftIcon className="w-5 h-5" />
        </button>
        
        <span className="text-sm text-gray-600">
          Question {currentQuestion} of {totalQuestions}
        </span>
        
        <button
          onClick={() => onNavigate(currentQuestion + 1)}
          disabled={currentQuestion >= totalQuestions}
          aria-label={`Go to question ${currentQuestion + 1}`}
          className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 disabled:opacity-50"
        >
          <ChevronRightIcon className="w-5 h-5" />
        </button>
      </div>
    </nav>
  );
}
```

### 8.2 Internationalization
```typescript
// app/lib/i18n/config.ts
import { createI18nClient } from 'next-international/client';
import { createI18nServer } from 'next-international/server';

export const locales = ['en', 'hi'] as const;
export type Locale = typeof locales[number];

export const { useI18n, useScopedI18n, useCurrentLocale, useChangeLocale } = createI18nClient({
  en: () => import('./en'),
  hi: () => import('./hi'),
});

export const { getI18n, getScopedI18n, getCurrentLocale } = createI18nServer({
  en: () => import('./en'),
  hi: () => import('./hi'),
});

// app/lib/i18n/en.ts
export default {
  common: {
    loading: 'Loading...',
    error: 'An error occurred',
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
  },
  exam: {
    start: 'Start Exam',
    pause: 'Pause',
    resume: 'Resume',
    submit: 'Submit',
    timeRemaining: 'Time Remaining',
    questions: 'Questions',
  },
  navigation: {
    home: 'Home',
    exams: 'Exams',
    results: 'Results',
    profile: 'Profile',
    settings: 'Settings',
  },
} as const;

// app/components/features/exam/ExamInterface.tsx
import { useI18n } from '@/lib/i18n/config';

export default function ExamInterface() {
  const t = useI18n();
  
  return (
    <div>
      <header className="flex justify-between items-center p-4">
        <h1>{t('exam.title')}</h1>
        <div className="flex items-center space-x-4">
          <span>{t('exam.timeRemaining')}: {timeRemaining}</span>
          <button onClick={pauseExam}>{t('exam.pause')}</button>
        </div>
      </header>
    </div>
  );
}
```

---

## 9. Error Handling & Error Boundaries

### 9.1 Error Boundary Component
```typescript
// app/components/ErrorBoundary.tsx
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    
    // Log error to monitoring service
    // logError(error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-4">
              We're sorry, but something unexpected happened.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

### 9.2 Error Handling in Components
```typescript
// app/components/features/exam/ExamList.tsx
export default function ExamList() {
  const { data: exams, error, isLoading } = useExams();
  
  if (isLoading) {
    return <ExamListSkeleton />;
  }
  
  if (error) {
    return (
      <div className="text-center py-8">
        <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Failed to load exams
        </h3>
        <p className="text-gray-600 mb-4">
          {error.message || 'An error occurred while loading exams'}
        </p>
        <button
          onClick={() => window.location.reload()}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }
  
  if (!exams || exams.length === 0) {
    return (
      <div className="text-center py-8">
        <DocumentIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No exams available
        </h3>
        <p className="text-gray-600">
          Check back later for new exams or contact support.
        </p>
      </div>
    );
  }
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {exams.map((exam) => (
        <ExamCard key={exam.id} exam={exam} />
      ))}
    </div>
  );
}
```

---

## 10. Testing Strategy

### 10.1 Component Testing
```typescript
// app/components/features/exam/__tests__/ExamCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import ExamCard from '../ExamCard';

const mockExam = {
  id: '1',
  title: 'SSC Practice Test',
  description: 'Practice test for SSC preparation',
  duration: 60,
  questionCount: 50,
  difficulty: 'medium',
};

describe('ExamCard', () => {
  it('renders exam information correctly', () => {
    const mockOnStart = jest.fn();
    const mockOnViewDetails = jest.fn();
    
    render(
      <ExamCard
        exam={mockExam}
        onStart={mockOnStart}
        onViewDetails={mockOnViewDetails}
      />
    );
    
    expect(screen.getByText('SSC Practice Test')).toBeInTheDocument();
    expect(screen.getByText('Practice test for SSC preparation')).toBeInTheDocument();
    expect(screen.getByText('50 Questions')).toBeInTheDocument();
    expect(screen.getByText('60 min')).toBeInTheDocument();
  });
  
  it('calls onStart when start button is clicked', () => {
    const mockOnStart = jest.fn();
    const mockOnViewDetails = jest.fn();
    
    render(
      <ExamCard
        exam={mockExam}
        onStart={mockOnStart}
        onViewDetails={mockOnViewDetails}
      />
    );
    
    fireEvent.click(screen.getByText('Start Exam'));
    expect(mockOnStart).toHaveBeenCalledWith('1');
  });
});
```

### 10.2 Hook Testing
```typescript
// app/hooks/__tests__/useExams.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useExams } from '../useExams';
import { examApi } from '@/lib/api/exam';

// Mock the API
jest.mock('@/lib/api/exam');

const mockExams = [
  { id: '1', title: 'Exam 1' },
  { id: '2', title: 'Exam 2' },
];

describe('useExams', () => {
  let queryClient: QueryClient;
  
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });
  
  it('fetches exams successfully', async () => {
    (examApi.getExams as jest.Mock).mockResolvedValue(mockExams);
    
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
    
    const { result } = renderHook(() => useExams(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    
    expect(result.current.data).toEqual(mockExams);
  });
});
```

---

## 11. Next Steps

1. **Set up Next.js project** with TypeScript and Tailwind CSS
2. **Create base components** and layout structure
3. **Implement authentication** flow and protected routes
4. **Build exam discovery** and quiz interface
5. **Add state management** with TanStack Query and Zustand

---

*This architecture provides a solid foundation for building a scalable, maintainable frontend application with modern React patterns and best practices.*
