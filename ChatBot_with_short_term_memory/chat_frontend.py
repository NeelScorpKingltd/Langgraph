import streamlit as st
from chat_backend import chatbot, retrive_all_threads
from langchain_core.messages import HumanMessage
import uuid
from pathlib import Path

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

/* Base canvas */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    background-color: #0d0f12 !important;
    color: #e4e4e7 !important;
}

/* ---------------- SIDEBAR: STRUCTURED & PURPOSEFUL ---------------- */
section[data-testid="stSidebar"] {
    background-color: #12141a !important;
    border-right: 1px solid #1f232b !important;
}

/* "+ New Chat" Button */
section[data-testid="stSidebar"] div.stButton:first-of-type button {
    background-color: #1e222b !important;
    border: 1px solid #2e3543 !important;
    color: #f4f4f5 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.2s ease !important;
}

section[data-testid="stSidebar"] div.stButton:first-of-type button:hover {
    background-color: #262c38 !important;
    border-color: #3f475a !important;
}

/* Conversation Buttons: Defined Cards, Not Naked Text */
section[data-testid="stSidebar"] div.stButton:not(:first-of-type) button {
    background-color: #161920 !important;
    border: 1px solid #222631 !important;
    border-radius: 8px !important;
    color: #a1a1aa !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 0.55rem 0.85rem !important;
    margin-bottom: 0.25rem !important;
    font-size: 0.86rem !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
    transition: all 0.15s ease !important;
}

section[data-testid="stSidebar"] div.stButton:not(:first-of-type) button:hover {
    background-color: #1d212b !important;
    border-color: #333a4a !important;
    color: #ffffff !important;
}

/* ---------------- CHAT: USER BOXED, ASSISTANT OPEN ---------------- */
/* Remove default wrappers */
div[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 1rem 0 !important;
}

/* User Message: A clean, self-contained action bubble */
div[data-testid="stChatMessage"]:nth-of-type(odd) {
    background-color: #16181f !important;
    border: 1px solid #232733 !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 1.25rem !important;
}

/* Assistant Message: NO container box, sits directly on canvas */
div[data-testid="stChatMessage"]:nth-of-type(even) {
    background-color: transparent !important;
    border: none !important;
    padding: 0.5rem 0.25rem 1.5rem 0.25rem !important;
}

/* Clean up markdown list spacing */
div[data-testid="stChatMessage"] ol,
div[data-testid="stChatMessage"] ul {
    padding-left: 1.4rem !important;
}

div[data-testid="stChatMessage"] li {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    line-height: 1.7 !important;
    margin-bottom: 0.5rem !important;
    color: #d1d5db !important;
}

/* ---------------- INPUT DOCK ---------------- */
div[data-testid="stChatInput"] {
    background-color: #14171f !important;
    border: 1px solid #242936 !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4) !important;
}
</style>
""", unsafe_allow_html=True)
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
        "Ongoing Conversation conversation",
    )
     title = " ".join(first_user_message.split())
     return title if len(title) <= 30 else title[:27] + "..."
    
     


#******************************************Session Setup***************************************************



if 'message_history' not in st.session_state:
     st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
     st.session_state['thread_id']=generate_thread_id() 

if 'chat_threads' not in st.session_state:
     all_theads=retrive_all_threads()[::-1]
     st.session_state['chat_threads']=all_theads

add_thread(st.session_state['thread_id'])

#****************************************Sidebar UI*********************************************************

st.sidebar.markdown("### Smart Chat")
if st.sidebar.button("+ New Chat", use_container_width=True):
    reset_chat()
    

st.sidebar.markdown("---")
st.sidebar.caption("CONVERSATIONS")

for thread_id in st.session_state['chat_threads'][::-1]:
    title=load_chat_header(thread_id)
    if st.sidebar.button(title, str(thread_id), use_container_width=True):
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
USER_AVATAR = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
    "stroke='%2371717a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
    "<circle cx='12' cy='8' r='5'/><path d='M20 21a8 8 0 0 0-16 0'/></svg>"
)
BOT_AVATAR = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
    "stroke='%23a1a1aa' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
    "<path d='m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z'/></svg>"
)

for message in st.session_state['message_history']:
     avatar = USER_AVATAR if message['role'] == 'user' else BOT_AVATAR
     with st.chat_message(message['role'], avatar=avatar):
          st.markdown(message['content'])

user_input = st.chat_input('Ask anything...')

if user_input:
    #first add message to message_history
    st.session_state['message_history'] .append({'role':'user', 'content':user_input})
    #message_history is list of dictionaries
    with st.chat_message('user', avatar=USER_AVATAR):
        st.markdown(user_input)



   
    with st.chat_message('assistant',avatar=BOT_AVATAR):

            ai_message=  st.write_stream(
                 message_chunk.content for message_chunk, metadata in chatbot.stream(
                      {'messages':[HumanMessage(content=user_input)]},
                      config=CONFIG,
                      stream_mode='messages'
                 )
            )
    st.session_state['message_history'].append({'role':'assistant','content':ai_message})

