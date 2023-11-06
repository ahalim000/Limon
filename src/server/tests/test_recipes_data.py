user_1_test_recipes = [
    # All fields except tag_ids
    {
        "name": "Recipe 1",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
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
    # Only required fields
    {
        "name": "Recipe 2",
    },
    # Some fields
    {
        "name": "Recipe 3",
        "source": "NY Times Cooking",
        "servings": 8,
        "cook_time": 120,
        "nutrition": "70 calories per serving",
        "steps": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
    },
    # Invalid type for "name" field
    {
        "name": 4,
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
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
    # Invalid type for "image_url" field
    {
        "name": "Recipe 5",
        "image_url": ["static/katherine-chase-zITJdTt5aLc-unsplash.png"],
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
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
    # Invalid type for "source" field
    {
        "name": "Recipe 6",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": False,
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
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
    # Invalid type for "servings" field
    {
        "name": "Recipe 7",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": "4",
        "servings_type": "servings",
        "prep_time": 60,
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
    # Invalid type for "servings_type" field
    {
        "name": "Recipe 8",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": {"servings_type": "servings"},
        "prep_time": 60,
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
    # Invalid type for "prep_time" field
    {
        "name": "Recipe 9",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 20.5,
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
    # Invalid type for "cook_time" field
    {
        "name": "Recipe 10",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
        "cook_time": "60",
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
    # Invalid type for "description" field
    {
        "name": "Recipe 11",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
        "cook_time": 60,
        "description": None,
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
    # Invalid type for "nutrition" field
    {
        "name": "Recipe 12",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
        "cook_time": 60,
        "description": "A traditional recipe.",
        "nutrition": 300,
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
    # Invalid type for "favorite" field
    {
        "name": "Recipe 13",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
        "cook_time": 60,
        "description": "A traditional recipe.",
        "nutrition": "300 calories per serving",
        "favorite": "False",
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
    # Invalid type for "tag_ids" field
    {
        "name": "Recipe 14",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
        "cook_time": 60,
        "description": "A traditional recipe.",
        "nutrition": "300 calories per serving",
        "favorite": False,
        "tag_ids": 3,
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
        "name": "Recipe 15",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
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
    # Invalid type for "ingredients" field
    {
        "name": "Recipe 16",
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
        "cook_time": 60,
        "description": "A traditional recipe.",
        "nutrition": "300 calories per serving",
        "favorite": False,
        "tag_ids": [],
        "steps": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
        "ingredients": [1, 2, 3, 4, 5],
    },
    # Required fields excluded
    {
        "image_url": "static/katherine-chase-zITJdTt5aLc-unsplash.png",
        "source": "Family cookbook",
        "servings": 4,
        "servings_type": "servings",
        "prep_time": 60,
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
]