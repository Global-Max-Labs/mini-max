import requests
import os
import base64
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# Check if MPS is available and set device
device = torch.device("mps") if torch.backends.mps.is_built() else torch.device("cpu")

MODEL = os.environ.get("TEXT_MODEL", "use")
print(f"Using model: Bert")

# Load the pre-trained model from Hugging Face and send it to the MPS device
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.to(device)

def get_text_embeddings(texts: list):
    """uses a pretrained sentence encoder from torch hub to get embeddings for a list of texts"""
    embeddings = model.encode(texts)
    return embeddings[0]

