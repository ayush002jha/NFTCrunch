import google.generativeai as genai
import json

def generate_report_summary(api_key: str, wallet_data: dict) -> str:
    """
    Generates a human-readable risk report using a fine-tuned prompt for standard Markdown.
    """
    if not api_key:
        raise ValueError("Google AI API key is required.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    data_json_string = json.dumps(wallet_data, indent=2)

    prompt = f"""
    You are "Wallet Guardian," an expert AI crypto security analyst.
    Analyze the provided JSON data and generate a "Wallet Health & Risk Report".

    **CRITICAL INSTRUCTIONS:**
    - Use standard Markdown (V1) for formatting. Use asterisks for bold (*text*) and hyphens for bullet points (- text).
    - If `"aml_is_sanctioned": true`, it is the most critical finding. Start the executive summary with a strong warning like **WARNING: This wallet is flagged as sanctioned.**
    - If data for a section is missing or contains an error, state that the information was "unavailable" or "could not be retrieved". Do not mention technical errors.
    - If wash trade data is "no_data_found", report it as "No relevant wash trading activity was detected."

    **REPORT STRUCTURE & CONTENT:**
    
    ***Executive Summary:***
    A concise paragraph summarizing the wallet's risk profile. Lead with any critical warnings. Mention the overall holdings (NFTs, tokens) and any other significant findings like wash trading.

    ***Key Risk Factors:***
    A bulleted list.
    - *Sanctioned:* State clearly if the wallet is flagged as sanctioned.
    - *AML Risk Level:* Report the AML risk level. If it's just a number, state that "The meaning of this specific level requires additional context".
    - *Wash Trading:* State whether any wash trading activity was detected.

    ***Asset Overview:***
    A paragraph summarizing the assets. Use the `nft_count` and `collection_count` from the profile data. Mention the total number of different tokens from the token balance pagination. Note that the actual value of many assets may be unavailable from the provided data.

    **Analyze this data:**
    ```json
    {data_json_string}
    ```

    Generate only the content for the three sections described above.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        return "An AI-powered summary could not be generated at this time."