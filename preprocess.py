import pandas as pd
import ast
import os
import json
from tqdm import tqdm
import argparse


def preprocess(input_csv, output_dir):
    df_full = pd.read_csv(input_csv)  # load full dataset

    df = df_full.iloc[:50000].copy()  # first 50k entries
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(f"{output_dir}/RecipeNLG_50k.csv", index=False)


    def clean_list_column(col):
        """
        Cleans stringified lists
        """
        return ast.literal_eval(col)


    df = pd.read_csv(f"{output_dir}/RecipeNLG_50k.csv")

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

    with open(f"{output_dir}/recipes_50k.jsonl", "w") as f:
        for recipe in recipes:
            f.write(json.dumps(recipe) + "\n")

    print(f"Created {len(recipes)} recipes with full ingredients.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='preprocess.py',
        description='Preprocesses the data by retrieving the first 50k entries.'
    )
    parser.add_argument(
        'input_csv',
        type=str,
        help='A string representing the name of the input .csv file containing the raw dataset to be preprocessed.'
    )
    parser.add_argument(
        'output_dir',
        type=str,
        help='A string representing the name of the output directory.'
    )
    args = parser.parse_args()

    preprocess(args.input_csv, args.output_dir)
