from crewai import Crew, Process
from agents import market_research_analyst, technology_expert, business_consultant
from tasks import create_tasks, create_emergency_tasks
from dotenv import load_dotenv
import sys
import os
import time
import logging
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdaptiveCrewHandler:
    """Adaptive handler that tries different strategies based on failures"""
    
    def __init__(self, product_name):
        self.product_name = product_name
        self.strategies = [
            {"name": "Full Analysis", "timeout": 600, "tasks": "full"},     # 10 minutes
            {"name": "Quick Analysis", "timeout": 300, "tasks": "quick"},   # 5 minutes
            {"name": "Emergency Analysis", "timeout": 120, "tasks": "emergency"}  # 2 minutes
        ]
        self.current_strategy = 0
    
    def get_current_strategy(self):
        """Get the current strategy configuration"""
        if self.current_strategy >= len(self.strategies):
            return None
        return self.strategies[self.current_strategy]
    
    def next_strategy(self):
        """Move to the next fallback strategy"""
        self.current_strategy += 1
        return self.get_current_strategy()
    
    def create_crew_for_strategy(self, strategy):
        """Create crew based on strategy"""
        print(f"🎯 Using strategy: {strategy['name']}")
        
        # Choose tasks based on strategy
        if strategy['tasks'] == 'emergency':
            tasks = create_emergency_tasks(self.product_name)
            print("🆘 Using emergency simplified tasks (no web search)")
        elif strategy['tasks'] == 'quick':
            tasks = create_tasks(self.product_name)  # Regular tasks but with timeout
            print("⚡ Using quick analysis tasks")
        else:
            tasks = create_tasks(self.product_name)
            print("🔍 Using full analysis tasks")
        
        # Create crew with strategy-specific settings
        crew = Crew(
            agents=[market_research_analyst, technology_expert, business_consultant],
            tasks=tasks,
            verbose=0 if strategy['tasks'] == 'emergency' else 1,
            process=Process.sequential,
            max_execution_time=strategy['timeout'],
        )
        
        return crew
    
    def execute_with_timeout(self, crew, timeout_seconds):
        """Execute crew with specific timeout"""
        result = [None]
        error = [None]
        
        def run_crew():
            try:
                result[0] = crew.kickoff()
            except Exception as e:
                error[0] = e
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_crew)
            try:
                future.result(timeout=timeout_seconds)
                if error[0]:
                    raise error[0]
                return result[0]
            except FuturesTimeoutError:
                raise TimeoutError(f"Crew execution timed out after {timeout_seconds} seconds")

def create_crewai_setup(product_name, max_attempts=3):
    """Create and execute CrewAI setup with adaptive fallback strategies"""
    
    print(f"\n{'='*60}")
    print(f"🚀 Starting Adaptive Business Analysis for: {product_name}")
    print(f"🎯 Will try up to {max_attempts} strategies if needed")
    print(f"{'='*60}\n")
    
    handler = AdaptiveCrewHandler(product_name)
    
    for attempt in range(max_attempts):
        strategy = handler.get_current_strategy()
        if not strategy:
            return "❌ All strategies exhausted. The API service appears to be unavailable."
        
        print(f"\n{'='*40}")
        print(f"📋 Attempt {attempt + 1}: {strategy['name']}")
        print(f"⏱️ Timeout: {strategy['timeout']/60:.1f} minutes")
        print(f"{'='*40}")
        
        try:
            # Create crew for current strategy
            crew = handler.create_crew_for_strategy(strategy)
            
            # Execute with timeout
            print(f"🔄 Executing {strategy['name'].lower()}...")
            result = handler.execute_with_timeout(crew, strategy['timeout'])
            
            print(f"\n✅ SUCCESS with {strategy['name']}!")
            print(f"{'='*60}")
            return result
            
        except TimeoutError as e:
            print(f"\n⏰ {strategy['name']} timed out")
            if attempt < max_attempts - 1:
                print("🔄 Trying next strategy...")
                handler.next_strategy()
                continue
            else:
                return f"❌ All strategies timed out. The service may be overloaded. Please try again later."
        
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for specific error types
            if "overloaded" in error_str or "503" in error_str:
                print(f"🚨 Service overloaded detected")
                if attempt < max_attempts - 1:
                    wait_time = (attempt + 1) * 60  # 1, 2, 3 minutes
                    print(f"⏳ Waiting {wait_time} seconds for service to recover...")
                    time.sleep(wait_time)
                    continue
                else:
                    return f"❌ Service is overloaded and all retry attempts failed. Please try again in 10-15 minutes."
            
            elif any(indicator in error_str for indicator in ["quota", "rate limit", "429"]):
                print(f"📊 API quota/rate limit reached")
                if attempt < max_attempts - 1:
                    wait_time = (attempt + 1) * 90  # 1.5, 3, 4.5 minutes
                    print(f"⏳ Waiting {wait_time} seconds for quota refresh...")
                    time.sleep(wait_time)
                    continue
                else:
                    return f"❌ API quota exhausted. Please try again later when your quota refreshes."
            
            else:
                print(f"❌ Unexpected error: {str(e)[:100]}...")
                if attempt < max_attempts - 1:
                    print("🔄 Trying next strategy...")
                    handler.next_strategy()
                    continue
                else:
                    return f"❌ Analysis failed with error: {str(e)}"
    
    return "❌ Analysis could not be completed after all attempts."

def get_product_name():
    """Get product name from user input with validation"""
    print("\n🎯 CrewAI Adaptive Business Analyzer")
    print("=" * 50)
    print("🧠 Smart Analysis with Fallback Strategies:")
    print("• Full Analysis (10 min) - Complete market research")
    print("• Quick Analysis (5 min) - Essential insights only")  
    print("• Emergency Analysis (2 min) - Basic assessment")
    print("=" * 50)
    print("💡 The system will automatically adapt if services are slow")
    
    while True:
        product_name = input("\n📝 Enter the product name to analyze: ").strip()
        
        if not product_name:
            print("❌ Please enter a valid product name.")
            continue
        
        if len(product_name) > 100:
            print("❌ Product name too long. Please use a shorter name (max 100 characters).")
            continue
        
        # Simple validation
        if len(product_name.split()) > 5:
            print("💡 Consider using a shorter, more specific product name for better results.")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                continue
        
        print(f"\n🔍 You want to analyze: '{product_name}'")
        confirm = input("Start analysis? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            return product_name

def check_service_status():
    """Check if required services are available"""
    required_keys = ['GOOGLE_API_KEY', 'SERPER_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing required API keys: {', '.join(missing_keys)}")
        print("Please ensure your .env file contains all required API keys.")
        return False
    
    print("✅ API keys found")
    
    # Try to test Gemini availability (optional)
    try:
        from agents import llm
        test_result = llm.invoke("test")
        print("✅ Gemini service is responsive")
        return True
    except Exception as e:
        if "overloaded" in str(e).lower() or "503" in str(e):
            print("⚠️ Gemini service is currently overloaded but will retry automatically")
            return True
        else:
            print(f"⚠️ Gemini service test failed: {str(e)[:100]}...")
            return True  # Continue anyway, let the adaptive handler deal with it

def save_results(results, product_name):
    """Save results to a file with error handling"""
    try:
        # Create a safe filename
        safe_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name.lower().replace(' ', '_')}_analysis.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Business Analysis Report for: {product_name}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Tool: CrewAI Adaptive Business Analyzer\n")
            f.write("=" * 60 + "\n\n")
            f.write(str(results))
        
        print(f"💾 Results saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving file: {str(e)}")
        return None

def main():
    """Main function with adaptive error handling"""
    try:
        print("🔧 Initializing CrewAI Adaptive Business Analyzer...")
        
        # Check service status
        if not check_service_status():
            sys.exit(1)
        
        # Get product name from user
        product_name = get_product_name()
        
        print(f"\n⚠️ Important Notes:")
        print(f"• System will adapt automatically if APIs are slow/overloaded")
        print(f"• You can interrupt with Ctrl+C if needed")
        print(f"• Results will be optimized based on available response time")
        
        # Run the adaptive analysis
        print(f"\n🚀 Starting adaptive analysis for '{product_name}'...")
        results = create_crewai_setup(product_name, max_attempts=3)
        
        # Check if we got valid results
        if isinstance(results, str) and results.startswith("❌"):
            print(f"\n{results}")
            print("\n💡 Suggestions:")
            print("• Try again in 10-15 minutes when services are less loaded")
            print("• Use a simpler, more specific product name")
            print("• Check your internet connection")
            return
        
        # Display results
        print("\n📊 ANALYSIS RESULTS:")
        print("=" * 60)
        print(results)
        
        # Ask if user wants to save results
        save_choice = input("\n💾 Save results to file? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes']:
            save_results(results, product_name)
        
        print("\n✨ Analysis completed successfully!")
        print("Thank you for using CrewAI Adaptive Business Analyzer!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user.")
        print("💡 The adaptive system was designed to handle API delays automatically.")
        sys.exit(0)
    except Exception as e:
        error_str = str(e).lower()
        if "overloaded" in error_str or "503" in error_str:
            print(f"\n🚨 Service Overloaded: The AI service is currently experiencing high demand.")
            print("💡 Please try again in 10-15 minutes when the load decreases.")
        elif any(keyword in error_str for keyword in ["quota", "rate limit", "timeout"]):
            print(f"\n📊 Service Limit: {str(e)}")
            print("💡 Please try again later when your API quota has refreshed.")
        else:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("💡 Please check your configuration and try again.")
        
        logger.error(f"Main function error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()