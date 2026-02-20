# 🤖 AI Interview Buddy

> **Elevate your career with a premium, AI-powered mock interview experience.**

AI Interview Buddy is a cutting-edge, cinematic platform designed to simulate professional, real-world interviews. By integrating advanced Generative AI and multi-agent systems, it provides job seekers with a realistic environment to practice technical and behavioral interviews, tailored specifically to their own resumes.

---

## 🌟 Key Features

### 1. **Professional Indian Interviewer Persona**
- Simulates a real-life industry expert interviewer.
- **Adaptive Difficulty**: Questions evolve based on your answers and depth of knowledge.
- **Critical Probing**: If you use buzzwords without explaining the "how" or "why", the AI will challenge you politely.
- **Two-Round Structure**:
    - **Round 1 (Technical)**: Deep-dive into Projects, Resume, and CS Fundamentals/DSA.
    - **Round 2 (HR/Behavioral)**: Culture fit, situational awareness, and communication assessment.

### 2. **Resume-Centric Simulation**
- Upload your PDF resume.
- The AI agents analyze your specific tech stack, project history, and experience level to generate relevant, high-fidelity questions.

### 3. **Immersive Audio Experience**
- **Real-time Voice Interactivity**: Integrated Speech-to-Text (STT) and Text-to-Speech (TTS).
- Cinematic visualizer feedback and high-definition message bubble transitions.

### 4. **Detailed Feedback Reports**
- Get a comprehensive analysis of your performance.
- Actionable tips on technical depth, communication clarity, and confidence.
- Final verdict: **Ready**, **Almost Ready**, or **Needs More Practice**.

---

## 🛠️ Tech Stack

- **Frontend**: 
  - [React](https://reactjs.org/) + [Vite](https://vitejs.dev/) (High-speed HMR)
  - [Tailwind CSS](https://tailwindcss.com/) (Modern styling)
  - [Framer Motion](https://www.framer.com/motion/) (Cinematic animations)
  - [Lucide React](https://lucide.dev/) (Clean iconography)

- **Backend**:
  - [FastAPI](https://fastapi.tiangolo.com/) (High-performance Python framework)
  - [SQLAlchemy](https://www.sqlalchemy.org/) (Database ORM)
  - [SQLite](https://sqlite.org/) (Lightweight, reliable local database)

- **AI Engine**:
  - [GPT-4o](https://openai.com/gpt-4) via **GitHub Models API**
  - Custom Multi-Agent Orchestration logic.

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: v18 or higher
- **Python**: v3.9 or higher
- **GitHub Models API Token**: Get your token from [GitHub Settings](https://github.com/settings/tokens).

### 📥 1. Installation

Clone the repository:
```bash
git clone https://github.com/naveen18112003/AI-Interview-Buddy.git
cd AI-Interview-Buddy
```

### ⚙️ 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure Environment Variables:
   Create a `.env` file in the `backend/` folder:
   ```env
   GITHUB_MODELS_API_KEY=your_github_token_here
   MODEL_NAME=gpt-4o
   DATABASE_URL=sqlite:///./data/ai_interview_buddy.db
   ```

### 💻 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

---

## 🎮 How to Run on VS Code

The easiest way to run the project is to open two terminals in VS Code:

### Terminal 1: Backend
1. Start from the project root:
   ```bash
   cd backend
   # Activate venv
   .\venv\Scripts\activate
   # Run server
   uvicorn app.main:app --reload
   ```
   *The API will be available at `http://localhost:8000`*

### Terminal 2: Frontend
1. Start from the project root:
   ```bash
   cd frontend
   # Run dev server
   npm run dev
   ```
   *The app will be available at `http://localhost:5173`*

---

## 🛠️ Environment Variables

Ensure you have a `.env` file in the `backend` directory with the following:

```env
GITHUB_MODELS_API_KEY=your_github_token_here
MODEL_NAME=gpt-4o
DATABASE_URL=sqlite:///./data/ai_interview_buddy.db
```
*Note: The `data` folder in backend will be created automatically.*

---

## 🐳 Running with Docker
If you prefer Docker, you can launch the entire stack with one command:
```bash
docker-compose up --build
```

---

## 📂 Project Structure

```text
AI Interview Buddy/
├── backend/            # FastAPI Backend
│   ├── app/           # Application Logic
│   │   ├── agents/    # AI Agent definitions
│   │   ├── prompts/   # System prompts & personas
│   │   ├── routes/    # API Endpoints
│   │   └── services/  # Business logic
│   └── data/          # SQLite database storage
├── frontend/           # React + Vite Frontend
│   ├── src/           # Components, Hooks, Pages
│   └── public/        # Static assets
└── docker-compose.yml  # Container orchestration
```

---

## 🛡️ License
This project is licensed under the MIT License - see the LICENSE file for details.

---

*Made with ❤️ by [Naveen](https://github.com/naveen18112003)*
