# Simple Azure OpenAI agent using LangChain
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from progress.observability import Observability
load_dotenv()

local_api_key = os.getenv("OBSERVABILITY_LOCAL_API_KEY")
local_endpoint = os.getenv("OBSERVABILITY_LOCAL_ENDPOINT")
staging_endpoint = os.getenv("OBSERVABILITY_ENDPOINT")
api_key = os.getenv("OBSERVABILITY_API_KEY")
app_id = os.getenv("APP_ID", "default")

Observability.instrument(
    app_name=f"azure-langchain-python-example-{app_id}",
    api_key=local_api_key,
    endpoint=local_endpoint,
)

model = "gpt-4o-mini"
llm = AzureChatOpenAI(
    azure_deployment=model,
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_API_ENDPOINT"),
    api_key=os.getenv("AZURE_API_KEY"),
    temperature=0.7
)

system_prompt = "You are a helpful assistant that answers questions accurately and concisely."
question = "What is the capital of Bulgaria?"

print(f"Question: {question}\n")

# Create messages
messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=question)
]

response = llm.invoke(messages)
print(f"Answer: {response.content}")
