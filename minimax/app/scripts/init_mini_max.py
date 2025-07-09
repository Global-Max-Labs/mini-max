import csv
import lancedb
import os
import pyarrow as pa
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from minimax.app.services.inference import get_text_embeddings
from minimax.app.core.config import settings

DB_PATH = settings.DB_PATH

def create_new_data_collection():
    # Create or connect to a LanceDB database
    db = lancedb.connect(DB_PATH)
    # Create a table for init_qa_action if it doesn't exist
    if "init_qa_action" not in db.table_names():
        # Create a proper PyArrow schema instead of a dictionary
        schema = pa.schema([
            pa.field("content", pa.string()),
            pa.field("content_embedding", pa.list_(pa.float32(), 384)),
            pa.field("space", pa.string()),
            pa.field("model_name", pa.string()),
            pa.field("metadata", pa.struct([
                pa.field("use_cases", pa.struct([
                    pa.field("chatbot", pa.struct([
                        pa.field("answer", pa.string()),
                        pa.field("action", pa.string())
                    ]))
                ]))
            ])),
            pa.field("cache", pa.bool_())
        ])
        db.create_table("init_qa_action", schema=schema)
    
    print("Data collection 'init_qa_action' created")
    return "init_qa_action"


def delete_data_collection():
    # Connect to the database
    db = lancedb.connect(DB_PATH)
    
    # Drop the table if it exists
    if "init_qa_action" in db.table_names():
        db.drop_table("init_qa_action")
        print("Data collection 'init_qa_action' deleted")
    else:
        print("No data collection to delete")


def get_all_text():
    texts = []
    # Use a path relative to the script location instead of the current working directory
    script_dir = Path(__file__).parent
    init_qa_action_path = (script_dir / "test_text.csv").resolve()
    print(f"Looking for CSV at: {init_qa_action_path}")
    
    if not init_qa_action_path.exists():
        raise FileNotFoundError(f"CSV file not found at {init_qa_action_path}")
        
    with open(init_qa_action_path, "r") as f:
        csv_texts = csv.DictReader(f)
        for text in csv_texts:
            print(text)
            texts.append(text)
    return texts


def save_all_text(data_collection_id, texts):
    # Connect to the database
    db = lancedb.connect(DB_PATH)
    
    # Get the table
    table = db.open_table(data_collection_id)
    
    # Prepare data for insertion
    records = []
    for text in texts:
        record = {
            "content": text["question"],
            "content_embedding": get_text_embeddings([text["question"]]),
            "space": "chatbot",
            "model_name": "use",
            "metadata": {"use_cases": {"chatbot": {"answer": text["answer"], "action": text["action"]}}},
            "cache": True
        }
        records.append(record)
    
    # Add data to the table
    if records:
        table.add(records)
    
    print("Text saved")


def delete_all_text(data_collection_id="init_qa_action"):
    # Connect to the database
    db = lancedb.connect(DB_PATH)
    
    # Get the table and clear it
    if data_collection_id in db.table_names():
        table = db.open_table(data_collection_id)
        # In LanceDB, we recreate the table to clear it
        schema = table.schema
        db.drop_table(data_collection_id)
        db.create_table(data_collection_id, schema=schema)
        print("All text deleted")
    else:
        print(f"Table {data_collection_id} does not exist")


def initialize():
    data_collection_id = create_new_data_collection()
    texts = get_all_text()
    save_all_text(data_collection_id, texts)
    print('Done')


def remove_init():
    delete_data_collection()
    # No need to separately delete texts as they're part of the collection


if __name__ == "__main__":
    remove_init()
    initialize()
