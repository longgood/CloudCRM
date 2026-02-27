# -*- encoding: utf-8 -*-

import json
import logging

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """You are a business card data extraction assistant.
Given the OCR text from a business card, extract structured information.
Return ONLY valid JSON with these fields (use null for missing):
{
  "name": "full name",
  "title": "job title",
  "company": "company name",
  "email": "email@example.com",
  "phone": "phone number",
  "address": "full address",
  "website": "website url",
  "notes": "any other relevant info"
}"""

DRAFT_SYSTEM_PROMPT = """You are a professional email assistant.
Generate a polite, professional introductory email based on:
1. The recipient's business card info
2. The sender's notes/prompt
3. The sender's company introduction template

Return JSON with exactly these fields: {"subject": "...", "body": "..."}
Write in the same language as the user's prompt. If unclear, default to Traditional Chinese."""


def extract_card_info(ocr_text, api_key):
    """Use OpenAI to extract structured info from OCR text."""
    import openai

    logger.info("Extracting card info via OpenAI")
    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"OCR Text:\n{ocr_text}"}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    logger.info(f"Extracted: {result.get('name', 'N/A')} - {result.get('company', 'N/A')}")
    return result


def generate_draft(extracted_json, user_prompt, company_template, api_key):
    """Use OpenAI to generate an email draft."""
    import openai

    logger.info("Generating draft email via OpenAI")
    client = openai.OpenAI(api_key=api_key)

    user_content = (
        f"Recipient info: {json.dumps(extracted_json, ensure_ascii=False)}\n"
        f"User's notes: {user_prompt}\n"
        f"Company template: {company_template}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": DRAFT_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    logger.info(f"Draft generated: subject='{result.get('subject', '')[:50]}...'")
    return result
