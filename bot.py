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
    """Sends a welcome message."""
    welcome_text = (
        "*Welcome to Wallet Guardian Bot!* 🛡️\n\n"
        "I provide brief, AI-powered risk reports for any crypto wallet.\n\n"
        "To start, just send me a wallet address.\n\n"
        "*Example:*\n"
        "`0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B`"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def handle_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles direct messages that look like a wallet address."""
    wallet_address = update.message.text
    if not (wallet_address.startswith("0x") and len(wallet_address) == 42):
        await start_command(update, context) # Show help if not a valid address format
        return
    
    context.args = [wallet_address]
    await check_wallet_command(update, context)

async def check_wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """The main function to check a wallet and generate a report."""
    if not context.args:
        await update.message.reply_text("Please provide a wallet address.", parse_mode=ParseMode.MARKDOWN)
        return

    wallet_address = context.args[0]
    
    processing_message = await update.message.reply_text(f"🔍 Analyzing `{wallet_address}`...", parse_mode=ParseMode.MARKDOWN)

    try:
        wallet_data = await get_all_wallet_data(BITSCRUNCH_API_KEY, wallet_address)
        
        print("--- Raw API Data ---")
        print(json.dumps(wallet_data, indent=2))
        print("--------------------")

        ai_summary = generate_report_summary(GOOGLE_AI_API_KEY, wallet_data)
        
        # The AI now generates the entire formatted report.
        header = f"🛡️ *Wallet Risk Report for:*\n`{wallet_address}`\n\n"
        final_report = header + ai_summary + "\n\n_Powered by bitsCrunch & Google AI_"

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
    print("Starting Wallet Guardian Bot...")
    if not all([TELEGRAM_BOT_TOKEN, BITSCRUNCH_API_KEY, GOOGLE_AI_API_KEY]):
        print("FATAL ERROR: One or more environment variables are missing.")
        return

    request = HTTPXRequest(connect_timeout=20.0, read_timeout=20.0, write_timeout=20.0)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).request(request).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("check_wallet", check_wallet_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet_address))
    application.add_error_handler(error_handler)
    
    print("Bot is now polling for updates...")
    application.run_polling()

if __name__ == '__main__':
    main()