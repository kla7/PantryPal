import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("processed/recipe_index.faiss")
with open("processed/recipe_metadata.json", "r") as f:
    recipes = json.load(f)

flan_model_name = "google/flan-t5-base"  # You can also use flan-t5-large
flan_tokenizer = AutoTokenizer.from_pretrained(flan_model_name)
flan_model = AutoModelForSeq2SeqLM.from_pretrained(flan_model_name)

def prompt_flan(prompt, max_new_tokens=150):
    inputs = flan_tokenizer(prompt, return_tensors="pt", truncation=True)
    outputs = flan_model.generate(**inputs, max_new_tokens=max_new_tokens)
    return flan_tokenizer.decode(outputs[0], skip_special_tokens=True)

# Normalize ingredient strings by removing quantities, units, and formatting
def normalize_ingredient(ingredient):
    ingredient = ingredient.lower()
    ingredient = re.sub(r"[^a-zA-Z ]", "", ingredient)  # remove punctuation/numbers
    ingredient = re.sub(r"\b(?:cup|c|tbsp|tsp|teaspoon|tablespoon|pint|quart|oz|ounce|grams|g|ml|litre|l|lb|pound|dash|pinch|pkg|box|boxes|can|cans|qt)\b", "", ingredient)
    ingredient = re.sub(r"\b(?:softened|chopped|minced|sliced|diced|crushed|shredded|melted|beaten|large|small|medium|fresh|dry|ground)\b", "", ingredient)
    ingredient = re.sub(r"\s+", " ", ingredient).strip()
    return ingredient

with open("dietary_restriction_exclusion_lists.json", "r") as f:
    avoid_data = json.load(f)

# Build a flat set of ingredients to avoid based on selected allergies
def build_avoid_set(selected_allergies):
    avoid_ingredients = set()
    for allergy in selected_allergies:
        avoid_ingredients.update(
            normalize_ingredient(item) for item in avoid_data.get(allergy, [])
        )
    return avoid_ingredients

def search_faiss_and_filter(user_ingredients, selected_allergies, mode="inclusive", top_k=10):
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
        avoid_ingredients = build_avoid_set(selected_allergies)

        # Allergen check
        if avoid_ingredients and any(avoid in ing for avoid in avoid_ingredients for ing in recipe_ingredients_set):
            continue  # Skip recipes with allergens

        if mode == "inclusive":
            if all(any(user_ing in rec_ing for rec_ing in recipe_ingredients_set) for user_ing in user_set):
                results.append(recipe)

        elif mode == "exclusive":
            if all(any(rec_ing in user_ing for user_ing in user_set) for rec_ing in recipe_ingredients_set) and user_set:
                results.append(recipe)

        if len(results) >= top_k:
            break

    return results

def print_full_recipes(recipes, selected_allergies=None, user_prompt=None):
    if not recipes:
        print("No matching recipes found.")
        return

    avoid_set = build_avoid_set(selected_allergies or [])

    for r in recipes:
        print(f"\n🧾 {r['title']}\n")
        print(f"Ingredients:\n{r['ingredients']}\n")
        print(f"Directions:\n{r['directions']}\n")

        if avoid_set or user_prompt:
            # Construct the prompt dynamically
            allergy_part = ""
            if avoid_set:
                allergy_part = f" Avoid these ingredients: {', '.join(avoid_set)}."

            full_prompt = (
                f"{user_prompt or 'Modify the recipe.'}{allergy_part}\n\n"
                f"Ingredients:\n{r['ingredients']}\n\nDirections:\n{r['directions']}"
            )

            rewritten = prompt_flan(full_prompt, max_new_tokens=300)
            print(f"🤖 Modified Version:\n{rewritten}\n")

        print("=" * 60)


# --- Example usage ---
user_input = ["milk", "vanilla", "nuts"]
avoid_ingredients = ["gluten_intolerance"]  # this should match keys in avoid_list.json
mode = "inclusive"
top_k = 5

matched_recipes = search_faiss_and_filter(
    user_input,
    mode=mode,
    top_k=top_k,
    selected_allergies=avoid_ingredients
)

print_full_recipes(matched_recipes)