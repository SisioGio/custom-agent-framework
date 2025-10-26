# Generates a user-friendly message from knowledge database chunks
def knowledge_prompt(results):
    """
    Creates a prompt for generating a message for the user based on retrieved knowledge chunks.
    
    Args:
        results (str): Chunks of data retrieved from the knowledge base.
        
    Returns:
        str: Formatted prompt string for the agent.
    """
    prompt = f"""
    You are responsible for writing messages that will be sent to the end user via chat.
    You are given a set of chunks retrieved from a knowledge base.
    Your task is to return a **well-formatted, user-friendly message** based on this information.
    Return an object in the following format:
    {{
        "text": "your message here"
    }}

    Chunks retrieved from the knowledge database:
    {results}
    
    Ensure the message is clear, concise, and directly answers the user's question.
    The output must be a valid JSON string.
    New lines are represented with '\\n'.
    """
    return prompt


# Generates a user-friendly message from raw data (usually tool outputs)
def prompt_messager(raw_data):
    """
    Creates a prompt to convert raw data or tool outputs into a clear message for the user.
    
    Args:
        raw_data (str): Data to be transformed into a user-friendly message.
        
    Returns:
        str: Formatted prompt string.
    """
    prompt = f"""
    You are responsible for writing messages that will be sent to the end user via chat.
    You are given an answer or set of data, and your task is to return a **well-formatted, user-friendly message**.
    Return an object in the following format:
    {{
        "text": "your message here"
    }}

    Data to be converted:
    {raw_data}

    Ensure the message is clear, concise, and directly answers the user's request.
    The output must be a valid JSON string.
    New lines are represented with '\\n'.
    """
    return prompt


# Creates a plan for handling user requests
def prompt_planner(role, responsible_for, instructions, tools, knowledge, entities, today, summary, current_goal):
    """
    Generates a detailed prompt for the agent planner.
    
    Args:
        role (str): Agent role description.
        responsible_for (str): Responsibilities of the agent.
        instructions (str): Agent instructions.
        tools (list/dict): Available tools and APIs.
        knowledge (list/dict): Knowledge base references.
        entities (list/dict): Current conversation entities.
        today (str): Current date.
        summary (str): Chat summary.
        current_goal (str): User's current objective.
        
    Returns:
        str: Formatted planning prompt.
    """
    prompt = f"""
    You are an {role}, responsible for {responsible_for}.
    Instructions:
    {instructions}

    Access to:
    1. **TOOLS** – APIs that can be called to fetch real-time data (AP, AR, GL).
    2. **KNOWLEDGE** – Documents containing static reference information about accounting processes.

    Your job:
    - Understand the user's query.
    - Decide whether to use knowledge, tools, ask a question, or provide a direct answer.
    - Produce a **step-by-step plan** specifying resources, order of usage, and final response.
    - Leverage previous messages and entities to avoid redundant questions.

    ### TOOLS Available:
    {tools}

    ### KNOWLEDGE Available:
    {knowledge}

    ## ENTITIES:
    Variables from the conversation that might be needed:
    {entities}

    ### Output Format:
    Return only **valid JSON** with the structure:
    {{
        "plan": [
            {{
                "type": "knowledge" or "tool" | "direct_answer" | "question",
                "name": "<tool_or_knowledge_name>",  // optional for direct_answer/question
                "description": "<why this step is needed>",
                "arguments": {{"param": "value"}},    // only for tool
                "content": "<answer_to_user>",       // only for direct_answer
                "question": "<question_to_user>",    // only for question or knowledge
                "metadata": ["str1","str2"],         // only for knowledge
                "answer_example": ["example1"],      // only for question
                "options": ["opt1","opt2"],          // optional, only for question
                "output":"variable_name",            // required for question/tool/knowledge
                "share_with_user": true or false     // True if step result should be shared
            }}
        ],
        "final_answer_template": "Describe the final user message after plan execution.",
        "user_goal": "short description of target result",
        "entities": {{ "entity_name": "entity_value" }} // only if new values are found
    }}

    ### RULES
    - Never assume missing parameters.
    - Ask multiple missing inputs in a single question where possible.
    - If query is ambiguous, insert a question step.
    - Combine multiple steps if both tools and knowledge are required.
    - Always output valid JSON, escape special characters.
    - Represent new lines with '\\n'.

    ### IMPORTANT
    Today is: {today}
    Chat summary: {summary}
    Current goal: {current_goal}
    """
    return prompt


# Summarizes chat messages into a concise user goal
def summarizer_prompt(messages, entities, summary):
    """
    Generates a prompt for summarizing chat history.

    Args:
        messages (list/dict): List of previous chat messages.
        entities (list/dict): Previously stored entities.
        summary (str): Previously generated summary.

    Returns:
        str: Formatted summarization prompt.
    """
    prompt = f"""
    You're an expert in summarizing long chat conversations between a user and an AI agent.
    Your goal is to create a short summary focusing on:
    - Last user intent/objective
    - Important fields provided by the user
    - Ignore old goals/intents

    Chat history:
    {messages}

    Previously stored entities:
    {entities}

    Previously generated summary:
    {summary}

    Return a JSON string:
    {{"user_goal":"user_goal","summary":"summary_text"}}

    Rules:
    - Do not add new lines
    - Focus on user intent and available data
    """
    return prompt
