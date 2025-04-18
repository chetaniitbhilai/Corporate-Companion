import streamlit as st
import os
import json
import re
import logging
from dotenv import load_dotenv
from user_management import UserManager
from meeting_schedular import MeetingScheduler
from file_organiser import FileOrganisation
from company_news import CompanyNews

load_dotenv()

class CorporateCompanion:
    def __init__(self):
        
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        self.user_manager = UserManager()
        self.scheduler = MeetingScheduler(genai_api_key=self.gemini_api_key)
        self.organiser = FileOrganisation(genai_api_key=self.gemini_api_key)
        self.company_news = CompanyNews(genai_api_key=self.gemini_api_key)
        
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            print(f"Error initializing Gemini API: {e}")
            self.model = None
    
    def find_user_by_email(self, email):
        return self.user_manager.find_user_by_email(email)
    
    def register_user(self, name, email, phone, department, employee_id, 
                     office_location, password, resume_file):
        return self.user_manager.register_user(
            name, email, phone, department, employee_id, 
            office_location, password, resume_file
        )
    
    def login_user(self, email, password):
        return self.user_manager.login_user(email, password)
    
    def get_all_employees(self):
        return self.scheduler.get_all_employees()
    
    def get_all_teams(self):
        return self.scheduler.get_all_teams()
    
    def get_team_members(self, team_name):
        return self.scheduler.get_team_members(team_name)
    
    def get_my_schedule(self, user_name, start_date=None, end_date=None):
        return self.scheduler.get_my_schedule(user_name, start_date, end_date)
    
    def process_intent(self, query, user_data):
        """Use Gemini to determine user intent and route to appropriate handler"""
        if not self.model:
            return "I'm having trouble understanding your request. My language processing system is currently unavailable."
        
        system_prompt = """
You are an intent classifier for a corporate assistant app. Analyze the user query and classify it into one of these categories:

1. MEETING_SCHEDULER: For scheduling, viewing, or managing meetings
2. USER_INFO: For inquiries about the user's profile information
3. FILE_ORGANISATION: For classifying the files given to you
4. COMPANY_NEWS: Any other things related to company like upcoming holidays, HR policies, upcoming events, team and project summaries.
5. GENERAL_QUERY: For general questions, small talk, or other requests

Return a JSON object with the following structure:
{
  "intent": "MEETING_SCHEDULER/USER_INFO/GENERAL_QUERY/FILE_ORGANISATION",
  "description": "Brief description of what the user wants to do",
  "parameters": {
    // For USER_INFO, always include the 'field' parameter with the specific field requested
    // Examples:
    // - "What's my phone number?" -> "field": "phone"
    // - "Tell me my email" -> "field": "email"
    // - "What department am I in?" -> "field": "department"
    // Common fields: name, email, phone, department, employee_id, office_location
  }
}

Be very specific when extracting the 'field' parameter for USER_INFO intent. Look for specific fields the user is asking about.

Return only the JSON object, no additional text.
"""     
        try:
            
            context = f"""
            User name: {user_data['name']}
            Department: {user_data['department']}
            Available employees: {', '.join(self.get_all_employees())}
            Available teams: {', '.join(self.get_all_teams())}
            """
            
            chat = self.model.start_chat(history=[])
            response = chat.send_message(f"{system_prompt}\n\nContext:\n{context}\n\nUser query: {query}")
            
            
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                intent_data = json.loads(json_match.group(0))
                
                
                intent = intent_data.get("intent", "GENERAL_QUERY")
                print(intent)
                if intent == "MEETING_SCHEDULER":
                    st.write(intent)
                    return self.scheduler.process_schedule_command(query, user_data)
                elif intent == "USER_INFO":
                    return self.handle_user_info_query(intent_data, user_data)
                elif intent == "FILE_ORGANISATION":
                    return self.organiser.organise_files(intent_data, user_data)
                elif intent == "COMPANY_NEWS":
                    return self.company_news.get_news(intent_data)
                else:
                    return self.handle_general_query(query, user_data)
            else:
                return "I couldn't understand your request properly. Could you please rephrase?"
                
        except Exception as e:
            return f"I'm having trouble processing your request. Error: {str(e)}"
    

    def handle_user_info_query(self, intent_data, user_data):
        """Handle queries about user information"""
        print("Intent data received:", intent_data)  
        
        
        description = intent_data.get("description", "").lower()
        
        
        parameters = intent_data.get("parameters", {})
        requested_field = parameters.get("field", "").lower()
        
        
        if not requested_field and description:
            
            if "phone" in description:
                requested_field = "phone"
            elif "email" in description:
                requested_field = "email"
            elif "name" in description:
                requested_field = "name"
            elif "department" in description:
                requested_field = "department"
            elif "employee id" in description or "id" in description:
                requested_field = "employee_id"
            elif "office" in description or "location" in description:
                requested_field = "office_location"
        
        print(f"Requested field identified: {requested_field}")  
        
        
        field_mapping = {
            "name": "name",
            "email": "email",
            "mail": "email",
            "phone": "phone",
            "mobile": "phone",
            "number": "phone",
            "department": "department",
            "dept": "department",
            "employee id": "employee_id",
            "employeeid": "employee_id",
            "id": "employee_id",
            "office": "office_location",
            "location": "office_location",
            "office location": "office_location"
        }
        
        
        actual_field = None
        if requested_field:
            actual_field = field_mapping.get(requested_field.replace(" ", "").lower())
        
        print(f"Actual field mapped: {actual_field}")  
        
        
        if actual_field and actual_field in user_data:
            field_name = actual_field.replace("_", " ").title()
            return f"Your {field_name}: {user_data[actual_field]}"
        else:
            
            info_text = "📄 *Here's the information you requested:*\n\n"
            info_text += f"👤 **Name**: {user_data.get('name', 'Not provided')}\n\n"
            info_text += f"📧 **Email**: {user_data.get('email', 'Not provided')}\n\n"
            info_text += f"📞 **Phone**: {user_data.get('phone', 'Not provided')}\n\n"
            info_text += f"🏢 **Department**: {user_data.get('department', 'Not provided')}\n\n"
            info_text += f"🆔 **Employee ID**: {user_data.get('employee_id', 'Not provided')}\n\n"
            info_text += f"📍 **Office Location**: {user_data.get('office_location', 'Not provided')}\n\n"

            
            return info_text

    
    def handle_general_query(self, query, user_data):
        """Handle general queries and small talk"""
        if not self.model:
            return "I can help you with scheduling meetings and accessing your information. What would you like to do?"
        
        system_prompt = f"""
        You are Corporate Companion, an assistant for {user_data['name']} who works at the company.
        
        Here is the user's profile information:
        - Name: {user_data['name']} 
        - Email: {user_data['email']}
        - Phone: {user_data['phone']}
        - Department: {user_data['department']}
        - Employee ID: {user_data['employee_id']}
        - Office Location: {user_data['office_location']}
        - Registration Date: {user_data['registration_date']}
        
        Your task is to answer questions in a helpful, professional manner.
        Keep responses concise and professional.
        
        """
        
        try:
            
            chat = self.model.start_chat(history=[])
            response = chat.send_message(f"{system_prompt}\n\nUser query: {query}")
            return response.text
        except Exception as e:
            return f"I'm having trouble processing your request. Error: {str(e)}"
    
    def get_nlp_response(self, query, user_data):
        """Main entry point for processing user queries"""
        return self.process_intent(query, user_data)


st.set_page_config(
    page_title="Corporate Companion",
    page_icon="💼",
    layout="centered"
)


@st.cache_resource
def get_companion():
    return CorporateCompanion()

companion = get_companion()


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


st.title("💼 Corporate Companion")
st.subheader("An LLM-based Chatbot for Employee Assistance")


if not st.session_state.logged_in:
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login")
            
            if submit_login:
                if email and password:
                    success, result = companion.login_user(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_data = result
                        st.success(f"Welcome back, {result['name']}!")
                        st.rerun()
                    else:
                        st.error(result)
                else:
                    st.warning("Please enter both email and password.")
    
    with tab2:
        st.header("New User Registration")
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            department = st.selectbox("Department", ["HR", "Engineering", "Marketing", "Sales", "Finance", "Operations", "IT", "Other"])
            employee_id = st.text_input("Employee ID")
            office_location = st.text_input("Office Location")
            password = st.text_input("Create Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
            submit_register = st.form_submit_button("Register")
            
            if submit_register:
                if not all([name, email, phone, department, employee_id, office_location, password, confirm_password]):
                    st.warning("Please fill in all required fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, result = companion.register_user(
                        name, email, phone, department, employee_id, 
                        office_location, password, resume_file
                    )
                    if success:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(result)
else:
    
    user_data = st.session_state.user_data
    
    
    with st.sidebar:
        st.subheader(f"Welcome, {user_data['name']}")
        st.write(f"**Department:** {user_data['department']}")
        st.write(f"**Office:** {user_data['office_location']}")
        
        st.subheader("Your Schedule")
        schedule = companion.get_my_schedule(user_data['name'])
        if schedule:
            current_date = None
            for meeting in schedule:
                if current_date != meeting["date"]:
                    st.write(f"**{meeting['day']}**")
                    current_date = meeting["date"]
                st.write(f"• {meeting['time']}: {meeting['description']}")
        else:
            st.write("No upcoming meetings")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.session_state.chat_history = []
            st.rerun()
    

    st.header("Chat with your Corporate Companion")
    
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    
    user_query = st.chat_input("Ask me anything or type a command...")
    if user_query:
        
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)
        
        
        assistant_response = companion.get_nlp_response(user_query, user_data)
        
        
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        st.chat_message("assistant").write(assistant_response)

if not st.session_state.logged_in:
    st.markdown("""
    ## Features
    - **Personal Assistant**: Get information about your profile and schedule
    - **Meeting Scheduler**: Schedule meetings with colleagues and teams
    - **Natural Language**: Use normal language to ask questions and schedule meetings
    
    ### Example Commands
    - "Schedule a meeting with the Marketing on 24th"
    - "Tell me the upcoming holidays"
    - "What's my employee ID?"
    """)

if __name__ == "__main__":
    
    pass