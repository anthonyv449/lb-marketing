"""
Generates professional review replies using the Anthropic API (Claude).
"""

import anthropic


class ClaudeService:

    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate_review_reply(
        self,
        business_name: str,
        reviewer_name: str,
        review_text: str,
        star_rating: str,
        tone: str,
        industry: str | None,
    ) -> str:
        sentiment_map = {
            "ONE": "negative",
            "TWO": "negative",
            "THREE": "mixed",
            "FOUR": "positive",
            "FIVE": "positive",
        }
        sentiment = sentiment_map.get(star_rating, "mixed")

        tone_descriptions = {
            "warm": "warm, personal, and genuine — like a real human who cares",
            "professional": "professional and polished — formal but not cold",
            "concise": "brief and friendly — 2 sentences max",
        }
        tone_desc = tone_descriptions.get(tone, tone_descriptions["warm"])

        max_sentences = "2 sentences max" if tone == "concise" else "2–4 sentences"
        industry_note = f" in the {industry} industry" if industry else ""

        system_prompt = (
            f"You write review replies for {business_name}{industry_note}. "
            f"Tone: {tone_desc}. "
            f"Length: {max_sentences}. "
            "Rules: "
            "- Never use filler phrases like \"We value your feedback\", "
            "\"Thank you for your review\", or \"We take this seriously\". "
            "- For negative or mixed reviews: apologise sincerely, take ownership, "
            "invite direct contact. "
            "- For positive reviews: express genuine gratitude, mention specific service "
            "if possible, invite them back. "
            f"- Sign off: The team at {business_name} "
            "- Output reply text ONLY — no preamble, labels, or quotation marks."
        )

        user_message = (
            f"Reviewer: {reviewer_name}\n"
            f"Rating: {star_rating} ({sentiment})\n"
            f"Review: {review_text}"
        )

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        return response.content[0].text
