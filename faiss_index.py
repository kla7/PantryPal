from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

chunks = []
with open("processed/recipe_chunks_50k.jsonl", "r") as f: # loading chunks
    for line in f:
        chunks.append(json.loads(line))

texts = [f"{c['title']}: {c['chunk']}" for c in chunks] # extract texts for embedding (e.g., combine title + chunk text)

model = SentenceTransformer("all-MiniLM-L6-v2") # load model (smallest one, i think)

batch_size = 8
all_embeddings = []

for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    emb = model.encode(batch, batch_size=batch_size, show_progress_bar=False)
    all_embeddings.extend(emb)

embeddings_np = np.array(all_embeddings).astype("float32")

index = faiss.IndexFlatL2(embeddings_np.shape[1]) # creating faiss index
index.add(embeddings_np)

faiss.write_index(index, "processed/recipe_index.faiss") # saving index to directory

with open("processed/recipe_metadata.json", "w") as f: #saving metadata
    json.dump(chunks, f)

print(f"Indexed {index.ntotal} recipe steps.")
