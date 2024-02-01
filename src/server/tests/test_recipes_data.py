from fastapi import UploadFile

user_1_test_recipes = [
    # All fields
    {
        "name": "Recipe 11",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family Cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 65,
        "cook_time": 60,
        "description": "A traditional recipe",
        "nutrition": "300 calories per serving",
        "favorite": False,
        "tag_ids": [],
        "steps": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
        "ingredients": [
            "1 small onion, finely chopped",
            "2 tsp salt",
            ".5 tsp oregano",
            "2 small red chiles, slivered",
            "1 28-oz can whole peeled tomatoes",
        ],
    },
    # Only required fields
    {
        "name": "Recipe 12",
    },
    # Required fields excluded
    {
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family Cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 65,
        "cook_time": 60,
        "description": "A traditional recipe.",
        "nutrition": "300 calories per serving",
        "favorite": False,
        "tag_ids": [],
        "steps": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
        "ingredients": [
            "1 small onion, finely chopped",
            "2 tsp salt",
            ".5 tsp oregano",
            "2 small red chiles, slivered",
            "1 28-oz can whole peeled tomatoes",
        ],
    },
    # Invalid type for "steps" field
    {
        "name": "Recipe 14",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family Cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 65,
        "cook_time": 60,
        "description": "A traditional recipe.",
        "nutrition": "300 calories per serving",
        "favorite": False,
        "tag_ids": [],
        "steps": "Step 1 Step 2 Step 3 Step 4 Step 5",
        "ingredients": [
            "1 small onion, finely chopped",
            "2 tsp salt",
            ".5 tsp oregano",
            "2 small red chiles, slivered",
            "1 28-oz can whole peeled tomatoes",
        ],
    },
    # Update Recipe 0 favorite field
    {"favorite": True},
    # Update Recipe 0 ingredients field
    {"ingredients": ["2 tbsp white vinegar"]},
    # Update Recipe 0 steps field
    {
        "steps": [
            "New Step 0",
            "New Step 1",
            "New Step 2",
            "New Step 3",
            "New Step 4",
            "New Step 5",
        ]
    },
    # Update Recipe 0 tags field
    {"tag_ids": []},
]

user_1_test_recipe_images = [{}]
