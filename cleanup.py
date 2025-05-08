import json
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

ingredients_remove_list = [
    r'glue'
]


def clean_recipes(jsonl_input: str, jsonl_output: str) -> None:
    """
    Remove recipes that are inedible.
    :param jsonl_input: 'A .jsonl file containing the raw recipes.'
    :param jsonl_output: 'A .jsonl file in which the cleaned recipes should be written.'
    """
    recipes = []
    cleaned_recipes = []

    with open(jsonl_input, 'r', encoding='utf-8') as f:
        for line in f:
            recipes.append(json.loads(line))

    for recipe in recipes:
        recipe_name = recipe['title'].lower()
        recipe_ingredients = recipe['ingredients'].lower()

        if any(re.search(keyword, recipe_name) for keyword in title_remove_list):
            print(recipe_name)
            continue

        if any(re.search(keyword, recipe_ingredients) for keyword in ingredients_remove_list):
            print(recipe_ingredients)
            continue

        cleaned_recipes.append(recipe)

    with open(jsonl_output, 'w', encoding='utf-8') as f:
        for recipe in cleaned_recipes:
            f.write(json.dumps(recipe) + '\n')

    print(f'Removed {len(recipes) - len(cleaned_recipes)} recipes.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='extract_ingredients.py',
        description='Extract ingredients from a file containing measurements.'
    )
    parser.add_argument(
        'input_jsonl',
        type=str,
        help='A .jsonl file containing the raw recipes.'
    )
    parser.add_argument(
        'output_jsonl',
        type=str,
        help='A .jsonl file in which the cleaned recipes should be written.'
    )
    args = parser.parse_args()

    jsonl_input = args.input_jsonl
    jsonl_output = args.output_jsonl

    clean_recipes(jsonl_input, jsonl_output)
