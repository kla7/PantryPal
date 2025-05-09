# PantryPal

**Authors:** Joyce Guo, Kasey La, Sohini Roy

PantryPal is an application that functions as a recipe recommendation system. It is meant to be useful for users that
have many ingredients but don’t know what to make with them. PantryPal suggests what recipe to make, along with the
full ingredient list and directions of the recipe, depending on the user input of ingredients.

## Instructions

The instructions for running the app are as follows:

### Requirements

* Python 3.10 or higher
* Install dependencies from [requirements.txt](https://github.com/kla7/PantryPal/blob/main/requirements.txt)

### Streamlit

To run the app:
* In your terminal, run
```
streamlit run app.py
```

* The default server is http://localhost:8501/

## App Features

* A select box where users can choose as many ingredients as they would like to include in their search.
* **Selection types:** Inclusive or exclusive search.
  * **Inclusive:** Recipes shown will include ingredients outside of the selected ingredients. 
  * **Exclusive:** Recipes shown will only contain ingredients from the selected ingredients.
* Filter options:
  * **Search keywords:** Keywords that the user can input, such as "pasta" or "Chinese", for more refined search
  results.
  * **Dietary restrictions:** Offers multiple choices for common types of diet restrictions, such as "vegetarian".
  * **Avoid list:** Ingredients that the user would like to exclude from the search, whether for allergies or
  preferences.
* Multiple search results are shown, with each recipe's title, list of ingredients, and list of directions.
* Optional login which unlocks the ability to save recipes for future reference.
* A list of all saved recipes can be seen in the sidebar.
  * A single saved recipe can be selected to be expanded, where its title, list of ingredients, and list of directions
  can be seen.
  * Each saved recipe can be removed if no longer needed.

## Contents of this repository

This folder contains 13 files and 1 directory:

1. This **README** file.
2. **search**, a directory containing the FAISS index file and the metadata json file used for FAISS vector search. 
3. **app.py**, a script containing the Streamlit app.
4. **cleanup.py**, a script that removes inedible recipes from the dataset.
5. **extract_dataset.py**, a script that extracts various metadata from the dataset for data mining purposes.
6. **extract_ingredients.py**, a script that extracts ingredients from the measurements for each recipe.
7. **faiss_index.py**, a script that creates the FAISS index file as well as the metadata file used for vector search.
8. **preprocess.py**, a script that extracts the recipe title, measurements, and directions for a subset of the dataset.
9. **search.py**, a script that handles querying with FAISS.
10. **cleaned_ingredients.json**, a file containing the extracted ingredients outputted from **extract_ingredients.py**.
11. **dietary_restriction_exclusion_list.json**, a file containing pre-determined lists of ingredients to exclude per
dietary restriction.
12. **environment.yml**, a file containing information to build a conda environment.
13. **requirements.txt**, a file containing the dependencies for the project.
14. **final_report.pdf**, a document containing the details of the project.

## Steps for replication

* Download the raw dataset from [Kaggle](https://www.kaggle.com/datasets/paultimothymooney/recipenlg).
* Run `preprocess.py` to retrieve a small subset of the dataset in `recipes_50k.jsonl`.
* Run `cleanup.py` to retrieve a cleaned recipes.jsonl file (e.g., `clean_recipes_50k.jsonl`).
* Run `faiss_index.py` using the cleaned recipes .jsonl file (e.g., `clean_recipes_50k.jsonl`) to retrieve
`recipe_index.faiss` and `recipe_metadata.json`.
    * In `app.py`, these two files are being retrieved from a directory called `search`. Please either add
  `recipe_index.faiss` and `recipe_metadata.json` to a subdirectory named `search` or adjust the code in `app.py`
  to reflect the correct location of the files.
