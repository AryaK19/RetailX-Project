import streamlit as st
from langchain_community.llms import Ollama
import time
import pandas as pd


customers_df = pd.read_csv('data/customers_indian2.csv')
stores_df = pd.read_csv('data/stores_indian2.csv')
orders_df = pd.read_csv('data/orders_indian2.csv')
products_df = pd.read_csv('data/products_indian.csv')


model = 'chatbot' 


st.set_page_config(page_title="RetailX Assistant Chatbot")
with st.sidebar:
    st.title("RetailX Assistant Chatbot")


ollama = Ollama(model=model,base_url="http://localhost:11434")

ollama.invoke(input="Hello")

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
if "data_context" not in st.session_state.keys():
    st.session_state.data_context = ""


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.session_state.data_context = ""
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

def get_response(user_input, data):
    
    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
    response = ollama.invoke(input=f"DATA://{data}\n\n{conversation_history}\nuser: {user_input}")
    print(conversation_history)
    return response

def determine_dataset(query):
    store_keywords = ["store", "branch", "location", "address", "contact", "phone"]
    order_keywords = ["order", "transaction", "status", "delivery", "shipment", "tracking", "order id"]
    product_keywords = ["product", "stock", "buy", "purchase", "price", "looking for"]
    customer_keywords = ["customer", "my name", "email", "customer id"]

    query_lower = query.lower()

    if any(keyword in query_lower for keyword in store_keywords):
        return "data-stores", stores_df
    elif any(keyword in query_lower for keyword in order_keywords):
        return "data-orders", orders_df
    elif any(keyword in query_lower for keyword in product_keywords):
        return "data-products", products_df
    elif any(keyword in query_lower for keyword in customer_keywords):
        return "data-customers", customers_df
    else:
        return None, None

def chatbot(query):

    data_label, dataset = determine_dataset(query)
    if dataset is not None:
        data = str(dataset)
        
        st.session_state.data_context = f"DATA://{data_label}"
        return get_response(query, data)
    else:
        
        st.session_state.data_context = ""
        return get_response(query, "No specific dataset")


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response = chatbot(prompt)
        placeholder = st.empty()
        full_response = ''
        for char in response:  
            full_response += char
            placeholder.markdown(full_response)
            time.sleep(0.05) 
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)