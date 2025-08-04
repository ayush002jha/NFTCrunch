import os
import re
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


def sanitize_markdown_v2(text: str) -> str:
    """Escapes characters for Telegram's MarkdownV2 parser."""
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Welcome to *Wallet Guardian Bot*\\! 🛡️\n\n"
        "I am an AI\\-powered security analyst for your crypto wallets\\. "
        "I use bitsCrunch's powerful APIs to provide a comprehensive health and risk report\\.\n\n"
        "To get started, use the command:\n"
        "`/check_wallet <your_wallet_address>`\n\n"
        "Example:\n"
        "`/check_wallet 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B`"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN_V2)

async def check_wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Please provide a wallet address\\. \nUsage: `/check_wallet <address>`", parse_mode=ParseMode.MARKDOWN_V2)
        return

    wallet_address = args[0]
    if not (wallet_address.startswith("0x") and len(wallet_address) == 42):
        await update.message.reply_text("That doesn't look like a valid wallet address\\. Please check and try again\\.", parse_mode=ParseMode.MARKDOWN_V2)
        return

    processing_message = await update.message.reply_text(f"🔍 Analyzing wallet `{wallet_address}`\\.\\.\\. This might take a moment\\.", parse_mode=ParseMode.MARKDOWN_V2)

    try:
        wallet_data = await get_all_wallet_data(BITSCRUNCH_API_KEY, wallet_address)
        
        print("--- Raw API Data ---")
        print(json.dumps(wallet_data, indent=2))
        print("--------------------")

        ai_summary = generate_report_summary(GOOGLE_AI_API_KEY, wallet_data)
        
        # Build the report using f-strings
        header = f"🛡️ *Wallet Health & Risk Report for:*\n`{wallet_address}`\n\n"
        
        # Start building the quick data points section
        quick_data_points = "\n---\n📊 *Quick Data Points*:\n"
        
        profile_data = wallet_data.get('profile', {}).get('data', [])
        if profile_data:
            profile = profile_data[0] # Use the first profile item
            sanctioned = "🔴 Yes" if profile.get('aml_is_sanctioned') else "🟢 No"
            risk_level = profile.get('aml_risk_level', 'N/A')
            
            classifications = []
            if profile.get('is_whale'): classifications.append("Whale")
            if profile.get('is_shark'): classifications.append("Shark")
            if profile.get('is_custodial'): classifications.append("Custodial")
            classification_str = ", ".join(classifications) if classifications else "None"

            quick_data_points += f"\\- *Sanctioned:* {sanctioned}\n"
            quick_data_points += f"\\- *AML Risk Level:* `{risk_level}`\n"
            quick_data_points += f"\\- *Holder Type:* {classification_str}\n"
        else:
            quick_data_points += "\\- *Profile Data:* `Not Available`\n"

        # Combine all parts of the report
        final_report = header + ai_summary + quick_data_points + "\n_Powered by bitsCrunch & Google AI_"

        # Sanitize the entire message before sending
        safe_report = sanitize_markdown_v2(final_report)

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=processing_message.message_id,
            text=safe_report,
            parse_mode=ParseMode.MARKDOWN_V2
        )

    except Exception as e:
        print(f"An error occurred in check_wallet_command: {e}")
        error_message = sanitize_markdown_v2("Sorry, a critical error occurred. Please check the console for details.")
        await context.bot.edit_message_text(
             chat_id=update.effective_chat.id,
             message_id=processing_message.message_id,
             text=error_message,
             parse_mode=ParseMode.MARKDOWN_V2
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