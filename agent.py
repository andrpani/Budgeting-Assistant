import json
import uuid
from dotenv import load_dotenv
from collections import namedtuple
from langchain.chat_models import init_chat_model
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from prompts import system_message

def custom_json_decoder(json_dict):
    return namedtuple('Configuration', json_dict.keys())(*json_dict.values())

load_dotenv()

def main():
    with open('config.json', 'r') as jsonfile:
        config = json.load(jsonfile, object_hook=custom_json_decoder)

    llm = init_chat_model(config.llm.model, model_provider=config.llm.model_provider, model_kwargs={'persistence': InMemorySaver()})
    # print(llm.invoke([HumanMessage('Hello my name is Andrea')]).content)
    # print()
    # print(llm.invoke([HumanMessage("Hello what's my name?")]).content)
    # print('\n\n')
    # print(llm.invoke([
    #     HumanMessage('Hello my name is Andrea'),
    #     AIMessage('Hello Andrea, how can I help you?'),
    #     HumanMessage("Do you know my name? It's in italian, tell me the english version, please")
    # ]).content)
    graph_builder = StateGraph(MessagesState)

    def call_agent(state: MessagesState):
        trimmed_messages = trimmer.invoke(state['messages'])
        prompt = prompt_template.invoke({
            'messages': trimmed_messages
        })
        response = agent.invoke(prompt)
        return {'messages': response}

    # adjust the trimming to fit the ability of the model
    trimmer = trim_messages(
        max_tokens=65,
        strategy="last",
        token_counter=llm,
        include_system=True,
        allow_partial=False,
        start_on="human",
    )

    db = SQLDatabase.from_uri("sqlite:///budgeting.db")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools() + []
    memory = InMemorySaver()
    prompt_template = ChatPromptTemplate([
        system_message.format(dialect=db.dialect, top_k=5),
        MessagesPlaceholder('messages')
    ])
    agent = create_react_agent(llm, tools=toolkit.get_tools(), checkpointer=memory,
                               prompt=system_message)
    #graph_builder.add_edge(START, 'agent')
    #graph_builder.add_node('agent', call_agent)
    #graph = graph_builder.compile(checkpointer=memory)
    thread_id = uuid.uuid4()
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        try:
            question = input()
            response = agent.invoke({'messages': [HumanMessage(question)]}, config)
            response['messages'][-1].pretty_print()
        except KeyboardInterrupt:
            break
    
    
if __name__ == '__main__':
    main()






