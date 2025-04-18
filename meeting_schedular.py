# meeting_scheduler.py
import os
import json
import re
import pandas as pd
from datetime import datetime, time as dtime, date 
import pandas as pd
from datetime import datetime, timedelta
import google.generativeai as genai

class MeetingScheduler:
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
        
        # Load employee teams data
        try:
            if os.path.exists("employee_teams.csv"):
                self.raw_teams_csv = pd.read_csv("employee_teams.csv")
                print("Loaded employee_teams.csv:")
                print(self.raw_teams_csv)
                self.employee_teams = self.raw_teams_csv
            else:
                print("No employee_teams.csv file found. Starting with empty teams data.")
                self.employee_teams = pd.DataFrame(columns=["Employee", "Team"])
        except Exception as e:
            print(f"Error loading employee teams data: {e}")
            self.employee_teams = pd.DataFrame(columns=["Employee", "Team"])

        # Load employee schedules data
        try:
            if os.path.exists("employee_schedules.csv"):
                self.raw_schedules_csv = pd.read_csv("employee_schedules.csv")
                print("Loaded employee_schedules.csv:")
                print(self.raw_schedules_csv)

                raw_schedules = self.raw_schedules_csv
                processed_schedules = []
                date_columns = raw_schedules.columns[1:]

                for _, row in raw_schedules.iterrows():
                    emp = row['Employee']
                    for d in date_columns:
                        if pd.notna(row[d]) and row[d]:
                            times = str(row[d]).strip('"').split(',')
                            for t in times:
                                t = t.strip().strip('"')
                                if t:
                                    processed_schedules.append({
                                        'Employee': emp,
                                        'date': d,
                                        'time': t,
                                        'description': "Busy/Unavailable"
                                    })

                self.employee_schedules = pd.DataFrame(processed_schedules)
                self.employee_schedules["date"] = pd.to_datetime(self.employee_schedules["date"], format="%Y-%m-%d", errors='coerce')

                def convert_time(x):
                    try:
                        return datetime.strptime(x.strip(), "%H:%M").time()
                    except:
                        print(f"Invalid time: {x}")
                        return None

                self.employee_schedules["time"] = self.employee_schedules["time"].apply(convert_time)
                self.employee_schedules = self.employee_schedules.dropna(subset=["date", "time"])

            else:
                print("No employee_schedules.csv file found. Starting with empty schedule.")
                self.employee_schedules = pd.DataFrame(columns=["Employee", "date", "time", "description"])
        except Exception as e:
            print(f"Error loading employee schedules data: {e}")
            self.employee_schedules = pd.DataFrame(columns=["Employee", "date", "time", "description"])

    def process_schedule_command(self, query, user_data):
        print(query,user_data)

        if not self.model:
            return "I'm having trouble understanding your request. My language processing system is currently unavailable."
        
        print(self.model)

        system_prompt = """I am going to give you a query to schedule a meeting with the current user with his/her department and all the available people's list.
        You need to return the output as a json format with the people in the list and date on which the person wants to schedule a meet and a list of people if he wants to schedule a meet with the department itself.
        if the query is like Schedule a meet with Alice 
        then search for alice in the list and return like
        {
        'department': 'Department in the query'  
        'employees': {['Alice']}
        'date' : '2025-04-03'  // if no date specified use today's date.
        }
        In both case of a single person or multiple or team return in this order only.
        let the department string be empty if no department in the query.
        In employees always add the person who is querying.
        """ 
        try:
            # Get context info that might help Gemini make better decisions
            context = f"""
            User name: {user_data['name']}
            Department: {user_data['department']}
            Query: {query}
            Available employees: {self.get_all_employees_with_team()}
            Today's date is: {date.today()}
            """
            print(context)
            
            chat = self.model.start_chat(history=[])
            response = chat.send_message(f"{system_prompt}\n\n More information :\n{context}\n")
            
            print(response)
            # Extract JSON from response
            response_text = response.candidates[0].content.parts[0].text

# Extract the last JSON block from the response (you can enhance this to extract multiple if needed)
            json_blocks = re.findall(r'\{[\s\S]*?\}', response_text)
            print(json_blocks)

            d = json.loads(json_blocks[0])
            print(d['employees'])
            output = self.schedule_and_update(json_blocks, query, user_data,d['date'], d['employees'])
            # print(output)

            return self.update_employee_csv(d['employees'],d['date'],output)

                
        except Exception as e:
            return f"I'm having trouble processing your request. Error: {str(e)}"
    

    def update_employee_csv(self, li, di, ti):
        print(li, di, ti)
        if ti == "00:00":
            return f"""One of the mentioned persons is busy on the {di} 😅. Try some other day 📅."""


        # Read the CSV file
        df = pd.read_csv("employee_schedules.csv")
        
        # Check if the date column exists, if not, add it
        if di not in df.columns:
            df[di] = ""  # Add the date column if not present

        # Iterate through the list of employees
        for name in li:
            # Check if the employee exists in the DataFrame
            if name in df["Employee"].values:
                # Update the schedule for the existing employee
                for i in range(len(df)):
                    if df.at[i, "Employee"] == name:
                        current_times = str(df.at[i, di])
                        times = [x.strip() for x in current_times.split(",") if x.strip()] if current_times else []
                        if ti not in times:
                            times.append(ti)
                            times.sort()
                            df.at[i, di] = ", ".join(times)
            else:
                # If the employee is not found, create a new row
                new_row = pd.DataFrame({"Employee": [name], di: [ti]})
                df = pd.concat([df, new_row], ignore_index=True)

        # Write the updated DataFrame back to the CSV file
        df.to_csv("employee_schedules.csv", index=False)

        return f"📅✅ Meet scheduled with the requested people at 🕒 {ti} hours"






    def schedule_and_update(self, json_blocks, query, user_data,d, employees):
        print(query,user_data)
        df = pd.read_csv("employee_schedules.csv")

        if d not in df.columns:
            return f"No schedule found for the date {d}."

        # Create a new DataFrame with only 'Employee' and the schedule for date d
        filtered_df = df[["Employee", d]].copy()
        filtered_df.rename(columns={d: "Schedule"}, inplace=True)
        print(filtered_df)
        # Convert to CSV-like string without index
        print(type(filtered_df))
        emps = employees
        print(emps)

        schedules = (
            filtered_df[filtered_df['Employee'].isin(emps)]['Schedule']
            .to_list()
        )
        print(type(schedules))
        # s = [t.strip() for val in schedules for t in val.split(',')]
        s=schedules
        s = [x for x in s if pd.notna(x)]
        bs = [t.strip() for val in s for t in val.split(',')]

        print(bs)
        print(type(s[0]))
        

        slots = ['09:00', '10:00', '11:00', '12:00', '15:00', '16:00', '17:00']  # exclude lunch hours (13:00, 14:00)
        print(type(slots[0]))
        for st in bs:
            if st in slots:
                slots.remove(st)
        print(slots)
        if(len(slots)==0):
            return '00:00'
        else:   
            return slots[0]
        


    def get_all_employees_with_team(self):
        """Get a list of all employees along with their teams"""
        if self.employee_teams.empty:
            return []
        
        pairs = self.employee_teams[['Employee', 'Team']].dropna().drop_duplicates()
        return sorted([tuple(x) for x in pairs.values])



    def get_all_employees(self):
        """Get a list of all employees from the teams data or schedules data"""
        employees = set()
        
        # Get employees from teams data
        if not self.employee_teams.empty:
            employees.update(self.employee_teams['Employee'].unique().tolist())  # Fixed column name
        
        # Get employees from schedules data
        if not self.employee_schedules.empty:
            employees.update(self.employee_schedules['Employee'].unique().tolist())
        
        return sorted(list(employees))
    
    def get_all_teams(self):
        """Get a list of all teams from the teams data"""
        if self.employee_teams.empty:
            return []
        return sorted(self.employee_teams['Team'].unique().tolist())  # Fixed column name

    def get_my_schedule(self, user_name, start_date=None, end_date=None):
        """Get a user's schedule within a date range"""
        if start_date is None:
            start_date = datetime.now().date()
        if end_date is None:
            end_date = start_date + timedelta(days=7)
            
        if not self.employee_schedules.empty:
            user_schedule = self.employee_schedules[
                (self.employee_schedules['Employee'] == user_name) & 
                (pd.to_datetime(self.employee_schedules['date']).dt.date >= start_date) &
                (pd.to_datetime(self.employee_schedules['date']).dt.date <= end_date)
            ]
            
            if not user_schedule.empty:
                # Format for better display
                formatted_schedule = []
                for _, meeting in user_schedule.sort_values(['date', 'time']).iterrows():
                    formatted_schedule.append({
                        'date': meeting['date'].strftime('%Y-%m-%d'),
                        'day': meeting['date'].strftime('%A'),
                        'time': meeting['time'].strftime('%I:%M %p'),
                        'description': meeting['description']
                    })
                return formatted_schedule
        
        return []

