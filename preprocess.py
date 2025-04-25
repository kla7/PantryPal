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

df['NER'] = df['NER'].apply(clean_list_column)
df['directions'] = df['directions'].apply(clean_list_column)

chunks = []
for _, row in tqdm(df.iterrows(), total=len(df)): # chunking
    title = row['title']
    ingredients = ", ".join(row['NER'])
    for step_id, step in enumerate(row['directions']):
        chunks.append({
            "title": title,
            "ingredients": ingredients,
            "chunk": f"Step {step_id+1}: {step}"
        })

with open("processed/recipe_chunks_50k.jsonl", "w") as f: #save to json
    for chunk in chunks:
        f.write(json.dumps(chunk) + "\n")

print(f"Created {len(chunks)} chunks across 50,000 recipes.")