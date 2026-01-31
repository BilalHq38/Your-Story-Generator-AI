# 📖 Story Teller - AI-Powered Interactive Storytelling

An immersive choose-your-own-adventure platform that generates dynamic, branching narratives with AI-powered text-to-speech narration in multiple languages.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)

---

## 🌟 Features

### 🎭 Dynamic Story Generation
- **AI-Powered Narratives**: Leverages Google's Gemini 2.5 Flash for intelligent story generation
- **Branching Storylines**: Every choice creates unique narrative paths
- **Multiple Genres**: Fantasy, sci-fi, mystery, romance, horror, and more
- **Customizable Settings**: Choose atmosphere, narrator persona, and language

### 🎙️ Advanced Text-to-Speech
- **Local MMS-TTS Integration**: Meta's Massively Multilingual Speech model
- **1,100+ Languages Supported**: Including English, Urdu, Hindi, Arabic, and more
- **Narrator Personas**: Five distinct narration styles (mysterious, epic, horror, comedic, romantic)
- **Instant Audio Playback**: Audio generated alongside story text for seamless experience
- **Smart Caching**: Audio files cached for instant replay

### 🌍 Multilingual Support
- **English & Urdu**: Full support with native TTS voices
- **Extensible**: Easy to add more languages
- **Context-Aware**: Stories maintain cultural and linguistic authenticity

### 📚 Story Management
- **Story Library**: Browse and continue your adventures
- **Session Tracking**: Resume stories exactly where you left off
- **Tree Visualization**: View your story's branching paths
- **History**: Track all choices made throughout your journey

---

## 🏗️ Architecture

### Backend (FastAPI + Python)
```
Backend/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── config.py          # Application settings
│   ├── story_generator.py # AI story generation with Gemini
│   ├── tts.py             # Text-to-speech service
│   ├── models.py          # Database models
│   └── prompts.py         # AI prompts for story generation
├── ai/
│   ├── mms_tts.py         # Meta MMS-TTS integration
│   └── __init__.py
├── routers/
│   ├── story.py           # Story CRUD endpoints
│   ├── tts.py             # TTS endpoints
│   └── jobs.py            # Background job endpoints
├── db/
│   └── database.py        # SQLAlchemy setup
├── models/
│   ├── story.py           # Story & StoryNode models
│   └── job.py             # Background job model
├── schema/
│   ├── story.py           # Pydantic schemas
│   └── job.py
└── alembic/               # Database migrations
```

### Frontend (React + TypeScript)
```
Frontend/
├── src/
│   ├── pages/
│   │   ├── HomePage.tsx         # Landing page
│   │   ├── CreateStoryPage.tsx  # Story creation form
│   │   ├── StoryPage.tsx        # Interactive story reader
│   │   ├── LibraryPage.tsx      # Story collection
│   │   └── StoryTreePage.tsx    # Story path visualization
│   ├── components/
│   │   ├── story/
│   │   │   ├── StoryContent.tsx      # Story text display
│   │   │   ├── ChoiceButtons.tsx     # Interactive choices
│   │   │   ├── AudioPlayer.tsx       # Audio playback controls
│   │   │   ├── GenreSelector.tsx     # Genre picker
│   │   │   ├── NarratorSelector.tsx  # Narrator persona picker
│   │   │   └── LanguageSelector.tsx  # Language picker
│   │   ├── layout/
│   │   │   ├── Layout.tsx       # Main layout wrapper
│   │   │   └── Navbar.tsx       # Navigation bar
│   │   └── ui/                  # Reusable UI components
│   ├── api/
│   │   ├── client.ts            # Axios client setup
│   │   ├── stories.ts           # Story API calls
│   │   └── jobs.ts              # Job polling
│   ├── stores/
│   │   └── storyStore.ts        # State management
│   └── styles/
│       └── globals.css          # Global styles with Tailwind
└── public/                      # Static assets
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+** (Backend)
- **Node.js 18+** (Frontend)
- **uv** (Python package manager) - [Install uv](https://github.com/astral-sh/uv)
- **Google Gemini API Key** - [Get API Key](https://ai.google.dev/)

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd "Story Teller"
```

### 2️⃣ Backend Setup

#### Install Dependencies

```bash
cd Backend
uv sync
```

#### Configure Environment Variables

Create a `.env` file in the `Backend` directory:

```env
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite

# Application Settings
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=sqlite:///./story_teller.db

# CORS (adjust for production)
ALLOWED_ORIGINS=["http://localhost:3000"]
```

#### Run Database Migrations

```bash
uv run alembic upgrade head
```

#### Start the Backend Server

```bash
uv run uvicorn main:app --reload --port 8000
```

Backend will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

### 3️⃣ Frontend Setup

#### Install Dependencies

```bash
cd ../Frontend
npm install
```

#### Configure Environment Variables

Create a `.env` file in the `Frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

#### Start the Development Server

```bash
npm run dev
```

Frontend will be available at: **http://localhost:3000**

---

## 🎮 Usage Guide

### Creating Your First Story

1. **Navigate to Create Story** (`/create`)
2. **Enter Story Details**:
   - Title and prompt (e.g., "A space adventure on Mars")
   - Select genre (Fantasy, Sci-Fi, Mystery, etc.)
   - Choose atmosphere (Magical, Dark, Whimsical, etc.)
   - Pick narrator persona (Mysterious, Epic, Horror, etc.)
   - Select language (English or Urdu)
3. **Generate Opening**: Click "Generate Story" to create the first scene
4. **Wait for Audio**: Audio narration generates automatically

### Making Choices

- Read the generated story text
- Listen to audio narration (optional)
- Select one of 2-3 presented choices
- Story continues based on your selection
- Audio generates instantly for each new scene

### Managing Stories

- **Library** (`/library`): View all your stories
- **Continue**: Resume stories from where you left off
- **Tree View** (`/story/:id/tree`): Visualize all branching paths
- **Delete**: Remove stories you no longer want

---

## 🔧 Configuration

### AI Model Settings

The application uses Google's Gemini with automatic fallback:

```python
# Primary model
GEMINI_MODEL=gemini-2.5-flash-lite

# Fallback order (automatic)
gemini-2.5-flash → gemini-2.0-flash → gemini-1.5-flash
```

### TTS Configuration

Located in `Backend/ai/mms_tts.py`:

```python
# Narrator speed adjustments
NARRATOR_SPEED = {
    "mysterious": 0.9,   # Slower, deliberate
    "epic": 1.1,         # Energetic
    "horror": 0.85,      # Very slow
    "comedic": 1.15,     # Fast, upbeat
    "romantic": 0.95,    # Gentle
}
```

### Supported Languages

Add more languages in `Backend/ai/mms_tts.py`:

```python
LANGUAGE_MODELS = {
    "english": ("facebook/mms-tts-eng", "eng"),
    "urdu": ("facebook/mms-tts-urd", "urd"),
    # Add more...
}
```

---

## 📡 API Endpoints

### Stories

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/stories` | List all stories with pagination |
| `POST` | `/api/v1/stories` | Create a new story |
| `GET` | `/api/v1/stories/{id}` | Get story details |
| `DELETE` | `/api/v1/stories/{id}` | Delete a story |
| `GET` | `/api/v1/stories/{id}/tree` | Get story tree structure |
| `POST` | `/api/v1/stories/{id}/generate/opening` | Generate opening scene |
| `POST` | `/api/v1/stories/{id}/node/{node_id}/continue` | Continue from a node |

### Text-to-Speech

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/tts/languages` | List supported languages |
| `POST` | `/api/v1/tts/synthesize` | Generate speech from text |
| `DELETE` | `/api/v1/tts/cache` | Clear audio cache |
| `POST` | `/api/v1/tts/unload` | Unload models to free memory |

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/jobs/{id}` | Get job status |
| `POST` | `/api/v1/jobs/{id}/cancel` | Cancel a running job |

---

## 🛠️ Development

### Backend Development

#### Run Tests

```bash
cd Backend
uv run pytest
```

#### Code Formatting

```bash
uv run black .
uv run ruff check --fix .
```

#### Type Checking

```bash
uv run mypy .
```

### Frontend Development

#### Run Tests

```bash
cd Frontend
npm test
```

#### Build for Production

```bash
npm run build
```

#### Preview Production Build

```bash
npm run preview
```

---

## 🗃️ Database Schema

### Stories Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `title` | String | Story title |
| `prompt` | Text | Initial prompt |
| `genre` | String | Story genre |
| `language` | String | Story language |
| `narrator_persona` | String | Narrator type |
| `atmosphere` | String | Story atmosphere |
| `session_id` | String | Unique session identifier |
| `created_at` | DateTime | Creation timestamp |

### Story Nodes Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `story_id` | Integer | Foreign key to stories |
| `parent_id` | Integer | Parent node (for branching) |
| `content` | Text | Story text content |
| `choices` | JSON | Available choices |
| `is_root` | Boolean | Is opening scene |
| `is_ending` | Boolean | Is final scene |
| `depth` | Integer | Depth in story tree |
| `node_metadata` | JSON | Audio URL and other metadata |

---

## 🎨 Customization

### Adding New Genres

Edit `Backend/core/prompts.py`:

```python
GENRE_DESCRIPTIONS = {
    "your_genre": "Description for AI context",
    # ...
}
```

Update `Backend/schema/story.py`:

```python
class GenreType(str, Enum):
    YOUR_GENRE = "your_genre"
```

### Adding Narrator Personas

Edit `Backend/ai/mms_tts.py`:

```python
NARRATOR_SPEED = {
    "your_narrator": 1.0,  # Speech speed
    # ...
}
```

---

## 🐛 Troubleshooting

### Backend Issues

**Issue**: `No module named 'google.generativeai'`
```bash
cd Backend
uv sync
```

**Issue**: TTS model not found
- Models download automatically on first use (~50MB per language)
- Check internet connection
- Ensure disk space for model cache

**Issue**: Database errors
```bash
cd Backend
uv run alembic upgrade head
```

### Frontend Issues

**Issue**: API connection failed
- Ensure backend is running on port 8000
- Check `VITE_API_BASE_URL` in `.env`

**Issue**: Audio not playing
- Check browser console for errors
- Verify TTS endpoint is accessible
- Clear browser cache

---

## 📦 Deployment

### Backend (Production)

1. Set environment variables:
```env
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

2. Use production ASGI server:
```bash
uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend (Production)

1. Build the app:
```bash
npm run build
```

2. Serve static files:
```bash
npm install -g serve
serve -s dist -p 3000
```

Or deploy to:
- **Vercel** (Recommended for React)
- **Netlify**
- **AWS S3 + CloudFront**

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Backend: Follow PEP 8, use type hints
- Frontend: Use TypeScript, follow ESLint rules
- Write meaningful commit messages
- Add tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** - AI story generation
- **Meta MMS-TTS** - Multilingual text-to-speech
- **FastAPI** - Modern Python web framework
- **React** - Frontend library
- **Tailwind CSS** - Styling framework

---

## 📧 Contact

For questions, issues, or suggestions:

- **GitHub Issues**: [Create an issue](../../issues)
- **Email**: your-email@example.com

---

## 🗺️ Roadmap

- [ ] Add more languages (Spanish, French, German)
- [ ] Implement user authentication
- [ ] Add story sharing functionality
- [ ] Create mobile app (React Native)
- [ ] Add story export (PDF, EPUB)
- [ ] Implement collaborative storytelling
- [ ] Add voice input for choices
- [ ] Create story templates library

---

**Made with ❤️ by [Your Name]**

*Experience the future of interactive storytelling.*
