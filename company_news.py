
import os
import json
import re
import pandas as pd
from datetime import datetime, time as dtime, date 
import pandas as pd
from datetime import datetime, timedelta
import google.generativeai as genai
import shutil

class CompanyNews:
    def __init__(self, genai_api_key=None):
        
        self.raw_teams_csv = None
        self.raw_schedules_csv = None

        
        self.model = None
        if genai_api_key:
            try:
                genai.configure(api_key=genai_api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                print(f"Error initializing Gemini API: {e}")

    def get_news(self, intent_data):
        
        print(intent_data)
        with open("stuff.txt", "r") as f:
            stuff = f.read()

        
        user_data = intent_data.get("description", {})
        
        
        prompt = f"""
        You are a helpful company assistant. Here is the internal news content:

        {stuff}

        Based on the following user data, generate a personalized summary of relevant news for:
        {user_data}
        """
        
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Error generating content with Gemini: {e}")
                return "Sorry, there was an error generating the response."
        else:
            return "Gemini model is not initialized."
