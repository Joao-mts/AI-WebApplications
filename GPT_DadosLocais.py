import openai
import os
from chave import apikey
import streamlit as st
from streamlit_chat import message
from langchain.llms import OpenAI 
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator

# Define a chave da API OpenAI
os.environ['OPENAI_API_KEY'] = apikey
llm = OpenAI()
# Cria um carregador de texto com o caminho do arquivo e a codificação
loader = TextLoader('C:/Users/john/Documents/ESTUDO/Project/chat_data_cleaned.txt', encoding = 'utf-8')
# Cria um índice a partir do carregador
index = VectorstoreIndexCreator().from_loaders([loader])

# Define o título da aplicação Streamlit
st.title("💬 ChatGPT com dados imputados")

# Cria um campo de entrada de texto para a mensagem do usuário
user_input = st.text_input('Mande uma mensagem')

# Inicializa o estado da sessão com uma mensagem inicial do assistente
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Como posso ajudá-lo?"}]

# Verifica se a chave "messages" existe no estado da sessão antes de tentar acessá-la
if "messages" in st.session_state:
    # Percorre as mensagens no estado da sessão e exibe cada uma
    for idx, msg in enumerate(st.session_state.messages):
        message(msg["content"], is_user=msg["role"] == "user", key=idx)

# Se o usuário inseriu uma mensagem e a chave da API OpenAI está definida
if user_input:
    if user_input == 'clear':
        st.session_state["messages"] = []
    else:
        # Adiciona a mensagem do usuário ao estado da sessão
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Exibe a mensagem do usuário
        message(user_input, is_user=True)
        # Envia uma solicitação à API OpenAI para gerar uma resposta doDesculpe pela resposta anterior, foi cortada. Aqui está a continuação do código:
        response = llm(user_input)
        # Obtém a mensagem da resposta
        msg = index.query(user_input , llm=ChatOpenAI())
        st.session_state.messages.append({"role": "assistant", "content": msg})
        message(msg, is_user=False)


