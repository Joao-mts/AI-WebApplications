"""
This is a Python script that serves as a frontend for a conversational AI model built with the `langchain` and `llms` libraries.
The code creates a web application using Streamlit, a Python library for building interactive web apps.
"""

# Import necessary libraries
import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI
import os
from chave import apikey


#@st.cache(allow_output_mutation=True)
#def get_word_count():
#    return 0

#def count_words(string):
#    words = string.split()
#    return len(words)


# Set Streamlit page configuration
st.title('ChatGPT')
# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
if "just_sent" not in st.session_state:
    st.session_state["just_sent"] = False
if "temp" not in st.session_state:
    st.session_state["temp"] = ""

def clear_text():
    st.session_state["temp"] = st.session_state["input"]
    st.session_state["input"] = ""


# Define function to get user input
def get_text():
    """
    Get the user input text.

    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input", 
                            placeholder="Mande uma mensagem ...", 
                            on_change=clear_text,    
                            label_visibility='hidden')
    input_text = st.session_state["temp"]
    return input_text


    # Define function to start a new chat
def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])        
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.store = {}
    st.session_state.entity_memory.buffer.clear()

# Set up sidebar with various options
#with st.sidebar.expander("🛠️ ", expanded=False):
#    # Option to preview memory store
#    if st.checkbox("Preview memory store"):
#        with st.expander("Memory-Store", expanded=False):
#            st.session_state.entity_memory.store
#    # Option to preview memory buffer
#    if st.checkbox("Preview memory buffer"):
#        with st.expander("Bufffer-Store", expanded=False):
#            st.session_state.entity_memory.buffer
#    MODEL = st.selectbox(label='Model', options=['gpt-3.5-turbo','text-davinci-003','text-davinci-002','code-davinci-002'])
#    K = st.number_input(' (#)Summary of prompts to consider',min_value=3,max_value=1000)

MODEL = "gpt-3.5-turbo-0613"
K = 10

with st.sidebar:
    st.markdown("---")
    st.markdown("# Sobre")
    st.markdown(
       "O dashboard a seguir é uma integração do ChatGpt com arquivos locais. "
       "É possível usá-lo com os dados da OpenAI e também com os dados locais."
            )
    st.markdown(
       "Essa ferramenta pode ser modificada de acordo com a necessidade de uso. "
            )
    st.markdown("---")
    st.markdown("# 简介")
    st.markdown(
       "ChatGPTm就是增加了记忆的ChatGPT。 "
       "你可以在右边的对话框问任何问题。"
            )
    st.markdown(
       "希望给国内没法注册使用ChatGPT的朋友带来方便！"
            )

    
# Set up the Streamlit app layout
st.title("Treinado com arquivo local 🤖  🧠")
#st.subheader(" Powered by 🦜 LangChain + OpenAI + Streamlit")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Ask the user to enter their OpenAI API key
#API_O = st.sidebar.text_input("API-KEY", type="password")
API_O = apikey

# Session state storage would be ideal
if API_O:
    # Create an OpenAI instance
    llm = OpenAI(temperature=0,
                openai_api_key=API_O, 
                model_name=MODEL, 
                verbose=False) 


    # Create a ConversationEntityMemory object if not already created
    if 'entity_memory' not in st.session_state:
            st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K )
        
        # Create the ConversationChain object with the specified configuration
    Conversation = ConversationChain(
            llm=llm, 
            prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
            memory=st.session_state.entity_memory
        )  
else:
    st.sidebar.warning('API key required to try this app.The API key is not stored in any form.')
    # st.stop()


# Add a button to start a new chat
#st.sidebar.button("New Chat", on_click = new_chat, type='primary')

#word_count = get_word_count()
# Get the user input
user_input = get_text()

# Generate the output using the ConversationChain object and the user input, and add the input/output to the session
if user_input:
    output = Conversation.run(input=user_input)  
    st.session_state.past.append(user_input)  
    st.session_state.generated.append(output)  

# Allow to download as well
download_str = []
# Display the conversation history using an expander, and allow the user to download it
with st.expander("Conversation", expanded=True):
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        st.info(st.session_state["past"][i],icon="👨‍💻")
        st.success(st.session_state["generated"][i], icon="🤖")
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])
                            
    # Can throw error - requires fix
    download_str = '\n'.join(download_str)
    #word_count += count_words(download_str)
    
    if download_str:
        st.download_button('Download 下载',download_str)

# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
        with st.sidebar.expander(label= f"Conversation-Session:{i}"):
            st.write(sublist)

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:   
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session
        
##st.write("我已经为你的这次使用支付了：", word_count, "人民币")
# st.write("我是史丹福机器人庞博士，我提供此应用的初衷是让国内的人也可以体验使用增加了记忆的ChatGPT。我在为你的每次使用支付调用OpenAI API的费用，目前入不敷出，请扫码微信或支付宝支付¥10人民币以便我能够一直提供这个AI小程序，谢谢！")
# st.write("我在我的《史丹福机器人庞博士》微信视频号也有很多关于ChatGPT和怎样使用ChatGPT魔法的视频，还有怎么使用这个小程序的视频，欢迎白嫖。也有系统的收费课程《零基础精通掌握ChatGPT魔法》给愿意知识付费的同学深入学习。 ")
# st.write("所有6节课在我的视频号主页的直播回放里， 每节课99元，第一节课大家可以免费试听。 如果想购买全部6节课，有50%折扣，只要299元。可以在我的视频号主页私信我购买，注明ChatGPT课程。")

#st.image(img, caption=None, width=200)

# Divide the app page into two columns
col1, col2, col3 = st.columns(3)
