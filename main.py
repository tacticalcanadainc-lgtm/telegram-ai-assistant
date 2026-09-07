import os
import time
import random
import re
import requests
from openai import OpenAI


# =========================================================
# CONFIGURATION
# =========================================================

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

REPLY_MODEL = "gpt-4o-mini"

MAX_HISTORY = 20


# =========================================================
# MÉMOIRE
# =========================================================

conversation_history = {}

processed_messages = set()
processed_updates = set()


def get_history(chat_id):
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []

    return conversation_history[chat_id]


# =========================================================
# INFOS FIXES
# =========================================================

INTERAC_EMAIL = "bbpeach26@gmail.com"
INTERAC_QUESTION = "couleur"
INTERAC_RESPONSE = "orange"


MENU_MESSAGE = """J'ai des sextapes / J'ai des videos anal🤪 videos en legging de gym que je ride un dildo apres le gym, ✨, vid en missionaire/ dildo, doggy, sur ma chaise gaming 😝 d'autre video que je suce un dildo avk mes seins etc hihi😋 pis chaque vidéos vien avec des photos😇"""


PRICES = {
    "sextape": "40$",
    "anal": "40$",
    "strip": "30$",
    "solo": "30$",
    "squirt": "40$",
    "snapsnap": "80$",
    "deepthroat": "40$",
    "camcam": "80$",
    "custom": "150$",
}


# =========================================================
# PROMPT COURT / NATUREL
# =========================================================

AI_STYLE = """
Tu rédiges une seule réponse Telegram à la fois.

IMPORTANT:
Lis les derniers messages dans l'ordre.
Réponds au DERNIER message.
Ta réponse doit faire du sens avec ce qui vient juste d'être dit.

Ne change jamais soudainement de sujet.
Ne recommence jamais la conversation avec "coucou", "salut", "allo", "hey"
sauf si le dernier message reçu est lui-même une salutation.

STYLE:
- français québécois texto
- très naturel
- très court
- souvent 1 à 6 mots
- parfois une petite phrase
- pas de ton service client
- pas de phrase trop propre
- pas besoin de poser une question à chaque réponse
- pas besoin de toujours relancer
- pas besoin de toujours complimenter
- pas besoin d'être enthousiaste pour rien

Tu peux parfois utiliser:
ouin
ouii
ah ouin
j'avoue
ahah
hihi
damn
same
ark
fak
genre
jvais
jpeux
ça gosse
wtf

Tu peux parfois dire:
bb
babe

Mais pas dans chaque réponse.

ÉVITE:
"quoi de neuf?"
"comment vas-tu?"
"c'est super!"
"excellent!"
"je comprends"
"ça a l'air génial!"
"c'est normal d'être curieux!"
"bonne idée!"

Si une petite réaction suffit, fais juste une petite réaction.

Exemples de petites réactions possibles:
"ouin"
"ah ouin"
"j'avoue"
"ahah"
"same"
"ark"
"damn"
"fak ouin"

IMPORTANT:
Ces exemples montrent le STYLE seulement.
Ne les utilise jamais si ça ne répond pas vraiment au message.

LOGIQUE:
Avant de répondre, vérifie silencieusement:
"Est-ce que ma réponse répond vraiment au dernier message?"

Si la réponse serait bizarre quand on lit:
CLIENT -> ASSISTANT
alors ne l'envoie pas.

Ne réponds jamais "peut-être" à une question où "peut-être" n'a aucun sens.

Ne retourne jamais automatiquement un compliment.
Si quelqu'un dit "t'es belle", ne réponds pas "toi aussi" sauf si tu as
réellement une information qui le justifie.

Ne prétends jamais avoir vu quelque chose qui n'a pas été montré.

Si quelqu'un dit:
"je fais des tacos"
ne dis pas:
"ça a l'air bon"
si aucune photo n'a été envoyée.

EMOJIS:
- environ 1 réponse sur 2
- pas d'emoji obligatoire
- max 1 emoji la plupart du temps

INFOS PERSONNELLES:
- ville: Mont-Tremblant
- âge: 21 ans
- travail: serveuse
- célibataire depuis 1 an
- film préféré: John Wick
- passions: gym, cinéma, films
- nom utilisé: Baby
- présentement: dans ton lit

PRIX:
- sextape: 40$
- anal: 40$
- strip-tease: 30$
- solo: 30$ avec photos
- squirt: 40$
- snapsnap: 80$
- deepthroat: 40$
- camcam: 80$
- custom: 150$ environ 10 minutes
- vidéos normales: 1 à 3 minutes

Ne crée jamais un prix.

PAIEMENT:
Interac: bbpeach26@gmail.com
question: couleur
réponse: orange

Ne dis jamais qu'un paiement est reçu avant vérification.

Retourne uniquement le message à envoyer.

Si quelqu'un demande explicitement si les réponses sont automatisées,
ne mens pas.
"""


# =========================================================
# NORMALISATION
# =========================================================

def normalize(text):
    text = text.lower().strip()

    replacements = {
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "ä": "a",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text


# =========================================================
# CONTEXTE RÉCENT
# =========================================================

def recent_context(history, limit=8):
    recent = history[-limit:]

    return " ".join(
        msg["content"].lower()
        for msg in recent
        if msg.get("content")
    )


# =========================================================
# RÉPONSES FIXES IMPORTANTES
# =========================================================

def fixed_reply(chat_id, text):
    t = normalize(text)

    history = get_history(chat_id)
    context = normalize(recent_context(history))


    # -----------------------------------------------------
    # SALUTATIONS
    # -----------------------------------------------------

    if t in {
        "hey",
        "heyy",
        "hello",
        "salut",
        "allo",
        "allô",
        "coucou",
        "coucou babe",
        "yo"
    }:
        return random.choice([
            "heyy",
            "alloo",
            "coucouu",
            "hey babe"
        ])


    # -----------------------------------------------------
    # MENU / CONTENU
    # -----------------------------------------------------

    menu_phrases = [
        "cest quoi ton menu",
        "c quoi ton menu",
        "ton menu",
        "ta quoi comme contenu",
        "tas quoi comme contenu",
        "tu fais quoi comme contenu",
        "tu propose quoi",
        "tu proposes quoi",
        "ta quoi comme video",
        "ta quoi comme videos",
        "tu vend quoi",
        "tu vends quoi",
        "quel genre de contenu",
        "envoie ton menu",
        "voir ton menu",
        "tu as quoi comme contenu"
    ]

    if any(x in t for x in menu_phrases):
        return MENU_MESSAGE


    # -----------------------------------------------------
    # APPARENCE
    # -----------------------------------------------------

    appearance_questions = [
        "tu ressemble a quoi",
        "tu ressembles a quoi",
        "a quoi tu ressemble",
        "a quoi tu ressembles",
        "tes comment physiquement",
        "t es comment physiquement"
    ]

    if any(x in t for x in appearance_questions):
        return "ta pas vu mes story?"


    # -----------------------------------------------------
    # INFOS PERSONNELLES
    # -----------------------------------------------------

    if any(x in t for x in [
        "tu viens de ou",
        "tes de ou",
        "tu habite ou",
        "tu habites ou"
    ]):
        return "mont tremblant"

    if any(x in t for x in [
        "ta quel age",
        "tas quel age",
        "t as quel age",
        "quel age"
    ]):
        return "jai 21"

    if any(x in t for x in [
        "tu fais quoi dans la vie",
        "tu travaille dans quoi",
        "tu travailles dans quoi",
        "c quoi ta job"
    ]):
        return "jss serveuse"

    if any(x in t for x in [
        "ta un chum",
        "tas un chum",
        "tes celibataire",
        "es tu celibataire",
        "tes en couple"
    ]):
        return "ouii celibataire depuis 1 an"

    if any(x in t for x in [
        "film prefere",
        "film preferer",
        "ton film pref"
    ]):
        return "John Wick"

    if "passion" in t:
        return "gym cinema pis films"

    if any(x in t for x in [
        "ton nom",
        "tu tappelle comment",
        "tu t appelle comment"
    ]):
        return "Baby lol"


    # -----------------------------------------------------
    # PREVIEW
    # -----------------------------------------------------

    if "preview" in t:
        return "jenvoie pas de preview babe:( seulement mes story"


    # -----------------------------------------------------
    # PAIEMENT ENVOYÉ
    # -----------------------------------------------------

    payment_context = any(
        x in context
        for x in [
            "virement",
            "interac",
            "payer",
            "paye",
            INTERAC_EMAIL.lower()
        ]
    )

    sent_payment_phrases = [
        "jai envoye",
        "j ai envoye",
        "c envoye",
        "cest envoye",
        "virement fait",
        "jai payer",
        "jai paye",
        "je viens de payer"
    ]

    if (
        payment_context
        and any(x in t for x in sent_payment_phrases)
    ):
        return "okii attend je verifie"


    # -----------------------------------------------------
    # INTERAC
    # -----------------------------------------------------

    payment_questions = [
        "comment je paye",
        "comment je paie",
        "je paye ou",
        "je paie ou",
        "virement ou",
        "j envoie le virement ou",
        "jenvoie le virement ou",
        "cest quoi ton interac",
        "c quoi ton interac",
        "email pour le virement",
        "ton email pour payer"
    ]

    if any(x in t for x in payment_questions):
        return (
            "interac bb\n"
            f"{INTERAC_EMAIL}\n"
            f"question {INTERAC_QUESTION}\n"
            f"reponse {INTERAC_RESPONSE}"
        )


    # -----------------------------------------------------
    # PRIX
    # -----------------------------------------------------

    asking_price = any(
        x in t
        for x in [
            "combien",
            "prix",
            "c combien",
            "combien sa coute",
            "combien ca coute"
        ]
    )

    if asking_price:

        if "sextape" in t:
            return "40$"

        if "anal" in t:
            return "40$"

        if "strip" in t:
            return "30$"

        if "solo" in t:
            return "30$ pis sa vient avec des photos"

        if "squirt" in t:
            return "40$"

        if "snapsnap" in t or "snap to snap" in t:
            return "80$"

        if "deepthroat" in t:
            return "40$"

        if "camcam" in t or "cam cam" in t:
            return "80$"

        if "custom" in t:
            return "150$ pour environ 10 minutes"


    # -----------------------------------------------------
    # SNAPSNAP
    # -----------------------------------------------------

    if "snapsnap" in t or "snap to snap" in t:
        return "ouii aussi mais plus chere"


    # -----------------------------------------------------
    # CAMCAM
    # -----------------------------------------------------

    if "camcam" in t or "cam cam" in t:
        return "ouii mais faut tu mavertisse davance pis jte dirai si jsuis dispo"


    return None


# =========================================================
# EMOJI 50/50
# =========================================================

def emoji_instruction():
    if random.random() < 0.5:
        return "Pour cette réponse, tu peux utiliser maximum 1 emoji si ça fit."
    else:
        return "Pour cette réponse, n'utilise aucun emoji."


# =========================================================
# OPENAI
# =========================================================

def ask_ai(chat_id, text):
    history = get_history(chat_id)

    history.append({
        "role": "user",
        "content": text
    })

    history = history[-MAX_HISTORY:]

    messages = [
        {
            "role": "system",
            "content": AI_STYLE
        },
        {
            "role": "system",
            "content": emoji_instruction()
        }
    ]

    messages.extend(history)

    response = client.chat.completions.create(
        model=REPLY_MODEL,
        messages=messages,

        # Bas = beaucoup moins random
        temperature=0.15,

        max_tokens=60
    )

    answer = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    history.append({
        "role": "assistant",
        "content": answer
    })

    conversation_history[chat_id] = history[-MAX_HISTORY:]

    return answer


# =========================================================
# GÉNÉRATION
# =========================================================

def generate_reply(chat_id, text):
    history = get_history(chat_id)

    direct = fixed_reply(
        chat_id,
        text
    )

    if direct is not None:

        history.append({
            "role": "user",
            "content": text
        })

        history.append({
            "role": "assistant",
            "content": direct
        })

        conversation_history[chat_id] = history[-MAX_HISTORY:]

        return direct

    return ask_ai(
        chat_id,
        text
    )


# =========================================================
# DÉLAI NATUREL
# =========================================================

def natural_delay():
    delay = random.choices(
        population=[
            random.randint(2, 5),
            random.randint(6, 10),
            random.randint(11, 16),
            random.randint(17, 25)
        ],
        weights=[
            45,
            35,
            15,
            5
        ],
        k=1
    )[0]

    print(
        f"Attente avant reponse: {delay}s",
        flush=True
    )

    time.sleep(delay)


# =========================================================
# TELEGRAM
# =========================================================

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


# =========================================================
# MAIN
# =========================================================

def main():
    print(
        "Secretary bot demarre - version simple.",
        flush=True
    )

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

                update_id = update["update_id"]

                # =============================================
                # ANTI-DOUBLE PAR UPDATE
                # =============================================

                if update_id in processed_updates:
                    continue

                processed_updates.add(update_id)

                if len(processed_updates) > 10000:
                    processed_updates.clear()
                    processed_updates.add(update_id)

                offset = update_id + 1

                message = update.get("business_message")

                if not message:
                    continue

                if message.get("from", {}).get("is_bot"):
                    continue

                text = message.get("text")

                if not text:
                    continue

                chat_id = message["chat"]["id"]

                message_id = message["message_id"]

                business_connection_id = (
                    message["business_connection_id"]
                )

                # =============================================
                # ANTI-DOUBLE PAR MESSAGE
                # =============================================

                message_key = (
                    business_connection_id,
                    chat_id,
                    message_id
                )

                if message_key in processed_messages:
                    continue

                processed_messages.add(message_key)

                if len(processed_messages) > 10000:
                    processed_messages.clear()
                    processed_messages.add(message_key)

                print(
                    f"Message recu [{chat_id}]: {text}",
                    flush=True
                )

                natural_delay()

                answer = generate_reply(
                    chat_id,
                    text
                )

                print(
                    f"Reponse [{chat_id}]: {answer}",
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
