"""Story generator using LangChain and Groq.
Production-safe for Vercel (serverless).
"""

import logging
import re
import threading
from typing import Any, Optional
from uuid import uuid4

from core.config import settings

logger = logging.getLogger(__name__)


# Narrator persona prompts
NARRATOR_PROMPTS = {
    "mysterious": """You are The Enigma, a mysterious narrator who speaks in riddles and shadows. 
Your prose is atmospheric and cryptic, revealing secrets slowly. Use metaphors involving darkness, 
mist, and hidden meanings. Build tension through ambiguity.""",
    
    "epic": """You are The Chronicler, a grand narrator of heroic tales and legends. 
Your prose is dramatic and sweeping, with epic descriptions of battles, quests, and destiny. 
Use powerful imagery and speak of honor, courage, and fate.""",
    
    "horror": """You are The Whisperer, a narrator of unsettling tales that creep under the skin. 
Your prose is creepy and atmospheric, building dread through subtle wrongness. 
Focus on sensory details that feel off, unexplained sounds, and building paranoia.""",
    
    "comedic": """You are The Jester, a witty narrator with impeccable comic timing. 
Your prose includes clever observations, ironic situations, and unexpected humor. 
Balance adventure with levity, finding absurdity in even dire situations.""",
    
    "romantic": """You are The Poet, a passionate narrator who stirs the heart. 
Your prose is emotional and sensory, focusing on connections between characters, 
longing, beauty, and the intensity of feeling. Use lyrical, flowing language.""",
}

# Atmosphere modifiers
ATMOSPHERE_PROMPTS = {
    "dark": "The atmosphere should be dark and foreboding. Shadows lurk in every corner, danger feels ever-present.",
    "magical": "The atmosphere should be mystical and enchanting. Wonder and magic fill the air, reality bends in beautiful ways.",
    "peaceful": "The atmosphere should be calm and serene. A gentle journey with moments of beauty and tranquility.",
    "tense": "The atmosphere should be suspenseful. Every moment matters, stakes are high, and tension builds constantly.",
    "whimsical": "The atmosphere should be light and playful. Adventure with a smile, quirky details, and cheerful energy.",
}

# Urdu narrator persona prompts
NARRATOR_PROMPTS_URDU = {
    "mysterious": """آپ 'معمہ' ہیں، ایک پراسرار راوی جو پہیلیوں اور سائیوں میں بات کرتا ہے۔ 
آپ کی نثر ماحولیاتی اور پراسرار ہے، راز آہستہ آہستہ ظاہر کرتی ہے۔ 
اندھیرے، دھند، اور چھپے معانی کے استعارے استعمال کریں۔ ابہام کے ذریعے کشیدگی پیدا کریں۔""",
    
    "epic": """آپ 'مؤرخ' ہیں، بہادری کی داستانوں اور افسانوں کے عظیم راوی۔ 
آپ کی نثر ڈرامائی اور وسیع ہے، لڑائیوں، مہمات، اور تقدیر کی شاندار تفصیلات کے ساتھ۔ 
طاقتور تصویر کشی کریں اور عزت، ہمت، اور قسمت کی بات کریں۔""",
    
    "horror": """آپ 'سرگوشی کرنے والا' ہیں، خوفناک کہانیوں کا راوی جو جلد کے نیچے رینگتی ہیں۔ 
آپ کی نثر خوفناک اور ماحولیاتی ہے، باریک غلطیوں کے ذریعے ڈر پیدا کرتی ہے۔ 
حسی تفصیلات پر توجہ دیں جو غلط لگتی ہیں، غیر واضح آوازیں، اور بڑھتا ہوا وہم۔""",
    
    "comedic": """آپ 'مسخرہ' ہیں، بے عیب مزاحیہ وقت کے ساتھ ایک ذہین راوی۔ 
آپ کی نثر میں ہوشیار مشاہدات، ستم ظریفی کے حالات، اور غیر متوقع مزاح شامل ہے۔ 
مہم جوئی کو ہلکا پن کے ساتھ متوازن کریں، سنگین حالات میں بھی بے تکا پن تلاش کریں۔""",
    
    "romantic": """آپ 'شاعر' ہیں، ایک پرجوش راوی جو دل کو ہلا دیتا ہے۔ 
آپ کی نثر جذباتی اور حسی ہے، کرداروں کے درمیان تعلقات، 
آرزو، خوبصورتی، اور احساس کی شدت پر توجہ مرکوز کرتی ہے۔ شاعرانہ، روانی والی زبان استعمال کریں۔""",
}

# Urdu atmosphere modifiers
ATMOSPHERE_PROMPTS_URDU = {
    "dark": "ماحول اندھیرا اور خوفناک ہونا چاہیے۔ ہر کونے میں سائے چھپے ہوئے ہیں، خطرہ ہر وقت محسوس ہوتا ہے۔",
    "magical": "ماحول جادوئی اور سحر انگیز ہونا چاہیے۔ حیرت اور جادو ہوا میں بھرے ہیں، حقیقت خوبصورت طریقوں سے مڑتی ہے۔",
    "peaceful": "ماحول پرسکون اور سکون بخش ہونا چاہیے۔ خوبصورتی اور سکون کے لمحات کے ساتھ ایک نرم سفر۔",
    "tense": "ماحول سسپنس سے بھرا ہونا چاہیے۔ ہر لمحہ اہم ہے، داؤ بلند ہے، اور کشیدگی مسلسل بڑھتی ہے۔",
    "whimsical": "ماحول ہلکا اور چنچل ہونا چاہیے۔ مسکراہٹ کے ساتھ مہم جوئی، عجیب تفصیلات، اور خوشگوار توانائی۔",
}


class StoryGenerator:
    """Generates story content using Groq AI via LangChain."""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.groq_model
        self.llm = None
        self._initialized = False
        self._lock = threading.Lock()

        if not settings.groq_api_key:
            logger.warning("GROQ_API_KEY not set — generation will fail")

    def _ensure_initialized(self) -> None:
        """Initialize the LLM on first use (thread-safe)."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            try:
                from langchain_groq import ChatGroq

                if not settings.groq_api_key:
                    raise RuntimeError("GROQ_API_KEY is required")

                self.llm = ChatGroq(
                    model=self.model_name,
                    api_key=settings.groq_api_key,
                    temperature=0.8,
                    max_tokens=3000,
                    timeout=60,       # ✅ safer for serverless
                    max_retries=2,    # ✅ tolerate cold starts
                )

                self._initialized = True
                logger.info("Groq LLM initialized (%s)", self.model_name)

            except Exception:
                logger.exception("Failed to initialize Groq LLM")
                raise
    
    def generate_stream(
        self,
        job_type: str,
        story: Any,
        parent_node: Optional[Any] = None,
        choice_text: Optional[str] = None,
    ):
        """
        Generate story content with streaming.
        
        Yields tokens as they are generated, then yields final parsed result.
        
        Args:
            job_type: 'generate_opening', 'generate_continuation', 'generate_ending'
            story: The Story model instance
            parent_node: Parent StoryNode for continuations
            choice_text: The choice made by the user
        
        Yields:
            {"type": "token", "content": str} for each token
            {"type": "done", "content": str, "choices": list, "is_ending": bool} at end
        """
        self._ensure_initialized()

        from langchain_core.messages import HumanMessage, SystemMessage

        system_prompt = self._build_system_prompt(
            story.narrator_persona,
            story.atmosphere,
            story.genre,
            story.language,
        )

        user_prompt = self._build_user_prompt(
            job_type,
            story,
            parent_node,
            choice_text,
            story.language,
        )

        full_content = ""

        try:
            for chunk in self.llm.stream([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]):
                if chunk and getattr(chunk, "content", None):
                    full_content += chunk.content
                    yield {"type": "token", "content": chunk.content}

            parsed = self._parse_response(
                full_content,
                is_ending=(job_type == "generate_ending"),
            )

            yield {
                "type": "done",
                "content": parsed["content"],
                "choices": parsed["choices"],
                "is_ending": parsed["is_ending"],
            }

        except Exception:
            logger.exception("Streaming generation failed")
            raise  # ❗ let FastAPI handle it properly
    
    def generate(
        self,
        job_type: str,
        story: Any,
        parent_node: Optional[Any] = None,
        choice_text: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate story content synchronously.
        
        Args:
            job_type: 'generate_opening', 'generate_continuation', 'generate_ending'
            story: The Story model instance
            parent_node: Parent StoryNode for continuations
            choice_text: The choice made by the user
        
        Returns:
            {"content": str, "choices": list[dict], "is_ending": bool}
        """
        self._ensure_initialized()

        from langchain_core.messages import HumanMessage, SystemMessage

        system_prompt = self._build_system_prompt(
            story.narrator_persona,
            story.atmosphere,
            story.genre,
            story.language,
        )

        user_prompt = self._build_user_prompt(
            job_type,
            story,
            parent_node,
            choice_text,
            story.language,
        )

        try:
            result = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])

            content = result.content
            return self._parse_response(
                content,
                is_ending=(job_type == "generate_ending"),
            )

        except Exception:
            logger.exception("Story generation failed")
            raise
    
    def _build_system_prompt(self, narrator: str, atmosphere: str, genre: str, language: str = "english") -> str:
        """Build the system prompt based on narrator, atmosphere, and language."""
        narrator_prompt = NARRATOR_PROMPTS.get(narrator, NARRATOR_PROMPTS["mysterious"])
        atmosphere_prompt = ATMOSPHERE_PROMPTS.get(atmosphere, ATMOSPHERE_PROMPTS["magical"])
        
        if language == "urdu":
            narrator_prompt_urdu = NARRATOR_PROMPTS_URDU.get(narrator, NARRATOR_PROMPTS_URDU["mysterious"])
            atmosphere_prompt_urdu = ATMOSPHERE_PROMPTS_URDU.get(atmosphere, ATMOSPHERE_PROMPTS_URDU["magical"])
            
            return f"""{narrator_prompt_urdu}

{atmosphere_prompt_urdu}

آپ ایک {genre} کہانی لکھ رہے ہیں۔ ان اصولوں پر عمل کریں:
1. آسان اردو میں لکھیں
2. تیسرے شخص میں لکھیں ("وہ گیا...")
3. کہانی تیزی سے آگے بڑھے
4. ہر حصہ 100-150 الفاظ کا ہو
5. 2-3 انتخابات دیں

اس فارمیٹ میں لکھیں:
[STORY]
کہانی...
[/STORY]

[CHOICES]
1. پہلا انتخاب
2. دوسرا انتخاب
3. تیسرا انتخاب
[/CHOICES]

[ENDING]false[/ENDING]"""
        
        return f"""{narrator_prompt}

{atmosphere_prompt}

You are writing a {genre} story. Be BRIEF and FAST:
1. Simple words only
2. Third-person ("He went...")
3. Focus on action, not descriptions
4. Keep each part 100-150 words MAX
5. Give 2-3 choices

Write in this format:
[STORY]
Story here...
[/STORY]

[CHOICES]
1. First choice
2. Second choice
3. Third choice
[/CHOICES]

[ENDING]false[/ENDING]"""
    
    def _build_user_prompt(
        self,
        job_type: str,
        story: Any,
        parent_node: Optional[Any],
        choice_text: Optional[str],
        language: str = "english",
    ) -> str:
        """Build the user prompt based on job type and language."""
        
        is_urdu = language == "urdu"
        
        if job_type == "generate_opening":
            if is_urdu:
                prompt = f""""{story.title}" کے عنوان سے ایک {story.genre} کہانی کا دلچسپ آغاز بنائیں۔

{f'کہانی کا تصور: {story.description}' if story.description else ''}

ایک ایسے ہُک سے شروع کریں جو فوری طور پر قاری کو اپنی طرف کھینچے۔ منظر قائم کریں، 
ایک دلچسپ صورتحال پیش کریں، اور مختلف مہم جوئی کے راستے ترتیب دینے والے انتخابات کے ساتھ ختم کریں۔

یاد رکھیں: خالص اردو میں لکھیں۔"""
            else:
                prompt = f"""Create an engaging opening for a {story.genre} story titled "{story.title}".

{f'Story concept: {story.description}' if story.description else ''}

Start with a hook that immediately draws the reader in. Establish the setting, introduce 
a compelling situation, and end with choices that set up different adventure paths."""
        
        elif job_type == "generate_continuation":
            previous_content = parent_node.content if parent_node else ""
            if is_urdu:
                prompt = f"""قاری کے انتخاب کی بنیاد پر کہانی جاری رکھیں۔

پچھلا منظر:
{previous_content}

قاری نے یہ انتخاب کیا: "{choice_text}"

اہم: پچھلے کرداروں اور واقعات کو یاد رکھیں۔ کہانی میں تسلسل برقرار رکھیں۔
اس انتخاب سے بیانیہ جاری رکھیں۔ فیصلے کے فوری نتائج دکھائیں،
کہانی کو آگے بڑھائیں، اور قاری کے لیے نئے انتخابات پیش کریں۔

یاد رکھیں: خالص اردو میں لکھیں۔"""
            else:
                prompt = f"""Continue the story based on the reader's choice.

Previous scene:
{previous_content}

The reader chose: "{choice_text}"

IMPORTANT: Maintain continuity with the characters and events mentioned above.
Continue the narrative from this choice. Show the immediate consequences of the decision,
develop the story, and present new choices for the reader."""
        
        elif job_type == "generate_ending":
            previous_content = parent_node.content if parent_node else ""
            if is_urdu:
                prompt = f"""اس کہانی کا تسلی بخش اختتام لکھیں۔

پچھلا منظر:
{previous_content}

اہم: تمام اہم کرداروں کا ذکر کریں اور کہانی کے واقعات کو سمیٹیں۔
ایک یادگار اختتام بنائیں جو بیانیہ کو سمیٹے۔ اختتام کو مناسب اور 
سفر کے مطابق محسوس ہونا چاہیے۔ کوئی انتخابات شامل نہ کریں - یہ اختتام ہے۔

[ENDING]true[/ENDING] اپنے جواب میں سیٹ کریں۔

یاد رکھیں: خالص اردو میں لکھیں۔"""
            else:
                prompt = f"""Write a satisfying ending for this story.

Previous scene:
{previous_content}

IMPORTANT: Reference the main characters and wrap up the story events mentioned above.
Create a memorable conclusion that wraps up the narrative. The ending should feel earned 
and appropriate for the journey taken. Do NOT include any choices - this is the end.

Set [ENDING]true[/ENDING] in your response."""
        
        else:
            prompt = f"Continue the story for {story.title}"
        
        return prompt
    
    def _parse_response(self, content: str, is_ending: bool = False) -> dict[str, Any]:
        """Parse the AI response into structured content."""
        story_match = re.search(r"\[STORY\](.*?)\[/STORY\]", content, re.DOTALL)
        story_content = story_match.group(1).strip() if story_match else content.strip()

        choices = []
        if not is_ending:
            match = re.search(r"\[CHOICES\](.*?)\[/CHOICES\]", content, re.DOTALL)
            if match:
                for line in re.findall(r"\d+\.\s*(.+)", match.group(1))[:4]:
                    choices.append({
                        "id": str(uuid4())[:8],
                        "text": line.strip(),
                        "consequence_hint": None,
                    })

        ending_match = re.search(r"\[ENDING\](true|false)\[/ENDING\]", content, re.I)

        return {
            "content": story_content,
            "choices": choices,
            "is_ending": is_ending or (ending_match and ending_match.group(1).lower() == "true"),
        }


def get_story_generator() -> StoryGenerator:
    """Create a new StoryGenerator instance (no pre-warming for serverless)."""
    return StoryGenerator()
