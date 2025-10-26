from static.tools import TOOLS
import re
from tools.logic import *


TOOL_FUNCTIONS = {
    "get_vendor_number": get_vendor_number,
    "get_vendor_statement": get_vendor_statement,
    "get_vendor_open_items": get_vendor_open_items,
    "get_customer_statement": get_customer_statement,
    "get_customer_open_items": get_customer_open_items,
    "get_trial_balance": get_trial_balance,
    "get_gl_account_balance": get_gl_account_balance,
}


def validate_input(value: str, regex: str, name: str):
    if not re.fullmatch(regex, value):
        raise ValueError(f"Invalid {name}: {value}. The format must be the following: {regex}.")
    return value


def process_tool(step):
    name = step['name']
    arguments = step['arguments'] ## json {'key':'value'}
    print(f'Executing tool {name} with arguments {arguments}')
    tool = next((item for item in TOOLS if item['name'] == name), None)
    if not tool:
        raise ValueError(f"Tool {name} not found.")

    tool_args = tool['arguments']
    for arg_def in tool_args:
        arg_name = arg_def['name']
        if arg_def.get('required', False) and arg_name not in arguments:
            raise ValueError(f"Missing required argument: {arg_name}")
        if arg_name in arguments:
            validate_input(str(arguments[arg_name]), arg_def['regex'], arg_name)

    func = TOOL_FUNCTIONS.get(name)
    if not func:
        raise ValueError(f"No implementation found for tool {name}")

    func_args = {arg['name']: arguments[arg['name']] for arg in tool_args if arg['name'] in arguments}
    result = func(**func_args)
    
    print(f"Result: {result}")
    return result
