import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import re

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("processed/recipe_index.faiss")
with open("processed/recipe_metadata.json", "r") as f:
    recipes = json.load(f)

# Normalize ingredient strings by removing quantities, units, and formatting
def normalize_ingredient(ingredient):
    ingredient = ingredient.lower()
    ingredient = re.sub(r"[^a-zA-Z ]", "", ingredient)  # remove punctuation/numbers
    ingredient = re.sub(r"\b(?:cup|c|tbsp|tsp|teaspoon|tablespoon|pint|quart|oz|ounce|grams|g|ml|litre|l|lb|pound|dash|pinch|pkg|box|boxes|can|cans|qt)\b", "", ingredient)
    ingredient = re.sub(r"\b(?:softened|chopped|minced|sliced|diced|crushed|shredded|melted|beaten|large|small|medium|fresh|dry|ground)\b", "", ingredient)
    ingredient = re.sub(r"\s+", " ", ingredient).strip()
    return ingredient


def search_faiss_and_filter(user_ingredients, mode="inclusive", top_k=10):
    query = ", ".join(user_ingredients)
    embedding = model.encode(
        [query], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False
    )[0].astype("float32")

    D, I = index.search(np.array([embedding]), top_k * 50)

    user_set = set(normalize_ingredient(i) for i in user_ingredients)
    results = []

    for idx in I[0]:
        if idx == -1 or idx < 0 or idx >= len(recipes):
            continue

        recipe = recipes[idx]
        ingredient_lines = recipe["ingredients"].split("\n")
        recipe_ingredients_set = set(normalize_ingredient(line) for line in ingredient_lines if line.strip())

        if mode == "inclusive":
            if all(any(user_ing in rec_ing for rec_ing in recipe_ingredients_set) for user_ing in user_set):
                results.append(recipe)

        elif mode == "exclusive":
            if all(any(rec_ing in user_ing for user_ing in user_set) for rec_ing in recipe_ingredients_set) and user_set:
                results.append(recipe)

        if len(results) >= top_k:
            break

    return results

def print_full_recipes(recipes):
    if not recipes:
        print("No matching recipes found.")
        return
    for r in recipes:
        print(f"\n🧾 {r['title']}\n")
        print(f"Ingredients:\n{r['ingredients']}\n")
        print(f"Directions:\n{r['directions']}\n")
        print("=" * 60)

# Example usage
user_input = ["milk", "vanilla", "nuts"]
mode = "inclusive"
top_k = 5

matched_recipes = search_faiss_and_filter(user_input, mode=mode, top_k=top_k)
print_full_recipes(matched_recipes)