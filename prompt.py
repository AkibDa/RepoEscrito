import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def enhance_prompt(user_prompt, instruction):
    system_message = f"""
    You are a prompt enhancer. 
    Task: Rewrite the user's prompt to follow the instruction.

    User Prompt: {user_prompt}
    Instruction: {instruction}

    Return only the enhanced prompt, nothing else.
    """
    
    response = model.generate_content(system_message)
    return response.text.strip()

# Interactive loop
def main():
    print("🚀 RepoEscrito - Prompt Enhancer (Gemini API)")
    print("Type your prompt below. Type 'exit' to quit.\n")

    while True:
        user_prompt = input("Enter a prompt to enhance (Type 'exit' to exit): ")
        if user_prompt.lower() == "exit":
            print("\n👋 Exiting RepoEscrito. Goodbye!")
            break

        instruction = input("🛠️ How should I enhance it? (e.g., detailed, concise, creative): ")
        enhanced = enhance_prompt(user_prompt, instruction)

        print("\n-----------------------------")
        print(f"📝 Original Prompt: {user_prompt}\n")
        print(f"📋 Instruction: {instruction}\n")
        print(f"✨ Enhanced Prompt: {enhanced}")
        print("-----------------------------\n")

if __name__ == "__main__":
    main()
