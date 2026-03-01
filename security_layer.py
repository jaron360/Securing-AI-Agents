"""
Security Layer for AI Agent
Provides input validation, output sanitization, and security guardrails
"""
import re
from typing import Tuple


class SecurityGuardrails:
    """Security validation and sanitization for AI agent"""
    
    # Patterns for detecting malicious input
    INJECTION_PATTERNS = [
        r'ignore\s+(all\s+)?(previous|prior|above)\s+instructions',
        r'disregard\s+(all\s+)?(previous|prior|above)',
        r'forget\s+(all\s+)?(previous|prior|above)',
        r'system\s+prompt',
        r'show\s+(me\s+)?(your|the)\s+(instructions|prompt|rules)',
        r'reveal\s+(your|the)\s+(instructions|prompt|rules)',
        r'developer\s+mode',
        r'jailbreak',
        r'bypass\s+(all\s+)?(restrictions|rules|filters)',
        r'act\s+as\s+(if|though)',
        r'pretend\s+(you|to)\s+(are|be)',
        r'roleplay',
        r'sudo\s+mode',
        r'admin\s+mode',
        r'unrestricted\s+mode',
    ]
    
    # Patterns for detecting sensitive data
    SENSITIVE_PATTERNS = [
        # API Keys and Tokens
        (r'sk-[a-zA-Z0-9\-_]{5,}', '[REDACTED_API_KEY]'),  # OpenAI/Stripe API keys
        (r'AKIA[0-9A-Z]{16}', '[REDACTED_AWS_KEY]'),  # AWS access keys
        (r'(?:aws_secret_access_key|AWS_SECRET_ACCESS_KEY)\s*[:=]\s*[^\s]+', 'aws_secret_access_key: [REDACTED]'),  # AWS secrets
        (r'eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+', '[REDACTED_JWT]'),  # JWT tokens
        (r'ghp_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]'),  # GitHub tokens
        (r'glpat-[a-zA-Z0-9\-_]{20,}', '[REDACTED_GITLAB_TOKEN]'),  # GitLab tokens
        (r'xox[baprs]-[0-9a-zA-Z\-]+', '[REDACTED_SLACK_TOKEN]'),  # Slack tokens
        (r'AIza[0-9A-Za-z\-_]{35}', '[REDACTED_GOOGLE_API_KEY]'),  # Google API keys
        
        # Personal Information
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]'),  # Emails
        (r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]'),  # SSN
        (r'\b\d{16}\b', '[REDACTED_CC]'),  # Credit card (16 digits)
        (r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b', '[REDACTED_CC]'),  # Credit card (formatted)
        (r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b', '[REDACTED_PHONE]'),  # US phone numbers
        
        # Credentials
        (r'password\s*[:=]\s*[^\s]+', 'password: [REDACTED]'),  # Passwords
        (r'(?:api_key|apikey|api-key)\s*[:=]\s*[^\s]+', 'api_key: [REDACTED]'),  # Generic API keys
        (r'(?:token|auth_token|access_token)\s*[:=]\s*[^\s]+', 'token: [REDACTED]'),  # Generic tokens
        (r'(?:secret|client_secret)\s*[:=]\s*[^\s]+', 'secret: [REDACTED]'),  # Secrets
        
        # IP Addresses (private ranges)
        (r'\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b', '[REDACTED_PRIVATE_IP]'),
        
        # Database Connection Strings
        (r'(?:mongodb|mysql|postgresql|postgres)://[^\s]+', '[REDACTED_DB_CONNECTION]'),
        
        # Private Keys
        (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----[^-]+-----END (?:RSA |EC )?PRIVATE KEY-----', '[REDACTED_PRIVATE_KEY]'),
    ]
    
    # Allowed cybersecurity news keywords (must contain at least one)
    ALLOWED_KEYWORDS = [
        'security', 'cybersecurity', 'vulnerability', 'vulnerabilities',
        'cve', 'breach', 'incident', 'incidents', 'attack', 'attacks',
        'threat', 'threats', 'malware', 'ransomware', 'exploit', 'exploits',
        'hack', 'hacker', 'hacking', 'news', 'latest', 'recent',
        'today', 'yesterday', '24 hours', 'this week', 'reddit',
        'hacker news', 'nvd', 'advisory', 'advisories', 'patch',
        'zero-day', 'zero day', 'phishing', 'compromise', 'compromised'
    ]
    
    # Blocked off-topic keywords (script creation, coding, etc.)
    BLOCKED_OFFTOPIC_KEYWORDS = [
        'write a script', 'create a script', 'write code', 'create code',
        'write a program', 'create a program', 'build a tool', 'develop',
        'write python', 'write bash', 'write javascript', 'write java',
        'generate code', 'code for', 'script for', 'function to',
        'help me code', 'help me write', 'help me create', 'help me build',
        'write me', 'create me', 'build me', 'make me a',
        'how do i code', 'how do i write', 'how do i create',
        'tutorial', 'teach me to', 'show me how to code',
        'programming', 'software development', 'app development'
    ]
    
    # Maximum input length (strict limit for security)
    MAX_INPUT_LENGTH = 60  # Maximum 60 characters per query
    
    # Minimum input length
    MIN_INPUT_LENGTH = 10  # At least 10 characters for meaningful query
    
    @classmethod
    def check_input(cls, user_input: str) -> Tuple[bool, str, str]:
        """
        Validate user input for security threats
        
        Returns:
            (is_safe, sanitized_input, reason)
        """
        # Check input length
        if len(user_input) > cls.MAX_INPUT_LENGTH:
            return False, "", f"Input too long ({len(user_input)} chars, max {cls.MAX_INPUT_LENGTH})"
        
        if len(user_input) < cls.MIN_INPUT_LENGTH:
            return False, "", "Input too short"
        
        # Check for excessive special characters (potential obfuscation)
        special_char_ratio = sum(1 for c in user_input if not c.isalnum() and not c.isspace()) / len(user_input)
        if special_char_ratio > 0.5:
            return False, "", "Excessive special characters detected"
        
        # Check for prompt injection patterns
        user_input_lower = user_input.lower()
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                return False, "", f"Potential prompt injection detected: {pattern}"
        
        # Check for requests to reveal system information
        system_reveal_keywords = ['system prompt', 'instructions', 'show me your', 'reveal your', 'what are your rules']
        if any(keyword in user_input_lower for keyword in system_reveal_keywords):
            return False, "", "Attempt to reveal system information detected"
        
        # Check for off-topic requests (script creation, coding, etc.)
        for keyword in cls.BLOCKED_OFFTOPIC_KEYWORDS:
            if keyword in user_input_lower:
                return False, "", "Off-topic request detected. This agent only provides cybersecurity news and incident information."
        
        # Check if query is on-topic (must contain at least one allowed keyword)
        has_allowed_keyword = any(keyword in user_input_lower for keyword in cls.ALLOWED_KEYWORDS)
        if not has_allowed_keyword:
            return False, "", "Query must be related to cybersecurity news, incidents, or vulnerabilities."
        
        # Check for malicious intent (but allow in context of news/research)
        # Only block if asking HOW to do malicious things, not asking ABOUT them
        malicious_how_patterns = [
            r'how\s+(can|do|to)\s+(i|you|we)\s+(hack|exploit|create\s+malware|bypass)',
            r'show\s+me\s+how\s+to\s+(hack|exploit|create\s+malware)',
            r'teach\s+me\s+(to\s+)?(hack|exploit|create\s+malware)',
            r'help\s+me\s+(hack|exploit|create\s+malware)',
            r'how\s+to\s+(hack|exploit|create\s+malware|bypass)',
        ]
        
        for pattern in malicious_how_patterns:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                return False, "", "Request for malicious instructions detected"
        
        # Check for sensitive data in input (warn but allow)
        for pattern, _ in cls.SENSITIVE_PATTERNS:
            if re.search(pattern, user_input):
                return False, "", "Sensitive data detected in input (API keys, passwords, etc.)"
        
        # Sanitize input (basic cleanup)
        sanitized = user_input.strip()
        
        return True, sanitized, "Input validated successfully"
    
    @classmethod
    def sanitize_output(cls, output: str) -> str:
        """
        Sanitize agent output to remove sensitive data
        
        Args:
            output: Raw agent output
            
        Returns:
            Sanitized output with sensitive data redacted
        """
        sanitized = output
        
        # Redact sensitive patterns
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized)
        
        # Additional cleanup
        sanitized = sanitized.strip()
        
        return sanitized
    
    @classmethod
    def validate_tool_output(cls, tool_name: str, output: str) -> Tuple[bool, str]:
        """
        Validate tool output before passing to agent
        
        Args:
            tool_name: Name of the tool
            output: Tool output
            
        Returns:
            (is_valid, sanitized_output)
        """
        # Check output length
        if len(output) > 50000:  # 50KB limit
            return False, "Tool output too large"
        
        # Sanitize output
        sanitized = cls.sanitize_output(output)
        
        return True, sanitized


def apply_security_guardrails(user_input: str) -> Tuple[bool, str, str]:
    """
    Convenience function to apply security guardrails
    
    Args:
        user_input: User's input string
        
    Returns:
        (is_safe, sanitized_input, reason)
    """
    return SecurityGuardrails.check_input(user_input)
