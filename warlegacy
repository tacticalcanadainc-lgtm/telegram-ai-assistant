import os
import time
import requests
from openai import OpenAI

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Plus tard, on personnalisera complètement ce texte
AI_STYLE = """
Tu réponds aux clients à ma place sur Telegram.

Règles:
- Réponds en français.
- Sois naturel et humain.
- Fais des réponses courtes adaptées à Telegram.
- Ne dis jamais que tu es une intelligence artificielle sauf si on te le demande.
- N'invente jamais un prix, une disponibilité ou une information.
- Si tu ne connais pas la réponse, dis simplement que tu vas vérifier.
- Pose une seule question à la fois.
"""

def ask_ai(message):
    response = client.responses.create(
        model="gpt-5-mini",
        instructions=AI_STYLE,
        input=message
    )
    return response.output_text


def send_business_message(chat_id, business_connection_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "business_connection_id": business_connection_id,
            "chat_id": chat_id,
            "text": text
        },
        timeout=30
    )


def main():
    offset = 0

    while True:
        try:
            response = requests.get(
                f"{TELEGRAM_API}/getUpdates",
                params={
                    "offset": offset,
                    "timeout": 30,
                    "allowed_updates": '["business_message"]'
                },
                timeout=40
            )

            data = response.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("business_message")

                if not message:
                    continue

                # Ignore les messages envoyés par le bot lui-même
                if message.get("from", {}).get("is_bot"):
                    continue

                text = message.get("text")

                if not text:
                    continue

                chat_id = message["chat"]["id"]
                business_connection_id = message["business_connection_id"]

                answer = ask_ai(text)

                send_business_message(
                    chat_id,
                    business_connection_id,
                    answer
                )

        except Exception as e:
            print("Erreur:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()
