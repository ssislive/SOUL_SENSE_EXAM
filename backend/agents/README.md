# AI Agents (Wave 3)

This directory contains the modular AI agent system.

## Agents

| Agent          | File                | Purpose                   |
| -------------- | ------------------- | ------------------------- |
| Base           | `base.py`           | Base class for all agents |
| Assessment     | `assessment.py`     | Question selection        |
| Insight        | `insight.py`        | Score-to-text conversion  |
| Safety         | `safety.py`         | Crisis detection          |
| Planner        | `planner.py`        | Task planning (Wave 5)    |
| Virtual Friend | `virtual_friend.py` | Chat agent (Wave 6)       |

## Usage

```python
from agents.assessment import AssessmentAgent

agent = AssessmentAgent()
result = agent.process(user_context)
```
