import argparse

import pandas as pd
import json
import os
from tqdm import tqdm
from collections import Counter


def extract_data(input_file: str, output_dir: str) -> None:
    """
    From the dataset, extract the data into JSON files for easier access.
    :param input_file: A string representing the name of the input file containing the raw dataset.
    :param output_dir: A string representing the output directory.
    """
    file_name = os.path.splitext(args.input_csv)[0]

    # get the total number of recipes for tqdm
    with open(input_file, 'r', encoding='utf-8') as f:
        total_rows = sum(1 for _ in f) - 1

    chunk_size = 10000
    total_chunks = (total_rows // chunk_size) + 1

    recipes_dict = {}
    measurements_dict = {}
    directions_dict = {}
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

            measurements_dict[recipe_id] = {
                'measurements': measurements
            }

            directions_dict[recipe_id] = {
                'directions': directions
            }

            ingredients_dict[recipe_id] = {
                'ingredients': ingredients
            }

    with open(f'{output_dir}/{file_name}_recipes.json', 'w', encoding='utf-8') as f:
        json.dump(recipes_dict, f, ensure_ascii=False, indent=2)

    print('Recipes extracted successfully.')

    with open(f'{output_dir}/{file_name}_measurements.json', 'w', encoding='utf-8') as f:
        json.dump(measurements_dict, f, ensure_ascii=False, indent=2)

    print('Measurements extracted successfully.')

    with open(f'{output_dir}/{file_name}_directions.json', 'w', encoding='utf-8') as f:
        json.dump(directions_dict, f, ensure_ascii=False, indent=2)

    print('Directions extracted successfully.')

    with open(f'{output_dir}/{file_name}_ingredients.json', 'w', encoding='utf-8') as f:
        json.dump(ingredients_dict, f, ensure_ascii=False, indent=2)

    print('Ingredients extracted successfully.')

    print('Data extraction complete!')


def extract_unique_ingredients(json_file: str, output_dir: str) -> None:
    """
    From the JSON file containing the ingredients for each recipe, extract the unique ingredients and their counts.
    :param json_file: A string representing the name of the JSON file containing the full list of ingredients.
    :param output_dir: A string representing the output directory.
    """
    file_name = os.path.splitext(args.input_csv)[0]

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

    with open(f'{output_dir}/{file_name}_unique_ingredients.json', 'w', encoding='utf-8') as f:
        json.dump(ingredients_counter, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='extract_dataset.py',
        description='Extracts the data from a .csv file containing the raw dataset.'
    )
    parser.add_argument(
        'input_csv',
        type=str,
        help='A string representing the name of the input .csv file containing the raw dataset to be extracted.'
    )
    parser.add_argument(
        'output_dir',
        type=str,
        help='A string representing the name of the output directory.'
    )
    parser.add_argument(
        '-e', '--extract_data',
        action='store_true',
        help='A boolean determining whether data should be extracted from the raw dataset.'
    )
    parser.add_argument(
        '-g', '--get_unique_ingredients',
        action='store_true',
        help='A boolean determining whether unique ingredients should be extracted from ingredients.json. '
             'Default is False'
    )
    args = parser.parse_args()

    file_name = os.path.splitext(args.input_csv)[0]

    if args.extract_data:
        extract_data(args.input_csv, args.output_dir)

    ingredients_json = f'{args.output_dir}/{file_name}_ingredients.json'

    if args.get_unique_ingredients:
        if os.path.exists(ingredients_json):
            extract_unique_ingredients(ingredients_json, args.output_dir)
        else:
            print(f'No unique ingredients found for {file_name}.')
