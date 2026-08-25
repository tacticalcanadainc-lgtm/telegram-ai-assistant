import os
import time
import requests
from openai import OpenAI

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


AI_STYLE = """
Tu gères mes conversations Telegram et tu dois écrire comme moi.

TON:
- Français québécois très familier, style texto.
- Ne parle JAMAIS comme une IA ou un service client.
- Fais des phrases simples, spontanées et naturelles.
- Tu peux faire des petites fautes et utiliser des formulations texto.
- N'essaie pas d'avoir une grammaire parfaite.
- Utilise parfois des mots anglais naturellement.
- Appelle parfois la personne "babe".
- Utilise naturellement des expressions comme:
  "parfait", "ouii", "non", "att", "hihi", "ahah",
  "fak", "genre", "jvais", "jpeux", "ta", "tes".
- Emojis fréquents mais pas à chaque phrase: 💕 ❤️ 😂 😉 😍
- Réponses courtes adaptées à Telegram.

STYLE DE VENTE:
- Sois direct et confiant.
- Quand la personne hésite, continue naturellement la conversation.
- Ne sois pas insistant au point d'être bizarre.
- Ne donne jamais un prix ou une promotion qui n'est pas fourni dans le contexte.
- Ne prétends jamais qu'un paiement a été reçu si tu ne le sais pas.
- Ne promets jamais d'envoyer quelque chose si cette action n'est pas réellement possible.

EXEMPLES DU TON:
"CouCou💕"
"Oui att"
"Parfait❤️"
"Profite du deal"
"tu veux laquelle babe"
"ouii ici babe"
"tu me diras quand ta envoyé💕"
"ahah ouii"
"sa depend tu veux quoi"
"jvais te montrer"
"Non😂💕"

IMPORTANT:
Imite le STYLE des exemples, mais ne copie pas automatiquement leurs
informations, prix ou offres. Réponds selon la conversation actuelle.
"""


def ask_ai(message):
    response = client.responses.create(
        model="gpt-5-mini",
        instructions=AI_STYLE,
        input=message
    )

    return response.output_text.strip()


def send_business_message(chat_id, business_connection_id, text):
    response = requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "business_connection_id": business_connection_id,
            "chat_id": chat_id,
            "text": text
        },
        timeout=30
    )

    response.raise_for_status()


def main():

    print("Secretary bot demarre.", flush=True)

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

            response.raise_for_status()

            data = response.json()

            for update in data.get("result", []):

                offset = update["update_id"] + 1

                message = update.get("business_message")

                if not message:
                    continue

                # Ignore les messages envoyés par des bots
                if message.get("from", {}).get("is_bot"):
                    continue

                text = message.get("text")

                if not text:
                    continue

                chat_id = message["chat"]["id"]
                business_connection_id = message["business_connection_id"]

                print(
                    f"Message Business reçu: {text}",
                    flush=True
                )

                answer = ask_ai(text)

                print(
                    f"Réponse: {answer}",
                    flush=True
                )

                send_business_message(
                    chat_id,
                    business_connection_id,
                    answer
                )

        except Exception as error:

            print(
                f"ERREUR: {type(error).__name__}: {error}",
                flush=True
            )

            time.sleep(5)


if __name__ == "__main__":
    main()
