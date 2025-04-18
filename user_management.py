
import os
import json
import uuid
from datetime import datetime
import pandas as pd

class UserManager:
    def __init__(self):
        self.user_data_dir = "user_data"
        
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
    
    def find_user_by_email(self, email):
        
        for user_folder in os.listdir(self.user_data_dir):
            user_path = os.path.join(self.user_data_dir, user_folder, "info.json")
            if os.path.exists(user_path):
                with open(user_path, 'r') as f:
                    user_data = json.load(f)
                    if user_data.get("email") == email:
                        return user_folder
        return None
    
    def save_user_data(self, user_id, data):
        
        user_folder = os.path.join(self.user_data_dir, user_id)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        
        # Save user info as JSON
        with open(os.path.join(user_folder, "info.json"), 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_user_data(self, user_id):
        
        user_path = os.path.join(self.user_data_dir, user_id, "info.json")
        if os.path.exists(user_path):
            with open(user_path, 'r') as f:
                return json.load(f)
        return None
    
    def save_resume(self, user_id, resume_file):
        
        if resume_file is not None:
            user_folder = os.path.join(self.user_data_dir, user_id)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            
            
            with open(os.path.join(user_folder, "resume.pdf"), 'wb') as f:
                f.write(resume_file.getbuffer())
            return True
        return False

    def register_user(self, name, email, phone, department, employee_id, 
                     office_location, password, resume_file):
        
        
        if self.find_user_by_email(email):
            return False, "An account with this email already exists."
        
        
        user_id = str(uuid.uuid4())
        
        
        user_data = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "phone": phone,
            "department": department,
            "employee_id": employee_id,
            "office_location": office_location,
            "password": password,
            "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        
        self.save_user_data(user_id, user_data)
        
        
        if resume_file:
            self.save_resume(user_id, resume_file)
            
        return True, user_id

    def login_user(self, email, password):
        
        user_id = self.find_user_by_email(email)
        if not user_id:
            return False, "Email not found. Please register."
        
        user_data = self.load_user_data(user_id)
        if user_data and user_data.get("password") == password:
            return True, user_data
        else:
            return False, "Invalid password."