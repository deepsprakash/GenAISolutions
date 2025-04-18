
# The code is a Gradio web application that generates a company brochure based on the company's name and website URL. It uses two different AI models (Ollama and Gemini) to create the brochure content. The user can select which model to use for generating the brochure. The application fetches the webpage content using BeautifulSoup, processes it, and streams the generated brochure content back to the user in real-time.
# The application is designed to be user-friendly, allowing users to input the company name and website URL easily. The generated brochure is displayed in a Markdown format, making it visually appealing and easy to read.    
# import libraries
import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
import requests
from bs4 import BeautifulSoup

# Load envs from .env file
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
ollama_via_openai = OpenAI(base_url='http://localhost:11434/v1',api_key='ollama')
# set gemini model
gemini_via_openai_client = OpenAI(
    api_key=google_api_key, 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

#set models
ollama_model = "llama3.2"
gemini_model = "gemini-1.5-flash"

# set system prompts for both models
system_prompt = 'You are a helpful AI assistant.You will be given the company name and the website. You are given a task of creating a company brochure about the company projects and achievements. Respond in markdown'
class Website:
    url: str
    title: str
    text: str

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"
    
def stream_ollama(prompt):
    response = ollama_via_openai.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    result = ""
    for chunk in response:
        result += chunk.choices[0].delta.content or ""
        yield result
    
def stream_gemini(prompt):
    response = gemini_via_openai_client.chat.completions.create(
        model=gemini_model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    result = ""
    for chunk in response:
        result += chunk.choices[0].delta.content or ""
        yield result
        
def create_brochure(company, url, model):
    prompt = f"Please generate a company brochure for {company}. Here is their landing page:\n"
    prompt += Website(url).get_contents()
    if model == "ollama":
        response = stream_ollama(prompt)
    elif model == "gemini":
        response = stream_gemini(prompt)
    else:
        raise ValueError("Invalid model selected. Choose either 'ollama' or 'gemini'.")
    yield from response


view = gr.Interface(fn = create_brochure,inputs = ["text", "text", gr.Radio(["ollama", "gemini"], label="Select Model")],
outputs = gr.Markdown(label="Company Brochure"), title="Company Brochure Generator", description="Generate a company brochure using Ollama or Gemini models.")
view.launch()

