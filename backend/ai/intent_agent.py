def detect_intent(question: str):

    q = question.lower()

    if "aws" in q or "ec2" in q or "cost" in q:
        return "aws"

    elif "github" in q or "repo" in q or "deployment" in q:
        return "github"

    elif "postman" in q or "saas" in q:
        return "saas"

    return "unknown"

def detect_intent(question: str):

    q = question.lower()

    if "aws" in q or "cost" in q:
        return "aws"

    elif "github" in q or "commit" in q or "deployment" in q or "workflow" in q:
        return "github"

    elif "postman" in q or "saas" in q:
        return "saas"

    return "unknown"