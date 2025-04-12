from google import genai
import os
from pinecone import Pinecone
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Retrieve API keys from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

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
        include_values=False,
        include_metadata=True
    )

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
    Nutzt Gemini, um aus dem Prompt die Stadt bzw. das Land zu extrahieren und filtert den Hotels-DataFrame so,
    dass nur Zeilen enthalten sind, bei denen einer der extrahierten Orte vorkommt. Es wird auch eine Spalte
    'matched_location' hinzugefügt, die alle passenden Elemente als kommaseparierten String enthält.
    """
    # Liste der eindeutigen Ortsnamen aus dem DataFrame bilden.
    unique_cities = df['city_name'].dropna().unique().tolist() if 'city_name' in df.columns else []
    unique_countries = df['country_name'].dropna().unique().tolist() if 'country_name' in df.columns else []
    unique_location_names = list(set(unique_cities + unique_countries))


    # Gemini-Prompt formulieren, der alle relevanten Ortsnamen prüfen soll.
    extraction_prompt = (
        f"Given the following list of unique location names from our dataset: {unique_location_names}, "
        f"extract from the following prompt which of these locations are mentioned: \"{user_prompt}\". "
        "Return the one location name from the list which is asked for in the language from the given list for example if the list says albanien instead of albania, return albanien!   "
    )
    extraction_response = query_gemini(extraction_prompt)
    extraction_response = extraction_response.replace("\n", "").replace("\t", "").strip()


    # Falls Gemini mehrere Elemente zurückliefert, diese zu einer Liste aufsplitten.
    locations = [loc.strip() for loc in extraction_response.split(",")] if extraction_response else []


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

    df_filtered = df[df["matched_location"].notnull()]

    return df_filtered




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


# Example usage:
if __name__ == "__main__":
    user_prompt = "I'm looking for luxury hotels in Albanien with excellent reviews and a great location."
    recommendations = get_hotel_recommendations(user_prompt)
    print("Hotel Recommendations:")
    print(recommendations)
