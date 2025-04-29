from datetime import datetime
import streamlit as st
import asyncio
import uuid
from agentss.main_agent import agent
from agents import Runner
from dotenv import load_dotenv
import os

load_dotenv()  

openai_key = st.secrets['OPENAI_API_KEY']
# openai_key = os.getenv('OPENAI_API_KEY')

if not openai_key:
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

# st.secrets['OPENAI_API_KEY'] = openai_key



st.set_page_config(
    page_title="Billy",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        border-left: 5px solid #4CAF50;
    }
    .chat-message .content {
        display: flex;
        margin-top: 0.5rem;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .message {
        flex: 1;
        color: #000000;
    }
    .timestamp {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)



if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{
                "role": "assistant",
                "content": "Hello there! 😁 How can I help you today? Need to book a dental appointment, have questions about our services, or something else? Let me know! 🦷✨",
                "timestamp": datetime.now().strftime("%I:%M %p")
            }]

if "processing_message" not in st.session_state:
    st.session_state.processing_message = None

if "model_type" not in st.session_state:
    st.session_state.model_type = None

def handle_user_message(user_input: str):
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })
    
    st.session_state.processing_message = user_input


def user_inpt():
    user_input = st.chat_input("Ask Billy...")
    if user_input:
        handle_user_message(user_input)

        st.rerun()



st.title("🦷 ARC Dental Assistant")
st.caption("AI Dental Assistant")
st.info('Appointment Booking & Lead Gen Chatbot', icon="🤖")
    

for message in st.session_state.chat_history:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=default" class="avatar" />
                    <div class="message">
                        <div>{message["content"]}</div>
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
            <div class="chat-message assistant">
                <div class="content">
                    <img src="https://api.dicebear.com/7.x/bottts/svg?seed=travel-agent" class="avatar" />
                    <div class="message">
                        {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


user_inpt()


if st.session_state.processing_message:
    user_input = st.session_state.processing_message
    st.session_state.processing_message = None

    with st.spinner("Thinking..."):
        try:
            if len(st.session_state.chat_history) > 1:
                input_list = []
                for msg in st.session_state.chat_history:
                    input_list.append({"role": msg["role"], "content": msg["content"]})
            else:
                # First message
                input_list = user_input

            result = asyncio.run(Runner.run(
            starting_agent=agent,
            input=input_list
            ))
            

            st.session_state.chat_history.append({
                "role": "assistant",
                "content":  result.final_output,
                "timestamp": datetime.now().strftime("%I:%M %p")
            }) 

        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })

        st.rerun()