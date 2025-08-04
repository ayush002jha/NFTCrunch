import google.generativeai as genai
import json

def generate_report_summary(api_key: str, wallet_data: dict) -> str:
    """
    Generates a human-readable risk report summary using a more robust prompt.
    """
    if not api_key:
        raise ValueError("Google AI API key is required.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    data_json_string = json.dumps(wallet_data, indent=2)

    prompt = f"""
    You are "Wallet Guardian called NFTCrunch," an expert AI crypto security analyst.
    Your task is to analyze the following JSON data for a cryptocurrency wallet and generate a concise, easy-to-understand "Wallet Health & Risk Report".

    **CRITICAL INSTRUCTIONS:**
    1.  **Prioritize High-Risk Factors:** If you see `"aml_is_sanctioned": true`, this is the MOST IMPORTANT finding. Mention it first in the executive summary with a strong warning.
    2.  **Handle Errors Gracefully:** If any section of the JSON data contains an "error" key (like the 'scores' data might), simply state that "Data for this section could not be retrieved" and move on. Do not mention the technical error details.
    3.  **Interpret "no_data_found":** If the "data" field for a section (like 'washtrade') contains the string "no_data_found", interpret this positively as "No relevant activity was detected."

    **REPORT STRUCTURE:**
    1.  **Executive Summary:** A single paragraph summarizing the wallet's overall risk profile. Lead with any critical warnings (like sanctions).
    2.  **Key Risk Factors:** A bulleted list of specific risks. Mention sanction status, AML risk level, and wash trading. If risks are low, state that clearly.
    3.  **Asset Overview:** Briefly describe the wallet's holdings (NFTs and Tokens). Mention the total number of NFTs and collections from the profile data.

    **Analyze this data:**
    ```json
    {data_json_string}
    ```

    Generate the report in Markdown V2 format. Be direct and clear.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        return "Could not generate an AI summary at this time."