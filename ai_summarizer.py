import google.generativeai as genai
import json

def generate_report_summary(api_key: str, wallet_data: dict) -> str:
    """
    Generates a human-readable risk report summary using Google's Gemini AI.
    """
    if not api_key:
        raise ValueError("Google AI API key is required.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash') # Use the fast and efficient model

    # Convert the dictionary to a JSON string for a cleaner prompt
    data_json_string = json.dumps(wallet_data, indent=2)

    prompt = f"""
    You are "Wallet Guardian called NFTCrunch," an expert AI crypto security analyst.
    Your task is to analyze the following JSON data for a cryptocurrency wallet and generate a concise, easy-to-understand "Wallet Health & Risk Report".

    The report should have three sections:
    1.  **Executive Summary:** A single paragraph summarizing the wallet's overall risk profile. Mention the most critical findings immediately.
    2.  **Key Risk Factors:** A bulleted list highlighting specific risks. Look for things like high-risk scores, scam labels, wash trading activity, or associations with sanctioned entities. If there are no major risks, state that the wallet appears to be low-risk.
    3.  **Asset Overview:** Briefly describe the wallet's holdings (NFTs and Tokens) based on the provided data.

    Analyze this data:
    ```json
    {data_json_string}
    ```

    Generate the report now in Markdown format. Be direct and clear.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        return "Could not generate an AI summary at this time."