import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Use Bedrock runtime client
bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION"))

def answer_question(question, context):
    prompt = f"""
Human: Use the following extracted document content to answer the question.

Context:
---------
{context}
---------

Question: {question}
Assistant:"""

    body = {
        "prompt": prompt,
        "max_tokens_to_sample": 500,
        "temperature": 0.2,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman:"]
    }

    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",  # You can change to claude-3-sonnet or titan
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())
    return response_body.get("completion", "No answer found.")
