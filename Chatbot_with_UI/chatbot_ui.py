import streamlit as st
from chat_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid
#******************************************Utility Functions************************************************

def generate_thread_id():
     thread_id=uuid.uuid4()
     return thread_id

def reset_chat():
     thread_id=generate_thread_id()
     st.session_state['thread_id']=thread_id
     add_thread(st.session_state['thread_id'])
     st.session_state['message_history']=[]
     

def add_thread(thread_id):
     if thread_id not in st.session_state['chat_threads']:
          st.session_state['chat_threads'].append(thread_id)

def load_chat(thread_id):
     state = chatbot.get_state(
          config={'configurable': {'thread_id': thread_id}}
     )
     return state.values.get('messages', [])

def load_chat_header(thread_id):
     state = chatbot.get_state(
          config={'configurable': {'thread_id': thread_id}}
     )
     messages = state.values.get('messages', [])
     first_user_message = next(
        (
            message.content
            for message in messages
            if isinstance(message, HumanMessage)
        ),
        "New conversation",
    )
     title = " ".join(first_user_message.split())
     return title if len(title) <= 30 else title[:27] + "..."
    
     


#******************************************Session Setup***************************************************



if 'message_history' not in st.session_state:
     st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
     st.session_state['thread_id']=generate_thread_id() 

if 'chat_threads' not in st.session_state:
     st.session_state['chat_threads']=[]

add_thread(st.session_state['thread_id'])

#****************************************Sidebar UI*********************************************************

st.sidebar.title('Smart Chat')
if st.sidebar.button('New Chat'):
    reset_chat()
    

st.sidebar.title('My Converstaions')

for thread_id in st.session_state['chat_threads'][::-1]:
    title=load_chat_header(thread_id)
    if st.sidebar.button(title, str(thread_id)):
        st.session_state['thread_id']=thread_id
        messages=load_chat(thread_id)

        temp_messages=[]

        for message in messages:
              if isinstance(message, HumanMessage):
                   role='user'
              else:
                   role='assistant'
              temp_messages.append({'role':role, 'content':message.content})

        st.session_state['message_history']=temp_messages




#******************************************Main UI**********************************************************

CONFIG={'configurable':{'thread_id':st.session_state['thread_id']}}
#load Conversation history 

for message in st.session_state['message_history']:
     with st.chat_message(message['role']):
          st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    #first add message to message_history
    st.session_state['message_history'] .append({'role':'user', 'content':user_input})
    #message_history is list of dictionaries
    with st.chat_message('user'):
        st.text(user_input)



   
    with st.chat_message('assistant'):

            ai_message=  st.write_stream(
                 message_chunk.content for message_chunk, metadata in chatbot.stream(
                      {'messages':[HumanMessage(content=user_input)]},
                      config=CONFIG,
                      stream_mode='messages'
                 )
            )
    st.session_state['message_history'].append({'role':'assistant','content':ai_message})

