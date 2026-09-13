from lifeledger_agent import run_agent, notifications

def run_demo():
    print("--- Running Scenario A: Routine Bill ---")
    run_agent("Here is your routine electric bill email identical in amount to the past 3 months for ElectricCo.")
    
    print("\n--- Running Scenario B: Scheduling Nudge ---")
    run_agent("You have a dentist appointment reminder needing rescheduling.")
    
    print("\n--- Running Scenario C: High Invoice ---")
    run_agent("New, unusually large invoice from MegaCorp for $5000 (60% above average).")
    
    print("\n--- Current Notifications ---")
    for n in notifications:
        print(f"[{n['urgency'].upper()}] {n['message']}")
        print(f"  Action Required: {n['action_required']} | Status: {n['status']}")
        print()

if __name__ == "__main__":
    run_demo()
