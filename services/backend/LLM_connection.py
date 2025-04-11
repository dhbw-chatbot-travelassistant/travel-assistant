from google import genai
import os
from pinecone import Pinecone
from dotenv import load_dotenv
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Retrieve API keys from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

print(f"{os.path.join(os.path.dirname(__file__), '.env')}")
print(f"GEMINI_API_KEY: {GEMINI_API_KEY}")
print(f"PINECONE_API_KEY: {PINECONE_API_KEY}")

# Initialize the Gemini client using the GEMINI_API_KEY
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize Pinecone using the new Pinecone class
pc = Pinecone(PINECONE_API_KEY)
# Assume that the index "hotels-index" is already created and populated.
index = pc.Index("hotels-gemini")


def query_gemini(content):
    """
    Query Gemini with the provided content.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=content,
    )
    return response.text


def get_category_from_text(response_text, categories):
    """
    From Gemini's response text, extract which of the given categories were mentioned.
    """
    occurring_categories = [
        category for category in categories if category in response_text]
    return occurring_categories


def query_pinecone_hotels(user_prompt):
    """
    Embed the user prompt using Pinecone's inference API and query the hotel index.
    Returns the top 100 matching hotels (with metadata) from namespace "ns1".
    """
    embedding_result = client.models.embed_content(
        model="text-embedding-004",
        contents=[user_prompt]
    )

    results = index.query(
        namespace="hotels",
        vector=embedding_result.embeddings[0].values,
        top_k=100,
        include_values=True,
        include_metadata=True
    )

    # Assuming 'embedding_result' is from your Gemini client, and your pinecone query returns matches
    # The prompt's embedding
    prompt_vector = embedding_result.embeddings[0].values
    # Your Pinecone query results with embeddings
    pinecone_matches = results.get("matches", [])

    # Plot the PCA visualization
    plot_prompt_embedding_with_cities(prompt_vector, pinecone_matches)

    return results.get("matches", [])


def hotels_to_df(hotels):
    """
    Convert the list of hotels (with metadata) to a Pandas DataFrame.
    Each hotel's metadata is flattened into a row, with the hotel ID added as a column.
    """
    hotel_data = []
    for hotel in hotels:
        row = hotel.get("metadata", {}).copy()
        row["id"] = hotel.get("id")
        hotel_data.append(row)
    return pd.DataFrame(hotel_data)


def filter_hotels_by_location_df(df, user_prompt):
    """
    Filter the hotels DataFrame to only include rows where the city or county name appears
    in the user prompt. If no rows match, return the original DataFrame.
    """
    prompt_lower = user_prompt.lower()

    def location_match(row):
        city = row.get("city_name", "").lower()
        county = row.get("country_name", "").lower()
        return (city in prompt_lower) or (county in prompt_lower)

    df["location_match"] = df.apply(location_match, axis=1)
    df_filtered = df.loc[df["location_match"]]
    df_filtered.drop(columns=["location_match"], inplace=True)
    return df_filtered if not df_filtered.empty else df


def sort_hotels_df(df, ordering_categories):
    """
    Sort hotels by the first ordering category provided (or default to hotel_rating)
    and then by hotel_rating as a secondary tiebreaker.
    Returns the top 10 sorted hotels as a DataFrame.
    """
    primary_category = ordering_categories[0] if ordering_categories else "hotel_rating"
    # Ensure the sorting columns exist and are numeric
    for col in [primary_category, "hotel_rating"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0
    df_sorted = df.sort_values(
        by=[primary_category, "hotel_rating"], ascending=False)
    return df_sorted.head(10)


def get_hotel_recommendations(user_prompt):
    """
    Process hotel recommendations as follows:
      1. Query Pinecone for similar hotels based on the user prompt.
      2. Convert the results to a Pandas DataFrame.
      3. Filter hotels based on location (city/county) in the user prompt.
      4. Use Gemini to determine the most important hotel metadata category for sorting.
      5. Sort the hotels using DataFrame operations and select the top 10.
      6. Ask Gemini to generate additional details and a compelling case for the top hotels.
    """
    # Step 1: Retrieve similar hotels from Pinecone.
    hotels = query_pinecone_hotels(user_prompt)

    # Step 2: Convert the hotels list into a DataFrame.
    hotels_df = hotels_to_df(hotels)
    # Step 3: Filter hotels based on location (if applicable).
    hotels_df = filter_hotels_by_location_df(hotels_df, user_prompt)

    # Step 4: Determine the ordering category using Gemini.
    categories = hotels_df.columns
    sorting_prompt = (
        f"Here is the original prompt:\n{user_prompt}\n\n"
        f"We now have some hotel recommendations. Which of these categories are most important to the user? "
        f"Therefore, by which category should we order by: {', '.join(categories)}.\n\n"
        "Please provide the category names and only that."
    )
    sorting_response = query_gemini(sorting_prompt)
    ordering_categories = get_category_from_text(sorting_response, categories)

    # Default to sorting by hotel_rating if Gemini returns no valid category.
    if not ordering_categories:
        ordering_categories = ["hotel_rating"]

    # Step 5: Sort the hotels using the DataFrame.
    top_hotels_df = sort_hotels_df(hotels_df, ordering_categories)

    # Prepare a list of hotel names for the final prompt.
    hotel_strings = top_hotels_df.apply(
        lambda row: f"{row['id']}: {row.to_dict()}", axis=1).tolist()

    # Step 6: Ask Gemini for additional details and a compelling case.
    additional_info = "descriptions about nearby attractions, amenities, or service"
    additional_info_prompt = (
        f"Here are the top hotel recommendations:\n{', '.join(hotel_strings)}\n\n"
        f"Can you provide additional information about these hotels? For example, {additional_info}. "
        "Then, please make a compelling case for each hotel to the user. ignore columns which are marked unknown. "
    )
    additional_info_response = query_gemini(additional_info_prompt)

    return additional_info_response


def plot_prompt_embedding_with_cities(prompt_vector, pinecone_matches, prompt_label=""):
    """
    Plot the user prompt embedding along with the embeddings of its nearest neighbors
    in 2D using PCA. Annotate every point (including the user prompt) with a label.
    For neighbor points, if a "city_name" exists in the match's metadata, it is used as the label;
    otherwise, the label defaults to its neighbor number. For the user prompt point, the 'prompt_label'
    is used.

    Parameters:
      - prompt_vector: list or numpy array of shape (512,) containing the prompt embedding.
      - pinecone_matches: list of dicts representing the Pinecone query matches. Each dict should contain:
            - "values": the embedding vector.
            - "metadata": a dict that may include a "city_name" key.
      - prompt_label (optional): a label for the user prompt point. This could be a city name if available,
            or simply a custom label (default is "User Prompt").
    """
    vectors = []
    labels = []

    # Append the prompt vector.
    vectors.append(prompt_vector)
    labels.append(prompt_label)

    # Append all neighbor vectors.
    for i, match in enumerate(pinecone_matches):
        vec = match.get("values")
        if vec is not None:
            vectors.append(vec)
            # Try to extract the city name from metadata; if not available, use neighbor number.
            city = match.get("metadata", {}).get("city_name")
            label = city if city else f"Neighbor {i + 1}"
            labels.append(label)

    # Convert list to a numpy array.
    vectors = np.array(vectors)

    # Reduce dimensions to 2D using PCA.
    pca = PCA(n_components=2)
    vectors_2d = pca.fit_transform(vectors)

    # Create the plot.
    plt.figure(figsize=(8, 6))

    # Plot each point and annotate with the corresponding label.
    for i, (x, y) in enumerate(vectors_2d):
        # Use a special marker for the user prompt point.
        if i == 0:
            plt.scatter(x, y, marker="X", color="red", s=100)
        else:
            plt.scatter(x, y, marker="o", color="blue", s=50)
        plt.text(x + 0.01, y + 0.01, labels[i], fontsize=9)

    plt.title(
        "2D PCA Projection: User Prompt and Nearest Neighbors (Annotated with City Names)")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.show()

# Example usage:
# Assuming 'prompt_vector' is the 512-dimensional vector for your user prompt,
# and 'pinecone_matches' is the list returned from your Pinecone query where each match includes a "values"
# field for the embedding and "metadata" with a "city_name".
#
# For instance:
# prompt_vector = embedding_result.embeddings[0].values
# pinecone_matches = query_pinecone_hotels(user_prompt)
# Optionally, if you have a city name associated with the prompt, you can pass it as follows:
# plot_prompt_embedding_with_cities(prompt_vector, pinecone_matches, prompt_label="Albania")
#
# Otherwise, it will simply display "User Prompt" for the first point.


# Example usage:
if __name__ == "__main__":
    user_prompt = "I'm looking for luxury hotels in Albanien with excellent reviews and a great location."
    recommendations = get_hotel_recommendations(user_prompt)
    print("Hotel Recommendations:")
    print(recommendations)
