# Frontend State Management LLD
**Component:** Student Portal State Management
**Technology:** TanStack Query, Zustand, React Context, React 18
**Version:** 1.0

---

## 1. State Management Architecture Overview

### 1.1 State Management Strategy
The frontend uses a multi-layered state management approach:
- **TanStack Query**: Server state management (API data, caching)
- **Zustand**: Client state management (UI state, user preferences)
- **React Context**: Global app state (theme, authentication)
- **Local Storage**: Persistent user preferences
- **URL State**: Route-based state (filters, pagination)

### 1.2 State Categories
```
Application State
├── Server State (TanStack Query)
│   ├── User data and authentication
│   ├── Exam and question data
│   ├── Results and analytics
│   └── Content and metadata
├── Client State (Zustand)
│   ├── UI state and interactions
│   ├── Form state and validation
│   ├── Navigation state
│   └── User preferences
├── Global State (React Context)
│   ├── Theme and appearance
│   ├── Authentication context
│   ├── Notification system
│   └── Internationalization
└── Persistent State (Local Storage)
    ├── User preferences
    ├── Recent searches
    ├── Offline data
    └── Cache preferences
```

---

## 2. TanStack Query (Server State)

### 2.1 Query Client Configuration
**Query Client Setup**:
```typescript
// lib/query-client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000,   // 10 minutes
      retry: 3,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// app/providers.tsx
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### 2.2 Query Hooks
**User Data Queries**:
```typescript
// hooks/queries/useUser.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userApi } from '@/lib/api/user';

export function useUser(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => userApi.getUser(userId),
    enabled: !!userId,
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: userApi.updateUser,
    onSuccess: (updatedUser) => {
      queryClient.setQueryData(['user', updatedUser.id], updatedUser);
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useUserProfile() {
  return useQuery({
    queryKey: ['user', 'profile'],
    queryFn: userApi.getProfile,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
```

**Exam Data Queries**:
```typescript
// hooks/queries/useExams.ts
export function useExams(filters: ExamFilters) {
  return useQuery({
    queryKey: ['exams', filters],
    queryFn: () => examApi.getExams(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useExam(examId: string) {
  return useQuery({
    queryKey: ['exam', examId],
    queryFn: () => examApi.getExam(examId),
    enabled: !!examId,
  });
}

export function useExamQuestions(examId: string) {
  return useQuery({
    queryKey: ['exam', examId, 'questions'],
    queryFn: () => examApi.getExamQuestions(examId),
    enabled: !!examId,
  });
}
```

**Results and Analytics Queries**:
```typescript
// hooks/queries/useResults.ts
export function useUserResults(userId: string, filters?: ResultFilters) {
  return useQuery({
    queryKey: ['user', userId, 'results', filters],
    queryFn: () => resultApi.getUserResults(userId, filters),
    enabled: !!userId,
  });
}

export function useResultAnalysis(resultId: string) {
  return useQuery({
    queryKey: ['result', resultId, 'analysis'],
    queryFn: () => resultApi.getResultAnalysis(resultId),
    enabled: !!resultId,
  });
}
```

### 2.3 Mutation Hooks
**Exam Attempts**:
```typescript
// hooks/mutations/useExamAttempts.ts
export function useStartExam() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: examApi.startExam,
    onSuccess: (attempt) => {
      queryClient.setQueryData(['exam-attempt', attempt.id], attempt);
      queryClient.invalidateQueries({ queryKey: ['user', 'active-attempts'] });
    },
  });
}

export function useSubmitAnswer() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: examApi.submitAnswer,
    onSuccess: (answer) => {
      queryClient.setQueryData(['answer', answer.id], answer);
      queryClient.invalidateQueries({ queryKey: ['exam-attempt', answer.attemptId] });
    },
  });
}

export function useFinishExam() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: examApi.finishExam,
    onSuccess: (result) => {
      queryClient.setQueryData(['result', result.id], result);
      queryClient.invalidateQueries({ queryKey: ['user', 'results'] });
      queryClient.invalidateQueries({ queryKey: ['user', 'progress'] });
    },
  });
}
```

### 2.4 Query Invalidation
**Smart Invalidation Strategy**:
```typescript
// hooks/queries/useQueryInvalidation.ts
export function useQueryInvalidation() {
  const queryClient = useQueryClient();
  
  const invalidateUserData = () => {
    queryClient.invalidateQueries({ queryKey: ['user'] });
    queryClient.invalidateQueries({ queryKey: ['profile'] });
    queryClient.invalidateQueries({ queryKey: ['progress'] });
  };
  
  const invalidateExamData = (examId?: string) => {
    if (examId) {
      queryClient.invalidateQueries({ queryKey: ['exam', examId] });
    } else {
      queryClient.invalidateQueries({ queryKey: ['exams'] });
    }
  };
  
  const invalidateResults = (userId?: string) => {
    if (userId) {
      queryClient.invalidateQueries({ queryKey: ['user', userId, 'results'] });
    } else {
      queryClient.invalidateQueries({ queryKey: ['results'] });
    }
  };
  
  return {
    invalidateUserData,
    invalidateExamData,
    invalidateResults,
  };
}
```

---

## 3. Zustand (Client State)

### 3.1 Store Architecture
**Store Structure**:
```typescript
// stores/index.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { createAuthSlice } from './slices/authSlice';
import { createUISlice } from './slices/uiSlice';
import { createExamSlice } from './slices/examSlice';
import { createPreferencesSlice } from './slices/preferencesSlice';

export const useAppStore = create<AppStore>()(
  devtools(
    persist(
      (...a) => ({
        ...createAuthSlice(...a),
        ...createUISlice(...a),
        ...createExamSlice(...a),
        ...createPreferencesSlice(...a),
      }),
      {
        name: 'app-storage',
        partialize: (state) => ({
          preferences: state.preferences,
          auth: { isAuthenticated: state.auth.isAuthenticated },
        }),
      }
    )
  )
);
```

### 3.2 Authentication Store
**Auth State Management**:
```typescript
// stores/slices/authSlice.ts
import { StateCreator } from 'zustand';

export interface AuthSlice {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
  clearError: () => void;
}

export const createAuthSlice: StateCreator<AuthSlice> = (set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  
  setUser: (user) => set({
    user,
    isAuthenticated: !!user,
    error: null,
  }),
  
  setLoading: (isLoading) => set({ isLoading }),
  
  setError: (error) => set({ error }),
  
  logout: () => set({
    user: null,
    isAuthenticated: false,
    error: null,
  }),
  
  clearError: () => set({ error: null }),
});
```

### 3.3 UI Store
**UI State Management**:
```typescript
// stores/slices/uiSlice.ts
export interface UISlice {
  // Navigation
  sidebarOpen: boolean;
  currentRoute: string;
  
  // Modals and overlays
  activeModal: string | null;
  modalData: Record<string, any>;
  
  // Notifications
  notifications: Notification[];
  
  // Loading states
  globalLoading: boolean;
  loadingStates: Record<string, boolean>;
  
  // Actions
  toggleSidebar: () => void;
  setCurrentRoute: (route: string) => void;
  openModal: (modalId: string, data?: any) => void;
  closeModal: () => void;
  addNotification: (notification: Notification) => void;
  removeNotification: (id: string) => void;
  setGlobalLoading: (loading: boolean) => void;
  setLoadingState: (key: string, loading: boolean) => void;
}

export const createUISlice: StateCreator<UISlice> = (set, get) => ({
  sidebarOpen: false,
  currentRoute: '/',
  activeModal: null,
  modalData: {},
  notifications: [],
  globalLoading: false,
  loadingStates: {},
  
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  setCurrentRoute: (route) => set({ currentRoute: route }),
  
  openModal: (modalId, data) => set({
    activeModal: modalId,
    modalData: data || {},
  }),
  
  closeModal: () => set({
    activeModal: null,
    modalData: {},
  }),
  
  addNotification: (notification) => set((state) => ({
    notifications: [...state.notifications, notification],
  })),
  
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter(n => n.id !== id),
  })),
  
  setGlobalLoading: (loading) => set({ globalLoading: loading }),
  
  setLoadingState: (key, loading) => set((state) => ({
    loadingStates: { ...state.loadingStates, [key]: loading },
  })),
});
```

### 3.4 Exam Store
**Exam State Management**:
```typescript
// stores/slices/examSlice.ts
export interface ExamSlice {
  // Current exam session
  currentExam: Exam | null;
  currentAttempt: ExamAttempt | null;
  currentQuestionIndex: number;
  
  // Quiz state
  answers: Record<string, string | string[]>;
  flaggedQuestions: Set<string>;
  timeRemaining: number;
  
  // Actions
  setCurrentExam: (exam: Exam | null) => void;
  setCurrentAttempt: (attempt: ExamAttempt | null) => void;
  setCurrentQuestionIndex: (index: number) => void;
  setAnswer: (questionId: string, answer: string | string[]) => void;
  toggleFlagged: (questionId: string) => void;
  setTimeRemaining: (time: number) => void;
  resetExamState: () => void;
}

export const createExamSlice: StateCreator<ExamSlice> = (set, get) => ({
  currentExam: null,
  currentAttempt: null,
  currentQuestionIndex: 0,
  answers: {},
  flaggedQuestions: new Set(),
  timeRemaining: 0,
  
  setCurrentExam: (exam) => set({ currentExam: exam }),
  
  setCurrentAttempt: (attempt) => set({ currentAttempt: attempt }),
  
  setCurrentQuestionIndex: (index) => set({ currentQuestionIndex: index }),
  
  setAnswer: (questionId, answer) => set((state) => ({
    answers: { ...state.answers, [questionId]: answer },
  })),
  
  toggleFlagged: (questionId) => set((state) => {
    const newFlagged = new Set(state.flaggedQuestions);
    if (newFlagged.has(questionId)) {
      newFlagged.delete(questionId);
    } else {
      newFlagged.add(questionId);
    }
    return { flaggedQuestions: newFlagged };
  }),
  
  setTimeRemaining: (time) => set({ timeRemaining: time }),
  
  resetExamState: () => set({
    currentExam: null,
    currentAttempt: null,
    currentQuestionIndex: 0,
    answers: {},
    flaggedQuestions: new Set(),
    timeRemaining: 0,
  }),
});
```

---

## 4. React Context (Global State)

### 4.1 Theme Context
**Theme Management**:
```typescript
// contexts/ThemeContext.tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: 'light' | 'dark';
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('system');
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');
  
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);
  
  useEffect(() => {
    const root = window.document.documentElement;
    
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      setResolvedTheme(systemTheme);
      root.classList.remove('light', 'dark');
      root.classList.add(systemTheme);
    } else {
      setResolvedTheme(theme);
      root.classList.remove('light', 'dark');
      root.classList.add(theme);
    }
    
    localStorage.setItem('theme', theme);
  }, [theme]);
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme, resolvedTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
```

### 4.2 Authentication Context
**Auth Context Management**:
```typescript
// contexts/AuthContext.tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useAppStore } from '@/stores';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isLoading, setUser, setLoading, logout: storeLogout } = useAppStore();
  const [isInitialized, setIsInitialized] = useState(false);
  
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('auth-token');
        
        if (token) {
          const user = await authApi.getCurrentUser();
          setUser(user);
        }
      } catch (error) {
        localStorage.removeItem('auth-token');
      } finally {
        setLoading(false);
        setIsInitialized(true);
      }
    };
    
    initializeAuth();
  }, [setUser, setLoading]);
  
  const login = async (credentials: LoginCredentials) => {
    try {
      setLoading(true);
      const { user, token } = await authApi.login(credentials);
      localStorage.setItem('auth-token', token);
      setUser(user);
    } finally {
      setLoading(false);
    }
  };
  
  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      localStorage.removeItem('auth-token');
      storeLogout();
    }
  };
  
  const refreshToken = async () => {
    try {
      const { user, token } = await authApi.refreshToken();
      localStorage.setItem('auth-token', token);
      setUser(user);
    } catch (error) {
      logout();
    }
  };
  
  if (!isInitialized) {
    return <div>Loading...</div>;
  }
  
  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      isLoading,
      login,
      logout,
      refreshToken,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

---

## 5. Form State Management

### 5.1 React Hook Form Integration
**Form State with Zustand**:
```typescript
// hooks/forms/useFormState.ts
import { useForm, UseFormReturn } from 'react-hook-form';
import { useAppStore } from '@/stores';

export function useFormState<T extends Record<string, any>>(
  formId: string,
  defaultValues: T
): UseFormReturn<T> {
  const { formStates, setFormState, clearFormState } = useAppStore();
  
  const form = useForm<T>({
    defaultValues,
    mode: 'onChange',
  });
  
  // Sync form state with Zustand store
  useEffect(() => {
    const subscription = form.watch((value) => {
      setFormState(formId, value);
    });
    
    return () => subscription.unsubscribe();
  }, [form, formId, setFormState]);
  
  // Restore form state on mount
  useEffect(() => {
    const savedState = formStates[formId];
    if (savedState) {
      form.reset(savedState);
    }
  }, [form, formId, formStates]);
  
  return form;
}

// Usage example
export function useExamForm() {
  return useFormState('exam-form', {
    title: '',
    description: '',
    topics: [],
    difficulty: 'medium',
    timeLimit: 60,
    questionCount: 25,
  });
}
```

### 5.2 Form Validation
**Custom Validation Hooks**:
```typescript
// hooks/forms/useFormValidation.ts
import { useMemo } from 'react';
import { useFormState } from 'react-hook-form';

export function useFormValidation<T extends Record<string, any>>(
  form: UseFormReturn<T>,
  validationRules: ValidationRules<T>
) {
  const { formState: { errors, isValid, isDirty } } = form;
  
  const validationErrors = useMemo(() => {
    const errorMessages: Record<string, string> = {};
    
    Object.entries(errors).forEach(([field, error]) => {
      if (error?.message) {
        errorMessages[field] = error.message;
      }
    });
    
    return errorMessages;
  }, [errors]);
  
  const canSubmit = useMemo(() => {
    return isValid && isDirty;
  }, [isValid, isDirty]);
  
  return {
    errors: validationErrors,
    isValid,
    isDirty,
    canSubmit,
  };
}
```

---

## 6. URL State Management

### 6.1 URL State Synchronization
**URL State with Zustand**:
```typescript
// hooks/url/useURLState.ts
import { useRouter, useSearchParams } from 'next/navigation';
import { useAppStore } from '@/stores';
import { useEffect } from 'react';

export function useURLState() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { filters, setFilters } = useAppStore();
  
  // Sync URL with store state
  useEffect(() => {
    const urlFilters = {
      category: searchParams.get('category') || undefined,
      difficulty: searchParams.get('difficulty') || undefined,
      search: searchParams.get('search') || undefined,
      page: parseInt(searchParams.get('page') || '1'),
      sort: searchParams.get('sort') || 'popular',
    };
    
    setFilters(urlFilters);
  }, [searchParams, setFilters]);
  
  // Update URL when store state changes
  const updateURL = (newFilters: Partial<typeof filters>) => {
    const params = new URLSearchParams(searchParams);
    
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value && value !== '') {
        params.set(key, String(value));
      } else {
        params.delete(key);
      }
    });
    
    router.push(`?${params.toString()}`);
  };
  
  return { filters, updateURL };
}
```

---

## 7. Performance Optimization

### 7.1 State Optimization
**Selective State Updates**:
```typescript
// hooks/optimization/useShallowSelector.ts
import { useAppStore } from '@/stores';
import { shallow } from 'zustand/shallow';

export function useShallowSelector<T>(
  selector: (state: AppState) => T
): T {
  return useAppStore(selector, shallow);
}

// Usage example
export function useUserProfile() {
  return useShallowSelector((state) => ({
    name: state.user?.name,
    email: state.user?.email,
    avatar: state.user?.avatar,
  }));
}
```

**Memoized Selectors**:
```typescript
// hooks/optimization/useMemoizedSelector.ts
import { useMemo } from 'react';
import { useAppStore } from '@/stores';

export function useMemoizedSelector<T>(
  selector: (state: AppState) => T,
  deps: any[] = []
): T {
  return useAppStore(useMemo(() => selector, deps));
}

// Usage example
export function useFilteredExams(filters: ExamFilters) {
  return useMemoizedSelector(
    (state) => {
      const exams = state.exams;
      return applyFilters(exams, filters);
    },
    [filters]
  );
}
```

---

## 8. State Persistence

### 8.1 Local Storage Integration
**Persistent State Management**:
```typescript
// stores/persistence/localStorage.ts
import { StateCreator } from 'zustand';

export interface PersistOptions {
  name: string;
  partialize?: (state: any) => any;
  version?: number;
  migrate?: (persistedState: any, version: number) => any;
}

export function withLocalStorage<T>(
  config: StateCreator<T>,
  options: PersistOptions
): StateCreator<T> {
  return (set, get, api) => {
    const savedState = loadFromStorage(options.name);
    
    if (savedState) {
      set(savedState);
    }
    
    const originalSet = set;
    set = (args, replace) => {
      originalSet(args, replace);
      
      const state = get();
      const stateToPersist = options.partialize ? options.partialize(state) : state;
      saveToStorage(options.name, stateToPersist);
    };
    
    return config(set, get, api);
  };
}

function loadFromStorage(key: string): any {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  } catch {
    return null;
  }
}

function saveToStorage(key: string, value: any): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Handle storage errors
  }
}
```

---

*This state management document provides the foundation for implementing robust state management in the frontend application. Each pattern should be implemented following the established architecture and include proper error handling and performance optimization.*
