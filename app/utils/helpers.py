import uuid
import hashlib
import json
from typing import Any, Dict, List
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()

def generate_uuid() -> str:
    """Generate a new UUID string"""
    return str(uuid.uuid4())

def generate_checksum(content: str) -> str:
    """Generate SHA-256 checksum for content"""
    return hashlib.sha256(content.encode()).hexdigest()

def normalize_text(text: str) -> str:
    """Normalize text for comparison (remove extra spaces, lowercase)"""
    if not text:
        return ""
    return " ".join(text.lower().split())

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity using normalized comparison"""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    if not norm1 or not norm2:
        return 0.0
    
    # Simple similarity calculation (can be improved with more sophisticated algorithms)
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"

def format_percentage(value: float, total: float) -> str:
    """Format percentage with proper handling of edge cases"""
    if total == 0:
        return "0.00%"
    
    percentage = (value / total) * 100
    return f"{percentage:.2f}%"

def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely load JSON string with error handling"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default

def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """Safely dump object to JSON string with error handling"""
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize to JSON: {e}")
        return default

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Basic phone number validation for Indian numbers"""
    import re
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Indian phone numbers are 10 digits (excluding country code)
    if len(digits_only) == 10:
        return True
    
    # With country code +91
    if len(digits_only) == 12 and digits_only.startswith('91'):
        return True
    
    return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized

def get_current_timestamp() -> datetime:
    """Get current timestamp in UTC"""
    return datetime.now(timezone.utc)

def format_timestamp(timestamp: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp to string"""
    return timestamp.strftime(format_str)

def parse_timestamp(timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse timestamp string to datetime object"""
    return datetime.strptime(timestamp_str, format_str)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """Flatten a nested list"""
    return [item for sublist in nested_list for item in sublist]

def remove_duplicates_preserve_order(lst: List[Any]) -> List[Any]:
    """Remove duplicates from list while preserving order"""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
