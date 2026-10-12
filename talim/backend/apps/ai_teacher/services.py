"""AI Teacher xizmatlari: Speech Recognition, Pronunciation/Accent tahlili, Lesson Generator, AI Chat.

Tashqi provayderlar:
 - STT: Whisper (self-hosted) yoki xizmat ko'rsatuvchi API
 - Pronunciation/Accent: forced-alignment + phoneme scoring modeli
 - AI Ustoz (chat): Claude + tool'lar (agent.py). Claude ishlamasa — xAI Grok -> Groq
 - Lesson generator, matematika, avatar: call_ai() — Claude -> xAI Grok -> Groq -> offline javob
"""
import logging

from django.conf import settings

logger = logging.getLogger(__name__)
def transcribe_audio(audio_url: str) -> dict:
    """Whisper orqali audio -> matn. Qaytaradi: {"text": str, "confidence": float}."""
    # TODO: real Whisper/STT xizmatiga ulash (self-hosted yoki API)
    return {"text": "", "confidence": 0.0}


def analyze_pronunciation_and_accent(audio_url: str, expected_text: str) -> dict:
    """Talaffuz balli, aksent turi va fonema darajasidagi xatolarni qaytaradi."""
    # TODO: forced-alignment modeliga ulash
    return {
        "pronunciation_score": 0.0,
        "accent_similarity": 0.0,
        "detected_accent": "unknown",
        "phoneme_errors": [],
    }


def run_speech_analysis(transcript):
    """Transcript yaratilgach chaqiriladi (signal orqali) — SpeechAnalysis yozuvini to'ldiradi."""
    from .models import SpeechAnalysis

    stt_result = transcribe_audio(transcript.audio_url)
    scoring = analyze_pronunciation_and_accent(transcript.audio_url, transcript.text)
    return SpeechAnalysis.objects.update_or_create(
        transcript=transcript,
        defaults={
            "recognized_text": stt_result["text"],
            "confidence": stt_result["confidence"],
            **scoring,
        },
    )[0]


OFFLINE_FALLBACK_REPLY = (
    "Hozircha internet aloqasi yo'q (yoki AI xizmati javob bermadi), shuning uchun offline rejimda "
    "javob beryapman: davom eting, savolingizni internet tiklangach yana yuborsangiz to'liq AI javobini olasiz."
)


def _extract_responses_text(data: dict) -> str:
    """xAI (va OpenAI-uslubidagi) /v1/responses javobidan matnni ajratib oladi."""
    if data.get("output_text"):
        return data["output_text"]
    texts = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") in ("output_text", "text"):
                    texts.append(c.get("text", ""))
    return "\n".join(t for t in texts if t).strip()



def _call_xai(prompt: str, system: str = "") -> str | None:
    """xAI Grok API orqali so‘rov yuboradi.
    Xatolik yuz bersa None qaytaradi va Groq'ga o'tiladi.
    """
    import requests

    if not settings.XAI_API_KEY:
        return None

    url = "https://api.x.ai/v1/responses"
    headers = {
        "Authorization": f"Bearer {settings.XAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": messages,
        "tool_choice": "none",
    }

    if system:
        payload["instructions"] = system

    try:
        resp = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
        print(f"xAI ulanish xatosi: {exc}")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"xAI so‘rov xatosi: {exc}")
        return None

    if resp.status_code == 429:
        print("xAI: so‘rovlar limiti tugagan.")
        return None

    if resp.status_code in (401, 403):
        print(f"xAI API kaliti yoki ruxsat xatosi: {resp.status_code}")
        return None

    if not resp.ok:
        print(f"xAI HTTP xatosi: {resp.status_code}")
        print(f"xAI javobi: {resp.text[:2000]}")
        return None

    try:
        data = resp.json()
        text = _extract_responses_text(data)

        if not text:
            print("xAI javobida matn topilmadi.")

        return text or None

    except (ValueError, KeyError, TypeError) as exc:
        print(f"xAI javobini o‘qish xatosi: {exc}")
        return None



def _call_groq(prompt: str, system: str = "") -> str:
    import requests

    api_key = getattr(settings, "GROQ_API_KEY", "")
    if not api_key:
        logger.warning("GROQ_API_KEY sozlanmagan.")
        return OFFLINE_FALLBACK_REPLY

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    messages = []

    if system:
        messages.append({
            "role": "system",
            "content": system,
        })

    messages.append({
        "role": "user",
        "content": prompt,
    })

    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": messages,
    }

    try:
        resp = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.exceptions.RequestException as exc:
        logger.warning("Groq ulanish xatosi: %s", exc)
        return OFFLINE_FALLBACK_REPLY

    # HTTP xatolarining haqiqiy sababini logga chiqaramiz.
    if not resp.ok:
        logger.error(
            "Groq API xatosi: status=%s, javob=%s",
            resp.status_code,
            resp.text[:2000],
        )

        if resp.status_code == 401:
            return "GROQ_API_KEY noto'g'ri yoki eskirgan."

        if resp.status_code == 403:
            return "Groq API so'rovni rad etdi. Kalit ruxsatlarini tekshiring."

        if resp.status_code == 404:
            return "Groq modeli yoki API manzili topilmadi."

        if resp.status_code == 429:
            return "AI so'rovlar chegarasiga yetdi. Keyinroq qayta urinib ko'ring."

        return OFFLINE_FALLBACK_REPLY

    try:
        data = resp.json()
        choices = data.get("choices", [])

        if not choices:
            logger.error("Groq javobida choices mavjud emas: %s", str(data)[:1000])
            return OFFLINE_FALLBACK_REPLY

        message = choices[0].get("message", {})
        content = message.get("content")

        # Ba'zi reasoning modellarida matn content ichida bo'lmasligi mumkin.
        if isinstance(content, str) and content.strip():
            return content.strip()

        logger.warning(
            "Groq javobida matn topilmadi: %s",
            str(data)[:1000],
        )
        return OFFLINE_FALLBACK_REPLY

    except (ValueError, KeyError, TypeError, IndexError) as exc:
        logger.exception("Groq javobini o'qish xatosi: %s", exc)
        return OFFLINE_FALLBACK_REPLY

def call_ai(prompt: str, system: str = "") -> str:
    """AI chaqiruvi (lesson generation va AI chat uchun umumiy).

    Provayder tartibi: 1) Claude (ANTHROPIC_API_KEY bo'lsa) → 2) xAI Grok (XAI_API_KEY bo'lsa) →
    3) Groq (GROQ_API_KEY bo'lsa) → 4) offline fallback javob.
    Hech qanday holatda xatoga chiqarmaydi — ilova internet bilan ham, internetsiz ham ishlayveradi.
    """
    from .agent import ClaudeUnavailable, simple_completion

    try:
        return simple_completion(prompt, system=system)
    except ClaudeUnavailable:
        pass
    xai_reply = _call_xai(prompt, system=system)
    if xai_reply is not None:
        return xai_reply
    return _call_groq(prompt, system=system)


def _extract_json(raw: str) -> dict:
    """Gemini javobi ko'pincha ```json ... ``` bilan o'ralgan bo'ladi — shu qobiqni tozalab JSON qilib o'qiydi."""
    import json
    import re

    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def generate_lesson(user, subject, cefr_level=None):
    """Lesson Generator: foydalanuvchi darajasiga mos dars tuzadi (vocab/grammar/exercise bloklari)."""
    from .models import GeneratedLesson
    import json

    system = (
        "Sen tajribali til/matematika o'qituvchisisan. Foydalanuvchi darajasiga mos, "
        "JSON formatida struktura qaytar: {title, objective, content_blocks: [{type, data}]}."
    )
    prompt = f"Fan: {subject.name}, daraja: {cefr_level.code if cefr_level else 'boshlang\'ich'}. Yangi dars tuzib ber."
    raw = call_ai(prompt, system=system)
    try:
        parsed = _extract_json(raw)
    except (ValueError, TypeError):
        parsed = {"title": f"{subject.name} darsi", "objective": "", "content_blocks": []}

    return GeneratedLesson.objects.create(
        user=user, subject=subject, cefr_level=cefr_level,
        title=parsed.get("title", f"{subject.name} darsi"),
        objective=parsed.get("objective", ""),
        content_blocks=parsed.get("content_blocks", []),
    )


def chat_with_ai(thread, user_message: str) -> "AIChatMessage":
    """AI Ustoz chati: tarixni Claude agentiga beradi (tool'lar bilan) va javobni saqlaydi.

    Claude sozlanmagan yoki ishlamasa, eski provayderlar (xAI -> Groq) tool'larsiz javob beradi.
    """
    from .agent import ClaudeUnavailable, history_to_messages, run_tutor
    from .models import AIChatMessage
    from .prompts import TUTOR_SYSTEM_PROMPT

    user_message = (user_message or "").strip()
    AIChatMessage.objects.create(thread=thread, role=AIChatMessage.Role.USER, content=user_message)
    if not thread.title:
        thread.title = user_message[:60]
    thread.save(update_fields=["title", "updated_at"])

    rows = thread.messages.order_by("created_at").values("role", "content")
    messages = history_to_messages(rows, settings.AI_TUTOR_HISTORY_LIMIT)

    meta = {}
    try:
        reply_text, tools_used = run_tutor(thread.user, thread, messages)
        meta = {"provider": "claude", "tools_used": tools_used}
    except ClaudeUnavailable:
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        reply_text = _call_xai(prompt, system=TUTOR_SYSTEM_PROMPT) or _call_groq(prompt, system=TUTOR_SYSTEM_PROMPT)
        meta = {"provider": "fallback"}

    if not reply_text:
        reply_text = "Kechirasiz, javob tayyorlay olmadim. Iltimos, qayta urinib ko'ring."
    return AIChatMessage.objects.create(
        thread=thread, role=AIChatMessage.Role.ASSISTANT, content=reply_text, meta=meta
    )
