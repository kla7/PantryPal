import pandas as pd
import ast
import os
import json
from tqdm import tqdm

df_full = pd.read_csv("archive/RecipeNLG_dataset.csv") # load full dataset

df = df_full.iloc[:50000].copy() # first 50k entries
os.makedirs("processed", exist_ok=True)
df.to_csv("processed/RecipeNLG_50k.csv", index=False)

def clean_list_column(col): #cleans stringified lists
    return ast.literal_eval(col)

df = pd.read_csv("processed/RecipeNLG_50k.csv")

df['ingredients'] = df['ingredients'].apply(clean_list_column)
df['directions'] = df['directions'].apply(clean_list_column)

recipes = []
for _, row in tqdm(df.iterrows(), total=len(df)):
    title = row['title']
    # Use full ingredients with measurements
    ingredients = "\n".join(f"- {ing}" for ing in row['ingredients'])
    numbered_directions = [f"{i+1}. {sentence}" for i, sentence in enumerate(row['directions'])]
    directions = "\n".join(numbered_directions)
    recipes.append({
        "title": title,
        "ingredients": ingredients,
        "directions": directions
    })

with open("processed/recipes_50k.jsonl", "w") as f:
    for recipe in recipes:
        f.write(json.dumps(recipe) + "\n")

print(f"Created {len(recipes)} recipes with full ingredients.")