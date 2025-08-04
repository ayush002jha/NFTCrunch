import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

from bitscrunch_api import get_all_wallet_data
from ai_summarizer import generate_report_summary

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BITSCRUNCH_API_KEY = os.getenv("BITSCRUNCH_API_KEY")
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

# --- Bot Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
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
    """Handles the /check_wallet command to generate a report."""
    args = context.args
    if not args:
        await update.message.reply_text("Please provide a wallet address. \nUsage: `/check_wallet <address>`", parse_mode=ParseMode.MARKDOWN)
        return

    wallet_address = args[0]

    # Simple validation for an Ethereum-like address
    if not (wallet_address.startswith("0x") and len(wallet_address) == 42):
        await update.message.reply_text("That doesn't look like a valid wallet address. Please check and try again.")
        return

    # Let the user know the bot is working
    processing_message = await update.message.reply_text(f"🔍 Analyzing wallet `{wallet_address}`... This might take a moment.", parse_mode=ParseMode.MARKDOWN)

    try:
        # Fetch all data concurrently
        wallet_data = await get_all_wallet_data(BITSCRUNCH_API_KEY, wallet_address)

        # Generate the AI summary
        ai_summary = generate_report_summary(GOOGLE_AI_API_KEY, wallet_data)
        
        # --- Format the final report ---
        final_report = f"🛡️ **Wallet Health & Risk Report for:**\n`{wallet_address}`\n\n"
        final_report += f"{ai_summary}\n\n"
        final_report += "--- \n"
        
        # Add a quick data summary
        risk_score = wallet_data.get('score', {}).get('data', [{}])[0].get('risk_score', 'N/A')
        final_report += f"📊 **Quick Data Points**:\n"
        final_report += f"- **Overall Risk Score:** `{risk_score}`\n"
        
        labels_data = wallet_data.get('labels', {}).get('data', [])
        labels = [label['label'] for label in labels_data] if labels_data else ["None"]
        final_report += f"- **Identified Labels:** `{', '.join(labels)}`\n"
        
        final_report += "\n*Powered by bitsCrunch & Google AI*"

        # Edit the "processing" message to show the final report
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
             text="Sorry, an error occurred while generating the report. Please try again later."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log the error for debugging."""
    print(f"Update {update} caused error {context.error}")


def main():
    """Start the bot."""
    print("Starting Wallet Guardian Bot...")

    # Basic validation for credentials
    if not all([TELEGRAM_BOT_TOKEN, BITSCRUNCH_API_KEY, GOOGLE_AI_API_KEY]):
        print("FATAL ERROR: One or more environment variables are missing.")
        print("Please check your .env file.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("check_wallet", check_wallet_command))

    # Register an error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling()


if __name__ == '__main__':
    main()