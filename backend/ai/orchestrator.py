from ai.intent_agent import detect_intent
from integrations.aws_connector import get_aws_data
from integrations.github_connector import get_github_data, get_failed_workflow_logs
from integrations.saas_connector import get_saas_data
from ai.llm_client import generate_response

ROOT_CAUSE_KEYWORDS = ["why", "fail", "error", "broke", "root cause", "what went wrong", "investigate", "diagnose", "fix"]


def get_context_data(question: str) -> dict:
    """Fetch the right data source based on question intent."""
    q = question.lower()
    intent = detect_intent(question)

    if any(kw in q for kw in ROOT_CAUSE_KEYWORDS) and intent == "github":
        return get_failed_workflow_logs()
    elif intent == "aws":
        return get_aws_data()
    elif intent == "saas":
        return get_saas_data()
    return get_github_data()


async def process_query(question: str, history: list = None) -> str:
    data = get_context_data(question)
    return generate_response(str(data), question, history)
