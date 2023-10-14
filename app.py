import os
import autogen
from dotenv import load_dotenv
import streamlit as st
from filelock import FileLock
import json
import time
import asyncio
import threading
from interactionsmanager import InteractionsManager
from streamlit_extras.stylable_container import stylable_container

load_dotenv()

openai_apikey = os.getenv("openai_apikey")

config_list35 = [
    {
        'model': 'gpt-3.5-turbo-16k',
        'api_key': openai_apikey,
    }

]

gpt_config = {
    "seed": 42,
    "temperature": 0,
    "config_list": config_list35,
    "request_timeout": 120,
}
user_proxy = autogen.UserProxyAgent(
   name="EmreYZ",
   system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
   code_execution_config=False,
   human_input_mode= "NEVER"
)
engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=gpt_config,
    system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
)
scientist = autogen.AssistantAgent(
    name="Scientist",
    llm_config=gpt_config,
    system_message="""Scientist. You follow an approved plan. You are able to devise a personality types test. You can define types, their characteristic adjectives and questions to assess. You can come up with a rationale to decied the personality type based on question responses. You don't write code."""
)
planner = autogen.AssistantAgent(
    name="Planner",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
''',
    llm_config=gpt_config,
)
executor = autogen.UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
)
critic = autogen.AssistantAgent(
    name="Critic",
    system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL.",
    llm_config=gpt_config,
)
groupchat = autogen.GroupChat(agents=[user_proxy, engineer, scientist, planner, executor, critic], messages=[], max_round=10)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt_config)

InteractionsManager.reset_interactions()

def async_chat_function():
    asyncio.run(user_proxy.a_initiate_chat(
        manager,
        message = """I want you to develop a personality test that is based on the 4-color personality. Execute the following tasks one by one:

    1. Define 4 personality types with engaging and creative names. Make sure that you do not mention the colors, just the names.
    2. Determine 3 adjectives for each of the personality types. Make sure that those adjectives define the personality type. Provide the adjectives as a table where the columns are the names of the personality types and rows are the adjectives.
    3. You will write 5 questions per personality types that are useful to determine the user's personality type. Consider that these questions will later be incorporated with an assessment logic to decide the personality type. Provide the questions as bullet lists for each personality type.
    4. Devise a logic to calculate how to define the personality type of the user based on the answers. Make sure that each one of the 20 questions affect the final outcome. Explain the logic briefly. Then, express this logic as a Python function called "determine_personality_type". Remember this logic and code as we will execute it later.
    5. You will write a brief information sections for each personality types. The information sections must follow this format:
    Your Personality Type: <Determined Personality Type>
    Your Characteristics: <Adjective 1 for the personality type> |  <Adjective 2 for the personality type> | <Adjective 3 for the personality type>
    In a Nutshell: <Brief description of the determined personality type>
    While writing the information sections make sure that you use the personality types and adjectives you created in previous tasks. Also, ensure that the "In a Nutshell" part describes the personality in line with the name of the personality, associated adjectives and associated questions. It must all make sense.
    6. We need a Streamlit application to present this personality test to users. Use a basic UI that features st.columns() to determine the layout of UI elements. Use st.title() for the title of the Personality Type Test, use st.text() to display the textual statement of the given question, use st.slider() ranging from 1 to 5 to let user input his rating choice for the given question, use st.button() for next and previous buttons that let user to go back and forth between questions, use st.progress() to show user his progress through the 20 questions, use st.button() when the user reaches to the last question to submit his replies, write the function called "determine_personality_type" from the previous task that implements the assessment logic you devised, use st.balloons() and st.success() to show the user his determined personality type and use st.markdown() to show the brief information section you created for this type upon completion of the assessment logic. Beware of the duplicate widget id error while setting up the elements, consider assigning unique key parameters to elements. Also, ensure that you don't try to acces a list item while the list is empty. Make sure that entire Streamlit app is a single .py file. Streamlit is already installed on the machine, don't worry about that. Write the code accordingly.
    """,
    ))


st.title("Otonom Yapay Zeka Ajanlarıyla Çalışma")

thread = threading.Thread(target=async_chat_function)
thread.start()


def Read_Interactions():
    lock = FileLock("interactions.json.lock")

    with lock:
        if not os.path.exists("interactions.json"):
            return   

        # If 'last_index' is not in session_state, initialize it to -1
        if 'last_index' not in st.session_state:
            st.session_state.last_index = -1

        with open("interactions.json", "r") as file:
            data = json.load(file)
            # Start reading from where you left off
            for idx in range(st.session_state.last_index + 1, len(data)):
                #st.write(data[idx])
                with stylable_container(
                    key="container_with_border",
                    css_styles="""
                    {
                        border: 1.5px solid rgba(102, 51, 0, 0.75);
                        border-radius: 1rem;
                        padding: calc(1em - 1px)
                    }
                    """,
                ):
                    st.subheader(f':robot_face: :violet[**{data[idx]["agent_name"]}:**]')
                st.write(data[idx]["agent_message"])
            # Update the session state with the new index
            st.session_state.last_index = len(data) - 1


while True:
    Read_Interactions()
    with st.spinner(text='Agents in Discussion...'):
        time.sleep(5)