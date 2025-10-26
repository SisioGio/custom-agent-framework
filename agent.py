import boto3
import json
import json
import datetime
from tools.invoke import process_tool
from helpers.bedrock_utils import ask_bedrock,generate_answer,query_knowledge_db,summarize_chat
from typing import Type
import logging
from prompts import summarizer_prompt,prompt_messager,prompt_planner,knowledge_prompt
from llm.super_llm import LLM



class Agent():
    def __init__(self,instructions,rules,knowledge_schema,tools_schema,entities,role,responsible_for):
        self.instructions = instructions
        self.rules = rules
        self.tools_schema = tools_schema
        self.knowledge_schema = knowledge_schema
        self.messages = []             
        self.current_plan = None           
        self.current_step = None          
        self.conversation_variable = {}  
        self.current_goal = None
        self.today = datetime.datetime.today()
        self.summary = None
        self.entities = entities
        self.cost = 0
        self.user_msg = None
        self.role = role
        self.responsible_for=responsible_for
        self.variables = {}
        self.logger = logging.getLogger("MAIN")
        
    def set_planner(self,llm:LLM):
        self.planner = llm
        
    def set_answer_generator(self,llm:LLM):
        self.generator = llm
        
    def set_summarizer(self,llm:LLM):
        self.summarizer = llm
    
    def summarize_chat(self):
        prompt = self.generate_summary_prompt()
        user_msg = self.messages[-1]['content']
        response = self.invoke_llm(prompt,user_msg)
        self.summary = response['summary']
        self.current_goal = response['user_goal']
        self.logger.info(f'[USER_INTENT] {self.current_goal}')
            
    def create_plan(self):
        system_prompt = prompt_planner(self.role,self.responsible_for,self.instructions,self.tools_schema,self.knowledge_schema,self.entities,self.today,self.summary,self.current_goal)
        response = self.invoke_llm(system_prompt,self.user_msg)
        self.plan = response['plan']
        self.current_goal  = response['user_goal']
        self.add_message("assistant", response)
        self.save_entities(response)
        return response 
    
    def save_entities(self,plan_response):
        if 'entities' in plan_response:
            entities = plan_response['entities']
            for key in entities:
                index = next((i for i, item in enumerate(self.entities) if item['name'] == key), None)
                
                if index>=0:
                    self.logger.info(f"Updating entity '{key}':{entities[key]}")
                    entity_obj = self.entities[index]
                    entity_obj['value'] = entities[key]
                    self.entities[index] = entity_obj
                else:
                    self.logger.info(f"Creating new entity '{key}':{entities[key]}")
                    self.entities.append({
                        'name':key,
                        'value':entities[key]
                    })
              
    def on_user_input(self,text):
        # Store message
        self.user_msg = text
        self.add_message("user",text)
        # Summarize chat content (avoid when <2 messages)
        self.summarize_chat()
        self.create_plan()
        self.process_plan()
          
    def generate_summary_prompt(self):
        messages = [f"{item['role']} : {item['content']}" for item in self.messages]
        entities = self.entities
        summary =self.summary
        # Add user message
        prompt = summarizer_prompt(messages,entities,summary)
        return prompt

    def invoke_llm(self,system_prompt,input):
        response,cost = self.summarizer.send_request(system_prompt=system_prompt,input_text=input)
        self.add_cost(cost)
        return response

    def add_cost(self,cost):
        self.cost =  (self.cost + cost) if cost != None else self.cost
        self.logger.info(f"New total cost {self.cost} USD")
    
    def direct_answer(self,step):
        output_text = step['content']
        self.render_message(output_text)
        
    def ask_question(self,step):
        output_text = step['question']
        self.render_message(output_text)
    
    def fetch_variables(self,step):
        step_args = step['arguments']
        for key in step_args.keys():
            if key in self.variables:
                step['arguments'][key] = self.variables[key]
        return step
    
    def save_variable(self,step,output):
        output_name = step['output'] if 'output' in step else None
        if output_name:
            self.variables[output_name] = output
        
    def generate_answer(self,current_goal,raw_data):
        prompt = prompt_messager(raw_data)
        response = self.invoke_llm(prompt,current_goal)
        self.add_message('assistant',response['text'])
        
    def render_output_tool(self,tool_output):
        message_to_user = self.generate_answer(self.current_goal,tool_output)
        self.render_message(message_to_user)
        
    def execute_tool(self,step,plan_variables):
        # Use stored variables in current tool (if required)
        step = self.fetch_variables(step)
        # Execute tool
        tool_output = process_tool(step)
        # Save variables to agent
        output_name= self.save_variable(step,tool_output)
        # Share with user (if required)
        if step['share_with_user']:
            self.render_output_tool(tool_output)
        else:
            # Store agent message
            self.add_message('assistant',f"{output_name} = {tool_output}")
            
    def format_knowledge_response(self,query,results):
        prompt = knowledge_prompt(results)
        response = self.invoke_llm(prompt,f"The user question is: {query}")
        return response['text']
    
    def query_knowledge_db(self,query):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime/client/retrieve_and_generate.html#
        br_agent = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
        knowledge_base_id = "TVD6QFV2G7"
        response = br_agent.retrieve(
                knowledgeBaseId=knowledge_base_id,
                retrievalQuery={"text": query},
                
        )
        # Min score for references
        reference_min_score = 0.5
        
        references = [item['location']['s3Location']['uri'] for item in response['retrievalResults'] if item['score']>reference_min_score]
        if len(references)==0:
            content = 'Your internal knowledge might not have this information in the system or the user needs to be more specific'
        else:
            content = '\n'.join([item['content']['text'] for item in response['retrievalResults']])
        formatted_response = self.format_knowledge_response(query,content)
        return formatted_response,references
    
    def ask_knowledge(self,step):
        query = step['question']
        metadata= step['metadata']
        query = f"{query} ({metadata})"
        response,references = self.query_knowledge_db(query)
        self.render_message(response)
        return response
              
    def process_plan(self):
        plan = self.plan
        plan_variables = {}
        try:
            for step in plan:
                if step['type'] == 'direct_answer':
                    self.direct_answer(step)
                    return
                elif step['type'] == 'question':
                    self.ask_question(step)
                    return
                elif step['type'] == 'tool':
                    self.execute_tool(step,plan_variables)
                elif step['type'] =='knowledge':
                    self.ask_knowledge(step)
                else:
                    raise Exception(f"Invalid tool type: {step['type']}")
            
        except Exception as e:
            self.logger.error(f"Exception: {e}")
            message_to_user = self.generate_answer(self.current_goal,f'While executing the step {step['type']} the following error occurred: {e}')
            self.render_message(message_to_user)

    def add_message(self,role,message):
        self.messages.append({
            'role':role,
            'content':message
        })

    def render_message(self,message):
        self.add_message("assistant",message)
        self.logger.info(f"\n[AGENT]: {message}\n")
        
    def start(self):
        self.render_message("Chat started. Type 'quit' or 'exit' to stop.\n")
        # self.on_user_input("I want to retrieve the vendor statement for the vendor Oerlikon SPA")
        self.on_user_input("Hi, I'm alessio. How are you?")
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() in {"quit", "exit"}:
                self.render_message("Ending chat.")
                break
            self.on_user_input(user_input)
            

