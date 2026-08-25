import os
import time
import requests
from openai import OpenAI


# =========================
# VARIABLES
# =========================

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


# =========================
# STYLE
# =========================

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
- Généralement 1 à 3 messages courts plutôt qu'un gros paragraphe.

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


# =========================
# OPENAI
# =========================

def generate_reply(message):
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=AI_STYLE,
        input=message
    )

    return response.output_text.strip()


# =========================
# TELEGRAM
# =========================

def get_updates(offset=None):

    params = {
        "timeout": 30
    }

    if offset is not None:
        params["offset"] = offset

    response = requests.get(
        f"{TELEGRAM_API}/getUpdates",
        params=params,
        timeout=40
    )

    response.raise_for_status()

    return response.json()


def send_message(chat_id, text):

    response = requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=30
    )

    response.raise_for_status()


# =========================
# BOT PRINCIPAL
# =========================

def main():

    print("Bot Telegram démarré.", flush=True)

    offset = None

    while True:

        try:

            data = get_updates(offset)

            for update in data.get("result", []):

                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                text = message.get("text")
                chat_id = message.get("chat", {}).get("id")

                if not text or not chat_id:
                    continue

                print(
                    f"Message reçu ({chat_id}): {text}",
                    flush=True
                )

                reply = generate_reply(text)

                print(
                    f"Réponse générée: {reply}",
                    flush=True
                )

                send_message(chat_id, reply)

        except Exception as error:

            print(
                f"ERREUR: {type(error).__name__}: {error}",
                flush=True
            )

            time.sleep(5)


# =========================
# DÉMARRAGE
# =========================

if __name__ == "__main__":
    main()
