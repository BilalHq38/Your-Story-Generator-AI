# 📖 Story Teller - AI-Powered Interactive Adventures

An immersive, AI-powered interactive fiction platform where every choice shapes your unique narrative. Built with FastAPI, React, and Google Gemini AI.

![Story Teller](https://img.shields.io/badge/Story%20Teller-AI%20Interactive%20Fiction-8b5cf6)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![React](https://img.shields.io/badge/React-18-61dafb)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178c6)

## ✨ What Makes Us Unique

### 🎭 Multiple Narrator Personas
Choose from 5 distinct AI narrators, each with their own storytelling style:

- **The Enigma** (Mysterious) - Speaks in riddles and shadows
- **The Chronicler** (Epic) - Grand tales of heroes and legends
- **The Whisperer** (Horror) - Unsettling tales that creep under your skin
- **The Jester** (Comedic) - Witty observations and unexpected humor
- **The Poet** (Romantic) - Passionate prose that stirs the heart

### 🌌 Story Atmospheres
Set the mood for your adventure:
- Dark & Foreboding
- Mystical & Enchanting
- Calm & Serene
- Suspenseful
- Light & Playful

### 🌳 Branching Story Trees
Visualize your journey with our story tree viewer. See all the paths you could have taken and explore alternate endings.

### ⚡ Real-Time Generation
Watch as the AI crafts your story in real-time with beautiful typewriter animations.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API Key

### Backend Setup

```bash
cd Backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies with uv (recommended)
pip install uv
uv pip install -e .

# Or with pip
pip install -e .

# Install Gemini integration
uv add langchain-google-genai

# Create .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000  
API docs: http://localhost:8000/docs

### Frontend Setup

```bash
cd Frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: http://localhost:3000

## 🔑 Getting Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to `Backend/.env`:

```env
GEMINI_API_KEY=your_api_key_here
```

## 📁 Project Structure

```
Story Teller/
├── Backend/                 # FastAPI backend
│   ├── core/               # Core business logic
│   │   ├── config.py       # Settings management
│   │   ├── story_generator.py  # AI generation
│   │   └── prompts.py      # Prompt templates
│   ├── db/                 # Database layer
│   │   └── database.py     # SQLAlchemy setup
│   ├── models/             # SQLAlchemy models
│   │   ├── story.py        # Story & StoryNode
│   │   └── job.py          # Async job tracking
│   ├── routers/            # API endpoints
│   │   ├── story.py        # Story CRUD + generation
│   │   └── jobs.py         # Job status tracking
│   ├── schema/             # Pydantic schemas
│   ├── alembic/            # Database migrations
│   └── main.py             # FastAPI app
│
└── Frontend/               # React frontend
    ├── src/
    │   ├── api/            # API client
    │   ├── components/     # React components
    │   │   ├── layout/     # Layout components
    │   │   ├── story/      # Story-specific components
    │   │   └── ui/         # Reusable UI components
    │   ├── pages/          # Page components
    │   ├── stores/         # Zustand state management
    │   ├── styles/         # Global styles
    │   └── types/          # TypeScript types
    └── public/             # Static assets
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy 2.0** - Database ORM with async support
- **Pydantic v2** - Data validation
- **LangChain** - AI orchestration
- **Google Gemini** - AI model
- **Alembic** - Database migrations
- **SQLite** (dev) / **PostgreSQL** (prod)

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Framer Motion** - Animations
- **Zustand** - State management
- **React Query** - Data fetching
- **Axios** - HTTP client

## 📖 API Endpoints

### Stories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/stories` | List all stories |
| POST | `/api/v1/stories` | Create a new story |
| GET | `/api/v1/stories/{id}` | Get story details |
| DELETE | `/api/v1/stories/{id}` | Delete a story |
| POST | `/api/v1/stories/{id}/generate/opening` | Generate story opening |
| GET | `/api/v1/stories/{id}/nodes` | Get all story nodes |

### Story Nodes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/stories/{id}/nodes/{node_id}` | Get node details |
| POST | `/api/v1/stories/{id}/nodes/{node_id}/continue` | Continue story |
| POST | `/api/v1/stories/{id}/nodes/{node_id}/ending` | Generate ending |
| GET | `/api/v1/stories/{id}/nodes/{node_id}/path` | Get path to node |

### Jobs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/jobs/{id}` | Get job status |
| POST | `/api/v1/jobs/{id}/cancel` | Cancel pending job |

## 🎨 Customization

### Adding New Narrator Personas
Edit `Backend/core/story_generator.py`:

```python
NARRATOR_PROMPTS = {
    "your_persona": """Your custom narrator description...""",
}
```

And update `Frontend/src/types/index.ts`:

```typescript
export type NarratorPersona = 
  | 'mysterious'
  | 'your_persona'  // Add here
```

### Changing AI Model
In `Backend/core/story_generator.py`:

```python
class StoryGenerator:
    def __init__(self, model_name: str = "gemini-1.5-pro"):  # Change model
```

## 🧪 Testing

```bash
# Backend tests
cd Backend
pytest

# Frontend tests
cd Frontend
npm run test
```

## 🚢 Deployment

### Backend (Railway/Render)
1. Set environment variables
2. Use PostgreSQL for production
3. Run `alembic upgrade head`

### Frontend (Vercel/Netlify)
1. Set `VITE_API_URL` to your backend URL
2. Build with `npm run build`

## 📄 License

MIT License - feel free to use this project for learning or building your own interactive fiction platform!

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

Built with ❤️ by developers who love interactive storytelling
