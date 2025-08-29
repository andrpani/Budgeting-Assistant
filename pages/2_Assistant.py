import uuid
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.chat.output_parser import ChatOutputParser
from utils.llm import pre_model_hook


st.title('Budgeting Assistant')

client = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    google_api_key=st.secrets['GOOGLE_API_KEY']
)

memory = InMemorySaver()
thread_id = uuid.uuid4()
config = RunnableConfig(configurable={"thread_id": thread_id})
db = SQLDatabase.from_uri("sqlite:///data/budgeting.db")
sql_toolkit = SQLDatabaseToolkit(db=db, llm=client)
tools = sql_toolkit.get_tools() + []
agent = create_react_agent(
    client,
    prompt='You are a helpful assistant',
    checkpointer=memory,
    pre_model_hook=pre_model_hook,
    tools=tools
)

if 'google_model' not in st.session_state:
    st.session_state.google_model = 'gemini-2.5-flash'

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input('Chat with the assistant...'):
    with st.chat_message('user'):
        st.markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('assistant'):
        #stream = client.stream(st.session_state.messages)
        #chain = agent | ChatOutputParser()
        #state = agent.invoke({'messages': st.session_state.messages}, config=config)
        stream = agent.stream({'messages': st.session_state.messages}, config=config, stream_mode='updates')
        stream = (step['agent']['messages'][-1].content for step in stream if 'agent' in step)
        #response = chain.invoke({'messages': st.session_state.messages}, config=config)
        #response = state['messages'][-1].content
        response = st.write_stream(stream)
        #print(response)
        #stream = (f'{x**2} ' for x in range(10))
        #response = st.write_stream(stream)
        for step in agent.stream({'messages': st.session_state.messages}, config=config):
            print(step)

    st.session_state.messages.append({'role': 'assistant', 'content': response})