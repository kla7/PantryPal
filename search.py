import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import extract_ingredients

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("processed/recipe_index.faiss")
with open("processed/recipe_metadata.json", "r") as f:
    recipes = json.load(f)


def normalize_ingredient(ingredient: str) -> str:
    """
    Normalize ingredient strings by removing quantities, units, and formatting.
    :param ingredient: The ingredient to normalize.
    :return: The normalized ingredient.
    """
    ingredient = extract_ingredients.extract_ingredients(ingredient)
    return ingredient


def search_faiss_and_filter(model, index, recipes, user_ingredients, avoid_ingredients, user_keywords, mode="inclusive", top_k=10):
    """
    Retrieves search results given the user's search parameters.
    :param model: Embedding model
    :param index: FAISS index
    :param recipes: Recipe metadata
    :param user_ingredients: List of the user's search ingredients
    :param avoid_ingredients: List of ingredients the user would like to avoid
    :param user_keywords: Additional search keywords that the user can optionally add
    :param mode: Selection type, inclusive or exclusive
    :param top_k: The number of results to retrieve
    :return: The filtered search results
    """
    ingredient_query = ", ".join(user_ingredients)
    ingredient_embedding = model.encode(
        [ingredient_query], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False
    )[0].astype("float32")

    D, I = index.search(np.array([ingredient_embedding]), 1000)

    if user_keywords:
        keyword_emb = model.encode(
            [user_keywords], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False
        )[0].astype("float32")

        candidate_embs = np.array([index.reconstruct(int(idx)) for idx in I[0]])
        sims = candidate_embs @ keyword_emb

        sorted_indices = np.argsort(-sims)[:500]
        filtered = I[0][sorted_indices]
    else:
        filtered = I[0]

    user_set = set(normalize_ingredient(i) for i in user_ingredients)
    avoid_set = set(normalize_ingredient(i) for i in avoid_ingredients)
    results = []

    for idx in filtered:
        if idx == -1 or idx < 0 or idx >= len(recipes):
            continue

        recipe = recipes[idx]
        ingredient_lines = recipe["ingredients"].split("\n")
        recipe_ing_set = set(normalize_ingredient(line) for line in ingredient_lines if line.strip())

        if mode == "inclusive":
            ing_overlap = recipe_ing_set.intersection(user_set)
            avoid_overlap = recipe_ing_set.intersection(avoid_set)
            if len(ing_overlap) > 0 and len(avoid_overlap) == 0:
                results.append(recipe)

        elif mode == "exclusive":
            if recipe_ing_set.issubset(user_set):
                results.append(recipe)

        if len(results) >= top_k:
            break

    return results


def print_full_recipes(recipes: list) -> None:
    """
    Print the recipes in a more human-friendly format for testing purposes.
    :param recipes: A list of recipes from search results
    """
    if not recipes:
        print("No matching recipes found.")
        return
    for r in recipes:
        print(f"\n🧾 {r['title']}\n")
        print(f"Ingredients:\n{r['ingredients']}\n")
        print(f"Directions:\n{r['directions']}\n")
        print("=" * 60)


if __name__ == '__main__':
    # Example usage
    user_ing = ["onion", "garlic", "butter"]
    avoid_list = []
    mode = "inclusive"
    user_keywords = "sauce"
    top_k = 5

    matched_recipes = search_faiss_and_filter(model, index, recipes, user_ing, avoid_list, user_keywords, mode=mode, top_k=top_k)
    print_full_recipes(matched_recipes)
