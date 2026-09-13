# LifeLedger

🔗 **Live Demo:** `https://your-app-url.here` — click 'Simulate' to see the agent process a bill, a scheduling request, and a flagged invoice in real time.
*(Note: Replace the URL above with the actual deployed URL once hosted on AWS App Runner)*

LifeLedger is an autonomous background AI agent built using the Strands Agents SDK (Python). It handles recurring life-admin tasks like bills, scheduling, and repetitive paperwork, only surfacing to the user when a real decision is needed.

## Architecture

1. **Intake / Memory Layer**: SQLite (`user_profile_store.py`) holding recurring patterns and confidence scores.
2. **Tools**: Tools registered using `@tool` for detecting, classifying, and executing tasks. Includes mocks for payment and calendar systems.
3. **Agent Orchestration**: Handled by the `LifeLedger` agent with a strict decision tree defined in the system prompt.

## Decision Logic

Every incoming item is evaluated based on the User Profile:
- **Routine**: Matched pattern with high confidence (e.g., standard monthly electric bill). Silently executed.
- **Needs Nudge**: New but low-risk pattern (e.g., scheduling a dentist appointment). Proposed actions prepared, awaits one-tap confirmation.
- **Needs Review**: Significant deviation from historical norm (e.g., 60% higher invoice). Flagged for full manual review with context.

## Local Setup

1. Install dependencies (Requires Python 3.11+):
   ```bash
   pip install -r requirements.txt
   ```
2. Run the command-line demo scenarios script:
   ```bash
   python demo_scenarios.py
   ```
3. Run the interactive web interface:
   ```bash
   python app.py
   ```
4. Open `http://localhost:8000` in your browser.

## Deployment

This app includes an `apprunner.yaml` for AWS App Runner deployment (preferred for this hackathon) and a `Procfile` for platforms like Heroku/Railway. 

To deploy to AWS App Runner:
1. Connect your GitHub repository to AWS App Runner.
2. Select the "Configuration file" option to use `apprunner.yaml`.
3. Deploy!
