import google.generativeai as genai
import json

def generate_report_summary(api_key: str, wallet_data: dict) -> str:
    """
    Generates a concise, analytical risk report using a "Risk Engine" AI persona.
    """
    if not api_key:
        raise ValueError("Google AI API key is required.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    data_json_string = json.dumps(wallet_data, indent=2)

    prompt = f"""
    You are a concise AI Wallet Risk Engine. Your sole purpose is to analyze the provided JSON data and produce a brief, scannable risk report.

    **CRITICAL OUTPUT RULES:**
    1.  Use standard Markdown for formatting (*bold*, _italic_, `code`).
    2.  Your entire response MUST follow this exact structure:
        - A single-sentence "Overall Risk Verdict".
        - A section header: "*Key Findings (6 Points):*".
        - Exactly six bulleted key points, each starting with an emoji and a bolded title.
    3.  Analyze the data to provide insights, not just repeat values.

    **ANALYSIS INSTRUCTIONS FOR KEY POINTS:**
    - **Sanction Status:** If `aml_is_sanctioned` is true, this is a CRITICAL risk.
    - **AML Risk:** Use the `aml_risk_level`. A higher number indicates higher risk.
    - **Holder Profile:** Note if the wallet is a `Whale` or `Shark`, as their activity can influence markets.
    - **Wash Trading:** Check the `washtrade` section. "no_data_found" means no wash trading was detected.
    - **Asset Concentration:** Report the `nft_count` and `collection_count` from the profile. High numbers in a single wallet can be a risk factor.
    - **Potential Profitability:** Use `realized_profit` from the `scores` data. If unavailable, state that.

    **Analyze this JSON data:**
    ```json
    {data_json_string}
    ```

    **PRODUCE THE REPORT NOW FOLLOWING ALL RULES.**
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        return "An AI-powered summary could not be generated at this time."