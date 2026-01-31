"""Prompt templates for story generation."""

SYSTEM_PROMPT = """You are a master storyteller creating an interactive "choose your own adventure" story.

Your writing style should be:
- Engaging and immersive with vivid descriptions
- Appropriate for all ages (no explicit content)
- Written in second person ("You walk into the room...")
- Each segment should be 150-300 words

You must ALWAYS format your response using these tags:
[STORY]
Your story content here...
[/STORY]

[CHOICES]
1. First choice option
2. Second choice option  
3. Third choice option
[/CHOICES]

[ENDING]false[/ENDING]

Set [ENDING] to true only if this is a natural conclusion to the story."""

SYSTEM_PROMPT_URDU = """آپ ایک ماہر کہانی کار ہیں جو ایک انٹرایکٹو "اپنی مرضی کی کہانی" بنا رہے ہیں۔

آپ کا لکھنے کا انداز ہونا چاہیے:
- دلچسپ اور عمیق، واضح تفصیلات کے ساتھ
- ہر عمر کے لیے مناسب (کوئی نامناسب مواد نہیں)
- دوسرے شخص میں لکھا گیا ("آپ کمرے میں داخل ہوتے ہیں...")
- ہر حصہ 150-300 الفاظ کا ہونا چاہیے
- خالص اردو میں لکھیں، انگریزی الفاظ سے گریز کریں

آپ کو ہمیشہ اپنا جواب ان ٹیگز میں فارمیٹ کرنا ہوگا:
[STORY]
یہاں آپ کی کہانی کا مواد...
[/STORY]

[CHOICES]
1. پہلا انتخاب
2. دوسرا انتخاب
3. تیسرا انتخاب
[/CHOICES]

[ENDING]false[/ENDING]

[ENDING] کو صرف true سیٹ کریں اگر یہ کہانی کا قدرتی اختتام ہے۔"""

STORY_START_PROMPT = """Create the opening of a new {genre} adventure story based on this premise:

{prompt}

Set the scene, introduce the protagonist (the reader), and present an interesting situation 
that offers meaningful choices. End with 3-4 choices for the reader to make.

Remember to use the required format with [STORY], [CHOICES], and [ENDING] tags."""

STORY_START_PROMPT_URDU = """اس تصور کی بنیاد پر ایک نئی {genre} مہم جوئی کہانی کا آغاز کریں:

{prompt}

منظر بیان کریں، مرکزی کردار (قاری) کا تعارف کروائیں، اور ایک دلچسپ صورتحال پیش کریں 
جو معنی خیز انتخابات پیش کرے۔ قاری کے لیے 3-4 انتخابات کے ساتھ ختم کریں۔

[STORY]، [CHOICES]، اور [ENDING] ٹیگز کا استعمال ضرور کریں۔"""

STORY_CONTINUE_PROMPT = """Continue this adventure story. The reader has made their choice.

Previous story content:
{previous_content}

The reader chose: "{choice_made}"

Continue the story from this choice, describing what happens next in an engaging way.
Present 3 new choices at the end (or conclude the story if it reaches a natural ending).

Remember to use the required format with [STORY], [CHOICES], and [ENDING] tags."""

STORY_CONTINUE_PROMPT_URDU = """اس مہم جوئی کہانی کو جاری رکھیں۔ قاری نے اپنا انتخاب کر لیا ہے۔

پچھلی کہانی کا مواد:
{previous_content}

قاری نے یہ انتخاب کیا: "{choice_made}"

اس انتخاب سے کہانی کو آگے بڑھائیں، دلچسپ انداز میں بیان کریں کہ آگے کیا ہوتا ہے۔
آخر میں 3 نئے انتخابات پیش کریں (یا اگر یہ قدرتی اختتام ہے تو کہانی ختم کریں)۔

[STORY]، [CHOICES]، اور [ENDING] ٹیگز کا استعمال ضرور کریں۔"""

STORY_BRANCH_PROMPT = """Create an alternative branch for this story based on a different choice.

Story context so far:
{story_context}

The reader wants to explore this path: "{prompt}"

Write this alternative branch of the story. It should feel like a natural continuation 
if the reader had made this choice instead. Present 3 new choices at the end.

Remember to use the required format with [STORY], [CHOICES], and [ENDING] tags."""

STORY_BRANCH_PROMPT_URDU = """اس کہانی کے لیے ایک متبادل شاخ بنائیں ایک مختلف انتخاب کی بنیاد پر۔

اب تک کی کہانی کا سیاق:
{story_context}

قاری اس راستے کی کھوج کرنا چاہتا ہے: "{prompt}"

کہانی کی یہ متبادل شاخ لکھیں۔ یہ قدرتی تسلسل کی طرح لگنا چاہیے 
جیسے قاری نے اس کے بجائے یہ انتخاب کیا ہو۔ آخر میں 3 نئے انتخابات پیش کریں۔

[STORY]، [CHOICES]، اور [ENDING] ٹیگز کا استعمال ضرور کریں۔"""

# Genre-specific flavor prompts
GENRE_PROMPTS = {
    "fantasy": "Include magical elements, mythical creatures, and enchanted settings.",
    "sci-fi": "Include futuristic technology, space exploration, or advanced civilizations.",
    "mystery": "Include clues, suspense, and puzzles to solve.",
    "horror": "Include suspenseful and eerie elements (keep it age-appropriate).",
    "adventure": "Include exploration, action, and exciting discoveries.",
    "romance": "Include meaningful relationships and emotional moments.",
}

GENRE_PROMPTS_URDU = {
    "fantasy": "جادوئی عناصر، افسانوی مخلوقات، اور سحر انگیز مناظر شامل کریں۔",
    "sci-fi": "مستقبل کی ٹیکنالوجی، خلائی تحقیق، یا ترقی یافتہ تہذیبیں شامل کریں۔",
    "mystery": "سراغ، سسپنس، اور حل کرنے کے لیے پہیلیاں شامل کریں۔",
    "horror": "سسپنس اور خوفناک عناصر شامل کریں (عمر کے مطابق رکھیں)۔",
    "adventure": "تلاش، ایکشن، اور دلچسپ دریافتیں شامل کریں۔",
    "romance": "معنی خیز رشتے اور جذباتی لمحات شامل کریں۔",
}


def get_prompts_for_language(language: str = "english") -> dict:
    """Get the appropriate prompts for the specified language."""
    if language == "urdu":
        return {
            "system": SYSTEM_PROMPT_URDU,
            "start": STORY_START_PROMPT_URDU,
            "continue": STORY_CONTINUE_PROMPT_URDU,
            "branch": STORY_BRANCH_PROMPT_URDU,
            "genres": GENRE_PROMPTS_URDU,
        }
    return {
        "system": SYSTEM_PROMPT,
        "start": STORY_START_PROMPT,
        "continue": STORY_CONTINUE_PROMPT,
        "branch": STORY_BRANCH_PROMPT,
        "genres": GENRE_PROMPTS,
    }
