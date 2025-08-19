import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

load_dotenv()

@tool
def get_user_age(name: str) -> str:
    """Use this tool to find the user's age."""
    # This is a placeholder for the actual implementation
    if "bob" in name.lower():
        return "42 years old"
    return "41 years old"


memory = InMemorySaver()
model = init_chat_model('gemini-2.5-flash', model_provider='google_genai')
app = create_react_agent(
    model,
    tools=[get_user_age],
    checkpointer=memory,
    prompt='You talk like an english gentleman'
)

thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}

while True:
    try:
        question = input()
        response = app.invoke({'messages': [HumanMessage(question)]}, config)
        print(response['messages'][-1].pretty_print())
    except KeyboardInterrupt:
        break



# # The thread id is a unique key that identifies
# # this particular conversation.
# # We'll just generate a random uuid here.
# # This enables a single application to manage conversations among multiple users.
# thread_id = uuid.uuid4()
# config = {"configurable": {"thread_id": thread_id}}

# # Tell the AI that our name is Bob, and ask it to use a tool to confirm
# # that it's capable of working like an agent.
# input_message = HumanMessage(content="hi! I'm bob. What is my age?")

# for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
#     event["messages"][-1].pretty_print()

# # Confirm that the chat bot has access to previous conversation
# # and can respond to the user saying that the user's name is Bob.
# input_message = HumanMessage(content="do you remember my name?")

# for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
#     event["messages"][-1].pretty_print()