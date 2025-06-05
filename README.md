# Business Product Launch Analyzer

> An intelligent multi-agent system that provides comprehensive business analysis for any product using adaptive fallback strategies and robust error handling.

## 🌟 Overview

The CrewAI Adaptive Business Analyzer is a sophisticated AI-powered tool that analyzes business opportunities for any product. It employs three specialized AI agents working together to provide market research, technical assessment, and business strategy recommendations. The system features adaptive fallback strategies to ensure reliable results even when APIs are overloaded or experiencing issues.

## 🤖 Meet the AI Team

### 1. Market Research Analyst
- **Role**: Analyzes target customers, market size, competitors, and pricing strategies
- **Expertise**: Market research, customer segmentation, competitive analysis
- **Output**: Focused market insights and customer targeting recommendations

### 2. Technology Expert  
- **Role**: Assesses technical feasibility and implementation requirements
- **Expertise**: Manufacturing processes, equipment needs, quality control, technical challenges
- **Output**: Practical technical roadmap and feasibility assessment

### 3. Business Consultant
- **Role**: Creates actionable business strategies and launch plans
- **Expertise**: Business models, revenue streams, timelines, risk assessment, funding estimates
- **Output**: Comprehensive business strategy with clear action items

## 🚀 Key Features

### Adaptive Fallback System
- **Full Analysis** (10 minutes): Complete market research with web searching
- **Quick Analysis** (5 minutes): Essential insights with reduced scope  
- **Emergency Analysis** (2 minutes): Basic assessment without web research
- Automatically switches strategies if APIs are slow or overloaded

### Robust Error Handling
- Exponential backoff for API rate limits
- Intelligent retry logic for overloaded services
- Timeout protection for all operations
- Graceful degradation when services are unavailable

### Smart Features
- Real-time web search integration for current market data
- Structured output with consistent formatting
- Progress tracking and status updates
- Results saving to formatted text files
- User-friendly console interface with emojis and clear messaging

## 🛠 Installation

### Prerequisites
- Python 3.8 or higher
- Google AI API key (for Gemini)
- Serper API key (for web search)

### Step 1: Clone the Repository
```bash
git clone https://github.com/naakaarafr/crewai-business-analyzer.git
cd crewai-business-analyzer
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables
Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

#### Getting API Keys:

**Google AI API Key (Gemini)**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new project or select existing one
3. Go to "Get API Key" and create a new key
4. Copy the API key to your `.env` file

**Serper API Key (Search)**
1. Visit [Serper.dev](https://serper.dev/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Copy the API key to your `.env` file

### Step 4: Verify Installation
```bash
python config.py
```
This will validate your API keys and display configuration information.

## 🎯 Usage

### Basic Usage
```bash
python crew.py
```

The system will guide you through the process:
1. Enter the product name you want to analyze
2. Confirm your choice
3. The system automatically selects the best analysis strategy
4. Review the comprehensive business analysis
5. Optionally save results to a file

### Example Analysis Flow
```
🎯 CrewAI Adaptive Business Analyzer
==================================================
💡 Enter the product name to analyze: Smart Plant Watering System

🔍 Starting adaptive analysis...
📋 Attempt 1: Full Analysis
⏱️ Timeout: 10.0 minutes

🔄 Market Research Analyst working...
🔄 Technology Expert assessing...  
🔄 Business Consultant strategizing...

✅ SUCCESS with Full Analysis!
```

## 📊 Output Structure

The analysis provides structured insights across three key areas:

### Market Analysis
- Target customer demographics and behavior
- Market size estimates (global/regional)
- Top 3 direct competitors analysis
- Recommended marketing channels
- Suggested pricing strategy

### Technical Assessment  
- Manufacturing methods and processes
- Required equipment and infrastructure
- Quality control requirements
- Technical challenges and solutions

### Business Strategy
- Optimal business model (B2B/B2C/subscription)
- Primary revenue streams
- Launch timeline with milestones
- Key success metrics (KPIs)
- Risk assessment and mitigation
- Initial funding requirements

## ⚙️ Configuration

### Model Settings
Edit `config.py` to customize:

```python
class Config:
    GEMINI_MODEL = "gemini-2.0-flash"  # AI model
    GEMINI_TEMPERATURE = 0.5           # Creativity level
    MAX_RETRIES = 3                    # Retry attempts
    BASE_RETRY_DELAY = 60              # Delay between retries
```

### Timeout Settings
Adjust timeouts in `crew.py`:

```python
strategies = [
    {"name": "Full Analysis", "timeout": 600},     # 10 minutes
    {"name": "Quick Analysis", "timeout": 300},     # 5 minutes  
    {"name": "Emergency Analysis", "timeout": 120}  # 2 minutes
]
```

## 🔧 Architecture

### File Structure
```
crewai-business-analyzer/
├── agents.py          # AI agent definitions with robust error handling
├── tasks.py           # Task definitions for each analysis phase
├── tools.py           # Web search tool configuration
├── crew.py            # Main orchestration and adaptive execution
├── config.py          # Configuration and API key management
├── requirements.txt   # Python dependencies
├── .env              # Environment variables (create this)
└── README.md         # This file
```

### Key Components

**RobustGeminiLLM Class**
- Enhanced ChatGoogleGenerativeAI with intelligent retry logic
- Exponential backoff for rate limits
- Timeout protection and error classification
- Service availability detection

**AdaptiveCrewHandler Class**  
- Strategy selection and fallback management
- Timeout handling for different analysis depths
- Progressive degradation when services are limited

**Task Creation System**
- Focused task definitions optimized for speed
- Emergency simplified tasks for service issues
- Context-aware task chaining between agents

## 🚨 Troubleshooting

### Common Issues

**"Model overloaded" errors**
- The system automatically waits and retries
- Falls back to simpler analysis if needed
- Try again during off-peak hours

**API quota exhausted**
- Check your Google AI and Serper usage limits
- Wait for quota refresh (usually 24 hours)
- Consider upgrading API plans for higher limits

**Timeout issues**
- System automatically tries shorter analysis
- Check internet connection stability
- Reduce timeout values in config if needed

**Missing API keys**
```bash
❌ Missing required API keys: GOOGLE_API_KEY, SERPER_API_KEY
```
- Verify `.env` file exists and contains both keys
- Check for typos in environment variable names
- Ensure no extra spaces around the `=` sign

### Debug Mode
Enable detailed logging by modifying `agents.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Tips

### Optimal Usage
- Use specific, focused product names (e.g., "wireless bluetooth earbuds" vs "audio device")
- Run during off-peak hours for faster API responses
- Keep product descriptions under 5 words for best results

### API Efficiency
- The system automatically optimizes API calls
- Emergency mode uses no web search to conserve quota
- Results are cached during the session to avoid duplicate calls

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/naakaarafr/Business-Product-Launch-Analyzer.git
cd Business-Product-Launch-Analyzer

# Create development environment  
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Additional dev tools
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent framework
- [Google AI](https://ai.google.dev/) - Gemini language model
- [Serper.dev](https://serper.dev/) - Web search API
- [LangChain](https://github.com/langchain-ai/langchain) - AI application framework

## 📞 Support

### Getting Help
- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact naakaarafr for urgent matters

### Useful Resources
- [CrewAI Documentation](https://docs.crewai.com/)
- [Google AI Studio](https://aistudio.google.com/)
- [Serper API Docs](https://serper.dev/api-docs)

---

**Made with ❤️ by [naakaarafr](https://github.com/naakaarafr)**

*Transform your product ideas into actionable business strategies with AI-powered intelligence.*
