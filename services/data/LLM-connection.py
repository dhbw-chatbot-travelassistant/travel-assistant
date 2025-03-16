from google import genai
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

api_key = os.getenv("GEMENI_API_KEY")
client = genai.Client(api_key="YOUR_API_KEY")

def query_gemeni(content):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=content,
    )
    return response.text

def get_category_from_text(response, categories):
    occurring_categories = [category for category in categories if category in response.text]
    return occurring_categories


def get_hotel_recommendations(user_prompt):
    # Get similar hotels to the request
    # TODO: get this from the pinecone database
    
    # For now, we will just return the same hotel
    
    hotels = "The Ritz-Carlton, Toronto"
    
    categories = [
        "countyCode", 
        "countyName", 
        "cityCode", 
        "cityName", 
        "HotelCode", 
        "HotelName", 
        "HotelRating", 
        "Address", 
        "Attractions", 
        "Description"
    ]
    
    sorting_prompt = f"Here is the original prompt: \n {user_prompt} \n\n We now have some hotel recommendations. Which of these categories are most important to the user? Therefore by which category should we order by : {", ".join(categories)}. \n\n Please provide the category names and only that." 
    sorting_response = query_gemeni(sorting_prompt)
    occuring_categories = get_category_from_text(sorting_response, categories)
    
    # If no categories are found, we will sort for rating
    if len(occuring_categories) == 0:
        occuring_categories = ["HotelRating"]
        
    # TODO: Sort hotels by the categories (in pinecone or not)
    
    
    # provide additional information about the hotel
    additional_info = "Address, Attractions, Description"
    additional_info_prompt = f"Here are the hotel recommendations: \n {hotels} \n\n Can you provide additional information about the hotels? For example, {additional_info}. And then make a compelling case for each of the hotels to the user."
    additional_info_response = query_gemeni(additional_info_prompt)
    
    
    return additional_info_response
    
