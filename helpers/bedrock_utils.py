import boto3
import json


client = boto3.client("bedrock-runtime", region_name="eu-central-1")

def generate_answer(user_goal,data):
    global messages
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    # Add user message
    system_prompt = f"""
        You are responsible for writing messages that will be sent to the end user via chat.
        You are given an answer or a set of data, and your task is to return a **well-formatted, user-friendly message** based on this information.
        You must return an object in the following format:
        {{
            "text": "your message here"
        }}

        The data of the message to be rewrote:
        -USER REQUEST GOAL: {user_goal}
        -RESULT: {str(data)}
        Please ensure the message is clear, concise, and directly answers the user's request.
        The output must be a valid JSON string.
        New lines are represented with '\\n'
        """
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "system":system_prompt,
        "messages": [
           
            {"role": "user", "content": str(data)}
        ],
        "max_tokens": 512,
        "temperature": 0.4
    }
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body)
    )
    response_body = json.loads(response["body"].read())
    output = response_body["results"] if "results" in response_body else response_body
    output = output['content'][0]['text']
    try:
        json_output= json.loads(output)
    except Exception as e:
        try:
            json_output= json.loads(output[output.find("{"):output.rfind("}")+1])
        except Exception as e:
            print(output)
            raise Exception("Could not conver into JSON")
    
    return json_output['text']

def format_knowledge_response(user_question,chunks):
 
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    # Add user message
    system_prompt = f"""
        You are responsible for writing messages that will be sent to the end user via chat.
        You are given a set of chunks retrieved from a knowledge base.
        Your task is to return a **well-formatted, user-friendly message** based on this information.
        You must return an object in the following format:
        {{
            "text": "your message here"
        }}

        The chunks retrieved from the knowledge db are:
        {chunks}
        Please ensure the message is clear, concise, and directly answers the user's question.
        The output must be a vaedlid JSON string.
        New lines are represented with '\\n'
        """
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "system":system_prompt,
        "messages": [
           
            {"role": "user", "content": f"The user asked: {user_question}"}
        ],
        "max_tokens": 512,
        "temperature": 0.4
    }
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body)
    )
    response_body = json.loads(response["body"].read())
    output = response_body["results"] if "results" in response_body else response_body
    output = output['content'][0]['text']
    try:
        json_output= json.loads(output)
    except Exception as e:
        try:
            json_output= json.loads(output[output.find("{"):output.rfind("}")+1])
        except Exception as e:
            print(output)
            raise Exception("Could not conver into JSON")
    
    return json_output['text']

br_agent = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime/client/retrieve_and_generate.html#
def query_knowledge_db(query):
    knowledge_base_id = "TVD6QFV2G7"
    query = "What are your products?"
    # model_arn = "your_model_arn"
    # "modelArn": model_arn,
    response = br_agent.retrieve(
    knowledgeBaseId=knowledge_base_id,
    retrievalQuery={"text": query}
    )
    references = [item['location']['s3Location']['uri'] for item in response['retrievalResults']]
    content = '\n'.join([item['content']['text'] for item in response['retrievalResults']])
    formatted_response = format_knowledge_response(query,content)
    print(f"[BOT]{formatted_response}")
    print(f'References: {references}')
    return {
        'response':formatted_response,
        'references':references
    }


def ask_bedrock(system_prompt,user_prompt):
    
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "system":system_prompt,
        "messages": [ 
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body)
    )
    response_body = json.loads(response["body"].read())
    output = response_body["output_text"] if "output_text" in response_body else response_body
    output = output['content'][0]['text']
    try:
        json_output= json.loads(output)
    except Exception as e:
        try:
            json_output= json.loads(output[output.find("{"):output.rfind("}")+1])
        except Exception as e:
            print(output)
            raise Exception("Could not conver into JSON")
    return json_output




def summarize_chat(messages,entities,summary,user_message):
    
    messages = [item['content'] for item in messages]
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    # Add user message
    system_prompt = f"""
        You're responsible and an expert in summarize long context messages chat between a user and an AI agent.
        Your goal is to create a short summary from the given conversation.
        The goal of the summarize is to focus on:
        - last user intent/objective
        - important fields provided by the user
        - ignore old user goals/intents
        The chat history is:
        {messages}
        
        Previously stored entities:
        {entities}
        
        The previously generated summary is:
        {summary}
        Return a response as JSON string:
        {{
            'user_goal':'user_goal',
            'summary':'summary_text'
        }}
        
        - New lines must be given as '\\n'
        
        
        
        """
  
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "system":system_prompt,
        "messages": [
           
            {"role": "user", "content": f"The user new message is: {user_message}"}
        ],
        "max_tokens": 512,
        "temperature": 0.4
    }
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body)
    )
    response_body = json.loads(response["body"].read())
    output = response_body["results"] if "results" in response_body else response_body
    output = output['content'][0]['text']
    try:
        json_output= json.loads(output)
    except Exception as e:
        try:
            json_output= json.loads(output[output.find("{"):output.rfind("}")+1])
        except Exception as e:
            print(output)
            raise Exception("Could not conver into JSON")
    
    return json_output
