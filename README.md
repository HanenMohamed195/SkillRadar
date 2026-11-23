# SkillRadar 🎯
### Smart Job Discovery & Skill-Based Matching Platform

SkillRadar is a data-driven platform designed to help job seekers discover relevant job opportunities and identify the skills required by the job market.

The project aims to collect job listings from multiple sources, process and organize job data, extract required skills, and match job opportunities with users based on their skills and CVs.

---

## 🎯 Project Objectives

- Collect job opportunities from multiple sources.
- Build a scalable data engineering pipeline.
- Clean and transform job market data.
- Extract and analyze in-demand skills.
- Match users with relevant job opportunities.
- Provide insights into job market trends.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development and data processing |
| FastAPI | Backend API |
| Supabase | Cloud PostgreSQL database |
| SQL | Database design and queries |
| Databricks | Planned data engineering and ETL |
| React | Planned frontend development |
| Power BI | Planned data visualization |
| Telegram Bot | Planned job notifications |

## 🏗️ Project Architecture

The planned architecture follows this workflow:

1. **Data Collection:** Collect job listings from external job sources and APIs.
2. **Data Processing:** Clean, transform, and validate collected data.
3. **Data Storage:** Store structured job and skill information in Supabase.
4. **Skill Extraction:** Identify technical skills from job descriptions and user CVs.
5. **Job Matching:** Compare user skills with job requirements.
6. **Visualization:** Analyze job market trends through Power BI.
7. **Notifications:** Notify users about relevant job opportunities.

### Data Engineering Architecture

The planned ETL pipeline will follow the Medallion Architecture:

- **Bronze Layer:** Raw job data.
- **Silver Layer:** Cleaned and standardized data.
- **Gold Layer:** Analytics-ready and structured data.

## 🗄️ Database Design

The current Supabase database includes six main tables:

| Table | Description |
|---|---|
| `jobs` | Stores job listings |
| `skills` | Stores available skills |
| `job_skills` | Connects jobs with required skills |
| `profiles` | Stores user profile information |
| `user_skills` | Stores users' skills and proficiency |
| `saved_jobs` | Stores users' saved jobs |

Row Level Security (RLS) policies are configured to control database access.

## 📁 Project Structure

```text
SkillRadar/
│
├── Backend/
│   ├── main.py
│   ├── supabase_client.py
│   └── .env.example
│
├── Database/
│   ├── 01_schema.sql
│   ├── 02_rls_policies.sql
│   └── 03_permissions.sql
│
├── App/
├── Docs/
├── ETL/
├── PowerBI/
├── Scraping/
├── TelegramBot/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Current Implementation Status

### Completed
- Initial project structure.
- FastAPI backend setup.
- Home and health-check API endpoints.
- Supabase cloud database connection.
- Initial database schema with six tables.
- Initial Row Level Security policies.
- SQL scripts organized and saved locally.
- Job retrieval endpoint connected to Supabase.

### In Progress / Planned
- Job scraping and API integrations.
- Automated job data collection.
- Databricks ETL pipeline.
- Bronze, Silver, and Gold data layers.
- Automated data loading into Supabase.
- CV parsing and skill extraction.
- Skill-based job matching.
- User authentication and profile management.
- React frontend.
- Telegram notifications.
- Power BI dashboard.
- Cloud deployment and scheduled workflows.

## ⚙️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/HanenMohamed195/SkillRadar.git
cd SkillRadar
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a file named `.env` inside the `Backend` folder:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_publishable_key
```

Never commit `.env` files or private credentials to GitHub.

### 5. Run the Backend

From the project root:

```bash
python -m uvicorn main:app --reload --app-dir Backend
```

### 6. Access the API

- API Home: `http://127.0.0.1:8000/`
- Health Check: `http://127.0.0.1:8000/api/health`
- Jobs Endpoint: `http://127.0.0.1:8000/api/jobs`
- API Documentation: `http://127.0.0.1:8000/docs`

## 🔮 Future Improvements

- Integrate multiple job data sources.
- Automate data collection and transformation.
- Improve skill extraction and matching accuracy.
- Build an interactive user dashboard.
- Deploy the platform to cloud infrastructure.

---

## 👩‍💻 Project

**SkillRadar** is being developed as a Data Engineering project as part of the DEPI scholarship.

**GitHub Repository:**  
https://github.com/HanenMohamed195/SkillRadar

*This project is currently under active development.*
