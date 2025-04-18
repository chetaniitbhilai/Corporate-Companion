# Corporate-Companion 🧑‍💼🤖

Corporate-Companion is a Streamlit-based AI assistant tailored to streamline internal corporate operations. This tool helps employees manage schedules, organize files, view company news, and much more—all through a simple and interactive interface.

## 🔧 Features

* 📅 **Smart Meeting Scheduler**: Finds the earliest common slot for multiple employees, respecting office and lunch hours.
* 👥 **Employee Management**: Create and manage user profiles and store their data and resumes.
* 🗂️ **File Organizer**: Automatically organizes files department-wise (e.g., HR, Finance).
* 📰 **Company News Access**: Fetch and display company updates.
* 📂 **User-Friendly UI**: Powered by Streamlit for an intuitive interface.
* 🎬 **Demo Available**: Demo video

## 📁 Repository Structure

| File / Folder | Description |
|--------------|-------------|
| `main.py` | Main entry point of the Streamlit app; handles intent processing |
| `demo.mp4` | Demo video showcasing application features |
| `employee_teams.csv` | Contains employee names and their respective departments |
| `employee_schedules.csv` | Contains employee schedules (availability, meetings, etc.) |
| `user_data/` | Stores user JSON data and resumes |
| `files/` | Contains various files from HR and Finance departments |
| `company_news.py` | Displays company-related information |
| `file_organiser.py` | Organizes files based on department |
| `meeting_schedular.py` | Handles smart meeting scheduling logic |
| `stuff.txt` | Miscellaneous company information |
| `user_management.py` | Handles user creation and management logic |
|  `journal.txt`   |  Problems faced, how it was solved |

## 🚀 Getting Started

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/Corporate-Companion.git
cd Corporate-Companion
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the app**:
```bash
streamlit run main.py
```

## Set env file 
In env file set Gemini api key
```bash
GEMINI_API_KEY = YOUR_KEY
```

## 📹 Demo Preview
Watch the application in action in `demo.mp4`.

## 📌 Notes
* Make sure to maintain correct formatting of the CSVs in `employee_teams.csv` and `employee_schedules.csv`.
* Store resumes as JSON in the `user_data/` folder for the assistant to read user information effectively.

## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss your ideas.
