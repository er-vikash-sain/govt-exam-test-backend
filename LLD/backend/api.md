# Backend LLD - API Design
**Component:** API Endpoints & Specifications
**Technology:** FastAPI, Pydantic, OpenAPI
**Version:** 1.0

---

## 1. API Overview

The API follows RESTful principles with consistent patterns for request/response handling, error management, and authentication. All endpoints are versioned and documented using OpenAPI 3.0.

---

## 2. API Base Structure

### 2.1 Base URL
```
Production: https://api.examplatform.com/v1
Staging: https://staging-api.examplatform.com/v1
Development: http://localhost:8000/v1
```

### 2.2 Common Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
Accept: application/json
X-Request-ID: <unique_request_id>
```

### 2.3 Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-12-01T10:00:00Z",
  "request_id": "req_123456789"
}
```

---

## 3. Authentication Endpoints

### 3.1 User Registration
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password123",
  "phone": "+919876543210",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1995-01-01",
  "state_id": "uuid",
  "education_level": "bachelor"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "verification_required": true
  },
  "message": "User registered successfully"
}
```

### 3.2 User Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "role": "student",
      "profile": {...}
    }
  }
}
```

### 3.3 Token Refresh
```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 4. User Management Endpoints

### 4.1 Get User Profile
```http
GET /users/me
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "profile": {
      "display_name": "John Doe",
      "first_name": "John",
      "last_name": "Doe",
      "city": "Mumbai",
      "state": {...},
      "education_level": "bachelor"
    },
    "wallet": {
      "balance_credits": 150,
      "total_earned": 500,
      "total_spent": 350
    }
  }
}
```

### 4.2 Update User Profile
```http
PATCH /users/me
```

**Request Body:**
```json
{
  "display_name": "John Doe Updated",
  "city": "Delhi",
  "bio": "Updated bio information"
}
```

---

## 5. Exam & Syllabus Endpoints

### 5.1 Get States
```http
GET /catalog/states
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Maharashtra",
      "code": "MH",
      "is_active": true
    }
  ]
}
```

### 5.2 Get Exam Bodies
```http
GET /catalog/exam-bodies?state_id=uuid&scope=national
```

**Query Parameters:**
- `state_id` (optional): Filter by state
- `scope`: national, state, university, private
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset (default: 0)

### 5.3 Get Exams
```http
GET /catalog/exams?body_id=uuid&level=graduate&language=en
```

**Query Parameters:**
- `body_id` (optional): Filter by exam body
- `level`: high_school, diploma, graduate, post_graduate
- `language`: en, hi, ta, te, bn, mr
- `is_active`: true/false

### 5.4 Get Topics
```http
GET /catalog/topics?exam_id=uuid&subject_id=uuid&difficulty=medium
```

**Query Parameters:**
- `exam_id`: Required
- `subject_id` (optional): Filter by subject
- `difficulty`: easy, medium, hard, expert
- `parent_id` (optional): For hierarchical topics

---

## 6. Quiz Management Endpoints

### 6.1 Get Available Quizzes
```http
GET /quizzes?exam_id=uuid&topic_ids=uuid1,uuid2&difficulty=mixed&question_count=50
```

**Query Parameters:**
- `exam_id`: Required
- `topic_ids`: Comma-separated topic UUIDs
- `difficulty`: easy, medium, hard, mixed
- `question_count`: Number of questions
- `time_limit`: Time in minutes
- `negative_marking`: true/false

### 6.2 Create Custom Quiz
```http
POST /quizzes
```

**Request Body:**
```json
{
  "exam_id": "uuid",
  "title": "Custom SSC Practice Test",
  "description": "Practice test for SSC preparation",
  "config": {
    "topics": ["uuid1", "uuid2"],
    "question_count": 50,
    "difficulty_mix": {
      "easy": 0.2,
      "medium": 0.6,
      "hard": 0.2
    },
    "time_limit": 60,
    "negative_marking": true,
    "negative_mark_value": 0.25
  }
}
```

### 6.3 Generate AI Quiz
```http
POST /ai/jobs
```

**Request Body:**
```json
{
  "type": "generate_quiz",
  "payload": {
    "exam_id": "uuid",
    "topics": ["uuid1", "uuid2"],
    "question_count": 50,
    "difficulty_mix": "mixed",
    "time_limit": 60,
    "language": "en",
    "question_types": ["single_choice", "multiple_choice"],
    "negative_marking": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid",
    "status": "pending",
    "estimated_completion": "2024-12-01T10:05:00Z"
  }
}
```

### 6.4 Get AI Job Status
```http
GET /ai/jobs/{job_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "type": "generate_quiz",
    "status": "completed",
    "progress": 100,
    "result": {
      "quiz_id": "uuid",
      "questions_generated": 50,
      "quality_score": 0.95
    }
  }
}
```

---

## 7. Test Taking Endpoints

### 7.1 Start Test Attempt
```http
POST /attempts
```

**Request Body:**
```json
{
  "quiz_id": "uuid",
  "enable_negative_marking": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "attempt_id": "uuid",
    "quiz": {
      "id": "uuid",
      "title": "SSC Practice Test",
      "total_questions": 50,
      "time_limit": 60,
      "negative_marking": true
    },
    "questions": [
      {
        "id": "uuid",
        "stem": "Question text here...",
        "options": [...],
        "question_type": "single_choice",
        "marks": 1.0
      }
    ],
    "started_at": "2024-12-01T10:00:00Z",
    "expires_at": "2024-12-01T11:00:00Z"
  }
}
```

### 7.2 Submit Answer
```http
POST /attempts/{attempt_id}/answer
```

**Request Body:**
```json
{
  "question_id": "uuid",
  "selected_option_ids": ["uuid1", "uuid2"],
  "time_spent_seconds": 45
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "answer_id": "uuid",
    "is_correct": true,
    "marks_earned": 1.0,
    "next_question": {...}
  }
}
```

### 7.3 Finish Test
```http
POST /attempts/{attempt_id}/finish
```

**Response:**
```json
{
  "success": true,
  "data": {
    "attempt_id": "uuid",
    "score_raw": 42.0,
    "score_percentage": 84.0,
    "total_marks": 50.0,
    "duration_seconds": 3540,
    "breakdown": {
      "correct_answers": 42,
      "incorrect_answers": 8,
      "unanswered": 0,
      "topic_wise": {...}
    }
  }
}
```

---

## 8. Results & Analytics Endpoints

### 8.1 Get Attempt Results
```http
GET /attempts/{attempt_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "quiz": {...},
    "score": {...},
    "answers": [...],
    "analytics": {
      "topic_performance": {...},
      "time_analysis": {...},
      "difficulty_analysis": {...}
    }
  }
}
```

### 8.2 Get User Analytics
```http
GET /analytics/user?time_range=30d&exam_id=uuid
```

**Query Parameters:**
- `time_range`: 7d, 30d, 90d, 1y, all
- `exam_id` (optional): Filter by specific exam
- `topic_id` (optional): Filter by specific topic

### 8.3 Download Result PDF
```http
GET /attempts/{attempt_id}/pdf
```

**Response:**
```json
{
  "success": true,
  "data": {
    "download_url": "https://s3.amazonaws.com/...",
    "expires_at": "2024-12-01T12:00:00Z"
  }
}
```

---

## 9. Payment & Subscription Endpoints

### 9.1 Get Wallet Balance
```http
GET /wallet/me
```

**Response:**
```json
{
  "success": true,
  "data": {
    "balance_credits": 150,
    "total_earned": 500,
    "total_spent": 350,
    "recent_transactions": [...]
  }
}
```

### 9.2 Purchase Credits
```http
POST /wallet/charge
```

**Request Body:**
```json
{
  "amount": 1000,
  "payment_method": "razorpay",
  "plan_id": "uuid"
}
```

### 9.3 Get Subscription Plans
```http
GET /plans
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Basic Plan",
      "price": 299,
      "period": "monthly",
      "credits": 500,
      "features": [...]
    }
  ]
}
```

---

## 10. Error Handling

### 10.1 Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "timestamp": "2024-12-01T10:00:00Z",
  "request_id": "req_123456789"
}
```

### 10.2 Common Error Codes
- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_ERROR`: Invalid or expired token
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

---

## 11. Rate Limiting

### 11.1 Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### 11.2 Rate Limit Rules
- **Authentication endpoints**: 5 requests per minute
- **AI generation**: 10 requests per hour
- **Quiz attempts**: 100 requests per hour
- **General API**: 1000 requests per hour

---

## 12. API Versioning

### 12.1 Version Strategy
- **URL versioning**: `/v1/`, `/v2/`
- **Backward compatibility** for at least 6 months
- **Deprecation notices** in response headers
- **Migration guides** for breaking changes

### 12.2 Version Deprecation
```http
X-API-Deprecated: true
X-API-Deprecation-Date: 2025-06-01
X-API-Sunset-Date: 2025-12-01
```

---

## 13. Next Steps

1. **Implement core endpoints** for authentication
2. **Create Pydantic schemas** for request/response validation
3. **Set up middleware** for authentication and rate limiting
4. **Write API tests** for all endpoints
5. **Generate OpenAPI documentation**

---

*This API design provides the foundation for the exam preparation platform. Refer to specific component LLDs for implementation details.*
