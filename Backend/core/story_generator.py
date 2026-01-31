"""Story generator using LangChain and Gemini."""

import logging
import re
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
    """Generates story content using Gemini AI via LangChain."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the story generator."""
        if not settings.gemini_api_key:
            logger.warning("Gemini API key not set (GEMINI_API_KEY/GOOGLE_API_KEY) - generation will fail")

        self.model_name = model_name or getattr(settings, "gemini_model", "gemini-2.5-flash")
        self.llm = None
        self._initialized = False

    def _model_fallbacks(self) -> list[str]:
        """Ordered list of model names to try if the current one fails."""
        candidates = [
            getattr(settings, "gemini_model", ""),
            self.model_name,
            # Fallback models when quota exhausted or rate limited
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-3.0-flash",

        ]
        seen: set[str] = set()
        ordered: list[str] = []
        for m in candidates:
            if m and m not in seen:
                seen.add(m)
                ordered.append(m)
        return ordered
    
    def _ensure_initialized(self):
        """Initialize the LLM on first use."""
        if self._initialized:
            return
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            api_key = settings.gemini_api_key
            if not api_key:
                raise ValueError(
                    "Gemini API key required. Set GEMINI_API_KEY (or GOOGLE_API_KEY) in Backend/.env"
                )
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=api_key,
                temperature=0.85,
                max_tokens=2500,
            )
            self._initialized = True
        except ImportError:
            logger.error("langchain_google_genai not installed. Run: uv add langchain-google-genai")
            raise ImportError("langchain_google_genai not installed. Run: uv add langchain-google-genai")
    
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
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            # Build system prompt based on narrator persona, atmosphere, and language
            narrator_persona = getattr(story, 'narrator_persona', 'mysterious')
            atmosphere = getattr(story, 'atmosphere', 'magical')
            genre = getattr(story, 'genre', 'Fantasy')
            language = getattr(story, 'language', 'english')
            
            system_prompt = self._build_system_prompt(narrator_persona, atmosphere, genre, language)
            user_prompt = self._build_user_prompt(job_type, story, parent_node, choice_text, language)
            
            logger.info(f"Generating {job_type} for story '{story.title}' in {language}")
            
            def _invoke_once():
                return self.llm.invoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ])

            # Synchronous invocation (with model fallback on 404, 429, or 400)
            def _should_switch_model(error_message: str) -> bool:
                """Check if error warrants switching to a different model."""
                # 404 - Model not found
                if "NOT_FOUND" in error_message and "models/" in error_message:
                    return True
                # 429 - Rate limit exceeded / quota exhausted
                if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message or "quota" in error_message.lower():
                    return True
                # 400 - Model doesn't support certain features (e.g., system instructions)
                if "INVALID_ARGUMENT" in error_message and "models/" in error_message:
                    return True
                return False

            try:
                result = _invoke_once()
            except Exception as e:
                message = str(e)
                if _should_switch_model(message):
                    last_error: Exception = e
                    for candidate in self._model_fallbacks():
                        if candidate == self.model_name:
                            continue
                        logger.warning(
                            "Model '%s' unavailable (error: %s); switching to '%s'",
                            self.model_name,
                            "rate limit" if "429" in message or "RESOURCE_EXHAUSTED" in message else "incompatible" if "INVALID_ARGUMENT" in message else "not found",
                            candidate,
                        )
                        try:
                            self.model_name = candidate
                            self._initialized = False
                            self._ensure_initialized()
                            result = _invoke_once()
                            break
                        except Exception as retry_error:
                            last_error = retry_error
                    else:
                        raise last_error
                else:
                    raise
            
            content = result.content if hasattr(result, 'content') else str(result)
            parsed = self._parse_response(content, is_ending=(job_type == "generate_ending"))
            
            logger.info(f"Generated {len(parsed['content'])} chars with {len(parsed['choices'])} choices")
            return parsed
            
        except Exception as e:
            logger.exception(f"Generation failed: {e}")
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

آپ ایک {genre} کہانی لکھ رہے ہیں۔ ان قواعد کی پیروی کریں:
1. خالص اردو میں لکھیں، انگریزی الفاظ سے گریز کریں
2. دوسرے شخص میں عمیق بیانیہ لکھیں ("آپ کمرے میں داخل ہوتے ہیں...")
3. ماحول سے مطابقت رکھنے والی واضح حسی تفصیلات بنائیں
4. ہر حصہ 150-300 الفاظ کے درمیان رکھیں
5. 2-4 معنی خیز انتخابات بنائیں جو مختلف کہانی کے راستوں کی طرف لے جائیں

آؤٹ پٹ فارمیٹ (ہمیشہ بالکل اس طرح پیروی کریں):
[STORY]
یہاں آپ کی کہانی کا مواد...
[/STORY]

[CHOICES]
1. پہلا انتخاب
2. دوسرا انتخاب
3. تیسرا انتخاب (اختیاری)
[/CHOICES]

[ENDING]false[/ENDING]"""
        
        return f"""{narrator_prompt}

{atmosphere_prompt}

You are writing a {genre} story. Follow these rules:
1. Write immersive, second-person narrative ("You walk into the room...")
2. Create vivid sensory descriptions that match the atmosphere
3. Keep each segment between 150-300 words
4. Generate 2-4 meaningful choices that lead to different story paths
5. Each choice should have real consequences for the narrative

Output Format (ALWAYS follow this exactly):
[STORY]
Your story content here...
[/STORY]

[CHOICES]
1. First choice option
2. Second choice option  
3. Third choice option (optional)
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
        """Build the user prompt based on job type, context, and language."""
        
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

اس انتخاب سے بیانیہ جاری رکھیں۔ فیصلے کے فوری نتائج دکھائیں،
کہانی کو آگے بڑھائیں، اور قاری کے لیے نئے انتخابات پیش کریں۔

یاد رکھیں: خالص اردو میں لکھیں۔"""
            else:
                prompt = f"""Continue the story based on the reader's choice.

Previous scene:
{previous_content}

The reader chose: "{choice_text}"

Continue the narrative from this choice. Show the immediate consequences of the decision,
develop the story, and present new choices for the reader."""
        
        elif job_type == "generate_ending":
            previous_content = parent_node.content if parent_node else ""
            if is_urdu:
                prompt = f"""اس کہانی کا تسلی بخش اختتام لکھیں۔

پچھلا منظر:
{previous_content}

ایک یادگار اختتام بنائیں جو بیانیہ کو سمیٹے۔ اختتام کو مناسب اور 
سفر کے مطابق محسوس ہونا چاہیے۔ کوئی انتخابات شامل نہ کریں - یہ اختتام ہے۔

[ENDING]true[/ENDING] اپنے جواب میں سیٹ کریں۔

یاد رکھیں: خالص اردو میں لکھیں۔"""
            else:
                prompt = f"""Write a satisfying ending for this story.

Previous scene:
{previous_content}

Create a memorable conclusion that wraps up the narrative. The ending should feel earned 
and appropriate for the journey taken. Do NOT include any choices - this is the end.

Set [ENDING]true[/ENDING] in your response."""
        
        else:
            prompt = f"Continue the story for {story.title}"
        
        return prompt
    
    def _parse_response(self, content: str, is_ending: bool = False) -> dict[str, Any]:
        """Parse the AI response into structured content."""
        
        # Extract story content
        story_match = re.search(r'\[STORY\](.*?)\[/STORY\]', content, re.DOTALL)
        story_content = story_match.group(1).strip() if story_match else content.strip()
        
        # Clean up any remaining tags if parsing failed
        story_content = re.sub(r'\[(STORY|CHOICES|ENDING)\]', '', story_content)
        story_content = re.sub(r'\[/(STORY|CHOICES|ENDING)\]', '', story_content)
        
        # Extract choices
        choices = []
        if not is_ending:
            choices_match = re.search(r'\[CHOICES\](.*?)\[/CHOICES\]', content, re.DOTALL)
            if choices_match:
                choices_text = choices_match.group(1).strip()
                choice_lines = re.findall(r'\d+\.\s*(.+)', choices_text)
                for text in choice_lines[:4]:  # Max 4 choices
                    choices.append({
                        "id": str(uuid4())[:8],
                        "text": text.strip(),
                        "consequence_hint": None,
                    })
        
        # Extract ending flag
        ending_match = re.search(r'\[ENDING\](.*?)\[/ENDING\]', content, re.IGNORECASE)
        detected_ending = ending_match and ending_match.group(1).strip().lower() == 'true'
        
        return {
            "content": story_content,
            "choices": choices,
            "is_ending": is_ending or detected_ending or len(choices) == 0,
        }

