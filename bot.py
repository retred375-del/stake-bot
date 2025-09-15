import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# --- Variables et fichier Excel ---
ASK_PSEUDO = 0
FICHIER_EXCEL = "utilisateurs.xlsx"

def enregistrer_utilisateur(user_id, pseudo, depot):
    """Sauvegarde l'utilisateur dans un fichier Excel"""
    if os.path.exists(FICHIER_EXCEL):
        df = pd.read_excel(FICHIER_EXCEL)
    else:
        df = pd.DataFrame(columns=["user_id", "pseudo", "depot"])

    if user_id in df["user_id"].values:
        df.loc[df["user_id"] == user_id, ["pseudo", "depot"]] = [pseudo, depot]
    else:
        df.loc[len(df)] = [user_id, pseudo, depot]

    df.to_excel(FICHIER_EXCEL, index=False)

# --- Étape d'accueil / menu principal ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎁 Accéder aux bonus", callback_data="start_bonus")],
        [InlineKeyboardButton("❓ J'ai besoin d'aide", web_app=WebAppInfo(url="https://musical-mooncake-272da9.netlify.app/"))],
        [InlineKeyboardButton("⭐ Découvrir les avantages de Stake", web_app=WebAppInfo(url="https://fastidious-belekoy-099b4e.netlify.app/"))]
    ]

    with open("image_stake.png", "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# --- Démarrage du flow Accéder au Bonus ---
async def handle_start_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("✅ Oui", callback_data="yes_account")],
        [InlineKeyboardButton("❌ Non", callback_data="no_account")]
    ]
    await query.message.reply_text(
        "As-tu déjà créé ton compte Stake ? 🎉",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- Gestion du choix "As-tu un compte ?" ---
async def handle_account_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "yes_account":
        await query.message.reply_text("Quel est ton pseudo Stake ? 😎")
        return ASK_PSEUDO
    else:
        keyboard = [
            [InlineKeyboardButton("❓ Tutoriel VPN", web_app=WebAppInfo(url="https://musical-mooncake-272da9.netlify.app/"))],
            [InlineKeyboardButton("✅ Reprendre la procédure", callback_data="restart_procedure")]
        ]
        await query.message.reply_text(
            "Crée ton compte grâce au lien ci-dessous, puis clique sur le bouton pour reprendre la procédure ! 😎\n\n"
            f"👉 [**Crée ton compte !**](https://stake.bet/?offer=lemaxen&c=DEZaLk72) 👈\n\n"
            "⚠️ Si le site ne fonctionne pas, il te suffit d'utiliser un VPN (Canada, Norvège), "
            "n'hésite pas à utiliser le tutoriel grâce au bouton ci-dessous. 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

# --- Demande du pseudo ---
async def ask_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pseudo"] = update.message.text
    keyboard = [
        [InlineKeyboardButton("✅ Oui", callback_data="deposit_yes")],
        [InlineKeyboardButton("❌ Non", callback_data="deposit_no")]
    ]
    await update.message.reply_text(
        "As-tu bien effectué ton dépôt de 20€ minimum ? 💸\n"
        "(Tu reçois ensuite les 30€ en cash, sans aucune condition, ce qui t'assure de gagner au minimum 10€, même si tu perds ton dépôt 😎)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- Gestion du choix "As-tu effectué ton dépôt ?" ---
async def handle_deposit_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pseudo = context.user_data.get("pseudo", "Inconnu")
    depot = "Oui" if query.data == "deposit_yes" else "Non"
    enregistrer_utilisateur(query.from_user.id, pseudo, depot)

    if query.data == "deposit_yes":
        await query.message.reply_text(
            "Tu as sélectionné l'offre : **30€ offerts**. Merci ! ✅\n\n"
            "Nous avons bien enregistré toutes tes réponses. Nous te recontacterons dans un court délai "
            "pour plus amples vérifications ou pour valider l'option précédemment choisie.\n\n"
            "Cordialement,\n"
            "L'équipe La Menace",
            parse_mode="Markdown"
        )
        keyboard = [
            [InlineKeyboardButton("🎁 Profiter du bonus spécial", callback_data="bonus")],
            [InlineKeyboardButton("📝 Modifier mes informations", callback_data="edit_info")]
        ]
        await query.message.reply_text(
            "👇 Choisis une option :",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "deposit_no":
        keyboard = [
            [InlineKeyboardButton("✅ Reprendre la procédure", callback_data="restart_procedure")],
            [InlineKeyboardButton("❓ J'ai besoin d'aide pour dépôt", web_app=WebAppInfo(url="https://musical-mooncake-272da9.netlify.app/"))]
        ]
        await query.message.reply_text(
            "Effectue ton dépôt, et utilise le bouton ci-dessous pour reprendre la procédure. 😎",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# --- Redemander le dépôt ---
async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("✅ Oui", callback_data="deposit_yes")],
        [InlineKeyboardButton("❌ Non", callback_data="deposit_no")]
    ]
    await query.message.reply_text(
        "As-tu bien effectué ton dépôt de 20€ minimum ? 💸\n"
        "(Tu reçois ensuite les 30€ en cash, sans aucune condition, ce qui t'assure de gagner au minimum 10€, même si tu perds ton dépôt 😎)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_edit_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🔄 D'accord ! Quel est ton pseudo Stake ? 😎")

def main():
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_start_bonus, pattern="^start_bonus$")],
        states={
            ASK_PSEUDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_deposit)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(handle_account_choice, pattern="^(yes_account|no_account)$"))
    app.add_handler(CallbackQueryHandler(handle_deposit_choice, pattern="^(deposit_yes|deposit_no)$"))
    app.add_handler(CallbackQueryHandler(handle_edit_info, pattern="^edit_info$"))
    app.add_handler(CallbackQueryHandler(handle_restart, pattern="^restart_procedure$"))

    # --- Utilisation du Webhook sur Render ---
    PORT = int(os.getenv("PORT", 8080))
    WEBHOOK_URL = "https://stake-bot-41sp.onrender.com"  # <<< Ton URL Render ici

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=os.getenv("BOT_TOKEN"),
        webhook_url=f"{WEBHOOK_URL}/{os.getenv('BOT_TOKEN')}"
    )

if __name__ == "__main__":
    main()
