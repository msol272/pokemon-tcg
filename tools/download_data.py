import json
import os
import requests

# Create a directory to save the images
if not os.path.exists("../app/static/images"):
    os.makedirs("../app/static/images")

# Base URL for the Pokémon TCG API
api_url = "https://api.pokemontcg.io/v2/cards"

# Parameters to filter for the Scarlet & Violet 151 set
params = {
    "q": "set.id:sv3pt5 OR set.id:sve"
}

# Make a GET request to the Pokémon TCG API
response = requests.get(api_url, params=params)

if response.status_code == 200:
    data = response.json()

    with open('../app/static/pokemon_cards_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Iterate through each card in the response
    for card in data['data']:
        card_number = card['id']
        image_url = card['images']['large']  # Get the large image URL

        # Download the image
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            with open(f"../app/static/images/{card_number}.jpg", 'wb') as img_file:
                img_file.write(image_response.content)
            print(f"Downloaded: {card_number}")
        else:
            print(f"Failed to download image for: {card_number}")
else:
    print("Failed to retrieve data from the Pokémon TCG API")
