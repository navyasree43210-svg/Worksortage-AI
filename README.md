# WorkShortage – AI-Powered Job Assistance Platform

## 📌 About the Project

**WorkShortage** is an AI-powered job assistance platform designed to help users discover job opportunities and access employment-related information easily. The project combines a user-friendly frontend, a Python backend, and AI-based voice and language support to improve the user experience.

The platform aims to make job-related information more accessible through simple interactions and AI assistance.

## 🎯 Objectives

- Help users access job-related information.
- Provide an easy-to-use interface.
- Integrate AI-powered voice assistance.
- Support language assistance for better accessibility.
- Build a scalable web application using Python technologies.

## ✨ Features

- **User-Friendly Interface:** Simple and accessible web interface.
- **Job Assistance:** Designed to support users in finding relevant job information.
- **AI Voice Assistant:** Uses Gemma-based AI capabilities to assist users through conversational interaction.
- **Language Support:** Aims to make interactions easier for users who prefer different languages.
- **FastAPI Backend:** Provides API endpoints for communication between the frontend and backend.
- **Health Check API:** Includes an endpoint to check whether the backend service is running.
- **API Documentation:** FastAPI provides interactive API documentation for testing endpoints.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Frontend and user interface |
| FastAPI | Backend API development |
| Gemma | AI-powered assistance |
| Uvicorn | Running the FastAPI application |
| Git and GitHub | Version control and source code hosting |

## 🏗️ Project Architecture

```text
WorkShortage/
│
├── frontend/http://127.0.0.1:11434/api/chat      # Streamlit frontend (if organized separately)
├── backend/https://yarn-tingle-stiffness.ngrok-free.dev/           # FastAPI backend (if organized separately)
├── requirements.txt   # Python dependencies
├── .gitignore         # Files excluded from Git
└── README.md          # Project documentation
```

*Note: Update this folder structure to match your actual project files before publishing.*

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/WorkShortage.git
cd WorkShortage
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment.

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

If your project has a `requirements.txt` file, run:

```bash
pip install -r requirements.txt
```

If you do not have one, install the packages required by your actual code, for example:

```bash
pip install streamlit fastapi uvicorn
```

### 4. Run the Backend

Run the command from the folder containing your FastAPI application. Replace `main:app` with your actual Python filename and FastAPI application variable if they are different.

```bash
uvicorn main:app --reload
```

The backend will usually run at:

```text
http://127.0.0.1:8000
```

Check the API health endpoint:

```text
http://127.0.0.1:8000/health
```

Open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

### 5. Run the Streamlit Frontend

Open another terminal and run the command from the folder containing your Streamlit application:

```bash
streamlit run app.py
```

Replace `app.py` with your actual frontend filename if necessary.

## 🔌 API Endpoints

The backend currently provides the following endpoints, based on the available API responses:

| Endpoint | Purpose |
|---|---|
| `/` | Returns basic API information |
| `/health` | Checks backend health |
| `/docs` | Opens interactive API documentation |
| `/jobs` | Provides access to job-related data |

**Note:** The exact request methods, response formats, and functionality of each endpoint should be verified against your FastAPI code.

## 🤖 AI Integration

The project uses **Gemma** for AI-related functionality, including voice assistance and language support.

The AI component is intended to make interactions more natural and accessible. The exact capabilities depend on how the model is integrated into the application.

## 👥 Team Members

This project is developed by a team of five members.

1. **Team Member 1:** Vidya Tanmay
2. **Team Member 2:** Navya Sri
3. **Team Member 3:** Mallika
4. **Team Member 4:** Jyothi
5. **Team Member 5:** Vinusha

## 🚀 Future Enhancements

- Improve job recommendations based on user interests and skills.
- Add user registration and profile management.
- Expand voice-based interaction.
- Improve multilingual support.
- Integrate verified job data sources.
- Add resume analysis and job matching features.
- Deploy the application on a stable hosting platform.

## 🔐 Security

- Never upload passwords, API keys, access tokens, or private credentials.
- Keep secret configuration values in environment variables or a local `.env` file.
- Add `.env` and virtual environment folders to `.gitignore`.
- Do not publish private user information or confidential project data.

## 📄 License

This project is currently intended for educational and demonstration purposes. Add a suitable open-source license if you want others to reuse or modify the code.

## 🙌 Acknowledgements

Thanks to the open-source Python community and the developers of Streamlit, FastAPI, and Gemma for the technologies that support this project.

---

**WorkShortage – Making job assistance more accessible through AI.**
