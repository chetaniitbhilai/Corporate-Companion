# meeting_scheduler.py
import os
import json
import re
import pandas as pd
from datetime import datetime, time as dtime, date 
import pandas as pd
from datetime import datetime, timedelta
import google.generativeai as genai
import shutil

# print(os.path.exists("employee_schedules.csv"))
# raw_schedules = pd.read_csv("employee_schedules.csv")
# print(raw_schedules)
class CompanyNews:
    def __init__(self, genai_api_key=None):
        # Class variables for raw CSVs
        self.raw_teams_csv = None
        self.raw_schedules_csv = None

        # Initialize Gemini API
        self.model = None
        if genai_api_key:
            try:
                genai.configure(api_key=genai_api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                print(f"Error initializing Gemini API: {e}")

    def get_news(self, intent_data):
        # Read the company news content from stuff.txt
        print(intent_data)
        with open("stuff.txt", "r") as f:
            stuff = f.read()

        # Get user-specific data from intent_data (you can adapt this based on how intent_data is structured)
        user_data = intent_data.get("description", {})
        
        # Create the prompt for Gemini, including both the news and user context
        prompt = f"""
        You are a helpful company assistant. Here is the internal news content:

        {stuff}

        Based on the following user data, generate a personalized summary of relevant news for:
        {user_data}
        """
        
        # Use the pre-initialized Gemini model to generate the response
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Error generating content with Gemini: {e}")
                return "Sorry, there was an error generating the response."
        else:
            return "Gemini model is not initialized."
