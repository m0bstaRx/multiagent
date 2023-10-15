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
import json_handler

load_dotenv()

openai_apikey = os.getenv("openai_apikey")
#TODO: "Voice control, Turkish translation are top priorities along with bug fixing for Live Mode"
#The function that conducts the Multi-agent configurations
def configure_multi_agent(seed=42, 
                        user_proxy_name = "EmreYZ",
                        user_proxy_system_message = '''A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.
                                                    ''',
                        coder_name = "Software Developer",
                        coder_system_message = '''Software Developer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
                        Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
                        If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
                        ''',
                        domain_expert_name = "Organizational Psychologist",
                        domain_expert_system_message = '''Organizational Psychologist. You follow an approved plan. You are able to devise a personality types test. 
                        You can define types, their characteristic adjectives and questions to assess. You can come up with a rationale to decied the personality type based on question responses. You don't write code.,
                        ''',
                        planner_name = "Planner",
                        planner_system_message = '''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
                        The plan may involve an engineer who can write code and a scientist who doesn't write code.
                        Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
                        ''',
                        executor_name = "Executor",
                        executor_system_message = '''Executor. Execute the code written by the software developer and report the result.
                        ''',
                        critic_name = "Critic",
                        critic_system_message = '''Critic. Double check the plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URLs.
                        You are supposed to provide constructive suggestions as critical feedback.
                        ''',
                          ):



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
    name= user_proxy_name,
    system_message=user_proxy_system_message,
    code_execution_config=False,
    human_input_mode= "NEVER"
    )
    software_developer = autogen.AssistantAgent(
        name=coder_name,
        llm_config=gpt_config,
        system_message=coder_system_message,
    )
    domain_expert = autogen.AssistantAgent(
        name=domain_expert_name,
        llm_config=gpt_config,
        system_message=domain_expert_system_message,
    )
    planner = autogen.AssistantAgent(
        name=planner_name,
        system_message=planner_system_message,
        llm_config=gpt_config,
    )
    executor = autogen.UserProxyAgent(
        name=executor_name,
        system_message=executor_system_message,
        human_input_mode="NEVER",
        code_execution_config={"last_n_messages": 3, "work_dir": "output"},
    )
    critic = autogen.AssistantAgent(
        name=critic_name,
        system_message=critic_system_message,
        llm_config=gpt_config,
    )
    groupchat = autogen.GroupChat(agents=[user_proxy, software_developer, domain_expert, planner, executor, critic], messages=[], max_round=10)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt_config)

#The function that conducts the Multi-agent configurations | end of section

    #Remove the interatactions log from the previous run
    InteractionsManager.reset_interactions()

    #Aysnchronously run the multi-agent panel interactions
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

    #Create a seperate thred for the async chat function to have it running while the WebUI is re-rendered periodically
    thread = threading.Thread(target=async_chat_function)
    thread.start()
    #Aysnchronously run the multi-agent panel interactions | end of section

#End of configure_multi_agent function||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

agents_working = True

#The function to display the interactions as they are logged locally

def pick_emoji(agent_name):
    emoji_shortcode = ''
    if agent_name == 'Software Developer':
        emoji_shortcode = ':computer:'
    elif agent_name == 'Organizational Psychologist':
        emoji_shortcode = ':brain:'
    elif agent_name == 'Planner':
        emoji_shortcode = ':card_index:'
    elif agent_name == 'Critic':
        emoji_shortcode = ':necktie:'
    elif agent_name == 'Executor':
        emoji_shortcode = ':robot_face:'
    elif agent_name == 'EmreYZ':
        emoji_shortcode = ':robot_face:'
    else:
        emoji_shortcode = ':robot_face:'
    
    return emoji_shortcode


def Read_Interactions(default_file_path = "interactions.json"):
    lock = FileLock(f"{default_file_path}.lock")

    with lock:
        if not os.path.exists(default_file_path):
            return   

        # If 'last_index' is not in session_state, initialize it to -1
        if 'last_index' not in st.session_state:
            st.session_state.last_index = -1

        with open(default_file_path, "r") as file:
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
#The function to display the interactions gradually as they are logged locally | end of section

#The function to display interactions previously recorded

def Replay_Interactions(filepath='./best/best.json'):
    replay_data = json_handler.get_data_from_json(filepath=filepath)

    for item in replay_data:
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
            st.subheader(f'{pick_emoji(item["agent_name"])} :violet[**{item["agent_name"]}:**]')
        
        if streaming_mode == ':unlock: ON':
            message_placeholder = st.empty()
            full_response = ""

            for chunk in item["agent_message"].split():
                full_response += chunk + " "
                time.sleep(0.02)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")               
            message_placeholder.empty()

        st.write(item["agent_message"])
        st.divider()
        with st.spinner(text='Agents in Discussion... :robot_face: :card_index: :brain: :computer: :necktie:'):
            time.sleep(5)
    st.sidebar.success("The interaction is completed!")
    st.balloons()
    return False
#The function to display interactions previously recorded | end of section


#Designing the Streamlit WebUI Layout and relevant interactions
st.set_page_config(page_title="Multi-Agent Panel", page_icon=":robot_face:", layout="centered", initial_sidebar_state="auto")

with stylable_container(
            key="container_with_border",
            css_styles="""
            {
                border: 2px solid rgba(173, 175, 6, 0.8);
                border-radius: 1rem;
                padding: calc(1em - 1px)
            }
            """,
        ):
    st.header("Agent Interactions")

st.divider()
st.sidebar.title("Multi-Agent AI Panel: Creating a Personality Test From Scratch")
st.sidebar.divider()

# Custom CSS 
st.markdown(
    '''
    <style>
    .streamlit-expanderHeader {
        background-color: maroon;
        color: white;
    }
    .streamlit-expanderContent {
        background-color: black;
        color: white;
    </style>
    ''',
    unsafe_allow_html=True
)

with st.sidebar.expander("**Panel of AI Agents**", True):
    st.info(f"{pick_emoji('EmreYZ')} EmreYZ (Human)")
    st.info(f"{pick_emoji('Software Developer')} Software Developer")
    st.info(f"{pick_emoji('Organizational Psychologist')} Organizational Psychologist")
    st.info(f"{pick_emoji('Planner')} Planner")
    st.info(f"{pick_emoji('Critic')} Critic")
    st.info(f"{pick_emoji('Executor')} Executor")

start_button = st.sidebar.button("Start The Panel Discussion")
st.sidebar.divider()

with st.sidebar.expander("Application Configuration"):
    mode_select = st.radio('Select App Mode',[':cinema: Replay Mode', ':black_circle_for_record: Live Mode'],0)
st.sidebar.divider()

with st.sidebar.expander("Human Involvement"):
    human_involvement = st.radio('Consult With The User?',[':white_check_mark: YES', ':x: NO'],1)
st.sidebar.divider()

with st.sidebar.expander("Straming Control"):
    streaming_mode = st.radio('Streaming Mode:',[':unlock: ON', ':lock_with_ink_pen: OFF'],1)
st.sidebar.divider()
#Designing the Streamlit WebUI Layout and relevant interactions | end of section

if start_button:
    # if mode_select == ':black_circle_for_record: Live Mode':
    #     configure_multi_agent()


    while agents_working:
        if mode_select == ':cinema: Replay Mode':
            agents_working = Replay_Interactions()

        elif mode_select == ':black_circle_for_record: Live Mode':
            configure_multi_agent()
            Read_Interactions()
            with st.spinner(text='Agents in Discussion...'):
                time.sleep(5)
        else:
            st.sidebar.info("There is a Mode Selection Error!")