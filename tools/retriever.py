from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def list_files_in_documents():
    folder_path = './documents'  
    files = os.listdir(folder_path)
    return files

def split_doc(file_name, chunk_size=500):
    with open(f"./documents/{file_name}", 'r', encoding='utf-8') as file:
        text = file.read()
        words = text.split()
        chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def get_embeddings(chunks):
    embeddings = []
    for chunk in chunks:
        response = client.embeddings.create(input=chunk, model="text-embedding-3-small")
        embeddings.append(response.data[0].embedding)
    return embeddings

def search_similar_chunk(query, chunks, embeddings, top_k=3):
    query_embedding = client.embeddings.create(input=query, model="text-embedding-3-small").data[0].embedding
    similarities = cosine_similarity([query_embedding], embeddings)[0]
    top_k_indices = similarities.argsort()[-top_k:][::-1]
    top_k_chunks = [(chunks[i], similarities[i]) for i in top_k_indices]
    return top_k_chunks