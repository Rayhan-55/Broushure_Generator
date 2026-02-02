!ollama pull llama3.2:1b
import requests
requests.get("http://localhost:11434").content

from openai import OpenAI
OLLAMA_BASE_URL="http://localhost:11434/v1"
ollama=OpenAI(base_url=OLLAMA_BASE_URL,api_key='ollama')

response=ollama.chat.completions.create(model="llama3.2:1b",messages=[{"role":"user","content":"Tell me the capital of bd"}])
response.choices[0].message.content