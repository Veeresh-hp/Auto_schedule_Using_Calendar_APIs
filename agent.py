import os
from dotenv import load_dotenv
from langchain.agents.agent import AgentExecutor
from langchain.agents import create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from tools.calendar_tools import list_events, create_event, get_free_slots
from tools.database_tools import log_meeting

# Load environment variables
load_dotenv()

@tool
def check_calendar(n_events: int = 10):
    """Checks the user's calendar for upcoming events. Returns a list of events."""
    return list_events(n_events)

@tool
def schedule_meeting(summary: str, start_time: str, duration_minutes: int = 60, attendees: str = None):
    """Schedules a meeting on the user's calendar.
    start_time should be in ISO format or a clear string like '2023-10-27 10:00:00'.
    attendees is a comma-separated string of emails.
    """
    result = create_event(summary, start_time, duration_minutes, attendees)
    # Log to DB
    log_meeting(summary, attendees if attendees else "", str(start_time))
    return result

@tool
def find_free_time(date_str: str):
    """Finds free slots or busy times for a given date to help with scheduling."""
    return get_free_slots(date_str)

def get_agent():
    # Use Gemini Pro model
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY not found in .env")
        
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
    
    tools = [check_calendar, schedule_meeting, find_free_time]
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a professional Customer Service Representative for a Meeting Scheduling Service. "
                "Your goal is to assist customers in finding 'approved dates' (which means available free slots) and managing their 'scheduled dates' (confirmed meetings). "
                "Always be polite, professional, and helpful. "
                "When a user asks for 'approved dates', use the `find_free_time` tool to check for free slots. "
                "When a user asks for 'scheduled dates', use the `check_calendar` tool to list upcoming events. "
                "Always check for availability before scheduling if the user asks for a specific time but hasn't confirmed it's free. "
                "When scheduling, ask for confirmation if details are ambiguous. "
                "Today's date is {date}. "
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    
    # Use create_tool_calling_agent for Gemini as it supports function calling
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

def run_agent(user_input, chat_history=[]):
    from datetime import datetime
    try:
        agent = get_agent()
        today = datetime.now().strftime("%Y-%m-%d")
        response = agent.invoke({
            "input": user_input, 
            "date": today,
            "chat_history": chat_history
        })
        return response['output']
    except Exception as e:
        return f"Error running agent: {str(e)}"
