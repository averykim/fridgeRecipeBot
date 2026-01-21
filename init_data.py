from pymongo import MongoClient

# Connect Docker MongoDB
client = MongoClient("mongodb://mongo:27017/") # docker-compose service name is mongo

# Select DB and Collection
db = client["recipe_db"]
collection = db["recipes"]

# Delete previous data
collection.delete_many({})

# initial data
docs = [
    {
        "name": "Chicken Stir Fry",
        "ingredients": ["chicken", "onion","garlic","vegetables","soysauce","oil"],
        "instructions": "Heat oil in a pan. Add chopped onions and garlic, then add chicken and stir fry for 10 minutes. Add vegetables and soy sauce, and stir fry for an additional 5 minutes.",
        "prep_time": 20,
        "difficulty": "Medium"
    },
    {
        "name": "Garlic Chicken",
        "ingredients": ["chicken","garlic","butter","parsley"],
        "instructions": "In a pan, melt butter. Add garlic and cook until fragrant. Add chicken and cook for 15 minutes. Garnish with parsley and serve.",
        "prep_time": 15,
        "difficulty": "Easy"
    },
    {
        "name": "Vegetable Soup",
        "ingredients": ["carrot","onion","potato","garlic","tomato","vegetablebroth"],
        "instructions": "In a large pot, sauté onions and garlic. Add carrots, potatoes, tomatoes, and vegetable broth. Simmer for 30 minutes and season with salt and pepper.",
        "prep_time": 30,
        "difficulty": "Easy"
    },
    {
        "name": "Beef Stir Fry",
        "ingredients": ["beef","onion","garlic","bellpepper","soysauce","oil"],
        "instructions": "Heat oil in a pan, add onions and garlic. Add sliced beef and stir fry until browned. Add bell pepper and soy sauce, cook for another 5 minutes.",
        "prep_time": 25,
        "difficulty": "Medium"
    },
    {
        "name": "Chicken Salad",
        "ingredients": ["chicken","lettuce","tomato","cucumber","oliveoil","lemonjuice"],
        "instructions": "Grill chicken and slice it. In a bowl, combine lettuce, tomato, cucumber, and sliced chicken. Drizzle with olive oil and lemon juice.",
        "prep_time": 15,
        "difficulty": "Easy"
    },
    {
        "name": "Spaghetti Bolognese",
        "ingredients": ["spaghetti","groundbeef","onion","garlic","tomato","oliveoil","basil"],
        "instructions": "Cook spaghetti according to package instructions. In a pan, sauté onions and garlic in olive oil. Add ground beef and cook until browned. Add tomatoes and basil, simmer for 15 minutes.",
        "prep_time": 40,
        "difficulty": "Medium"
    }
]

# Insert data
collection.insert_many(docs)
print(f"Inserted {len(docs)} recipes into MongoDB.")
