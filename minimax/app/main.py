import os
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
import lancedb
from minimax.app.core.config import settings
from minimax.app.scripts.init_mini_max import remove_init, initialize
from minimax.app.services.inference import get_text_embeddings
from minimax.app.core.config import settings

app = FastAPI()

# app.include_router(data_collection.router)
# app.include_router(text.router)


@app.get("/")
async def root():
    return {"New Phone": "Who Dis?"}


class TextSearchRequest(BaseModel):
    content: str
    space: str


@app.post("/api/text/chat/", tags=["text"])
async def search_similar_text(req: TextSearchRequest):
    # Connect to LanceDB
    db = lancedb.connect(settings.DB_PATH)
    
    try:
        table = db.open_table("init_qa_action")
        count = table.count_rows()
        print(count)
        if count == 0:
            remove_init()
            initialize()
            table = db.open_table("init_qa_action")
    except Exception as e:
        print("Table 'init_qa_action' not found, creating with default values...")
        remove_init()
        initialize()
        table = db.open_table("init_qa_action")

    embedding = get_text_embeddings([req.content])
    
    # Search for similar text using the content
    results = table.search(embedding, vector_column_name="content_embedding").limit(1).to_list()
    
    try:
        if results:
            result = results[0]
            score = result["_distance"]
            print("score: ", score)
            
            if score < 0.55:
            # if score < 0.55:
                print("score from user query", score)
                answer = result["metadata"]["use_cases"]["chatbot"]
            else:
                answer = {"answer": "I'm not sure how to help with that", "action": ""}
        else:
            answer = {"answer": "No matching response found", "action": ""}
            
    except KeyError as exc:
        print(exc)
        answer = {"answer": "Error processing request", "action": ""}

    return answer

