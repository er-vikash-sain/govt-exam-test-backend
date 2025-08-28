# Backend LLD - AI Integration
**Component:** AI Generation System
**Technology:** OpenAI API, Anthropic Claude, FastAPI, Celery
**Version:** 1.0

---

## 1. AI Integration Overview

The AI integration system provides intelligent content generation for exam questions, explanations, and study materials using multiple AI providers with fallback mechanisms and quality control.

---

## 2. System Architecture

### 2.1 AI Service Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   AI Service    │    │   AI Providers  │
│   (Request)     │◄──►│   (Orchestrator)│◄──►│   (OpenAI/      │
└─────────────────┘    └─────────────────┘    │   Claude)       │
         │                       │            └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Redis Queue   │    │   Content       │
│   (Jobs)        │    │   Validator     │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Celery        │    │   Quality       │
│   Workers       │    │   Monitor       │
└─────────────────┘    └─────────────────┘
```

### 2.2 Data Flow
1. **User Request** → AI generation parameters
2. **Job Creation** → Queue in Redis
3. **Worker Processing** → AI provider selection
4. **Content Generation** → AI model inference
5. **Validation** → Quality checks and filtering
6. **Storage** → Database persistence
7. **Notification** → User completion alert

---

## 3. AI Provider Management

### 3.1 Provider Abstraction
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from enum import Enum

class AIProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"

class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_content(
        self,
        prompt: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content using AI model"""
        pass
    
    @abstractmethod
    async def get_cost_estimate(
        self,
        prompt: str,
        parameters: Dict[str, Any]
    ) -> float:
        """Estimate cost for generation"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available"""
        pass

class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT-4 and GPT-3.5 integration"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self.provider = AIProvider.OPENAI
    
    async def generate_content(
        self,
        prompt: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content using OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": parameters.get("system_prompt", "")},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=parameters.get("max_tokens", 1000),
                temperature=parameters.get("temperature", 0.7),
                response_format={"type": "json_object"}
            )
            
            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": self.model,
                "provider": self.provider.value
            }
        except Exception as e:
            raise AIProviderError(f"OpenAI generation failed: {str(e)}")

class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude integration"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.provider = AIProvider.ANTHROPIC
    
    async def generate_content(
        self,
        prompt: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content using Anthropic Claude"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=parameters.get("max_tokens", 1000),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "content": response.content[0].text,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "model": self.model,
                "provider": self.provider.value
            }
        except Exception as e:
            raise AIProviderError(f"Anthropic generation failed: {str(e)}")
```

### 3.2 Provider Selection Strategy
```python
class AIProviderManager:
    """Manages AI provider selection and fallback"""
    
    def __init__(self):
        self.providers = {
            AIProvider.OPENAI: OpenAIProvider(OPENAI_API_KEY, "gpt-4"),
            AIProvider.ANTHROPIC: AnthropicProvider(ANTHROPIC_API_KEY),
            AIProvider.HUGGINGFACE: HuggingFaceProvider(HF_API_KEY),
        }
        self.provider_priority = [
            AIProvider.OPENAI,      # Primary provider
            AIProvider.ANTHROPIC,   # Secondary provider
            AIProvider.HUGGINGFACE, # Fallback provider
        ]
    
    async def select_provider(
        self,
        content_type: str,
        complexity: str
    ) -> BaseAIProvider:
        """Select appropriate AI provider based on requirements"""
        
        # Check provider availability
        available_providers = []
        for provider_type in self.provider_priority:
            provider = self.providers[provider_type]
            if await provider.is_available():
                available_providers.append(provider)
        
        if not available_providers:
            raise AIProviderError("No AI providers available")
        
        # Select provider based on content type and complexity
        if content_type == "question_generation" and complexity == "high":
            # Use GPT-4 for complex questions
            for provider in available_providers:
                if provider.provider == AIProvider.OPENAI and "gpt-4" in provider.model:
                    return provider
        
        # Return first available provider
        return available_providers[0]
    
    async def generate_with_fallback(
        self,
        prompt: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content with automatic fallback"""
        
        last_error = None
        for provider_type in self.provider_priority:
            try:
                provider = self.providers[provider_type]
                if await provider.is_available():
                    return await provider.generate_content(prompt, parameters)
            except Exception as e:
                last_error = e
                continue
        
        raise AIProviderError(f"All providers failed: {last_error}")
```

---

## 4. Prompt Engineering

### 4.1 Prompt Templates
```python
class PromptManager:
    """Manages AI prompt templates and generation"""
    
    def __init__(self):
        self.templates = {
            "question_generation": {
                "system": """You are an expert exam question creator for Indian competitive exams. 
                Create high-quality, accurate questions that test understanding and application.
                Follow these guidelines:
                - Questions must be clear and unambiguous
                - Options should be plausible and well-distributed
                - Include detailed explanations
                - Ensure cultural sensitivity
                - Follow exam pattern requirements""",
                
                "user_template": """Generate {question_count} {difficulty} level questions for {subject} topic: {topic_name}
                
                Requirements:
                - Question type: {question_type}
                - Language: {language}
                - Include negative marking: {negative_marking}
                - Target audience: {exam_level} students
                
                Return response in JSON format:
                {{
                    "questions": [
                        {{
                            "stem": "Question text",
                            "options": ["A", "B", "C", "D"],
                            "correct_answer": "A",
                            "explanation": "Detailed explanation",
                            "difficulty": "medium",
                            "topic": "topic_name"
                        }}
                    ]
                }}"""
            },
            
            "explanation_generation": {
                "system": """You are an expert educator explaining concepts clearly and concisely.
                Provide step-by-step explanations that help students understand the topic.""",
                
                "user_template": """Generate a clear explanation for the following question:
                
                Question: {question_text}
                Correct Answer: {correct_answer}
                
                Requirements:
                - Language: {language}
                - Style: {style} (step-by-step, conceptual, or practical)
                - Length: {length} words
                
                Return response in JSON format:
                {{
                    "explanation": "Detailed explanation text",
                    "key_points": ["point1", "point2", "point3"],
                    "related_concepts": ["concept1", "concept2"]
                }}"""
            }
        }
    
    def generate_prompt(
        self,
        template_name: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Generate prompt from template with parameters"""
        template = self.templates[template_name]
        
        # Format system prompt
        system_prompt = template["system"]
        
        # Format user prompt
        user_prompt = template["user_template"].format(**parameters)
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }
```

### 4.2 Content-Specific Prompts
```python
class ContentPromptGenerator:
    """Generates content-specific prompts for different exam types"""
    
    @staticmethod
    def ssc_question_prompt(topic: str, difficulty: str) -> str:
        """Generate SSC-specific question prompt"""
        return f"""Create a {difficulty} level question for SSC exam on {topic}.
        
        SSC Question Guidelines:
        - Focus on general knowledge and reasoning
        - Use clear, simple language
        - Include current affairs if relevant
        - Ensure options are distinct
        - Provide practical examples"""
    
    @staticmethod
    def banking_question_prompt(topic: str, difficulty: str) -> str:
        """Generate Banking-specific question prompt"""
        return f"""Create a {difficulty} level question for Banking exam on {topic}.
        
        Banking Question Guidelines:
        - Emphasize quantitative aptitude
        - Include numerical problems
        - Test logical reasoning
        - Use banking terminology appropriately
        - Include real-world scenarios"""
    
    @staticmethod
    def upsc_question_prompt(topic: str, difficulty: str) -> str:
        """Generate UPSC-specific question prompt"""
        return f"""Create a {difficulty} level question for UPSC exam on {topic}.
        
        UPSC Question Guidelines:
        - Focus on analytical thinking
        - Include current affairs
        - Test decision-making ability
        - Use government and policy context
        - Ensure comprehensive coverage"""
```

---

## 5. Content Generation Pipeline

### 5.1 Generation Workflow
```python
class ContentGenerationPipeline:
    """Manages the complete content generation workflow"""
    
    def __init__(self):
        self.provider_manager = AIProviderManager()
        self.prompt_manager = PromptManager()
        self.validator = ContentValidator()
        self.storage = ContentStorage()
    
    async def generate_questions(
        self,
        exam_id: str,
        topic_ids: List[str],
        question_count: int,
        difficulty_mix: Dict[str, float],
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate questions for specific exam and topics"""
        
        # Calculate questions per difficulty
        questions_per_difficulty = self._calculate_question_distribution(
            question_count, difficulty_mix
        )
        
        generated_questions = []
        total_cost = 0.0
        
        for difficulty, count in questions_per_difficulty.items():
            if count > 0:
                questions = await self._generate_difficulty_questions(
                    exam_id, topic_ids, difficulty, count, language
                )
                generated_questions.extend(questions)
                total_cost += questions.get("cost", 0.0)
        
        # Validate and store questions
        validated_questions = await self.validator.validate_questions(
            generated_questions
        )
        
        # Store in database
        question_ids = await self.storage.store_questions(validated_questions)
        
        return {
            "question_ids": question_ids,
            "total_questions": len(validated_questions),
            "total_cost": total_cost,
            "quality_score": self._calculate_quality_score(validated_questions)
        }
    
    async def _generate_difficulty_questions(
        self,
        exam_id: str,
        topic_ids: List[str],
        difficulty: str,
        count: int,
        language: str
    ) -> List[Dict[str, Any]]:
        """Generate questions for specific difficulty level"""
        
        # Select appropriate provider
        provider = await self.provider_manager.select_provider(
            "question_generation", difficulty
        )
        
        # Generate prompt
        prompt_data = self.prompt_manager.generate_prompt(
            "question_generation",
            {
                "question_count": count,
                "difficulty": difficulty,
                "subject": "exam_subject",
                "topic_name": ", ".join(topic_ids),
                "question_type": "single_choice",
                "language": language,
                "negative_marking": "true",
                "exam_level": "graduate"
            }
        )
        
        # Generate content
        response = await provider.generate_content(
            prompt_data["user_prompt"],
            {
                "system_prompt": prompt_data["system_prompt"],
                "max_tokens": 2000,
                "temperature": 0.7
            }
        )
        
        # Parse and validate response
        questions = self._parse_ai_response(response["content"])
        
        return {
            "questions": questions,
            "cost": response.get("cost", 0.0),
            "provider": response["provider"],
            "model": response["model"]
        }
```

### 5.2 Batch Processing
```python
class BatchContentGenerator:
    """Handles batch content generation for multiple exams"""
    
    def __init__(self):
        self.pipeline = ContentGenerationPipeline()
        self.queue_manager = QueueManager()
    
    async def generate_batch(
        self,
        batch_config: Dict[str, Any]
    ) -> str:
        """Generate batch content and return job ID"""
        
        # Create batch job
        job_id = str(uuid.uuid4())
        
        # Queue generation tasks
        for exam_config in batch_config["exams"]:
            task = {
                "job_id": job_id,
                "exam_id": exam_config["exam_id"],
                "topics": exam_config["topics"],
                "question_count": exam_config["question_count"],
                "difficulty_mix": exam_config["difficulty_mix"],
                "language": exam_config.get("language", "en")
            }
            
            await self.queue_manager.enqueue_task(
                "question_generation",
                task
            )
        
        return job_id
    
    async def get_batch_status(self, job_id: str) -> Dict[str, Any]:
        """Get batch generation status"""
        return await self.queue_manager.get_job_status(job_id)
```

---

## 6. Content Validation & Quality Control

### 6.1 Content Validator
```python
class ContentValidator:
    """Validates AI-generated content for quality and accuracy"""
    
    def __init__(self):
        self.validators = [
            StructureValidator(),
            ContentQualityValidator(),
            DuplicateDetector(),
            CulturalSensitivityValidator(),
            LanguageValidator()
        ]
    
    async def validate_questions(
        self,
        questions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate generated questions"""
        
        validated_questions = []
        
        for question in questions:
            validation_result = await self._validate_single_question(question)
            
            if validation_result["is_valid"]:
                validated_questions.append(question)
            else:
                # Log validation failures for improvement
                await self._log_validation_failure(question, validation_result)
        
        return validated_questions
    
    async def _validate_single_question(
        self,
        question: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a single question"""
        
        validation_errors = []
        
        for validator in self.validators:
            try:
                result = await validator.validate(question)
                if not result["is_valid"]:
                    validation_errors.extend(result["errors"])
            except Exception as e:
                validation_errors.append(f"Validation error: {str(e)}")
        
        return {
            "is_valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "quality_score": self._calculate_quality_score(validation_errors)
        }

class StructureValidator:
    """Validates question structure and format"""
    
    async def validate(self, question: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        
        # Check required fields
        required_fields = ["stem", "options", "correct_answer", "explanation"]
        for field in required_fields:
            if field not in question or not question[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate options
        if "options" in question:
            if len(question["options"]) < 2:
                errors.append("Question must have at least 2 options")
            
            if "correct_answer" in question:
                correct = question["correct_answer"]
                if correct not in question["options"]:
                    errors.append("Correct answer must be one of the options")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

class DuplicateDetector:
    """Detects duplicate or similar questions"""
    
    async def validate(self, question: Dict[str, Any]) -> Dict[str, Any]:
        # Implement duplicate detection logic
        # This could use semantic similarity, checksums, or ML models
        
        # For now, return basic validation
        return {
            "is_valid": True,
            "errors": []
        }
```

---

## 7. Cost Management & Optimization

### 7.1 Cost Tracking
```python
class CostTracker:
    """Tracks AI generation costs and usage"""
    
    def __init__(self):
        self.db = Database()
    
    async def track_generation_cost(
        self,
        user_id: str,
        provider: str,
        model: str,
        tokens_used: int,
        cost_usd: float,
        content_type: str
    ):
        """Track generation cost for billing and monitoring"""
        
        cost_record = {
            "user_id": user_id,
            "provider": provider,
            "model": model,
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "content_type": content_type,
            "timestamp": datetime.utcnow()
        }
        
        await self.db.insert("ai_generation_costs", cost_record)
    
    async def get_user_costs(
        self,
        user_id: str,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """Get cost summary for user"""
        
        query = """
        SELECT 
            provider,
            model,
            content_type,
            SUM(tokens_used) as total_tokens,
            SUM(cost_usd) as total_cost,
            COUNT(*) as generation_count
        FROM ai_generation_costs
        WHERE user_id = %s 
        AND timestamp >= NOW() - INTERVAL %s
        GROUP BY provider, model, content_type
        """
        
        results = await self.db.execute(query, (user_id, time_range))
        
        return {
            "total_cost": sum(r["total_cost"] for r in results),
            "total_tokens": sum(r["total_tokens"] for r in results),
            "breakdown": results
        }
    
    async def check_user_budget(
        self,
        user_id: str,
        estimated_cost: float
    ) -> bool:
        """Check if user has sufficient budget"""
        
        user_wallet = await self.db.get_user_wallet(user_id)
        daily_cost = await self.get_user_daily_cost(user_id)
        
        # Check daily limit
        if daily_cost + estimated_cost > user_wallet["daily_limit"]:
            return False
        
        # Check total balance
        if estimated_cost > user_wallet["balance"]:
            return False
        
        return True
```

### 7.2 Optimization Strategies
```python
class ContentOptimizer:
    """Optimizes content generation for cost and quality"""
    
    def __init__(self):
        self.cost_tracker = CostTracker()
        self.quality_monitor = QualityMonitor()
    
    async def optimize_generation_parameters(
        self,
        content_type: str,
        complexity: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Optimize generation parameters based on user history"""
        
        # Get user's successful generations
        user_history = await self.quality_monitor.get_user_history(user_id)
        
        # Analyze cost vs quality patterns
        optimal_params = self._analyze_optimal_parameters(user_history)
        
        # Adjust based on user's budget
        budget_constraints = await self._get_budget_constraints(user_id)
        
        return self._apply_budget_constraints(optimal_params, budget_constraints)
    
    def _analyze_optimal_parameters(
        self,
        user_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user history to find optimal parameters"""
        
        # Group by content type and complexity
        grouped_history = {}
        for item in user_history:
            key = (item["content_type"], item["complexity"])
            if key not in grouped_history:
                grouped_history[key] = []
            grouped_history[key].append(item)
        
        optimal_params = {}
        
        for (content_type, complexity), items in grouped_history.items():
            # Find parameters that give best quality/cost ratio
            best_ratio = 0
            best_params = None
            
            for item in items:
                ratio = item["quality_score"] / item["cost_usd"]
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_params = item["generation_params"]
            
            optimal_params[(content_type, complexity)] = best_params
        
        return optimal_params
```

---

## 8. Quality Monitoring & Improvement

### 8.1 Quality Metrics
```python
class QualityMonitor:
    """Monitors content quality and provides feedback"""
    
    def __init__(self):
        self.metrics = [
            "accuracy_rate",
            "user_satisfaction",
            "completion_rate",
            "error_reports"
        ]
    
    async def track_question_quality(
        self,
        question_id: str,
        metrics: Dict[str, Any]
    ):
        """Track quality metrics for questions"""
        
        quality_record = {
            "question_id": question_id,
            "accuracy_rate": metrics.get("accuracy_rate", 0.0),
            "user_satisfaction": metrics.get("user_satisfaction", 0.0),
            "completion_rate": metrics.get("completion_rate", 0.0),
            "error_reports": metrics.get("error_reports", 0),
            "timestamp": datetime.utcnow()
        }
        
        await self.db.insert("question_quality_metrics", quality_record)
    
    async def get_quality_report(
        self,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """Generate quality report for monitoring"""
        
        query = """
        SELECT 
            AVG(accuracy_rate) as avg_accuracy,
            AVG(user_satisfaction) as avg_satisfaction,
            AVG(completion_rate) as avg_completion,
            SUM(error_reports) as total_errors,
            COUNT(*) as total_questions
        FROM question_quality_metrics
        WHERE timestamp >= NOW() - INTERVAL %s
        """
        
        result = await self.db.execute(query, (time_range,))
        
        return {
            "average_accuracy": result[0]["avg_accuracy"],
            "average_satisfaction": result[0]["avg_satisfaction"],
            "average_completion": result[0]["avg_completion"],
            "total_errors": result[0]["total_errors"],
            "total_questions": result[0]["total_questions"]
        }
```

---

## 9. Error Handling & Resilience

### 9.1 Error Management
```python
class AIErrorHandler:
    """Handles AI generation errors and provides fallbacks"""
    
    def __init__(self):
        self.error_patterns = {
            "rate_limit": "Rate limit exceeded",
            "quota_exceeded": "Quota exceeded",
            "model_unavailable": "Model temporarily unavailable",
            "content_policy": "Content policy violation",
            "network_error": "Network connection error"
        }
    
    async def handle_generation_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle generation errors with appropriate responses"""
        
        error_type = self._classify_error(error)
        
        if error_type == "rate_limit":
            return await self._handle_rate_limit(context)
        elif error_type == "quota_exceeded":
            return await self._handle_quota_exceeded(context)
        elif error_type == "model_unavailable":
            return await self._handle_model_unavailable(context)
        else:
            return await self._handle_generic_error(error, context)
    
    async def _handle_rate_limit(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle rate limit errors"""
        
        # Implement exponential backoff
        retry_after = self._calculate_retry_delay(context.get("retry_count", 0))
        
        return {
            "error_type": "rate_limit",
            "retry_after": retry_after,
            "suggestion": "Retry after waiting or use different provider"
        }
    
    async def _handle_quota_exceeded(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle quota exceeded errors"""
        
        # Switch to different provider or model
        alternative_provider = await self._find_alternative_provider(context)
        
        return {
            "error_type": "quota_exceeded",
            "alternative_provider": alternative_provider,
            "suggestion": "Use alternative provider or upgrade plan"
        }
```

---

## 10. Next Steps

1. **Implement AI provider** abstraction layer
2. **Create prompt templates** for different content types
3. **Set up content validation** and quality control
4. **Implement cost tracking** and budget management
5. **Add quality monitoring** and improvement loops

---

*This AI integration system provides intelligent content generation with quality control, cost management, and fallback mechanisms for reliable operation.*
