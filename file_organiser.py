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
class FileOrganisation:
    def __init__(self, genai_api_key=None):
        # Class variables for raw CSVs
        self.raw_teams_csv = None
        self.raw_schedules_csv = None

        # Initialize Gemini API
        self.model = None
        if genai_api_key:
            try:
                genai.configure(api_key="AIzaSyDF1XCJo8Ko6RP6TNgxDGJSDYuydAqw9Ow")
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                print(f"Error initializing Gemini API: {e}")

    def organise_files(self, intent_data, user_data):
        print(intent_data, user_data)

        # Step 1: List all files in the 'files' directory
        directory = "files"
        file_list = os.listdir(directory)
        file_list = [f for f in file_list if os.path.isfile(os.path.join(directory, f))]

        # Save file names to a file (optional, for record)
        with open("file_list.txt", "w") as f:
            for file in file_list:
                f.write(file + "\n")

        # Step 2: Ask Gemini to classify each file
        if not self.model:
            print("Gemini model not initialized.")
            return

        prompt = "Classify the following file names into departments like 'finance' or 'hr':\n\n"
        prompt += "\n".join(file_list)
        prompt += "\n\nReturn the classification as a JSON dictionary like: {\"finance\": [..], \"hr\": [..]}"

        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            print(result)
            # Use regex to extract JSON from response
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if not json_match:
                print("No valid JSON found in Gemini response.")
                return
            file_mapping = json.loads(json_match.group())
            print(file_mapping)

        except Exception as e:
            print(f"Error during Gemini classification: {e}")
            return

        summary = "📂 **File Classification Summary**\n\n"

        for dept, files in file_mapping.items():
            dept_dir = os.path.join(directory, dept.lower())
            os.makedirs(dept_dir, exist_ok=True)
            emoji = "💰" if dept.lower() == "finance" else "👥"
            summary += f"{emoji} **{dept.capitalize()} Department:**\n \n"
            for file in files:
                src = os.path.join(directory, file)
                dst = os.path.join(dept_dir, file)
                if os.path.exists(src):
                    shutil.copy(src, dst)
                    summary += f"  ➤ Moved `{file}` to `{dept}`\n \n"
            summary += "\n"

        if os.path.exists("file_list.txt"):
            os.remove("file_list.txt")

        return summary


    