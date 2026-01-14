from openai import OpenAI


class AncientReverseAI:
    """
    تبدیل هوشمند متن باستانی به:
    - فارسی
    - انگلیسی
    با استفاده از هوش مصنوعی
    """

    SUPPORTED_SCRIPTS = [
        'cuneiform', 'pahlavi', 'manichaean',
        'hieroglyph', 'akkadian', 'oracle_bone',
        'avestan', 'linear_b', 'hebrew',
        'sanskrit', 'brahmi'
    ]

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://ai.liara.ir/api/v1/6825d0c28c48644ab8263648",
        model: str = "openai/gpt-4o-mini"
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def translate(self, ancient_text: str, script: str) -> str:
        """
        دریافت ترجمه فارسی و انگلیسی از متن باستانی
        """

        if script not in self.SUPPORTED_SCRIPTS:
            return f"❌ Script not supported. Valid options: {self.SUPPORTED_SCRIPTS}"

        system_prompt = f"""
You are a professional historical linguist and ancient script expert.

The user will provide text written in the ancient script: {script}.

Your task is STRICTLY to:
1. Accurately transliterate and interpret the ancient text.
2. Provide:
   - A precise Persian (Farsi) translation
   - A precise English translation

Rules:
- Do NOT invent content.
- Do NOT add commentary.
- If ambiguous or damaged, clearly state it.
- Preserve original historical meaning.
- Output format MUST be exactly:

Persian:
<translation>

English:
<translation>
"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": ancient_text}
                ],
                temperature=0.2
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            return f"❌ AI Reverse Error: {str(e)}"
