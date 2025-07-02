import requests
import os
import base64
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from functools import lru_cache

# Get the directory where this file (inference.py) is located
current_dir = os.path.dirname(os.path.abspath(__file__))
cache_folder = os.path.join(current_dir, "sentence_transformer_cache")

@lru_cache(maxsize=1)
def get_model():
    print(f"Using model: Bert")
    device = torch.device("mps") if torch.backends.mps.is_built() else torch.device("cpu")
    # Specify a persistent cache directory
    os.makedirs(cache_folder, exist_ok=True)
    
    model = SentenceTransformer(
        'sentence-transformers/all-MiniLM-L6-v2',
        cache_folder=cache_folder
    )
    model.to(device)
    return model

model = get_model()

def get_text_embeddings(texts: list):
    """uses a pretrained sentence encoder from torch hub to get embeddings for a list of texts"""
    embeddings = model.encode(texts)
    return embeddings[0]

