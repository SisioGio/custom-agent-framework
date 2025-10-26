from agent import Agent
from knowledge import KNOWLEDGE
from tools.tools_descriptions import TOOLS
from llm.super_llm import LLM


# Define important entities
entities = [
    {
        'name':'user_name',
        'description':'name of the user',
        'value':''
    },
    {
        'name':'entity',
        'description':'name of the entity for which the user is interested',
        'examples':['IT','PL','DE','FR','ES'],
        'value':''
    },
    
    {
        'name':'user_role',
        'description':'role of the user',
        'value':''
    }
]

instructions = "You're an helpful assistant expert in accounting."
rules = "Never provide false information"
role = 'AI Agent for Accounting'
responsible_for = 'Help users into resolving their issues and requests'

agent = Agent("You're an helpful assistant expert in accounting.",rules,KNOWLEDGE,TOOLS,entities=entities,role=role,responsible_for=responsible_for)

planner = LLM('Planner')
generator = LLM('Generator')
summarizer = LLM('Summarizer')

agent.set_planner(planner)


agent.set_answer_generator(generator)
agent.set_summarizer(summarizer)
agent.start()

