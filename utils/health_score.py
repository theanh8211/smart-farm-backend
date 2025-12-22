from datetime import datetime, timedelta
from models.agent import Agent

def calculate_health_score(agent: Agent) -> int:
    score = 100
    if not agent.is_online:
        score -= 40
    if agent.last_seen:
        if datetime.utcnow() - agent.last_seen > timedelta(minutes=30):
            score -= 30
        if datetime.utcnow() - agent.last_seen > timedelta(hours=6):
            score = max(0, score - 30)
    return max(0, score)