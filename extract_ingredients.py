import re
import json
import argparse

units = {'c', 'cup', 'cups', 't', 'tsp', 'teaspoon', 'teaspoons', 'tbsp', 'tablespoon', 'tablespoons',
         'oz', 'ounce', 'ounces', 'lb', 'lbs', 'pound', 'pounds', 'can', 'cans', 'jar', 'jars',
         'carton', 'cartons', 'pkg', 'pkgs', 'package', 'packages', 'container', 'containers',
         'box', 'boxes', 'bag', 'bags', 'slice', 'slices', 'bottle', 'bottles', 'bottled',
         'stick', 'sticks', 'bunch', 'bunches', 'qt', 'qts', 'quart', 'quarts', 'sq',
         'whole', 'sm', 'small', 'medium', 'large', 'to', 'each', 'a', 'pinch', 'pinches',
         'dash', 'dashes', 'ear', 'ears', 'plus', 'level', 'san', 'drop', 'drops', 'shake', 'shakes',
         'gal', 'gallon', 'gallons', 'pieces', 'wedge', 'wedges', 'clove', 'cloves', 'pt', 'pint', 'pints'}

phrases = {'to taste', 'for garnish', 'if desired', 'as desired', 'to cover top'}


def remove_phrases(text: str) -> str:
    """
    For each measurement, remove unnecessary phrases to retain just the ingredient.
    :param text: A measurement containing an ingredient.
    :return: Text with the phrase removed.
    """
    for phrase in phrases:
        text = re.sub(r'\b' + re.escape(phrase) + r'\b', '', text)
    return text


def extract_ingredients(line: str) -> str:
    """
    For each measurement, extract the ingredient by removing numbers and units.
    :param line: A measurement containing an ingredient.
    :return: The extracted ingredient.
    """
    text = line.lower()

    if ',' in text:
        text = text.split(',')[0]

    text = re.sub(r'[\(\[].*?[\)\]]', '', text)

    text = remove_phrases(text)

    text = re.sub(r'\d+(?!-[a-z])', '', text)
    text = re.sub(r"[^a-z0-9\-\s,'&]", '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    tokens = text.split()

    filtered = [
        tok for i, tok in enumerate(tokens)
        if not (tok in units and not (tok in units and i == len(tokens) - 1))
    ]

    if filtered and (filtered[0] == 'of' or filtered[0] == 'or' or filtered[0] == '-'):
        filtered = filtered[1:]

    if filtered and (filtered[-1] == 'of' or filtered[-1] == 'or' or filtered[0] == '-'):
        filtered = filtered[:-1]

    return ' '.join(filtered)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='extract_ingredients.py',
        description='Extract ingredients from a file containing measurements.'
    )
    parser.add_argument(
        'input_json',
        type=str,
        help='A json file containing the measurements.'
    )
    parser.add_argument(
        'output_json',
        type=str,
        help='A json file in which the extracted ingredients should be written.'
    )
    args = parser.parse_args()

    json_file = args.input_json
    output_file = args.output_json
    ingredients_dict = {}

    with open(json_file, 'r', encoding='utf-8') as f:
        recipes_dict = json.load(f)

    for recipe_id, measurements in recipes_dict.items():
        if recipe_id not in ingredients_dict:
            ingredients_dict[recipe_id] = []
        for measurement in measurements['measurements']:
            ingredient = extract_ingredients(measurement)
            if ingredient:
                ingredients_dict[recipe_id].append(ingredient)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ingredients_dict, f, indent=2, ensure_ascii=False)


