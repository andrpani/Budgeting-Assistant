import json
import uuid
import os
import base64
import sqlite3
from dotenv import load_dotenv
from collections import namedtuple
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from prompts import system_message, agent_prompt
from data.models import StructuredData, Purchase
from pathlib import Path
from typing import List

def custom_json_decoder(json_dict):
    return namedtuple('Configuration', json_dict.keys())(*json_dict.values())

def extract_purchases(llm: BaseChatModel, filename: Path) -> List[Purchase]:
    purchases = []

    with open(filename, "rb") as f:
        encoded_file = base64.b64encode(f.read()).decode("utf-8")
        if filename.suffix.endswith('pdf'):
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Describe the local pdf file"},
                    {
                        "type": "file",
                        "source_type": "base64",
                        "data": encoded_file,
                        "mime_type": "application/pdf",
                    }
                ]
            )
            extracted_data = llm.invoke([message])
            purchases.extend(extracted_data.purchases)
        elif filename.suffix.endswith('.png') or filename.suffix.endswith('.jpg') or filename.suffix.endswith('.jpeg'):
            extension = filename.suffix.replace('jpg', 'jpeg').split('.')[-1]
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Describe the local image"},
                    {
                        "type": "image",
                        "source_type": "base64",
                        "data": encoded_file,
                        "mime_type": f"image/{extension}",
                    }
                ]
            )
            extracted_data = llm.invoke([message])
            purchases.extend(extracted_data.purchases)

    return purchases

def pre_model_hook(state):
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=384,
        start_on="human",
        end_on=("human", "tool"),
    )
    return {"llm_input_messages": trimmed_messages}

load_dotenv()

def main():
    purchases = []

    with open('config.json', 'r') as jsonfile:
        config = json.load(jsonfile, object_hook=custom_json_decoder)
    llm = init_chat_model(config.llm.model, model_provider=config.llm.model_provider)
    llm_structured = llm.with_structured_output(StructuredData)
    
    # list all files in the input directory, excluding the ones already processed
    # and listed in the corresponding file
    processed_files = set()
    file_path = Path(config.processed_filename)
    dir_path = Path(config.input_dir)

    if not file_path.is_file():
        file_path.touch()
    else: 
        with open(file_path, 'r') as f:
            for filename in f:
                processed_files.add(Path(filename.strip()))

    files_to_process = [filename for filename in dir_path.iterdir() 
                            if filename.is_file() and filename not in processed_files]
    if files_to_process:
        print(f'Processing {len(files_to_process)} new files using {config.llm.model}:')
        for index, filename in enumerate(files_to_process):
            purchases.extend(extract_purchases(llm_structured, filename))
            with open(config.processed_filename, 'a') as f:
                f.write(str(filename) + '\n')
            print(f'  {index + 1}: "{str(filename)}" finished')

        print('Processing completed')

        print('Extracted files:')
        print(purchases)
    
        # save extracted data into the db
        with sqlite3.connect(config.db_name) as db_connection:
            cursor = db_connection.cursor()
            # insert the purchases and items
            for purchase in purchases:
                purchase_dict = purchase.model_dump()
                del purchase_dict['items']
                cursor.execute("INSERT INTO Purchase(Title, Date, Total) " \
                                            "VALUES (:title, :date, :total)", purchase_dict)
                db_connection.commit()
                purchase_id = cursor.lastrowid
                for item in purchase.items:
                    item_dict = item.model_dump()
                    item_dict['purchase_id'] = purchase_id
                    cursor.execute("INSERT INTO PurchaseItem(Name, Quantity, UnitPrice, TotPrice, Info, PurchaseID)" \
                                        "VALUES (:name, :quantity, :unit_price, :tot_price, :info, :purchase_id)", item_dict)
                    db_connection.commit()
        
    else: print('No new files to process')

    # agent
    memory = InMemorySaver()
    thread_id = uuid.uuid4()
    config = {"configurable": {"thread_id": thread_id}}
    db = SQLDatabase.from_uri("sqlite:///budgeting.db")
    sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = sql_toolkit.get_tools() + []
    agent = create_react_agent(
        llm,
        prompt='You are a helpful assistant',
        checkpointer=memory,
        pre_model_hook=pre_model_hook,
        tools=tools
    )

    while True:
        try:
            question = input('Chat with the Budgenting-Assistant: ')
            response = agent.invoke({'messages': [HumanMessage(question)]}, config)
            response['messages'][-1].pretty_print()
        except KeyboardInterrupt:
            break


    

    # def call_agent(state: MessagesState):
    #     trimmed_messages = trimmer.invoke(state['messages'])
    #     prompt = prompt_template.invoke({
    #         'messages': trimmed_messages
    #     })
    #     response = agent.invoke(prompt)
    #     return {'messages': response}

    # # adjust the trimming to fit the ability of the model
    # trimmer = trim_messages(
    #     max_tokens=65,
    #     strategy="last",
    #     token_counter=llm,
    #     include_system=True,
    #     allow_partial=False,
    #     start_on="human",
    # )

    # db = SQLDatabase.from_uri("sqlite:///budgeting.db")
    # toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    # tools = toolkit.get_tools() + []
    # memory = InMemorySaver()
    # prompt_template = ChatPromptTemplate([
    #     system_message.format(dialect=db.dialect, top_k=5),
    #     MessagesPlaceholder('messages')
    # ])
    # agent = create_react_agent(llm, tools=toolkit.get_tools(), checkpointer=memory,
    #                            prompt=system_message)
    # #graph_builder.add_edge(START, 'agent')
    # #graph_builder.add_node('agent', call_agent)
    # #graph = graph_builder.compile(checkpointer=memory)
    # thread_id = uuid.uuid4()
    # config = {"configurable": {"thread_id": thread_id}}

    # while True:
    #     try:
    #         question = input()
    #         response = agent.invoke({'messages': [HumanMessage(question)]}, config)
    #         response['messages'][-1].pretty_print()
    #     except KeyboardInterrupt:
    #         break
    
    
if __name__ == '__main__':
    main()






