
import os
import json
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from telegram.request import HTTPXRequest

from bitscrunch_api import get_all_wallet_data
from ai_summarizer import generate_report_summary

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BITSCRUNCH_API_KEY = os.getenv("BITSCRUNCH_API_KEY")
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command or any text is received."""
    welcome_text = (
        "*Welcome to Wallet Guardian Bot!* 🛡️\n\n"
        "I am an AI-powered security analyst for your crypto wallets. "
        "I use bitsCrunch's powerful APIs to provide a comprehensive health and risk report.\n\n"
        "To get started, simply send me a wallet address, or use the command:\n"
        "`/check_wallet <your_wallet_address>`\n\n"
        "*Example:*\n"
        "`0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B`"
    )
    # Using ParseMode.MARKDOWN (V1)
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)


async def handle_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles direct messages that look like a wallet address."""
    wallet_address = update.message.text
    if not (wallet_address.startswith("0x") and len(wallet_address) == 42):
        # If it's not a wallet address, show the welcome message
        await start_command(update, context)
        return
    
    # It looks like a wallet address, so we'll run the check
    context.args = [wallet_address]
    await check_wallet_command(update, context)


async def check_wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """The main function to check a wallet and generate a report."""
    if not context.args:
        await update.message.reply_text("Please provide a wallet address.\n*Usage:* `/check_wallet <address>`", parse_mode=ParseMode.MARKDOWN)
        return

    wallet_address = context.args[0]
    
    processing_message = await update.message.reply_text(f"🔍 Analyzing wallet `{wallet_address}`... This might take a moment.", parse_mode=ParseMode.MARKDOWN)

    try:
        wallet_data = await get_all_wallet_data(BITSCRUNCH_API_KEY, wallet_address)
        
        print("--- Raw API Data ---")
        print(json.dumps(wallet_data, indent=2))
        print("--------------------")

        ai_summary = generate_report_summary(GOOGLE_AI_API_KEY, wallet_data)
        
        # Build the final report using Markdown V1 syntax
        final_report = f"🛡️ *Wallet Health & Risk Report for:*\n`{wallet_address}`\n\n"
        final_report += f"{ai_summary}\n\n"
        final_report += "---\n"
        
        final_report += "📊 *Quick Data Points*:\n"
        
        profile_data = wallet_data.get('profile', {}).get('data', [])
        if profile_data:
            profile = profile_data[0]
            sanctioned = "🔴 Yes" if profile.get('aml_is_sanctioned') else "🟢 No"
            risk_level = profile.get('aml_risk_level', 'N/A')
            
            classifications = []
            if profile.get('is_whale'): classifications.append("Whale")
            if profile.get('is_shark'): classifications.append("Shark")
            if profile.get('is_custodial'): classifications.append("Custodial")
            classification_str = ", ".join(classifications) if classifications else "None"

            final_report += f"- *Sanctioned:* {sanctioned}\n"
            final_report += f"- *AML Risk Level:* `{risk_level}`\n"
            final_report += f"- *Holder Type:* {classification_str}\n"
        else:
            final_report += "- *Profile Data:* Not Available\n"
        
        final_report += "\n_Powered by bitsCrunch & Google AI_"

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_message.message_id,
            text=final_report,
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        print(f"An error occurred in check_wallet_command: {e}")
        await context.bot.edit_message_text(
             chat_id=update.effective_chat.id,
             message_id=processing_message.message_id,
             text="Sorry, a critical error occurred. Please check the console for details."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

def main():
    print("Starting NFTCrunch - Wallet Guardian Bot...")
    if not all([TELEGRAM_BOT_TOKEN, BITSCRUNCH_API_KEY, GOOGLE_AI_API_KEY]):
        print("FATAL ERROR: One or more environment variables are missing.")
        return

    request = HTTPXRequest(connect_timeout=20.0, read_timeout=20.0, write_timeout=20.0)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).request(request).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("check_wallet", check_wallet_command))
    
    # ADDED: Handler for any non-command text message
    # It will first check if the message is a wallet address, otherwise it shows the help text.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet_address))

    application.add_error_handler(error_handler)
    
    print("Bot is now polling for updates...")
    application.run_polling()

if __name__ == '__main__':
    main()