# imports
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display, update_display
from openai import OpenAI

# constants

MODEL_GPT = 'gpt-4o-mini'
MODEL_LLAMA = 'llama3.2'
# set up environment
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Check the key

if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")

openai = OpenAI()
ollama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
# here is the question; type over this to ask something new

question = """
Please explain what this code does and why:
yield from {book.get("author") for book in books if book.get("author")}
"""

system_prompt = """
You are a helpful assistant to explain python codes. Include thourough explanations to the queries asked. Respond with \
markdown
"""

user_prompt = f"Please explain what this code does :{question}"
# Get gpt-4o-mini to answer, with streaming
def stream_coderesponse():
    stream = ollama_via_openai.chat.completions.create(
        model = MODEL_LLAMA,
        messages = [
            {'role':'system', 'content':system_prompt},
            {'role': 'user', 'content':user_prompt}],        
         stream = True
    )
    response = ""
    display_handle = display(Markdown(""), display_id=True)
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        response = response.replace("```","").replace("markdown", "")
        update_display(Markdown(response), display_id=display_handle.display_id)
            
        
    
# Get Llama 3.2 to answer
stream_coderesponse()