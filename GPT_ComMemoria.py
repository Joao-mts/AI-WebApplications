import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI
import os

st.title('ChatGPT')

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

def get_text():
    input_text = st.text_input("You: ", st.session_state["input"], key="input", 
                            placeholder="Mande uma mensagem ...", 
                            on_change=clear_text,    
                            label_visibility='hidden')
    input_text = st.session_state["temp"]
    return input_text

def new_chat():
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

with st.sidebar.expander("🛠️ ", expanded=False):
   MODEL = st.selectbox(label='Model', options=['gpt-3.5-turbo','text-davinci-003','text-davinci-002','code-davinci-002'])
   K = st.number_input(' (#)Summary of prompts to consider',min_value=3,max_value=1000)

# MODEL = "gpt-3.5-turbo-0613"
# K = 10

with st.sidebar:
    st.markdown("---")
    st.markdown("# Sobre")
    st.markdown(
       "Este aplicativo web é uma integração com o ChatGPT. "
       "É possível usá-lo, por enquanto, apenas com os dados da OpenAI."
            )
    st.markdown(
       "Essa ferramenta pode ser modificada de acordo com a necessidade de uso. "
            )
    st.markdown("---")
    st.markdown("Informações de uso")
    st.markdown(
       "Para utilizá-lo, é necessário configurar a chave API no código. "
       "Note que a OPENAI cobre a utilização por Tokens, dispinobilizando apenas um teste gratuito de $5,00. "
            )
    st.markdown(
       " "
            )

    
st.title("Com memória 🤖  🧠")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

API_O = os.environ.get("OPENAI_API_KEY")

if API_O:
    llm = OpenAI(temperature=0,
                openai_api_key=API_O, 
                model_name=MODEL, 
                verbose=False) 

    if 'entity_memory' not in st.session_state:
            st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K )
        
    Conversation = ConversationChain(
            llm=llm, 
            prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
            memory=st.session_state.entity_memory
        )  
else:
    st.sidebar.warning('Erro ao obter a chave API.')
    
user_input = get_text()

if user_input:
    output = Conversation.run(input=user_input)  
    st.session_state.past.append(user_input)  
    st.session_state.generated.append(output)  

download_str = []

with st.expander("Chat", expanded=True):
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        st.info(st.session_state["past"][i],icon="👨‍💻")
        st.success(st.session_state["generated"][i], icon="🤖")
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])
                            
    download_str = '\n'.join(download_str)
    
    if download_str:
        st.download_button('Baixar',download_str)

col1, col2, col3 = st.columns(3)
