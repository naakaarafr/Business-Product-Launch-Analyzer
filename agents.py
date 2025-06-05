from crewai import Agent
from tools import search_tool
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import time
import logging
import signal
from typing import Any, Dict, List, Optional
from langchain.schema import BaseMessage
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
import threading
from functools import wraps
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def timeout_handler(func):
    """Decorator to add timeout functionality to methods"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        timeout = getattr(self, 'timeout', 180)  # Reduced to 3 minutes
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(self, *args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            logger.error(f"Method {func.__name__} timed out after {timeout} seconds")
            raise TimeoutError(f"Operation timed out after {timeout} seconds")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    return wrapper

class RobustGeminiLLM(ChatGoogleGenerativeAI):
    """
    Enhanced ChatGoogleGenerativeAI with better error handling for overloaded models
    """
    
    def __init__(self, max_retries: int = 5, base_delay: int = 10, timeout: int = 180, **kwargs):
        # Remove custom parameters from kwargs before passing to parent
        kwargs.pop('max_retries', None)
        kwargs.pop('base_delay', None)
        kwargs.pop('timeout', None)
        
        # Set more conservative defaults
        kwargs.setdefault('temperature', 0.1)  # Lower temperature for consistency
        kwargs.setdefault('verbose', False)    # Reduce verbosity
        
        # Call parent constructor first
        super().__init__(**kwargs)
        
        # Set custom attributes using object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'max_retries', max_retries)
        object.__setattr__(self, 'base_delay', base_delay)
        object.__setattr__(self, 'timeout', timeout)
    
    def _calculate_backoff_delay(self, attempt: int) -> int:
        """Calculate delay with exponential backoff and jitter"""
        # Exponential backoff: 10s, 20s, 40s, 80s, 160s
        delay = self.base_delay * (2 ** attempt)
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.1, 0.3) * delay
        return int(delay + jitter)
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if error is retryable"""
        error_str = str(error).lower()
        retryable_indicators = [
            "503", "overloaded", "service unavailable", "timeout",
            "quota", "rate limit", "429", "too many requests", 
            "resource exhausted", "limit exceeded", "rate_limit_exceeded",
            "temporarily unavailable", "server error", "internal error"
        ]
        return any(indicator in error_str for indicator in retryable_indicators)
    
    @timeout_handler
    def _generate(self, messages: List[BaseMessage], **kwargs) -> Any:
        """Override the _generate method with robust retry logic"""
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Generation attempt {attempt + 1}/{self.max_retries + 1}")
                
                # Add timeout to the kwargs for this specific call
                generation_kwargs = kwargs.copy()
                generation_kwargs['timeout'] = 120  # 2 minute timeout per attempt
                
                result = super()._generate(messages, **generation_kwargs)
                logger.info("Generation successful")
                return result
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                logger.warning(f"Generation attempt {attempt + 1} failed: {str(e)[:200]}...")
                
                # Check if this is a retryable error
                if self._is_retryable_error(e) and attempt < self.max_retries:
                    delay = self._calculate_backoff_delay(attempt)
                    
                    # Special handling for overloaded model
                    if "overloaded" in error_str or "503" in error_str:
                        delay = max(delay, 60)  # Minimum 1 minute wait for overloaded model
                        print(f"🔄 Model overloaded. Waiting {delay} seconds before retry... (Attempt {attempt + 1})")
                    else:
                        print(f"⚠️ API error. Waiting {delay} seconds... (Attempt {attempt + 1})")
                    
                    logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    continue
                else:
                    # Non-retryable error or max retries reached
                    break
        
        # If we get here, all retries failed
        error_msg = f"Failed after {self.max_retries + 1} attempts. Last error: {str(last_error)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    @timeout_handler
    def invoke(self, input_data, **kwargs):
        """Override invoke method with robust error handling"""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Invoke attempt {attempt + 1}/{self.max_retries + 1}")
                result = super().invoke(input_data, **kwargs)
                logger.info("Invoke successful")
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Invoke attempt {attempt + 1} failed: {str(e)[:200]}...")
                
                if self._is_retryable_error(e) and attempt < self.max_retries:
                    delay = self._calculate_backoff_delay(attempt)
                    
                    if "overloaded" in str(e).lower() or "503" in str(e):
                        delay = max(delay, 60)
                        print(f"🔄 Service overloaded. Waiting {delay} seconds... (Attempt {attempt + 1})")
                    else:
                        print(f"⚠️ Service error. Waiting {delay} seconds... (Attempt {attempt + 1})")
                    
                    time.sleep(delay)
                    continue
                else:
                    break
        
        error_msg = f"Invoke failed after {self.max_retries + 1} attempts. Last error: {str(last_error)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def create_llm_with_robust_handling():
    """Create LLM with robust error handling and fallback options"""
    print("🔧 Initializing Gemini with robust error handling...")
    
    # Try different model configurations in order of preference
    model_configs = [
        {
            "model": "gemini-2.0-flash",  # Try experimental first
            "temperature": 0.1,
            "max_retries": 5,
            "base_delay": 10,
            "timeout": 180
        }
    ]
    
    for i, config in enumerate(model_configs):
        try:
            print(f"🧪 Trying {config['model']}...")
            
            llm = RobustGeminiLLM(
                model=config["model"],
                verbose=False,
                temperature=config["temperature"],
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                max_retries=config["max_retries"],
                base_delay=config["base_delay"],
                timeout=config["timeout"]
            )
            
            # Test the LLM with a simple query
            test_response = llm.invoke("Say 'OK' if you're working")
            print(f"✅ {config['model']} initialized and tested successfully")
            return llm
            
        except Exception as e:
            print(f"❌ {config['model']} failed: {str(e)[:100]}...")
            if i == len(model_configs) - 1:
                # Last model failed, raise the error
                raise Exception(f"All model configurations failed. Last error: {str(e)}")
            continue
    
    raise Exception("Failed to initialize any LLM configuration")

# Initialize LLM with robust handling
try:
    llm = create_llm_with_robust_handling()
except Exception as e:
    print(f"🚨 Critical Error: Could not initialize any LLM: {str(e)}")
    print("📝 Please check:")
    print("   1. Your GOOGLE_API_KEY is valid")
    print("   2. Your API quota is not exhausted")
    print("   3. Gemini service is available")
    raise

# Create agents with shorter timeouts and better error handling
print("👥 Creating agents with optimized settings...")

market_research_analyst = Agent(
    role="Market Research Analyst",
    goal="Provide quick, focused market analysis with key insights",
    backstory="""You are an efficient market research analyst who provides concise, 
                actionable insights. You focus on the most important market data and 
                avoid lengthy explanations.""",
    verbose=False,  # Reduced verbosity
    allow_delegation=False,
    tools=[search_tool],
    llm=llm,
    max_execution_time=240  # 4 minutes max per agent
)

technology_expert = Agent(
    role="Technology Expert",
    goal="Assess technical feasibility with practical recommendations",
    backstory="""You are a practical technology expert who focuses on implementable 
                solutions. You provide clear technical assessments without unnecessary 
                complexity.""",
    verbose=False,
    allow_delegation=False,
    tools=[search_tool],
    llm=llm,
    max_execution_time=240
)

business_consultant = Agent(
    role="Business Consultant",
    goal="Create actionable business strategies and launch plans",
    backstory="""You are a results-oriented business consultant who creates practical, 
                implementable business strategies. You focus on clear action items and 
                realistic timelines.""",
    verbose=False,
    allow_delegation=False,
    tools=[search_tool],
    llm=llm,
    max_execution_time=240
)

print("🚀 All agents initialized successfully with robust error handling!")