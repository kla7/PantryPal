import json
import csv
import re
import argparse

title_remove_list = [
    r'preserv\w* children',
    r'happy family',
    r'paints*\b( remover)?',
    r'cleaner\b',
    r'laundry',
    r'clay'
]

measurement_remove_list = [
    r'glue'
]


def clean_recipes(json_file: str, csv_file: str) -> None:
    """
    Remove recipes that are inedible.
    :param json_file: 'A json file containing the raw recipes.'
    :param csv_file: 'A csv file in which the cleaned recipes should be written.'
    :return:
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        recipes_dict = json.load(f)

    remove_ids = []

    for recipe_id, recipe in recipes_dict.items():
        recipe_name = recipe['recipe_name'].lower()

        if any(re.search(keyword, recipe_name) for keyword in title_remove_list):
            print(recipe_name)
            remove_ids.append(recipe_id)

    cleaned_recipes = []

    for recipe_id, recipe in recipes_dict.items():
        if recipe_id in remove_ids:
            continue
        cleaned_recipes.append({
            'Unnamed: 0': recipe_id,
            'title': recipe['recipe_name'],
            'ingredients': json.dumps(recipe['measurements']),
            'directions': json.dumps(recipe['directions']),
            'link': recipe['link'],
            'source': recipe['source'],
            'NER': json.dumps(recipe['ingredients']),
        })

    print(f'Removed {len(remove_ids)} recipes.')

    fieldnames = ['Unnamed: 0', 'title', 'ingredients', 'directions', 'link', 'source', 'NER']

    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for recipe in cleaned_recipes:
            writer.writerow(recipe)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='extract_ingredients.py',
        description='Extract ingredients from a file containing measurements.'
    )
    parser.add_argument(
        'input_json',
        type=str,
        help='A json file containing the raw recipes.'
    )
    parser.add_argument(
        'output_csv',
        type=str,
        help='A csv file in which the cleaned recipes should be written.'
    )
    args = parser.parse_args()

    json_input = args.input_json
    csv_output = args.output_csv

    clean_recipes(json_input, csv_output)
