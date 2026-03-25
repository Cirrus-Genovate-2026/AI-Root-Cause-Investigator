from fastapi import APIRouter
from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str


async def process_query(q: str):
    """Process AI query"""
    # This will be enhanced with actual AI logic
    return "Your infrastructure is running smoothly. All systems operational."


router = APIRouter(prefix="/api", tags=["query"])


@router.post("/query")
async def query_ai(request: QueryRequest):
    """Process AI query about infrastructure"""
    response = await process_query(request.question)
    return {"response": response}


@router.post("/ai/query")
async def ai_query(request: QueryRequest):
    """AI query endpoint"""
    question = request.question.lower()
    
    responses = {
        "cost": "Your monthly AWS costs are $420, up 5% from last month. EC2 instances are your largest expense at $180/month.",
        "deployment": "Your latest deployment (v2.1.3) completed successfully 2 minutes ago. All tests passed.",
        "github": "You have 3 recent commits and 5 active workflows. Current build status: all passing.",
        "postman": "API health is at 98.5%. 42 endpoints are being monitored across 4 collections.",
        "default": "I can help you with infrastructure queries. Ask me about costs, deployments, API health, or resource status!"
    }
    
    for key, response in responses.items():
        if key in question:
            return {"response": response}
    
    return {"response": responses["default"]}
