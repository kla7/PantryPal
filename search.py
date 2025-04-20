import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline

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

# # example
# user_input = ["milk", "vanilla", "nuts"]

# inclusive_results = search_recipes(user_input, mode="inclusive", top_k=10)
# exclusive_results = search_recipes(user_input, mode="exclusive", top_k=10)

# print("Inclusive Results:")
# for r in inclusive_results:
#     print(f" - {r['title']} → {r['chunk']}")

# print("\n Exclusive Results:")
# for r in exclusive_results:
#     print(f" - {r['title']} → {r['chunk']}")

# 1. Get user input
user_input = ["milk", "vanilla", "nuts"]
mode = "inclusive"
top_k = 5

# 2. Search the FAISS index
retrieved_chunks = search_recipes(user_input, mode=mode, top_k=top_k)

# 3. Build a prompt using the retrieved results
def build_prompt(user_ingredients, retrieved_chunks):
    context = "\n".join([f"{chunk['title']}: {chunk['chunk']}" for chunk in retrieved_chunks])
    prompt = f"""You are a helpful recipe assistant.

User Ingredients: {", ".join(user_ingredients)}

Here are some relevant recipe snippets:
{context}

Using these, write a new, complete recipe that uses the given ingredients. Be creative but stay practical.

Generated Recipe:"""
    return prompt

# 4. Load a text generation pipeline (using a small CPU-friendly model)
generator = pipeline("text-generation", model="google/flan-t5-base")  # Swap out for bigger ones later

# 5. Generate the recipe
prompt = build_prompt(user_input, retrieved_chunks)
output = generator(prompt, max_new_tokens=300, do_sample=True, temperature=0.8)

# 6. Show the result
print("\n🍽️ Suggested Recipe:\n")
print(output[0]['generated_text'])

