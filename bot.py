import os
import json
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from telegram.request import HTTPXRequest

from bitscrunch_api import get_all_wallet_data
from ai_summarizer import generate_report_summary

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BITSCRUNCH_API_KEY = os.getenv("BITSCRUNCH_API_KEY")
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

# --- Bot Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Welcome to **Wallet Guardian Bot**! 🛡️\n\n"
        "I am an AI-powered security analyst for your crypto wallets. "
        "I use bitsCrunch's powerful APIs to provide a comprehensive health and risk report.\n\n"
        "To get started, use the command:\n"
        "`/check_wallet <your_wallet_address>`\n\n"
        "Example:\n"
        "`/check_wallet 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B`"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def check_wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Please provide a wallet address. \nUsage: `/check_wallet <address>`", parse_mode=ParseMode.MARKDOWN)
        return

    wallet_address = args[0]
    if not (wallet_address.startswith("0x") and len(wallet_address) == 42):
        await update.message.reply_text("That doesn't look like a valid wallet address. Please check and try again.")
        return

    processing_message = await update.message.reply_text(f"🔍 Analyzing wallet `{wallet_address}`... This might take a moment.", parse_mode=ParseMode.MARKDOWN)

    try:
        wallet_data = await get_all_wallet_data(BITSCRUNCH_API_KEY, wallet_address)
        
        # Log the raw data for debugging purposes
        print("--- Raw API Data ---")
        print(json.dumps(wallet_data, indent=2))
        print("--------------------")

        ai_summary = generate_report_summary(GOOGLE_AI_API_KEY, wallet_data)
        
        final_report = f"🛡️ **Wallet Health & Risk Report for:**\n`{wallet_address}`\n\n"
        final_report += f"{ai_summary}\n\n"
        final_report += "--- \n"
        
        final_report += f"📊 **Quick Data Points**:\n"
        
        # Correctly parse the new data structure from the API
        scores_data = wallet_data.get('scores', {}).get('data', [])
        if scores_data:
            portfolio_value = scores_data[0].get('portfolio_value', 'N/A')
            realized_profit = scores_data[0].get('realized_profit', 'N/A')
            final_report += f"- **Portfolio Value:** `{portfolio_value}`\n"
            final_report += f"- **Realized Profit:** `{realized_profit}`\n"
        else:
            final_report += "- **Portfolio Value:** `Not Available`\n"

        profile_data = wallet_data.get('profile', {}).get('data', [])
        if profile_data:
            notable_holder = profile_data[0].get('notable_holder_classification', ["None"])
            final_report += f"- **Holder Classification:** `{', '.join(notable_holder)}`\n"
        else:
            final_report += "- **Holder Classification:** `Not Available`\n"
        
        final_report += "\n*Powered by bitsCrunch & Google AI*"

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
             text="Sorry, an error occurred while generating the report. Please check the console for details."
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
    application.add_error_handler(error_handler)
    
    print("Bot is now polling for updates...")
    application.run_polling()

if __name__ == '__main__':
    main()