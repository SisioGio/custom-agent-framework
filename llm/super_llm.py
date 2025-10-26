import json
import logging
import boto3
from abc import ABC, abstractmethod
from botocore.exceptions import ClientError
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html
client = boto3.client("bedrock-runtime",region_name='eu-central-1')

class LLM():
    def __init__(self,name,model_id='anthropic.claude-3-5-sonnet-20240620-v1:0',temperature=.7,top_p=.9,stop_sequence=[],max_tokens=512,top_k=250):
        self.name = name
        self.model_id = model_id
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.stop_sequence = stop_sequence
        self.max_tokens=max_tokens
        self.input_token_price = 0.0000003
        self.output_token_price = 0.00000015
        self.logger = logging.getLogger(name)
        logging.basicConfig(level=logging.INFO)
        
    def log(self,text,type='i'):
        if type =='i':
            self.logger.info(text)
        elif type == 'e':
            self.logger.error(text)
        elif type =='d':
            self.logger.debug(text)

    def generate_body(self,system_prompt,input_text):
        body = {
                "anthropic_version": "bedrock-2023-05-31", 
                "max_tokens": self.max_tokens,
                "system": system_prompt,    
                "messages": [
                    {
                        "role": 'user',
                        "content": [
                           
                            { "type": "text", "text": input_text }
                ]
                    }
                ],
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "stop_sequences": []
            }              

        
        return body
    
    def get_request_cost(self,response):
        logging.debug(response)
        usage = response['usage']
        input_tokens = usage['input_tokens']
        output_tokens = usage['output_tokens']
        self.total_cost = input_tokens*self.input_token_price + output_tokens*self.output_token_price
        self.log(f"Total cost is {format(self.total_cost, ".6f")}")
        return self.total_cost
    
    def send_request(self,system_prompt:str,input_text:str):
        try:
            self.log(f"Sending request: {input_text}")
            body = self.generate_body(system_prompt,input_text)
            
            
            response = client.invoke_model(
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json',
                modelId=self.model_id,
                trace='ENABLED_FULL',
                performanceConfigLatency='standard'
            )
            response_body = json.loads(response.get("body").read())
            total_cost = self.get_request_cost(response_body)
            finish_reason = response_body.get("error")

            if finish_reason is not None:
                raise Exception(f"Text generation error. Error is {finish_reason}")

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
            
            return json_output,total_cost
        
        
        except ClientError as e:
            code = e.response["Error"]["Code"]
            err_msg = e.response['Error']['Message']
            self.log(err_msg,'e')
            raise Exception(code)
        except Exception as e:
            raise Exception(e)
            

