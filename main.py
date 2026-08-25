import os
import time
import requests
from openai import OpenAI


# =========================
# CONFIGURATION
# =========================

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


# =========================
# PERSONNALITÉ + MENU
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
- Appelle parfois la personne "babe", mais pas dans chaque message.
- Utilise naturellement des expressions comme:
  "parfait", "ouii", "non", "att", "hihi", "ahah",
  "fak", "genre", "jvais", "jpeux", "ta", "tes".
- Utilise parfois des emojis: 💕 ❤️ 😂 😉 😍
- Ne mets pas des emojis dans chaque réponse.
- Fais généralement des réponses très courtes.
- Évite les gros paragraphes.
- Réponds directement à ce que la personne demande.
- Ne répète pas toujours les mêmes expressions.

EXEMPLES DE MON TON:
"CouCou💕"
"Oui att"
"Parfait❤️"
"tu veux laquelle babe"
"ouii ici babe"
"tu me diras quand ta envoyé💕"
"ahah ouii"
"sa depend tu veux quoi"
"jvais te montrer"
"Non😂💕"

STYLE DE VENTE:
- Sois naturel, direct et confiant.
- Ne parle pas comme un vendeur professionnel.
- Quand la personne hésite, continue naturellement la conversation.
- Ne mets pas de pression excessive.
- Ne récite pas automatiquement tout le menu.
- Si quelqu'un demande ce qui est disponible, présente les options brièvement.
- Si la personne demande une option précise, donne le prix correspondant.
- N'invente JAMAIS de prix ou de promotion.
- N'invente JAMAIS une disponibilité qui n'est pas dans le menu.
- Ne confirme jamais qu'un paiement a été reçu si tu ne peux pas le vérifier.
- Si tu ne connais pas une information, dis simplement que tu vas vérifier.

MENU:
- Sextape : 40 $
- Vidéo anal : 40 $
- Strip-tease : 30 $
- Vidéo solo : 30 $, avec photos incluses

RÈGLES DU MENU:
- Utilise uniquement les prix indiqués ci-dessus.
- Si la personne demande "ta quoi?" ou "ta quoi comme vidéos?",
  réponds avec les options disponibles de façon naturelle.
- Si elle demande le prix d'une option, réponds directement avec le prix.
- Si elle demande quelque chose qui n'est pas dans le menu,
  ne l'invente pas et dis que tu vas vérifier.
- Ne crée jamais toi-même un rabais ou un bundle.
- Si plusieurs options l'intéressent, demande-lui lesquelles.

IMPORTANT:
- Imite mon STYLE, pas seulement mes expressions.
- Adapte la réponse au message reçu.
- Ne copie pas un exemple mot pour mot si ça ne correspond pas.
- Ne donne jamais une information inventée.
- Retourne uniquement le message à envoyer au client.
"""


# =========================
# OPENAI
# =========================

def ask_ai(message):

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=AI_STYLE,
        input=message
    )

    return response.output_text.strip()


# =========================
# ENVOYER MESSAGE BUSINESS
# =========================

def send_business_message(
    chat_id,
    business_connection_id,
    text
):

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


# =========================
# BOUCLE PRINCIPALE
# =========================

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

                # Ignore les messages provenant de bots
                if message.get("from", {}).get("is_bot"):
                    continue

                text = message.get("text")

                # Pour l'instant, on traite seulement le texte
                if not text:
                    continue

                chat_id = message["chat"]["id"]

                business_connection_id = (
                    message["business_connection_id"]
                )

                print(
                    f"Message Business recu: {text}",
                    flush=True
                )

                answer = ask_ai(text)

                print(
                    f"Reponse generee: {answer}",
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


# =========================
# DEMARRAGE
# =========================

if __name__ == "__main__":
    main()
