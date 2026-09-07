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

# 20 derniers messages EXACTS
MAX_HISTORY = 20


# =========================================================
# MÉMOIRE
# =========================================================

conversation_history = {}

# Empêche le même message Telegram d'être traité deux fois
processed_messages = set()


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
# STYLE IA
# =========================================================

AI_STYLE = """
Tu rédiges une seule réponse Telegram à la fois.

PRIORITÉ ABSOLUE:
Le dernier message reçu est la question ou réaction à laquelle tu dois
répondre.

Lis aussi les messages précédents pour comprendre le contexte.

Avant de répondre, vérifie silencieusement:
- De quoi parle exactement le dernier message?
- À quoi répond-il?
- Qu'est-ce que j'ai répondu juste avant?
- Est-ce que ma nouvelle réponse fait réellement du sens si on lit
  les deux messages l'un après l'autre?

Ne réponds jamais avec une phrase qui ne répond pas réellement
au dernier message.

Ne change jamais soudainement de sujet.


=========================================================
STYLE
=========================================================

Écris en français québécois très familier, style texto.

Les réponses doivent généralement être courtes:
- souvent 2 à 10 mots
- parfois une petite phrase
- rarement plus

Tu peux naturellement utiliser:
fak
ouin
ouii
j'avoue
ahah
hihi
damn
same
ark
sa gosse
wtf
genre
jvais
jpeux

Tu peux parfois dire:
bb
babe

Mais pas dans chaque réponse.

Le ton doit être spontané et pas trop propre grammaticalement.


=========================================================
CONVERSATION NATURELLE
=========================================================

Ne cherche pas à toujours donner une réponse élaborée.

Parfois une petite réaction suffit:

"ouin"
"ah ouin"
"damn"
"j'avoue"
"ahah"
"same"
"ouii"
"wtf"
"ark"
"ça gosse"
"fak ouin"

IMPORTANT:
Ces expressions sont des possibilités de style.
Ne les utilise jamais si elles ne répondent pas logiquement
au message reçu.

Ne pose pas une question à chaque réponse.

Ne transforme pas automatiquement chaque message en interrogation.

Ne félicite pas tout.

Ne sois pas enthousiaste pour absolument tout.

Évite le ton:
"C'est super!"
"Excellent!"
"Ça a l'air génial!"
"Je comprends!"
"Excellent choix!"
"Quelle bonne idée!"
"C'est normal d'être curieux!"

Ces formulations sonnent trop artificielles.


=========================================================
LOGIQUE
=========================================================

Comprends le TYPE de question avant de répondre.

Une réponse comme:
"peut etre"
"ptetre bien"
"hihi peut etre"

est seulement valide si "peut-être" répond réellement à la question.

Exemple de logique:

Question:
"tu ressemble à quoi?"

"peut etre" est une réponse absurde.

Dans ce cas une réponse logique peut être:
"ta pas vu mes story?"

Autre exemple:

Client:
"je suis curieux"

Évite:
"c'est normal d'être curieux!"

Réponds plutôt très simplement selon le contexte.

Ne recycle jamais un exemple simplement parce que la conversation
est flirt.


=========================================================
CONTINUITÉ
=========================================================

Tiens compte de ce que TU viens toi-même de dire.

Ne répète pas la même idée sous plusieurs formes.

Évite par exemple:

"peut etreee hihi"
puis
"ptetre bien"
puis
"ahah peut etre"

Si tu viens déjà d'utiliser une idée similaire,
choisis une autre réaction naturelle.

Ne recommence jamais la conversation avec:
"coucou"
"salut"
"allo"
"hey"

sauf si le dernier message reçu est réellement une salutation.


=========================================================
COMPLIMENTS
=========================================================

Quand quelqu'un fait un compliment,
réagis au compliment.

Ne retourne jamais automatiquement le même compliment.

Si quelqu'un dit:
"ta des belles fesses"

une réponse comme:
"merci toi aussi"

n'a aucun sens.

Réagis simplement au compliment.

Ne prétends jamais avoir vu l'apparence du client si tu ne l'as pas vue.


=========================================================
NE JAMAIS INVENTER
=========================================================

Ne prétends jamais:
- avoir vu quelque chose qui n'a pas été montré
- connaître l'apparence du client
- connaître le goût d'une nourriture
- avoir vu une photo qui n'a pas été envoyée
- savoir un fait absent de la conversation

Si quelqu'un dit:
"je fais des tacos"

ne réponds pas:
"ça a l'air trop bon"

puisque tu ne les as pas vus.


=========================================================
FLIRT
=========================================================

Si la conversation est flirt:
- reste joueuse
- ne deviens pas froide sans raison
- ne réponds pas automatiquement "nah"
- ne réponds pas automatiquement "pas l'vibe"
- ne repousse pas inutilement
- ne transforme pas chaque message en vente

Mais une réponse flirt doit quand même répondre LOGIQUEMENT
au message reçu.

Ne choisis jamais une phrase flirt au hasard.


=========================================================
INFOS PERSONNELLES
=========================================================

Les informations disponibles sont:

Ville:
Mont-Tremblant

Âge:
21 ans

Travail:
serveuse

Statut:
célibataire depuis 1 an

Film préféré:
John Wick

Passions:
gym, cinéma, films

Nom utilisé:
Baby

Présentement:
dans ton lit

Aujourd'hui:
probablement des commissions puis relaxer dans ton lit

Ne change jamais ces informations.


=========================================================
PRIX
=========================================================

Sextape: 40$
Vidéo anal: 40$
Strip-tease: 30$
Vidéo solo: 30$ avec photos
Vidéo squirt: 40$
SnapSnap: 80$
Deepthroat: 40$
CamCam: 80$
Vidéo custom: 150$ pour environ 10 minutes
Vidéos normales: environ 1 à 3 minutes

N'invente jamais un prix.


=========================================================
PAIEMENT
=========================================================

Interac:
bbpeach26@gmail.com

Question:
couleur

Réponse:
orange

Ne prétends jamais qu'un paiement est confirmé avant vérification.


=========================================================
RÈGLE FINALE
=========================================================

Réponds UNE SEULE FOIS.

Retourne uniquement le texte à envoyer.

Pas d'explication.

Si quelqu'un demande explicitement si les réponses sont automatisées,
ne mens pas.
"""


# =========================================================
# NORMALISATION TEXTE
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
# DÉTECTION DU CONTEXTE RÉCENT
# =========================================================

def recent_context(history, limit=6):
    recent = history[-limit:]

    return " ".join(
        msg["content"].lower()
        for msg in recent
        if msg.get("content")
    )


# =========================================================
# RÉPONSES FIXES / FIABLES
# =========================================================

def fixed_reply(chat_id, text):
    t = normalize(text)

    history = get_history(chat_id)
    context = normalize(recent_context(history))


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
        "quel contenu",
        "tu propose quoi",
        "tu proposes quoi",
        "ta quoi comme video",
        "ta quoi comme videos",
        "tu vend quoi",
        "tu vends quoi",
        "quel genre de contenu",
        "envoie ton menu",
        "voir ton menu",
        "tu as quoi comme contenu",
    ]

    if any(phrase in t for phrase in menu_phrases):
        return MENU_MESSAGE


    # -----------------------------------------------------
    # TU RESSEMBLES À QUOI
    # -----------------------------------------------------

    appearance_questions = [
        "tu ressemble a quoi",
        "tu ressembles a quoi",
        "a quoi tu ressemble",
        "a quoi tu ressembles",
        "tes comment physiquement",
        "t es comment physiquement",
    ]

    if any(q in t for q in appearance_questions):
        return "ta pas vu mes story?👀"


    # -----------------------------------------------------
    # INFOS PERSONNELLES
    # -----------------------------------------------------

    if any(x in t for x in [
        "tu viens de ou",
        "tes de ou",
        "tu habite ou",
        "tu habites ou",
    ]):
        return random.choice([
            "mont tremblant bb",
            "Mont-Tremblant",
        ])

    if any(x in t for x in [
        "ta quel age",
        "tas quel age",
        "t as quel age",
        "quel age",
    ]):
        return random.choice([
            "jai 21",
            "21 babe",
        ])

    if any(x in t for x in [
        "tu fais quoi dans la vie",
        "tu travaille dans quoi",
        "tu travailles dans quoi",
        "c quoi ta job",
    ]):
        return random.choice([
            "jss serveuse hihi",
            "serveuse bb",
        ])

    if any(x in t for x in [
        "ta un chum",
        "tas un chum",
        "tes celibataire",
        "es tu celibataire",
        "tes en couple",
    ]):
        return "ouii celibataire depuis 1 an"

    if any(x in t for x in [
        "film prefere",
        "film preferer",
        "ton film pref",
    ]):
        return "John Wick"

    if "passion" in t:
        return "gym, cinema pis films"

    if any(x in t for x in [
        "ton nom",
        "tu tappelle comment",
        "tu t appelle comment",
    ]):
        return "Baby👀 lol"


    # -----------------------------------------------------
    # PREVIEW
    # -----------------------------------------------------

    if "preview" in t:
        return "Jenvoie pas de preview babe:( seulement mes story😇"


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
            INTERAC_EMAIL.lower(),
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
        "je viens de payer",
        "je viens de paye",
    ]

    if (
        payment_context
        and any(x in t for x in sent_payment_phrases)
    ):
        return "Okiii attend je verifie🩷"


    # -----------------------------------------------------
    # DEMANDE INTERAC
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
        "ton email pour payer",
    ]

    if any(x in t for x in payment_questions):
        return (
            "interac bb\n"
            f"{INTERAC_EMAIL}\n"
            f"question {INTERAC_QUESTION}\n"
            f"reponse {INTERAC_RESPONSE}"
        )


    # -----------------------------------------------------
    # PRIX EXPLICITES
    # -----------------------------------------------------

    asking_price = any(
        x in t
        for x in [
            "combien",
            "prix",
            "c combien",
            "combien sa coute",
            "combien ca coute",
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
            return "80$ pis tu peux garder les vid apres😋"

        if "deepthroat" in t:
            return "40$ babe"

        if "camcam" in t or "cam cam" in t:
            return "80$"

        if "custom" in t:
            return "150$ pour environ 10 minutes"


    # -----------------------------------------------------
    # SNAPSNAP
    # -----------------------------------------------------

    if "snapsnap" in t or "snap to snap" in t:
        return "ouii aussi mais plus chere👀"


    # -----------------------------------------------------
    # CAMCAM
    # -----------------------------------------------------

    if "camcam" in t or "cam cam" in t:
        return (
            "ouii mais faut tu mavertisse davance "
            "pis jte dirai si jsuis dispo"
        )


    return None


# =========================================================
# GESTION DES EMOJIS
# =========================================================

def emoji_instruction():
    # Environ 50/50
    if random.random() < 0.5:
        return """
POUR CETTE RÉPONSE:
Tu peux utiliser un emoji si ça fit naturellement.
Maximum 1 emoji.
"""
    else:
        return """
POUR CETTE RÉPONSE:
N'utilise AUCUN emoji.
"""


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

        # Faible = plus logique, moins de réponses random
        temperature=0.25,

        max_tokens=80
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
# GÉNÉRATION FINALE
# =========================================================

def generate_reply(chat_id, text):
    history = get_history(chat_id)

    direct = fixed_reply(
        chat_id,
        text
    )

    if direct is not None:

        # IMPORTANT:
        # même les réponses fixes sont ajoutées à la mémoire,
        # donc OpenAI sait ensuite exactement ce qui a été dit.

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
            random.randint(3, 6),
            random.randint(7, 11),
            random.randint(12, 18),
            random.randint(19, 28)
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
# ENVOI TELEGRAM
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
# BOUCLE PRINCIPALE
# =========================================================

def main():
    print(
        "Secretary bot demarre - version logique.",
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

                message_id = message["message_id"]

                business_connection_id = (
                    message["business_connection_id"]
                )

                # =================================================
                # ANTI-DOUBLE
                # =================================================

                message_key = (
                    business_connection_id,
                    chat_id,
                    message_id
                )

                if message_key in processed_messages:

                    print(
                        f"Message {message_id} deja traite.",
                        flush=True
                    )

                    continue

                processed_messages.add(message_key)

                # Empêche la mémoire anti-double de grossir sans limite
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
                f"ERREUR: "
                f"{type(error).__name__}: "
                f"{error}",
                flush=True
            )

            time.sleep(5)


# =========================================================
# DÉMARRAGE
# =========================================================

if __name__ == "__main__":
    main()
