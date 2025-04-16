import pandas as pd
import json
from tqdm import tqdm
from collections import Counter


def extract_data(input_file: str) -> None:
    """
    From the dataset, extract the data into JSON files for easier access.
    :param input_file: A string representing the name of the input file containing the raw dataset.
    """
    # get the total number of recipes for tqdm
    with open(input_file, 'r', encoding='utf-8') as f:
        total_rows = sum(1 for _ in f) - 1

    chunk_size = 10000
    total_chunks = (total_rows // chunk_size) + 1

    recipes_dict = {}
    ingredients_dict = {}

    use_cols = ['Unnamed: 0', 'title', 'ingredients', 'directions', 'link', 'source', 'NER']

    tqdm_iter = tqdm(
        pd.read_csv(input_file, usecols=use_cols, chunksize=chunk_size),
        desc='Extracting recipes',
        total=total_chunks,
        unit='chunk'
    )

    for chunk in tqdm_iter:
        for _, row in chunk.iterrows():
            recipe_id = str(row['Unnamed: 0'])
            measurements = eval(row['ingredients']) if isinstance(row['ingredients'], str) else row['ingredients']
            directions = eval(row['directions']) if isinstance(row['directions'], str) else row['directions']
            ingredients = eval(row['NER']) if isinstance(row['NER'], str) else row['NER']

            recipes_dict[recipe_id] = {
                'recipe_name': row['title'],
                'measurements': measurements,
                'directions': directions,
                'link': row['link'],
                'source': row['source'],
                'ingredients': ingredients
            }

            # for recording only the ingredients from the "NER" column
            ingredients_dict[recipe_id] = {
                'ingredients': ingredients
            }

    with open('../data/recipes.json', 'w', encoding='utf-8') as f:
        json.dump(recipes_dict, f, ensure_ascii=False, indent=2)

    print('Recipes extracted successfully.')

    with open('../data/ingredients.json', 'w', encoding='utf-8') as f:
        json.dump(ingredients_dict, f, ensure_ascii=False, indent=2)

    print('Ingredients extracted successfully.')


def extract_unique_ingredients(json_file: str) -> None:
    """
    From the JSON file containing the ingredients for each recipe, extract the unique ingredients and their counts.
    :param json_file: A string representing the name of the JSON file containing the full list of ingredients.
    """
    ingredients_counter = Counter()

    with open(json_file, 'r', encoding='utf-8') as f:
        ingredients_dict = json.load(f)

        tqdm_iter = tqdm(
            ingredients_dict.items(),
            desc='Extracting unique ingredients',
            total=len(ingredients_dict),
            unit='ingredient'
        )

        for _, value in tqdm_iter:
            for ingredient in value['ingredients']:
                ingredients_counter[ingredient] += 1

    print(f'# of total ingredients: {ingredients_counter.total()}')
    print(f'# of unique ingredients: {len(ingredients_counter)}')
    print(f'Top 50 most common ingredients: {ingredients_counter.most_common(50)}')

    with open('unique_ingredients.json', 'w', encoding='utf-8') as f:
        json.dump(ingredients_counter, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    # dataset from https://www.kaggle.com/datasets/paultimothymooney/recipenlg
    extract_data('../data/RecipeNLG_dataset.csv')
    extract_unique_ingredients('../data/ingredients.json')
