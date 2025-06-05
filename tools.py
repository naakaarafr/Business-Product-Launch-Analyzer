from dotenv import load_dotenv
load_dotenv()
import os
from crewai_tools import SerperDevTool

# Set the API key
os.environ['SERPER_API_KEY'] = os.getenv('SERPER_API_KEY')

# Initialize the tool for internet searching capabilities
search_tool = SerperDevTool()