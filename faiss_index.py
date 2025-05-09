from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import argparse


def index_faiss(input_file: str, output_dir: str) -> None:
    """
    Create FAISS index from input file.
    :param input_file: Input .jsonl file containing the recipes.
    :param output_dir: Directory in which to save the FAISS index.
    """
    recipes = []

    with open(input_file, "r", encoding="utf-8") as f:  # load recipes
        for line in f:
            recipes.append(json.loads(line))

    texts = [f"{r['title']}: {r['ingredients']}\n{r['directions']}" for r in recipes]  # texts for embedding

    model = SentenceTransformer("all-MiniLM-L6-v2")  # embedding model

    batch_size = 8
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        emb = model.encode(batch, batch_size=batch_size, show_progress_bar=False)
        all_embeddings.extend(emb)

    embeddings_np = np.array(all_embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings_np.shape[1])  # creating FAISS index
    index.add(embeddings_np)

    faiss.write_index(index, f"{output_dir}/recipe_index.faiss")

    with open(f"{output_dir}/recipe_metadata.json", "w") as f:
        json.dump(recipes, f)

    print(f"Indexed {index.ntotal} full recipes.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='faiss_index.py',
        description='Create FAISS index.'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='A jsonl file containing the raw recipes.'
    )
    parser.add_argument(
        'output_dir',
        type=str,
        help='The directory in which the index and metadata should be written.'
    )
    args = parser.parse_args()

    index_faiss(args.input_file, args.output_dir)
