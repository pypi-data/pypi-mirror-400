from google import genai
from google.genai import types

def gemini_generate_code(api_key, previous_code, instructions):
    # 1. Initialize the Client
    # The new SDK uses a centralized client for all model interactions
    client = genai.Client(api_key=api_key)
    
    # 2. Create the prompt
    prompt = f"""
    CONTEXT (Existing Notebook Code):
    {previous_code}

    INSTRUCTIONS for New Cell:
    {instructions}
    
    Code:
    """

    # 3. Generate content
    # Note: System instructions are now passed inside the config argument
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an assistant that writes Python code for Jupyter cells. "
                               "Return ONLY the code, no markdown formatting or explanations."
        )
    )

    # 4. Process the response
    # We need to strip the ```python ` and trailing ```
    # There is no simple way to get gemini not add this :-) 
    code = response.text
    if code.startswith("```python"):
        code = code[len("```python"):].strip()
    if code.endswith("```"):
        code = code[:-3].strip()
    return code

# Usage
# new_code = generate_notebook_cell(api_key, previous_code, "Plot a sine wave with numpy")
