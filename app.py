import streamlit as st
import os
import base64
from PIL import Image
import io

# Add better error handling for imports
try:
    from agent import run_agent
    from utils.auth import authenticate_google_calendar
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

st.set_page_config(page_title="Meeting Scheduler Agent", page_icon="📅", layout="wide")

def get_base64_of_bin_file(bin_file):
    # Resize image to reduce size (max width 1920px)
    try:
        img = Image.open(bin_file)
        # Convert to RGB if RGBA to avoid issues with JPEG, though we use PNG here
        # But for background, we can optimize
        max_width = 1920
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG", optimize=True, quality=85)
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        # Fallback to raw read if PIL fails
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()

def main():
    # Check if imports were successful
    if not IMPORTS_OK:
        st.error(f"❌ Import Error: {IMPORT_ERROR}")
        st.info("Please ensure all required files exist:\n- agent.py\n- utils/auth.py\n- tools/calendar_tools.py\n- tools/database_tools.py")
        return
    
    st.markdown(
        """
        <div style="display: flex; justify-content: center;">
            <div class="title-container">
                <h1>📅 <span class="gradient-text">Meeting Scheduler Agent</span></h1>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Sidebar for configuration/auth status
    with st.sidebar:
        st.header("🔐 Status")
        if os.path.exists('token.pickle'):
            st.success("✓ Authenticated with Google Calendar")
        else:
            st.warning("⚠ Not Authenticated")
            if st.button("🔑 Authenticate Now"):
                try:
                    authenticate_google_calendar()
                    st.success("Authentication successful! Please reload.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Authentication failed: {e}")
        
        st.markdown("---")
        st.markdown("### ⚡ Quick Actions")
        if st.button("📆 Check Calendar"):
            st.session_state.prompt_trigger = "Check my scheduled dates"
        if st.button("➕ Schedule Meeting"):
            st.session_state.prompt_trigger = "I want to schedule a meeting"
        if st.button("🔍 Find Free Slots"):
            st.session_state.prompt_trigger = "Find approved dates (free slots) for today"
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("AI-powered meeting scheduler with natural language processing")

    # Background Image Logic
    background_style = ""
    if os.path.exists("Bg_image.png"):
        bin_str = get_base64_of_bin_file("Bg_image.png")
        background_style = f"""
            background-image: url("data:image/png;base64,{bin_str}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        """
    else:
        # Fallback to gradient if image missing
        background_style = """
            background: linear-gradient(-45deg, #0a0e27, #1a1f3a, #2d1b4e, #1e2a4a) !important;
            background-size: 400% 400% !important;
            animation: gradientShift 15s ease infinite !important;
        """

    # Advanced CSS with modern design, animations, and effects
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        /* Force Dark Theme for the entire app */
        :root {{
            --primary-color: #667eea;
            --background-color: #0a0e27;
            --secondary-background-color: #1a1f3a;
            --text-color: #e2e8f0;
            backdrop-filter: blur(10px);
        }}

        * {{
            font-family: 'Inter', sans-serif;
        }}
        
        /* Main App Container - Force Background */
        .stApp, [data-testid="stAppViewContainer"] {{
            {background_style}
            color: #e2e8f0 !important;
            position: relative;
        }}

        /* Dimming Overlay */
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6); /* Adjust opacity to control dimness */
            z-index: 0;
            pointer-events: none; /* Allow clicks to pass through */
        }}
        
        /* Ensure content is above overlay */
        .block-container {{
            position: relative;
            z-index: 1;
            padding-top: 2rem !important; /* Move content up */
        }}
        
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        /* Sidebar - Force Background */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.98) 100%) !important;
            border-right: 1px solid rgba(99, 102, 241, 0.2);
            backdrop-filter: blur(10px);
        }}
        
        /* Title Container */
        .title-container {{
            background: rgba(10, 14, 39, 0.6);
            padding: 1rem 3rem; /* Reduced padding */
            border-radius: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(12px);
            margin: 0 auto 2rem auto;
            width: fit-content;
            display: block;
        }}

        /* Title Styling */
        h1 {{
            color: #e2e8f0 !important;
            font-weight: 800 !important;
            font-size: 3rem !important;
            text-align: center;
            margin: 0 !important;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            letter-spacing: -1px;
        }}
        
        .gradient-text {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent !important;
            background-clip: text;
            color: transparent !important;
            filter: drop-shadow(0 2px 10px rgba(118, 75, 162, 0.3));
        }}
        
        /* Chat Messages */
        .stChatMessage {{
            background: rgba(25, 30, 50, 0.8) !important; /* Slightly darker/opaque for readability over image */
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(5px);
        }}
        
        /* Force text color for all Streamlit elements (Light Mode Fix) */
        .stMarkdown, .stText, p, span, div {{
            color: #e2e8f0 !important;
        }}
        
        /* Specific fix for Chat Messages content */
        .stChatMessageContent {{
            color: #e2e8f0 !important;
        }}
        
        /* Fix for Chat Input in Light Mode */
        .stChatInputContainer {{
            background-color: rgba(30, 41, 59, 0.9) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(99, 102, 241, 0.3) !important;
        }}
        
        .stChatInputContainer textarea {{
            color: #e2e8f0 !important;
            caret-color: #e2e8f0 !important;
            background-color: transparent !important;
        }}
        
        /* Placeholder text color */
        ::placeholder {{
            color: rgba(226, 232, 240, 0.6) !important;
            opacity: 1;
        }}
        
        /* Fix for user input background being white in light mode */
        div[data-testid="stChatInput"] {{
            background-color: transparent !important;
        }}
        
        /* Input Fields */
        .stChatInputContainer, .stTextInput > div > div {{
            background-color: rgba(30, 41, 59, 0.9) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(99, 102, 241, 0.3) !important;
            color: #e2e8f0 !important;
        }}
        
        input, textarea {{
            color: #e2e8f0 !important;
            background: transparent !important;
        }}
        
        /* Buttons */
        .stButton button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }}
        
        .stButton button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
        }}

        /* Success/Warning/Error/Info Alerts */
        .stAlert {{
            background-color: rgba(30, 41, 59, 0.9) !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}
        
        /* Hide default Streamlit elements that might clash */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 10px;
            background: #0a0e27;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #667eea;
            border-radius: 5px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Main chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Meeting Scheduler Agent. How can I help you organize your calendar today?"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    prompt = st.chat_input("What would you like to schedule? 💬")
    
    # Check for sidebar button triggers
    if "prompt_trigger" in st.session_state and st.session_state.prompt_trigger:
        prompt = st.session_state.prompt_trigger
        st.session_state.prompt_trigger = None # Reset trigger

    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Convert chat history to LangChain format
                from langchain_core.messages import HumanMessage, AIMessage
                chat_history = []
                for msg in st.session_state.messages[:-1]: # Exclude current user message
                    if msg["role"] == "user":
                        chat_history.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        chat_history.append(AIMessage(content=msg["content"]))
                
                response = run_agent(prompt, chat_history)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()