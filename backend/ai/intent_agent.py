def detect_intent(question: str):

    q = question.lower()

    if ("aws" in q or "ec2" in q or "cost" in q or "cloud" in q or "instance" in q
            or "s3" in q or "rds" in q or "database" in q or "db" in q
            or "bucket" in q or "lambda" in q or "server" in q or "infrastructure" in q):
        return "aws"

    elif ("github" in q or "repo" in q or "commit" in q or "deployment" in q
          or "workflow" in q or "pipeline" in q or "ci" in q or "cd" in q
          or "build" in q or "branch" in q or "pull request" in q or "pr" in q
          or "issue" in q or "health" in q or "status" in q or "deploy" in q):
        return "github"

    elif "postman" in q or "saas" in q or "api" in q or "test" in q or "collection" in q:
        return "saas"

    return "github"