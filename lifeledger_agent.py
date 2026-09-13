import json
import uuid
from datetime import datetime

# Assuming strands-agents SDK for agent + tool orchestration
try:
    from strands_agents import Agent, tool
except ImportError:
    # Mocking for the sake of the environment if not installed
    def tool(func):
        return func
    class Agent:
        def __init__(self, system_prompt, tools):
            self.system_prompt = system_prompt
            self.tools = {t.__name__: t for t in tools}
        def run(self, input_text: str):
            pass

from user_profile_store import UserProfileStore

store = UserProfileStore()
notifications = []

@tool
def detect_bill(email_text: str) -> dict:
    """Parses an email/text for vendor, amount, due date; returns structured bill data."""
    text_lower = email_text.lower()
    if "electric" in text_lower:
        return {"vendor": "ElectricCo", "amount": 100, "due_date": "2023-11-01", "type": "bill"}
    elif "megacorp" in text_lower or "invoice" in text_lower:
        return {"vendor": "MegaCorp", "amount": 5000, "due_date": "2023-11-15", "type": "bill"}
    return {"vendor": "Unknown", "amount": 0, "due_date": "", "type": "bill"}

@tool
def classify_bill_routine(bill: dict, user_profile: dict) -> str:
    """Compares the new bill to historical patterns for that vendor."""
    if not user_profile:
        return "needs_review"
    
    amount = bill.get("amount", 0)
    amount_range = user_profile.get("amount_range", [0, 0])
    
    if amount_range[0] <= amount <= amount_range[1] and user_profile.get("confidence", 0) > 90:
        return "routine"
    elif amount > amount_range[1] * 1.5:
        return "needs_review"
    else:
        return "needs_nudge"

@tool
def pay_bill(bill: dict) -> dict:
    """Simulated/mock payment execution tool."""
    return {"status": "paid", "bill": bill, "tx_id": str(uuid.uuid4())}

@tool
def detect_scheduling_request(message_text: str) -> dict:
    """Parses a message for meeting/appointment intent."""
    text_lower = message_text.lower()
    if "dentist" in text_lower:
        return {"event_type": "dentist", "timeframe": "next week", "participants": ["Dr. Smith"], "type": "scheduling"}
    return {"event_type": "meeting", "timeframe": "soon", "participants": [], "type": "scheduling"}

@tool
def propose_times(event: dict, calendar: dict) -> list:
    """Cross-references a mock calendar and returns 2-3 proposed time slots."""
    return ["2023-10-24 10:00 AM", "2023-10-25 02:00 PM", "2023-10-26 11:00 AM"]

@tool
def book_event(event: dict, chosen_time: str) -> dict:
    """Simulated calendar-booking tool."""
    return {"status": "booked", "event": event, "time": chosen_time}

@tool
def detect_recurring_form(text: str, user_profile: dict) -> dict:
    """Matches incoming form/paperwork requests against previously seen form types."""
    return {"form_type": "tax_doc", "match": True}

@tool
def prefill_form(form_type: str, user_profile: dict) -> dict:
    """Returns a pre-filled form payload ready for user confirmation."""
    return {"form_type": form_type, "data": {"name": "User", "id": "123"}, "status": "prefilled"}

@tool
def notify_user(message: str, urgency: str, action_required: bool) -> dict:
    """The single "surface to human" tool."""
    task_id = str(uuid.uuid4())
    notification = {
        "task_id": task_id,
        "message": message,
        "urgency": urgency,
        "action_required": action_required,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending" if action_required else "logged"
    }
    notifications.append(notification)
    return notification

@tool
def log_decision(task_id: str, outcome: str, user_feedback: str) -> None:
    """Updates the confidence score and pattern history for future runs."""
    store.log_decision(task_id, outcome, user_feedback)
    
system_prompt = """You are LifeLedger, a background life-admin agent. Your job is to 
silently handle recurring bills, scheduling, and paperwork for the 
user. You must NEVER take irreversible action (paying money, booking 
commitments) unless: (a) the task matches a well-established routine 
pattern with high confidence, and the user has previously approved 
near-identical tasks multiple times, or (b) the user has explicitly 
approved this specific instance. When in doubt, always classify as 
needs_review rather than routine. Be concise and specific in every 
notification — always state what you found, what you propose, and 
what one action the user needs to take, if any.

Step 1: Classify the task type (bill / scheduling / form / unknown).
Step 2: Run the appropriate detect_* tool to extract structured data.
Step 3: Run the classify_*_routine logic to bucket it into:
    a) ROUTINE → auto-execute the corresponding action tool (pay_bill / book_event / prefill+submit_form) WITHOUT asking the user. Then call notify_user with urgency="info", action_required=False as a passive log entry only.
    b) NEEDS_NUDGE → prepare the action but do NOT execute it. Call notify_user with a clear one-tap decision and urgency="normal", action_required=True.
    c) NEEDS_REVIEW → do not prepare or execute anything irreversible. Call notify_user with full context and reasoning, urgency="high", action_required=True.
Step 4: On receiving user response (approve/deny/modify), log_decision updates the pattern confidence score.
"""

tools_list = [
    detect_bill, classify_bill_routine, pay_bill,
    detect_scheduling_request, propose_times, book_event,
    detect_recurring_form, prefill_form,
    notify_user, log_decision
]

agent = Agent(system_prompt=system_prompt, tools=tools_list)

def process_message_mock(text: str):
    """
    Since we don't have a real strands-agents LLM loop hooked up to a live model here,
    we mock the orchestration logic as requested by the prompt for the demo scenarios.
    """
    text_lower = text.lower()
    if "electric" in text_lower:
        bill = detect_bill(text)
        prof = store.get_pattern("electric_bill")
        classification = classify_bill_routine(bill, prof)
        if classification == "routine":
            pay_bill(bill)
            notify_user("Auto-paid ElectricCo bill of $100. Matched historical pattern.", "info", False)
    elif "dentist" in text_lower:
        req = detect_scheduling_request(text)
        times = propose_times(req, {})
        notify_user(f"Dentist appointment reminder detected. 3 time slots proposed: {', '.join(times)} — confirm one?", "normal", True)
    elif "invoice" in text_lower or "megacorp" in text_lower:
        bill = detect_bill(text)
        notify_user("This bill is 60% higher than your average for MegaCorp. Needs manual review before payment.", "high", True)
    else:
        notify_user("Unknown request received.", "normal", True)

def run_agent(text: str):
    process_message_mock(text)
