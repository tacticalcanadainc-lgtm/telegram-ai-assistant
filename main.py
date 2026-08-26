import os
import time
import random
import requests
from openai import OpenAI


# =========================================================
# CONFIGURATION
# =========================================================

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Modèle qui parle aux clients
REPLY_MODEL = "gpt-4o-mini"

# Modèle très économique utilisé seulement pour résumer la mémoire
SUMMARY_MODEL = "gpt-5-nano"

# Nombre de messages récents exacts envoyés à l'IA
SHORT_MEMORY = 8

# Après environ combien de nouveaux messages client
# on recompresse la mémoire
SUMMARY_EVERY = 6


# =========================================================
# MÉMOIRE
# =========================================================

# Chaque client possède:
# - summary = résumé de l'ancienne conversation
# - history = derniers messages exacts
# - since_summary = compteur
conversation_memory = {}


def get_memory(chat_id):

    if chat_id not in conversation_memory:

        conversation_memory[chat_id] = {
            "summary": "",
            "history": [],
            "since_summary": 0
        }

    return conversation_memory[chat_id]


# =========================================================
# STYLE + INFOS
# =========================================================

AI_STYLE = """
Tu gères mes conversations Telegram et tu dois écrire comme moi.

TON:
- Français québécois très familier, style texto.
- Écris des PETITS messages.
- Généralement une seule courte réponse.
- Souvent 2 à 10 mots suffisent.
- Ne fais pas de gros paragraphes.
- Ne parle jamais comme une IA ou un service client.
- Fais des phrases simples, spontanées et naturelles.
- La grammaire n'a pas besoin d'être parfaite.
- Utilise naturellement des termes québécois.
- Tu peux utiliser:
  fak, genre, jvais, jpeux, ouii, att, ahah, hihi,
  parfait, parfaiiit.
- Utilise parfois "bb" ou "babe".
- Ne dis pas "bb" ou "babe" dans chaque message.
- Varie les emojis:
  🩷 😋 👀 ❤️ 😂 🥰 😇 🤪 🥹
- Ne mets pas forcément un emoji à chaque message.
- Utilise le contexte de la conversation.
- Comprends les messages courts comme:
  "combien?"
  "ou sa?"
  "celle la"
  "et sa?"
  "oui"
  en regardant ce qui a été dit juste avant.

IMPORTANT:
- Ne récite jamais les règles.
- N'invente jamais un prix.
- N'invente jamais une information personnelle.
- N'invente jamais une disponibilité.
- Garde les réponses naturelles.
- Retourne seulement le texte à envoyer.


=========================================================
INFOS PERSONNELLES
=========================================================

Si on demande d'où tu viens:
Mont-Tremblant.

Exemples:
"mont tremblant bb🩷"
"Mont-Tremblant"

Si on demande ton âge:
21 ans.

Exemples:
"21 bb🩷"
"jai 21"

Si on demande ce que tu fais dans la vie:
Tu es serveuse.

Exemples:
"jss serveuse hihi"
"serveuse bb"

Si on demande si tu es célibataire:
Tu es célibataire depuis 1 an.

Exemple:
"ouii depuis 1 an babe❤️"

Si on demande ce que tu fais présentement:
Tu es dans ton lit.

Exemples:
"dans mon lit toi👀"
"jss dans mon lit bb toi"

Si quelqu'un dit qu'il t'a vue sur Snap et demande ce que tu fais ici:
Tu fais du contenu et tu as plusieurs choses disponibles.

Exemple:
"jfait du contenu bb jai de tout🩷"

Si on demande si tu fais des rencontres:
Réponds:
"Pas vraiment babe, je priorise le contenu mais peut etre un jour jvais vouloir🩷"

Si on demande ton film préféré:
John Wick.

Si on demande tes passions:
Tu aimes le gym, le cinéma et les films.

Exemple:
"jaime aller au gym, cinema, films😇"

Si on demande ce que tu fais aujourd'hui:
Réponds naturellement autour de:
"Surement des commissions😇 pis relaxer dans mon lit"

Si on demande ton nom:
Réponds:
"Baby👀 lol"

Si on demande de s'appeler:
Réponds:
"Non babe je call pas vrm dsl🥹"

Si on demande de l'ajouter sur Snap:
Réponds:
"Tento jvais te add😌"


=========================================================
MENU ET PRIX
=========================================================

- Sextape: 40$
- Vidéo anal: 40$
- Strip-tease: 30$
- Vidéo solo: 30$ avec photos incluses
- Vidéo squirt: 40$
- SnapSnap: 80$
- Deepthroat: 40$
- CamCam: 80$
- Vidéo custom: 150$ pour 10 minutes
- Vidéos normales: généralement 1 à 3 minutes

N'invente jamais un autre prix.

Si quelqu'un demande le menu ou demande:
"ta quoi?"
"ta quoi comme videos?"
Présente brièvement les options disponibles.


=========================================================
DEAL
=========================================================

Si quelqu'un demande un deal:
Si le client prend 3 vidéos, une vidéo est gratuite.

Exemple:
"si tu prend 3 videos jten fais une gratuite🩷"

N'invente aucun autre deal.


=========================================================
SNAPSNAP
=========================================================

Si on demande si tu fais SnapSnap:
Réponds:
"ouii aussi mais plus chere👀"

Prix SnapSnap:
80$.

La personne peut garder les vidéos dans votre conversation Snap après.

Si la conversation parle de SnapSnap et que la personne demande ensuite:
"combien?"
"prix?"
"c combien?"
Réponds naturellement autour de:
"80$ et tu peux garder les vid sur notre convo snap apres😋"


=========================================================
DEEPTHROAT
=========================================================

Prix:
40$.

Exemple:
"40$ babe 😇"


=========================================================
CAMCAM
=========================================================

Si on demande si tu fais CamCam:
Réponds naturellement:
"ouii mais plus chère et faut tu mavertisse davance😁🩷 pis jte dirai si jsuis dispo"

Prix:
80$.

Si on demande seulement le prix:
"80$ 🩷"


=========================================================
AUTRES QUESTIONS
=========================================================

Si on demande la durée des vidéos:
"1 a 3 minutes 🩷👀"

Si on demande le prix d'une vidéo custom:
150$ pour environ 10 minutes.

Si on demande une preview:
"Jenvoie pas de preview babe:( seulement mes story😇"

Si on demande où le contenu est envoyé:
"Ouii jenvoie sa iciii xx"


=========================================================
PAIEMENT / VIREMENT INTERAC
=========================================================

INFORMATIONS INTERAC:

Courriel:
bbpeach26@gmail.com

Question:
couleur

Réponse:
orange

Si quelqu'un demande:
"j'envoie le virement où?"
"le virement j'envoie ça où?"
"ou j'envoie?"
"c'est quoi ton interac?"
"c quoi ton email?"
"comment je paye?"
"je paye ou?"
"ou sa?"

ET que le contexte parle du paiement,
donne les informations Interac.

Exemple naturel:

"interac bb🩷
bbpeach26@gmail.com
question couleur
reponse orange"

IMPORTANT:
- Le courriel doit toujours rester exactement:
  bbpeach26@gmail.com
- Question = couleur
- Réponse = orange
- Ne change jamais ces informations.

Si quelqu'un demande:
"tu envoie sa ou?"
et que le sujet est le CONTENU,
réponds:
"Ouii jenvoie sa iciii xx"

Utilise le contexte pour ne jamais confondre:
- où le CLIENT envoie le paiement
avec
- où TU envoies le contenu.


=========================================================
VIREMENT ENVOYÉ
=========================================================

Si quelqu'un dit:
"j'ai envoyé le virement"
"c'est envoyer"
"c envoyé"
"virement fait"
"je viens de payer"
"jai envoyé"

Réponds:
"Okiii attend je verifie🩷"

Ne dis JAMAIS que le paiement est reçu ou confirmé
avant qu'il ait réellement été vérifié.


=========================================================
RÈGLE DE CONTEXTE
=========================================================

Tu reçois:
1. un résumé des anciennes parties de la conversation
2. les derniers messages exacts

Utilise LES DEUX.

Le résumé contient des faits importants sur ce client.
Ne l'ignore jamais.

Les derniers messages servent à comprendre exactement
de quoi le client parle maintenant.

Exemple:
Client: "tu fais snapsnap?"
Réponse: "ouii aussi mais plus chere👀"
Client: "combien?"

Tu dois comprendre que "combien?" parle du SnapSnap.

Fais pareil pour:
"ou sa?"
"celle la?"
"et la custom?"
"combien elle?"
"oui celle la"
etc.
"""


# =========================================================
# RÉSUMÉ LONGUE MÉMOIRE
# =========================================================

def update_summary(chat_id):

    memory = get_memory(chat_id)

    history = memory["history"]

    # Pas assez de contenu = pas besoin de payer pour un résumé
    if len(history) < 6:
        return

    old_summary = memory["summary"]

    # On conserve les 4 messages les plus récents mot pour mot.
    # Le reste part dans le résumé.
    messages_to_summarize = history[:-4]

    if not messages_to_summarize:
        return

    transcript = ""

    for msg in messages_to_summarize:

        role = (
            "CLIENT"
            if msg["role"] == "user"
            else "ASSISTANT"
        )

        transcript += (
            f"{role}: {msg['content']}\n"
        )

    summary_instructions = """
Résume cette conversation Telegram de façon ULTRA compacte.

Le résumé sert de mémoire permanente à un assistant.

Garde seulement les informations utiles pour continuer logiquement:
- ce que le client veut
- produits/services mentionnés
- prix déjà donnés
- deals proposés
- questions déjà répondues
- préférences du client
- décisions prises
- mode de paiement
- si le client dit avoir envoyé un paiement
- ce qui doit encore être vérifié
- promesses ou choses à faire plus tard
- contexte nécessaire pour comprendre des phrases futures comme
  "combien?", "celle-là", "où ça?", etc.

N'invente RIEN.

Ne supprime pas un fait important contenu dans l'ancien résumé.

Écris très compactement.
Maximum environ 120 mots.
"""

    input_text = f"""
ANCIEN RÉSUMÉ:
{old_summary if old_summary else "Aucun"}

NOUVEAUX MESSAGES À MÉMORISER:
{transcript}
"""

    try:

        response = client.responses.create(
            model=SUMMARY_MODEL,
            instructions=summary_instructions,
            input=input_text,
            max_output_tokens=180
        )

        new_summary = response.output_text.strip()

        if new_summary:

            memory["summary"] = new_summary

            # On garde seulement la partie récente exacte.
            memory["history"] = history[-4:]

            memory["since_summary"] = 0

            print(
                f"Memoire resumee pour {chat_id}",
                flush=True
            )

    except Exception as error:

        # Si le résumé échoue, le bot continue quand même.
        print(
            f"Erreur resume memoire: {error}",
            flush=True
        )


# =========================================================
# OPENAI + MÉMOIRE
# =========================================================

def ask_ai(chat_id, text):

    memory = get_memory(chat_id)

    memory["history"].append({
        "role": "user",
        "content": text
    })

    memory["since_summary"] += 1

    # Résume seulement de temps en temps.
    if memory["since_summary"] >= SUMMARY_EVERY:
        update_summary(chat_id)

    # Après le résumé, récupère la mémoire actualisée.
    memory = get_memory(chat_id)

    history = memory["history"][-SHORT_MEMORY:]

    messages = [
        {
            "role": "system",
            "content": AI_STYLE
        }
    ]

    # Mémoire longue compacte
    if memory["summary"]:

        messages.append({
            "role": "system",
            "content": (
                "MÉMOIRE LONGUE DE CE CLIENT:\n"
                + memory["summary"]
            )
        })

    # Mémoire courte exacte
    messages.extend(history)

    response = client.chat.completions.create(
        model=REPLY_MODEL,
        messages=messages,
        temperature=0.8,

        # Tes réponses sont courtes,
        # donc pas besoin d'autoriser 500 tokens.
        max_tokens=70
    )

    answer = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    memory["history"].append({
        "role": "assistant",
        "content": answer
    })

    # Sécurité: évite qu'un bug fasse grossir
    # l'historique indéfiniment avant le prochain résumé.
    if len(memory["history"]) > 14:
        memory["history"] = memory["history"][-14:]

    return answer


# =========================================================
# DÉLAI NATUREL
# =========================================================

def natural_delay():

    delay = random.choices(
        population=[
            random.randint(3, 6),
            random.randint(7, 12),
            random.randint(13, 20),
            random.randint(21, 30)
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
# ENVOYER MESSAGE TELEGRAM BUSINESS
# =========================================================

def send_business_message(
    chat_id,
    business_connection_id,
    text
):

    response = requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "business_connection_id":
                business_connection_id,
            "chat_id":
                chat_id,
            "text":
                text
        },
        timeout=30
    )

    response.raise_for_status()


# =========================================================
# BOUCLE PRINCIPALE
# =========================================================

def main():

    print(
        "Secretary bot demarre - mode economique.",
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
                    "allowed_updates":
                        '["business_message"]'
                },
                timeout=40
            )

            response.raise_for_status()

            data = response.json()

            for update in data.get(
                "result",
                []
            ):

                offset = (
                    update["update_id"] + 1
                )

                message = update.get(
                    "business_message"
                )

                if not message:
                    continue

                if (
                    message
                    .get("from", {})
                    .get("is_bot")
                ):
                    continue

                text = message.get("text")

                if not text:
                    continue

                chat_id = (
                    message["chat"]["id"]
                )

                business_connection_id = (
                    message[
                        "business_connection_id"
                    ]
                )

                print(
                    f"Message recu: {text}",
                    flush=True
                )

                # Délai humain variable
                natural_delay()

                # Réponse avec mémoire courte
                # + mémoire longue résumée
                answer = ask_ai(
                    chat_id,
                    text
                )

                print(
                    f"Reponse: {answer}",
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
