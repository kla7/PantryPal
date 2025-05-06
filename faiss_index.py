from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

recipes = []
with open("processed/recipes_50k.jsonl", "r") as f: #load recipes
    for line in f:
        recipes.append(json.loads(line))

texts = [f"{r['title']}: {r['ingredients']}\n{r['directions']}" for r in recipes] #texts for embedding

model = SentenceTransformer("all-MiniLM-L6-v2") #embedding model

batch_size = 8
all_embeddings = []

for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    emb = model.encode(batch, batch_size=batch_size, show_progress_bar=False)
    all_embeddings.extend(emb)

embeddings_np = np.array(all_embeddings).astype("float32")

index = faiss.IndexFlatL2(embeddings_np.shape[1]) #creating FAISS index
index.add(embeddings_np)

faiss.write_index(index, "processed/recipe_index.faiss")

with open("processed/recipe_metadata.json", "w") as f:
    json.dump(recipes, f)

print(f"Indexed {index.ntotal} full recipes.")