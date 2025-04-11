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

print(
    f"Loading env file from: {os.path.join(os.path.dirname(__file__), '.env')}")
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


def plot_embeddings(prompt_vector, matches, title, prompt_label="User Prompt"):
    """
    Plot the prompt embedding and the embedding vectors from `matches` in 2D via PCA.
    Each point is annotated with a label (city name if available, or a fallback).

    Parameters:
      - prompt_vector: the embedding vector (list/np.array of shape (512,)) for the prompt.
      - matches: list of dicts; each should have a "values" key (the embedding vector)
                 and a "metadata" dict, possibly with "city_name".
      - title: Title of the plot.
      - prompt_label: Label for the prompt point.
    """
    vectors = []
    labels = []

    # Add prompt vector
    vectors.append(prompt_vector)
    labels.append(prompt_label)

    # Add neighbor vectors
    for i, match in enumerate(matches):
        vec = match.get("values")
        if vec is not None:
            vectors.append(vec)
            city = match.get("metadata", {}).get("city_name")
            label = city if city else f"Neighbor {i+1}"
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


def hotels_to_df(hotels):
    """
    Convert the list of hotel matches into a Pandas DataFrame.
    Each hotel's metadata is flattened and the hotel id is added as a column.
    """
    hotel_data = []
    for hotel in hotels:
        row = hotel.get("metadata", {}).copy()
        row["id"] = hotel.get("id")
        hotel_data.append(row)
    return pd.DataFrame(hotel_data)


def filter_hotels_by_location_df(df, user_prompt):
    """
    Use Gemini to extract the city or country from the prompt and filter the hotels DataFrame to only include rows
    where the corresponding location appears. Also adds a 'matched_location' column with the actual value from the DataFrame.
    """
    # Build a list of unique location names from the DataFrame.
    unique_cities = df['city_name'].dropna().unique().tolist()
    unique_countries = df['country_name'].dropna().unique().tolist()
    unique_location_names = list(set(unique_cities + unique_countries))

    # Formulate the prompt for Gemini using the unique location names.
    extraction_prompt = (
        f"Given the following list of unique location names from our dataset: {unique_location_names}, "
        f"extract from the following prompt which of these locations are mentioned: \"{user_prompt}\". "
        "Return the one location name from the list which is asked for in the language from the given list!"
    )
    extraction_response = query_gemini(extraction_prompt)
    extraction_response = extraction_response.replace(
        "\n", " ").replace("\t", " ").strip()
    print(f"Gemini extraction response: {extraction_response}")

    # If Gemini returns a non-empty response, use that location; otherwise, the list is empty.
    locations = [extraction_response] if extraction_response else []
    print(f"Extracted locations: {locations}")

    def location_match(row):
        # Get the city and country for this row and normalize them.
        city = str(row.get("city_name", "")).lower().strip()
        country = str(row.get("country_name", "")).lower().strip()
        for loc in locations:
            loc_norm = loc.lower().strip()
            # Check for an exact match first.
            if loc_norm == city or loc_norm == country:
                return loc
            # Optionally, check if the extracted location is contained in the row value.
            if loc_norm in city or loc_norm in country:
                return loc
        return None

    # Apply matching to create a new column with the matched location (if any)
    df["matched_location"] = df.apply(location_match, axis=1)
    print(f"Matched locations: {df['matched_location'].unique()}")
    # Filter rows where a match was found. If no rows remain, return the original DataFrame.
    df_filtered = df[df["matched_location"].notnull()]
    print(f"Unique countrynames: {df_filtered['country_name'].unique()}")
    print(f"{df_filtered}")
    return df_filtered


def sort_hotels(matches, ordering_categories):
    """
    Sort the Pinecone matches by a primary category (or hotel_rating as default).
    Returns the top 10 matches.
    """
    df = hotels_to_df(matches)
    primary_category = ordering_categories[0] if ordering_categories else "hotel_rating"

    for col in [primary_category, "hotel_rating"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0
    df_sorted = df.sort_values(
        by=[primary_category, "hotel_rating"], ascending=False).head(10)

    sorted_ids = df_sorted["id"].tolist()
    sorted_matches = [m for m in matches if m.get("id") in sorted_ids]
    return sorted_matches


def process_and_visualize(user_prompt):
    """
    Process hotel recommendations, plotting PCA visualizations after each major step:
    1. Raw results from Pinecone.
    2. After location-based filtering using Gemini extraction.
    3. After sorting to top 10 hotels.
    """
    # Step 1: Query Pinecone
    prompt_vector, matches = query_pinecone_hotels(user_prompt)
    print(f"Initial Pinecone query returned {len(matches)} matches.")
    plot_embeddings(
        prompt_vector,
        matches,
        title="Step 1: Initial PCA Projection (All Pinecone Matches)",
        prompt_label="User Prompt"
    )

    # Step 2: Filter by Location using robust Gemini extraction.
    df_hotels = hotels_to_df(matches)
    df_filtered = filter_hotels_by_location_df(df_hotels, user_prompt)
    print(f"After location filtering: {len(df_filtered)} rows remain.")

    # Reconstruct the matches list from the filtered DataFrame.
    # We assume that each hotel row from the DataFrame can be mapped back by the hotel "id".
    filtered_ids = df_filtered["id"].tolist()
    filtered_matches = [m for m in matches if m.get("id") in filtered_ids]
    plot_embeddings(
        prompt_vector,
        filtered_matches,
        title="Step 2: PCA Projection After Robust Location Filtering",
        prompt_label="User Prompt"
    )

    # Step 3: Determine ordering category and sort.
    categories = df_filtered.columns.tolist()
    sorting_prompt = (
        f"Original prompt:\n{user_prompt}\n\n"
        f"Given these hotel recommendation categories: {', '.join(categories)}, "
        "which category is most important for sorting?"
    )
    sorting_response = query_gemini(sorting_prompt)
    ordering_categories = get_category_from_text(sorting_response, categories)
    if not ordering_categories:
        ordering_categories = ["hotel_rating"]

    sorted_matches = sort_hotels(filtered_matches, ordering_categories)
    print(f"After sorting, top {len(sorted_matches)} matches selected.")
    plot_embeddings(
        prompt_vector,
        sorted_matches,
        title="Step 3: PCA Projection of Top Sorted Hotels",
        prompt_label="User Prompt"
    )

    # Optional: Retrieve additional information from Gemini.
    hotel_ids = [str(m.get("id")) for m in sorted_matches]
    additional_info = "descriptions about nearby attractions, amenities, or service"
    additional_info_prompt = (
        f"Here are the top hotel recommendations (by ID):\n"
        f"{', '.join(hotel_ids)}\n\n"
        f"Please provide additional information about these hotels, e.g., {additional_info}. "
        "Then make a compelling case for each hotel."
    )
    additional_info_response = query_gemini(additional_info_prompt)
    print("Additional Hotel Information from Gemini:")
    print(additional_info_response)

    return sorted_matches


# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    user_prompt = "I’m planning a trip to Albania and I’m looking for a hotel that isn’t overrun by tourists. It’s also important that the hotel has a wellness area. Do you have any suggestions for suitable accommodations?"
    final_recommendations = process_and_visualize(user_prompt)
