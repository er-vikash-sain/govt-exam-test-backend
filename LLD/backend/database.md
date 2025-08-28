# Backend LLD - Database Design
**Component:** Database Schema & Models
**Technology:** PostgreSQL 16, SQLAlchemy 2.0, Alembic
**Version:** 1.0

---

## 1. Database Overview

The database design follows a normalized structure optimized for exam preparation platform requirements. It supports hierarchical exam structures, flexible question management, and comprehensive user analytics.

---

## 2. Core Database Schema

### 2.1 Users & Authentication

#### `users` Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    status user_status NOT NULL DEFAULT 'active',
    locale VARCHAR(10) DEFAULT 'en_IN',
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);
```

#### `user_profiles` Table
```sql
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    gender gender_type,
    city VARCHAR(100),
    state_id UUID REFERENCES states(id),
    education_level education_level_type,
    current_institution VARCHAR(200),
    bio TEXT,
    profile_picture_url VARCHAR(500),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `user_sessions` Table
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500) NOT NULL,
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.2 Exam & Syllabus Structure

#### `states` Table
```sql
CREATE TABLE states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    country_code VARCHAR(3) DEFAULT 'IND',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `exam_bodies` Table
```sql
CREATE TABLE exam_bodies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    state_id UUID REFERENCES states(id),
    scope exam_scope NOT NULL DEFAULT 'national',
    website_url VARCHAR(500),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `exams` Table
```sql
CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    body_id UUID NOT NULL REFERENCES exam_bodies(id),
    level exam_level NOT NULL DEFAULT 'graduate',
    languages TEXT[] DEFAULT '{en}',
    description TEXT,
    eligibility_criteria TEXT,
    exam_pattern JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `syllabi` Table
```sql
CREATE TABLE syllabi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    effective_from DATE NOT NULL,
    effective_until DATE,
    content JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(exam_id, version)
);
```

#### `subjects` Table
```sql
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    syllabus_id UUID NOT NULL REFERENCES syllabi(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL,
    description TEXT,
    weightage_percentage DECIMAL(5,2),
    order_index INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `topics` Table
```sql
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES topics(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    difficulty_band difficulty_level DEFAULT 'medium',
    weightage_percentage DECIMAL(5,2),
    order_index INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.3 Question Bank

#### `questions` Table
```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(id),
    subject_id UUID NOT NULL REFERENCES subjects(id),
    topic_id UUID NOT NULL REFERENCES topics(id),
    question_type question_type NOT NULL DEFAULT 'single_choice',
    stem TEXT NOT NULL,
    explanation TEXT,
    difficulty difficulty_level NOT NULL DEFAULT 'medium',
    source question_source NOT NULL DEFAULT 'ai_generated',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    status question_status NOT NULL DEFAULT 'draft',
    checksum VARCHAR(64) NOT NULL,
    version INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    created_by UUID REFERENCES users(id),
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `question_options` Table
```sql
CREATE TABLE question_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    order_index INTEGER NOT NULL,
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `question_attachments` Table
```sql
CREATE TABLE question_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    file_type attachment_type NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_name VARCHAR(200) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.4 Quiz & Attempts

#### `quiz_templates` Table
```sql
CREATE TABLE quiz_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `quizzes` Table
```sql
CREATE TABLE quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    config JSONB NOT NULL,
    generated_from_template_id UUID REFERENCES quiz_templates(id),
    status quiz_status NOT NULL DEFAULT 'draft',
    total_questions INTEGER NOT NULL,
    total_time_minutes INTEGER NOT NULL,
    passing_percentage DECIMAL(5,2),
    negative_marking BOOLEAN DEFAULT FALSE,
    negative_mark_value DECIMAL(3,2) DEFAULT 0.25,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `quiz_questions` Table
```sql
CREATE TABLE quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id),
    order_index INTEGER NOT NULL,
    section_name VARCHAR(100),
    marks DECIMAL(5,2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `attempts` Table
```sql
CREATE TABLE attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id),
    user_id UUID NOT NULL REFERENCES users(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    status attempt_status NOT NULL DEFAULT 'in_progress',
    score_raw DECIMAL(8,2),
    score_percentage DECIMAL(5,2),
    total_marks DECIMAL(8,2),
    duration_seconds INTEGER,
    breakdown JSONB,
    ip_address INET,
    user_agent TEXT,
    device_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `attempt_answers` Table
```sql
CREATE TABLE attempt_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id),
    selected_option_ids UUID[],
    is_correct BOOLEAN,
    marks_earned DECIMAL(5,2),
    time_spent_seconds INTEGER,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.5 AI & Content Generation

#### `ai_jobs` Table
```sql
CREATE TABLE ai_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type ai_job_type NOT NULL,
    status ai_job_status NOT NULL DEFAULT 'pending',
    payload JSONB NOT NULL,
    provider ai_provider NOT NULL DEFAULT 'openai',
    model_name VARCHAR(100),
    token_cost INTEGER,
    cost_usd DECIMAL(10,4),
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `ai_content` Table
```sql
CREATE TABLE ai_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_job_id UUID NOT NULL REFERENCES ai_jobs(id),
    content_type ai_content_type NOT NULL,
    content JSONB NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    quality_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.6 Payments & Subscriptions

#### `wallets` Table
```sql
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) UNIQUE,
    balance_credits INTEGER DEFAULT 0,
    total_earned_credits INTEGER DEFAULT 0,
    total_spent_credits INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `transactions` Table
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    type transaction_type NOT NULL,
    amount INTEGER NOT NULL,
    reason VARCHAR(200),
    gateway_ref VARCHAR(200),
    status transaction_status NOT NULL DEFAULT 'pending',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `subscriptions` Table
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    status subscription_status NOT NULL DEFAULT 'active',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    auto_renew BOOLEAN DEFAULT TRUE,
    payment_method_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 3. Enums & Custom Types

### 3.1 User Management
```sql
CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin', 'content_creator', 'institute_admin');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'pending_verification');
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other', 'prefer_not_to_say');
CREATE TYPE education_level_type AS ENUM ('high_school', 'diploma', 'bachelor', 'master', 'phd', 'other');
```

### 3.2 Exam & Content
```sql
CREATE TYPE exam_scope AS ENUM ('national', 'state', 'university', 'private');
CREATE TYPE exam_level AS ENUM ('high_school', 'diploma', 'graduate', 'post_graduate', 'professional');
CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard', 'expert');
CREATE TYPE question_type AS ENUM ('single_choice', 'multiple_choice', 'numerical', 'assertion_reason', 'passage_based');
CREATE TYPE question_source AS ENUM ('ai_generated', 'manual', 'imported', 'curated');
CREATE TYPE question_status AS ENUM ('draft', 'pending_review', 'approved', 'rejected', 'archived');
```

### 3.3 Quiz & Attempts
```sql
CREATE TYPE quiz_status AS ENUM ('draft', 'published', 'archived');
CREATE TYPE attempt_status AS ENUM ('in_progress', 'completed', 'abandoned', 'timed_out');
CREATE TYPE ai_job_type AS ENUM ('generate_questions', 'generate_explanations', 'generate_quiz', 'content_moderation');
CREATE TYPE ai_job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE ai_provider AS ENUM ('openai', 'anthropic', 'huggingface', 'local');
CREATE TYPE ai_content_type AS ENUM ('questions', 'explanations', 'rationales', 'study_material');
```

### 3.4 Payments
```sql
CREATE TYPE transaction_type AS ENUM ('credit', 'debit', 'refund', 'bonus');
CREATE TYPE transaction_status AS ENUM ('pending', 'completed', 'failed', 'cancelled');
CREATE TYPE subscription_status AS ENUM ('active', 'expired', 'cancelled', 'suspended');
```

---

## 4. Indexes & Performance

### 4.1 Primary Indexes
```sql
-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

-- Questions
CREATE INDEX idx_questions_exam_id ON questions(exam_id);
CREATE INDEX idx_questions_topic_id ON questions(topic_id);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_status ON questions(status);
CREATE INDEX idx_questions_checksum ON questions(checksum);

-- Attempts
CREATE INDEX idx_attempts_user_id ON attempts(user_id);
CREATE INDEX idx_attempts_quiz_id ON attempts(quiz_id);
CREATE INDEX idx_attempts_status ON attempts(status);
CREATE INDEX idx_attempts_started_at ON attempts(started_at);

-- AI Jobs
CREATE INDEX idx_ai_jobs_status ON ai_jobs(status);
CREATE INDEX idx_ai_jobs_type ON ai_jobs(type);
CREATE INDEX idx_ai_jobs_created_at ON ai_jobs(created_at);
```

### 4.2 Composite Indexes
```sql
-- Question search optimization
CREATE INDEX idx_questions_exam_topic_difficulty ON questions(exam_id, topic_id, difficulty);

-- Attempt analytics
CREATE INDEX idx_attempts_user_quiz_status ON attempts(user_id, quiz_id, status);

-- Quiz generation
CREATE INDEX idx_quizzes_exam_status ON quizzes(exam_id, status);
```

---

## 5. Database Relationships

### 5.1 Hierarchical Structure
```
exams (1) ── (many) syllabi (1) ── (many) subjects (1) ── (many) topics
  │                                                                    │
  └── (many) questions ── (many) question_options                     │
                                                                    │
  └── (many) quizzes ── (many) quiz_questions                       │
                                                                    │
  └── (many) attempts ── (many) attempt_answers                      │
                                                                    │
  └── (many) ai_jobs ── (many) ai_content                           │
```

### 5.2 User Relationships
```
users (1) ── (1) user_profiles
  │
  ├── (many) attempts
  ├── (many) transactions
  ├── (many) subscriptions
  └── (1) wallet
```

---

## 6. Data Migration Strategy

### 6.1 Alembic Migrations
- **Version control** for database schema changes
- **Rollback capability** for failed migrations
- **Data migration** scripts for complex changes
- **Environment-specific** migration configurations

### 6.2 Migration Best Practices
- **Backward compatibility** during migrations
- **Zero-downtime** deployments
- **Data validation** after migrations
- **Rollback testing** procedures

---

## 7. Backup & Recovery

### 7.1 Backup Strategy
- **Daily full backups** with point-in-time recovery
- **Hourly incremental backups** for critical data
- **Cross-region replication** for disaster recovery
- **Automated backup testing** and validation

### 7.2 Recovery Procedures
- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour
- **Automated failover** procedures
- **Data integrity** verification after recovery

---

## 8. Security & Compliance

### 8.1 Data Protection
- **Encryption at rest** for sensitive data
- **Column-level encryption** for PII
- **Audit logging** for all data modifications
- **Access control** at database level

### 8.2 Compliance Features
- **GDPR compliance** with data deletion
- **DPDP compliance** for Indian users
- **Data retention** policies
- **Privacy controls** and consent management

---

## 9. Monitoring & Maintenance

### 9.1 Performance Monitoring
- **Query performance** tracking
- **Index usage** analysis
- **Connection pool** monitoring
- **Slow query** identification

### 9.2 Maintenance Tasks
- **Regular vacuum** and analyze operations
- **Index maintenance** and optimization
- **Statistics updates** for query planning
- **Deadlock detection** and resolution

---

## 10. Next Steps

1. **Review schema design** with development team
2. **Create Alembic migration** files
3. **Set up database** with initial schema
4. **Implement data models** in SQLAlchemy
5. **Create seed data** for development

---

*This database design provides the foundation for the exam preparation platform. Refer to specific component LLDs for implementation details.*
