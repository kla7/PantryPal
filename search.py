import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("processed/recipe_index.faiss") #load index
with open("processed/recipe_metadata.json", "r") as f:
    chunks = json.load(f) #load chunks

def search_recipes(user_ingredients, mode, top_k=10):
    query = ", ".join(user_ingredients)
    embedding = model.encode([query], normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True, device="cpu")[0].astype("float32")

    D, I = index.search(np.array([embedding]), top_k * 50) # retrieve top_k * 50 to cast a wider net

    results = []
    user_set = set(i.strip().lower() for i in user_ingredients)

    for idx in I[0]:
        if idx == -1: #if it cannot find enough recipes
            continue

        if idx < 0 or idx >= len(chunks): #bounds check
            continue

        try:
            chunk = chunks[idx]
            recipe_ingredients = set(i.strip().lower() for i in chunk["ingredients"].split(", "))
        except Exception as e:
            print(f"Failed to process index {idx}: {e}")
            continue

        if mode == "inclusive":
            if recipe_ingredients & user_set:  # at least one match
                results.append(chunk)

        elif mode == "exclusive":
            if recipe_ingredients.issubset(user_set) and recipe_ingredients & user_set:
                results.append(chunk)


    return results[:top_k]

# example
user_input = ["milk", "vanilla", "nuts"]

inclusive_results = search_recipes(user_input, mode="inclusive", top_k=10)
exclusive_results = search_recipes(user_input, mode="exclusive", top_k=10)

print("Inclusive Results:")
for r in inclusive_results:
    print(f" - {r['title']} → {r['chunk']}")

print("\n Exclusive Results:")
for r in exclusive_results:
    print(f" - {r['title']} → {r['chunk']}")

