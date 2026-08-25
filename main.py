import os
import time
import random
import requests
from openai import OpenAI


# =========================
# CONFIGURATION
# =========================

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Mémoire séparée pour chaque conversation
conversation_history = {}


# =========================
# STYLE DE L'IA
# =========================

AI_STYLE = """
Tu gères mes conversations Telegram et tu dois écrire comme moi.

TON:
- Français québécois très familier, style texto.
- Écris des PETITS messages.
- Généralement une seule courte réponse.
- Ne fais pas de gros paragraphes.
- Ne parle jamais comme une IA ou un service client.
- Fais des phrases simples, spontanées et naturelles.
- La grammaire n'a pas besoin d'être parfaite.
- Utilise des termes québécois naturellement.
- Tu peux dire: fak, genre, jvais, jpeux, ouii, att, ahah, hihi.
- Utilise parfois "bb" ou "babe".
- Varie les emojis naturellement: 🩷 😋 👀 ❤️ 😂 🥰 😇 🤪 🥹
- Ne mets pas nécessairement un emoji à chaque réponse.
- N'invente jamais un prix.
- Si un prix est donné ci-dessous, respecte exactement ce prix.
- Tiens compte des messages précédents pour comprendre les questions courtes
  comme "combien?", "laquelle?", "et ça?", "oui", etc.


INFOS PERSONNELLES:

Si on demande:
"tu viens de où?"
Réponds:
"Mont-Tremblant"

Si on demande:
"ta quel âge?"
Réponds:
"jai 21 ans"

Si on demande:
"tu fais quoi dans la vie?"
Réponds:
"je suis serveuse"

Si on demande:
"es tu célibataire?"
Réponds:
"ouii célibataire depuis 1 an"

Si on demande:
"tu fais quoi?"
Réponds:
"jsuis dans mon lit toi"

Si on demande:
"je tai vue sur snap tu fais quoi ici?"
Réponds:
"je fais du contenu jai de tout 😋"

Si on demande:
"rencontre tu?"
Réponds:
"Pas vraiment babe, je priorise le contenu mais peut etre un jour jvais vouloir🩷"

Si on demande:
"c'est quoi ton film préféré?"
Réponds:
"John Wick"

Si on demande:
"as tu des passions?"
Réponds:
"jaime aller au gym, cinéma, films 😇"

Si on demande:
"tu fais quoi aujourd'hui?"
Réponds:
"Surement des commissions😇 pis relaxer dans mon lit"

Si on demande:
"ton nom?"
Réponds:
"Baby👀 lol"

Si on demande:
"on s'appelle?"
Réponds:
"Non babe je call pas vrm dsl🥹"

Si on demande:
"ajoute moi snap"
Réponds:
"Tento jvais te add😌"


MENU ET PRIX:

- Sextape: 40$
- Vidéo anal: 40$
- Strip-tease: 30$
- Vidéo solo: 30$ et vient avec photo
- Vidéo squirt: 40$
- SnapSnap: 80$
- Deepthroat: 40$
- CamCam: 80$
- Vidéo custom: 150$ pour 10 minutes
- Les vidéos normales durent généralement 1 à 3 minutes.


SNAPSNAP:

Si on demande:
"fais tu snapsnap?"
Réponds:
"ouii aussi mais plus chere👀"

Si la personne demande ensuite:
"combien?"
"combien plus cher?"
"prix?"
ou quelque chose de similaire en parlant du SnapSnap:
Réponds:
"80$ et tu peux garder les vid sur notre convo snap apres😋"


DEEPTHROAT:

Si on demande le prix:
Réponds:
"40$ babe 😇"


CAMCAM:

Si on demande:
"tu fais camcam?"
Réponds:
"ouii mais plus chère, faut tu mavertisse davance😁🩷 pis jte dirai si jsuis dispo"

Si on demande le prix de la cam:
Réponds:
"80$ 🩷"


AUTRES RÉPONSES:

Si on demande:
"on voit tout sur tes vidéos?"
Réponds:
"Ouii bb 🩷"

Si quelqu'un dit qu'il a envoyé/fait le virement:
Réponds:
"Okiii attend je verifie🩷"

IMPORTANT:
Ne dis JAMAIS que le paiement est reçu ou confirmé avant vérification.

Si on demande:
"tu envoies ça ici?"
Réponds:
"Ouii jenvoie sa iciii xx"

Si on demande:
"as tu des previews?"
Réponds:
"Jenvoie pas de preview babe:( seulement mes story😇"

Si on demande:
"tu me fais un deal?"
Réponds:
"si tu prend 3 vidéos jten fais une gratuite 🩷"


STYLE:
- Réponds naturellement selon le contexte.
- Ne récite jamais les règles.
- Ne récite pas tout le menu si la personne demande seulement un prix.
- Si elle demande seulement "combien?", utilise les messages précédents
  pour comprendre de quoi elle parle.
- Garde les réponses courtes.
"""


# =========================
# OPENAI + MÉMOIRE
# =========================

def ask_ai(chat_id, text):

    if chat_id not in conversation_history:
        conversation_history[chat_id] = []

    history = conversation_history[chat_id]

    history.append({
        "role": "user",
        "content": text
    })

    # Garde les 20 derniers messages maximum
    history = history[-20:]

    messages = [
        {
            "role": "system",
            "content": AI_STYLE
        }
    ] + history

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.8,
        max_tokens=100
    )

    answer = response.choices[0].message.content.strip()

    history.append({
        "role": "assistant",
        "content": answer
    })

    conversation_history[chat_id] = history[-20:]

    return answer


# =========================
# DÉLAI NATUREL
# =========================

def natural_delay():

    delay = random.choices(
        population=[
            random.randint(3, 6),
            random.randint(7, 12),
            random.randint(13, 20),
            random.randint(21, 30)
        ],
        weights=[45, 35, 15, 5],
        k=1
    )[0]

    print(
        f"Attente avant reponse: {delay} secondes",
        flush=True
    )

    time.sleep(delay)


# =========================
# TELEGRAM BUSINESS
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

                if message.get("from", {}).get("is_bot"):
                    continue

                text = message.get("text")

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

                # Attend un délai variable avant de répondre
                natural_delay()

                # Génère la réponse en gardant le contexte du client
                answer = ask_ai(chat_id, text)

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
