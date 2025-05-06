import uuid
import json
import numpy as np
from fastapi import APIRouter, Request
from apps.nlp_router.src.models.text import TextSearchRequest

router = APIRouter()


@router.post("/api/text/chat/", tags=["text"])
async def search_similar_text(req: TextSearchRequest):
    # resp = get_ranked_distance(req.content, req.space)
    resp = [["hello", "0.5"]]
    score = resp[0][1]
    try:
        answer = {"answer": "Please connect me to bubble network"}
        print("score: ", float(score))
        if float(score) < 0.55:
        # if float(score) < 0.24:
            print("score from user query", float(score))
            answer = json.loads(resp[0][0].metadata)["use_cases"]["chatbot"] # change this to return chatbot, to include answer and action. then add action as a third column in th csv file.
    except KeyError as exc:
        print(exc)

    return answer
