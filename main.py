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

REPLY_MODEL = "gpt-4o-mini"
SUMMARY_MODEL = "gpt-5-nano"

SHORT_MEMORY = 8
SUMMARY_EVERY = 6


# =========================================================
# MÉMOIRE
# =========================================================

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
# STYLE
# =========================================================

AI_STYLE = """
COLLE ICI TON AI_STYLE ACTUEL COMPLET
AVEC TON MENU, TES PRIX, INTERAC, QUESTIONS/RÉPONSES, ETC.

Garde toutes tes informations actuelles exactement comme elles sont.


=========================================================
FLIRT / GARDER LA CONVERSATION OUVERTE
=========================================================

Ton objectif est de garder une vibe joueuse, intéressée, chaleureuse
et flirt quand le client flirte.

Quand le client te complimente, te taquine ou pose une question intime:

- Ne le repousse pas inutilement.
- Ne réponds pas automatiquement:
  "nah"
  "non"
  "pas l'vibe"
  "pas envie"
  "je veux pas"
- Évite de fermer la conversation.
- Réponds court.
- Reste taquine et mystérieuse.
- Utilise le français québécois texto.
- Tu peux relancer avec une petite question.
- Utilise parfois 👀 😋 🩷 😂
- Ne transforme pas automatiquement chaque flirt en vente.
- Ne promets pas une rencontre ou une action réelle qui n'est pas prévue.


EXEMPLES:

Client:
"tu dors pas?"

Réponses possibles:
"pas encore hihi😋 toi?"
"non pas encore👀 toi non plus ahah"


Client:
"tu me trouves beau?"

Réponses possibles:
"ahah tu veux vrm savoir toi👀"
"peut etreee😋🩷"


Client:
"tu penses à moi?"

Réponses possibles:
"peut etreee👀😂"
"ahah tes curieux toi🩷"


Client:
"tu te touches?"

Ne réponds PAS:
"nah"
"non"
"pas l'vibe"
"juste relaxer"

Réponds plutôt de manière taquine sans fermer la conversation:

"ahah tes curieux toi👀😋"
"pourquoi tu veux savoir sa toi👀"
"ahah peut etreee😋"


Client:
"tes horny?"

Réponses possibles:
"ahah peut etreee👀🩷"
"tes curieux toi😂👀"


Client:
"tu fais quoi dans ton lit?"

Réponses possibles:
"jchill hihi pourquoi tes curieux👀"
"ahah pourquoi tu veux savoir😋"


=========================================================
RÈGLE IMPORTANTE DE CONVERSATION
=========================================================

Ne réponds pas seulement à la phrase littéralement.

Regarde les derniers messages pour comprendre:
- la vibe
- le sujet actuel
- ce que le client essaie de savoir
- si le client flirte
- ce qu'il voulait acheter
- le prix dont vous parliez

Les réponses doivent sembler faire partie de LA MÊME conversation.

Si une réponse positive, taquine ou mystérieuse permet naturellement
de continuer la conversation, préfère ça à une réponse froide.

Ne répète pas toujours les mêmes formulations.

Retourne uniquement le message à envoyer au client.
"""


# =========================================================
# RÉSUMÉ ÉCONOMIQUE DE LA MÉMOIRE
# =========================================================

def update_summary(chat_id):
    memory = get_memory(chat_id)
    history = memory["history"]

    if len(history) < 6:
        return

    old_summary = memory["summary"]

    # Garde les 4 derniers messages mot pour mot.
    messages_to_summarize = history[:-4]

    if not messages_to_summarize:
        return

    transcript = ""

    for msg in messages_to_summarize:
        role = "CLIENT" if msg["role"] == "user" else "ASSISTANT"
        transcript += f"{role}: {msg['content']}\n"

    summary_instructions = """
Résume cette conversation Telegram de façon ULTRA compacte.

Le résumé sert uniquement de mémoire.

Conserve:
- sujet actuel
- ce que veut le client
- prix déjà mentionnés
- options discutées
- deals proposés
- préférences
- questions déjà répondues
- paiement mentionné
- contexte de flirt utile
- informations nécessaires pour comprendre une réponse courte comme
  "combien?", "celle la", "ou sa?", "oui", "et sa?"

N'invente rien.
Conserve les informations importantes de l'ancien résumé.
Maximum environ 120 mots.
"""

    input_text = f"""
ANCIEN RÉSUMÉ:
{old_summary if old_summary else "Aucun"}

NOUVEAUX MESSAGES:
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
            memory["history"] = history[-4:]
            memory["since_summary"] = 0

            print(
                f"Memoire resumee pour {chat_id}",
                flush=True
            )

    except Exception as error:
        print(
            f"Erreur resume memoire: {error}",
            flush=True
        )


# =========================================================
# OPENAI
# =========================================================

def ask_ai(chat_id, text):
    memory = get_memory(chat_id)

    memory["history"].append({
        "role": "user",
        "content": text
    })

    memory["since_summary"] += 1

    if memory["since_summary"] >= SUMMARY_EVERY:
        update_summary(chat_id)

    memory = get_memory(chat_id)

    history = memory["history"][-SHORT_MEMORY:]

    messages = [
        {
            "role": "system",
            "content": AI_STYLE
        }
    ]

    if memory["summary"]:
        messages.append({
            "role": "system",
            "content":
                "MÉMOIRE LONGUE DE CE CLIENT:\n"
                + memory["summary"]
        })

    messages.extend(history)

    response = client.chat.completions.create(
        model=REPLY_MODEL,
        messages=messages,
        temperature=0.6,
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
        weights=[45, 35, 15, 5],
        k=1
    )[0]

    print(
        f"Attente avant reponse: {delay}s",
        flush=True
    )

    time.sleep(delay)


# =========================================================
# TELEGRAM BUSINESS
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
                    f"Message recu: {text}",
                    flush=True
                )

                natural_delay()

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
                f"ERREUR: {type(error).__name__}: {error}",
                flush=True
            )

            time.sleep(5)


# =========================================================
# DÉMARRAGE
# =========================================================

if __name__ == "__main__":
    main()
