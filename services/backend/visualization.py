#!/usr/bin/env python
from google import genai
import os
from pinecone import Pinecone
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# ---------------------------
# Initialization and Setup
# ---------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

print(f"Loading env file from: {os.path.join(os.path.dirname(__file__), '.env')}")
print(f"GEMINI_API_KEY: {GEMINI_API_KEY}")
print(f"PINECONE_API_KEY: {PINECONE_API_KEY}")

client = genai.Client(api_key=GEMINI_API_KEY)
pc = Pinecone(PINECONE_API_KEY)
index = pc.Index("hotels-gemini")

# ---------------------------
# Helper Functions
# ---------------------------

def query_gemini(content):
    """Query Gemini with the provided content."""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=content,
    )
    return response.text

def get_category_from_text(response_text, categories):
    """
    From Gemini's response text, extract which of the given categories were mentioned.
    """
    occurring_categories = [cat for cat in categories if cat in response_text]
    return occurring_categories

def hotels_to_df(hotels):
    """
    Convert the list of hotel matches into a Pandas DataFrame.
    Each hotel's metadata is flattened, the hotel id is added as a column,
    and the Pinecone embedding vector is stored in a new column named "vector".
    """
    hotel_data = []
    for hotel in hotels:
        row = hotel.get("metadata", {}).copy()
        row["id"] = hotel.get("id")
        # Store the Pinecone embedding vector in a new column.
        row["vector"] = hotel.get("values")
        hotel_data.append(row)
    return pd.DataFrame(hotel_data)

def plot_embeddings_df(prompt_vector, df, title, prompt_label="User Prompt"):
    """
    Plot the prompt embedding and the embedding vectors from a DataFrame in 2D via PCA.
    Uses the 'matched_location' field for labeling if available, falling back to 'city_name' if not.
    
    Parameters:
      - prompt_vector: the embedding vector (list/np.array) for the prompt.
      - df: DataFrame containing hotel information with a "vector" column.
      - title: Title of the plot.
      - prompt_label: Label for the prompt point.
    """
    vectors = []
    labels = []
    
    # Add the prompt vector first.
    vectors.append(prompt_vector)
    labels.append(prompt_label)
    
    # Then add the vectors from the DataFrame.
    for idx, row in df.iterrows():
        vec = row.get("vector")
        if vec is not None:
            vectors.append(vec)
            # Use matched_location if available, else city_name, else generic label.
            label = row.get("matched_location") or row.get("country_name") or f"Neighbor {idx+1}"
            labels.append(label)
    
    vectors = np.array(vectors)
    pca = PCA(n_components=2)
    vectors_2d = pca.fit_transform(vectors)
    
    plt.figure(figsize=(8, 6))
    for i, (x, y) in enumerate(vectors_2d):
        if i == 0:
            plt.scatter(x, y, marker="X", color="red", s=100)
        else:
            plt.scatter(x, y, marker="o", color="blue", s=50)
        plt.text(x + 0.01, y + 0.01, labels[i], fontsize=9)
    
    plt.title(title)
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.show()


def query_pinecone_hotels(user_prompt):
    """
    Embed the user prompt and query the Pinecone hotel index.
    Returns a tuple with the prompt embedding and the list of Pinecone matches.
    """
    embedding_result = client.models.embed_content(
        model="text-embedding-004",
        contents=[user_prompt]
    )
    prompt_vector = embedding_result.embeddings[0].values
    results = index.query(
        namespace="hotels",
        vector=prompt_vector,
        top_k=100,
        include_values=True,
        include_metadata=True
    )
    matches = results.get("matches", [])
    return prompt_vector, matches

def filter_hotels_by_location_df(df, user_prompt):
    """
    Nutzt Gemini, um aus dem Prompt die Stadt bzw. das Land zu extrahieren und filtert den Hotels-DataFrame so,
    dass nur Zeilen enthalten sind, bei denen einer der extrahierten Orte vorkommt. Es wird auch eine Spalte
    'matched_location' hinzugefügt, die alle passenden Elemente als kommaseparierten String enthält.
    """
    # Liste der eindeutigen Ortsnamen aus dem DataFrame bilden.
    unique_cities = df['city_name'].dropna().unique().tolist() if 'city_name' in df.columns else []
    unique_countries = df['country_name'].dropna().unique().tolist() if 'country_name' in df.columns else []
    unique_location_names = list(set(unique_cities + unique_countries))
    print(f"Unique location names: {unique_countries}")

    # Gemini-Prompt formulieren, der alle relevanten Ortsnamen prüfen soll.
    extraction_prompt = (
        f"Given the following list of unique location names from our dataset: {unique_location_names}, "
        f"extract from the following prompt which of these locations are mentioned: \"{user_prompt}\". "
        "Return the one location name from the list which is asked for in the language from the given list for example if the list says albanien instead of albania, return albanien! If two instances of the same country or city in different languages are there, return both with comma as separator. "
    )
    extraction_response = query_gemini(extraction_prompt)
    extraction_response = extraction_response.replace("\n", "").replace("\t", "").strip()
    print(f"Gemini extraction response: {extraction_response}")

    # Falls Gemini mehrere Elemente zurückliefert, diese zu einer Liste aufsplitten.
    locations = [loc.strip() for loc in extraction_response.split(",")] if extraction_response else []
    print(f"Extracted locations: {locations}")

    def location_match(row):
        matches = []
        # Extrahiere und normalisiere den city_name und country_name der Zeile.
        city = str(row.get("city_name", "")).lower().strip()
        country = str(row.get("country_name", "")).lower().strip()
        for loc in locations:
            loc_norm = loc.lower().strip()
            # Prüfe auf exakte Übereinstimmung oder Teilübereinstimmung.
            if loc_norm == city or loc_norm == country or loc_norm in city or loc_norm in country:
                matches.append(loc)
        if matches:
            # Doppelte Einträge entfernen und als kommaseparierten String zurückgeben.
            unique_matches = list(dict.fromkeys(matches))
            return ", ".join(unique_matches)
        else:
            return None

    df["matched_location"] = df.apply(location_match, axis=1)
    print(f"Matched locations: {df['matched_location'].unique()}")
    df_filtered = df[df["matched_location"].notnull()]
    if "country_name" in df_filtered.columns:
        print(f"Unique countrynames: {df_filtered['country_name'].unique()}")
    print(df_filtered)
    return df_filtered


def process_and_visualize(user_prompt):
    """
    Process hotel recommendations with three main steps:
      1. Query Pinecone and visualize initial embeddings using the DataFrame.
      2. Filter the DataFrame by location using Gemini extraction and re-visualize.
      3. Sort the filtered DataFrame and visualize the top 10 hotels.
    Additionally, query Gemini for extra information on the selected hotels.
    """
    # Step 1: Query Pinecone and build the DataFrame.
    prompt_vector, matches = query_pinecone_hotels(user_prompt)
    df_hotels = hotels_to_df(matches)
    print(f"df_hotels columns: {df_hotels.columns}")
    print(f"Initial Pinecone query returned {len(df_hotels)} matches.")
    plot_embeddings_df(
        prompt_vector,
        df_hotels,
        title="Step 1: Initial PCA Projection (All Pinecone Matches)",
        prompt_label="User Prompt"
    )

    # Step 2: Filter by location using Gemini extraction.
    df_filtered = filter_hotels_by_location_df(df_hotels, user_prompt)
    if "country_name" in df_filtered.columns:
        print(f"Unique country names: {df_filtered['country_name'].unique()}")
    print(f"After location filtering: {len(df_filtered)} rows remain.")
    plot_embeddings_df(
        prompt_vector,
        df_filtered,
        title="Step 2: PCA Projection After Robust Location Filtering",
        prompt_label="User Prompt"
    )

    # Step 3: Determine sorting category and sort the filtered DataFrame.
    categories = df_filtered.columns.tolist()
    print(f"Available categories for sorting: {categories}")
    sorting_prompt = (
        f"Original prompt:\n{user_prompt}\n\n"
        f"Given these hotel recommendation categories: {', '.join(categories)}, "
        "which category is most important for sorting?"
    )
    sorting_response = query_gemini(sorting_prompt)
    ordering_categories = get_category_from_text(sorting_response, categories)
    if not ordering_categories:
        ordering_categories = ["hotel_rating"]

    df_sorted = sort_hotels_df(df_filtered, ordering_categories)
    print(f"After sorting, top {len(df_sorted)} matches selected.")
    plot_embeddings_df(
        prompt_vector,
        df_sorted,
        title="Step 3: PCA Projection of Top Sorted Hotels",
        prompt_label="User Prompt"
    )



    return df_sorted

# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    user_prompt = (
        "I’m planning a trip to Albania and I’m looking for a hotel that isn’t overrun by tourists. "
        "It’s also important that the hotel has a wellness area. Do you have any suggestions for suitable accommodations?"
    )
    final_recommendations = process_and_visualize(user_prompt)

