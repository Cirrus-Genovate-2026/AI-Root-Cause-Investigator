from ai.intent_agent import detect_intent
from integrations.aws_connector import get_aws_cost
from integrations.github_connector import get_github_data
from integrations.saas_connector import get_saas_data
from ai.llm_client import generate_response


async def process_query(question: str):

    intent = detect_intent(question)

    data = {}

    if intent == "aws":
        data = get_aws_cost()

    elif intent == "github":
        data = get_github_data()

    elif intent == "saas":
        data = get_saas_data()

    else:
        return "Sorry, I couldn't understand the request."

    ai_response = generate_response(str(data), question)

    return ai_response