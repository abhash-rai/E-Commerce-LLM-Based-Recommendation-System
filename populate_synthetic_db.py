import random

from db.sql_db import DB

db = DB()

db.initialize_database()

def generate_users():
    first_names = ["John", "Jane", "Talia", "Emily", "Michael", "Sarah", "Chris", "Jessica", "David", "Laura"]
    last_names = ["Doe", "Smith", "Johnson", "Ling", "Brown", "Lee", "Davis", "Taylor", "Rai", "Williams"]
    interests = [
        "gym equipment",
        "musical instruments",
        "tech gadgets",
        "books",
        "movies",
        "cooking",
        "traveling",
        "gaming",
        "sports",
        "photography",
    ]
    
    for _ in range(100):
        while True:
            try:
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                email = f"{first_name.lower()}.{last_name.lower()}@example.com"

                if random.random() < 0.2:  # 20% chance
                    description = ''
                else:
                    description = f"I love {random.choice(interests)} and {random.choice(interests)}."
                
                # Simulating the database function to record a user
                db.record_user(email, description)
                break
            except:
                continue

def generate_categories():
    categories = [
        ("Tech", "All about the latest gadgets, electronics, and technology."),
        ("Fitness", "Equipment and products for a healthy and active lifestyle."),
        ("Books", "A collection of fiction, non-fiction, and educational books."),
        ("Music", "Instruments, accessories, and everything musical."),
        ("Fashion", "Clothing, accessories, and the latest fashion trends."),
        ("Gaming", "Video games, consoles, and accessories for gamers."),
        ("Home Decor", "Beautiful items to enhance your living space."),
        ("Travel", "Luggage, maps, and essentials for the travel enthusiast."),
        ("Sports", "Gear and equipment for various sports activities."),
        ("Cooking", "Tools, utensils, and appliances for the kitchen."),
    ]
    
    for name, description in categories:
        # Simulating the database function to record a category
        db.record_category(name, description)

def generate_products():
    # Products for each category
    products = {
        1: [("Smartphone", "Latest model with high-end specs", 1000.00, 50),
            ("Laptop", "Gaming laptop with powerful GPU", 1500.00, 30),
            ("Smartwatch", "Track your fitness and health", 250.00, 100),
            ("Wireless Earbuds", "Bluetooth earbuds with noise cancellation", 150.00, 200),
            ("Tablet", "Portable tablet for reading and work", 400.00, 80)],
        
        2: [("Dumbbells", "Adjustable dumbbells for home gym", 150.00, 40),
            ("Treadmill", "Foldable treadmill with multiple workout modes", 800.00, 10),
            ("Yoga Mat", "Eco-friendly yoga mat for comfort", 25.00, 120),
            ("Resistance Bands", "Set of resistance bands for strength training", 35.00, 60),
            ("Protein Powder", "Whey protein for muscle gain", 50.00, 200)],
        
        3: [("Novel Book", "Fiction novel by a best-selling author", 15.00, 300),
            ("Textbook", "Comprehensive guide on computer science", 60.00, 100),
            ("Cookbook", "Healthy recipes for daily meals", 25.00, 150),
            ("Biography", "Autobiography of a famous celebrity", 20.00, 200),
            ("Children's Book", "Fun and educational book for kids", 10.00, 180)],
        
        4: [("Guitar", "Electric guitar with amp for beginners", 300.00, 20),
            ("Piano", "Grand piano for home use", 5000.00, 5),
            ("Drums", "Complete drum set with cymbals", 800.00, 8),
            ("Violin", "Professional violin for music students", 400.00, 15),
            ("Headphones", "Noise-canceling headphones for musicians", 200.00, 50)],
        
        5: [("Jacket", "Stylish leather jacket for winter", 120.00, 70),
            ("Sneakers", "Comfortable sneakers for everyday wear", 80.00, 150),
            ("Watch", "Luxury wristwatch with a stainless steel strap", 200.00, 50),
            ("Handbag", "Designer handbag for women", 150.00, 40),
            ("Sunglasses", "Polarized sunglasses for sun protection", 60.00, 200)],
        
        6: [("PlayStation 5", "Next-gen gaming console with high-speed SSD", 500.00, 10),
            ("Xbox Series X", "Powerful gaming console for smooth gameplay", 500.00, 15),
            ("Gaming Chair", "Ergonomic chair for long gaming sessions", 200.00, 40),
            ("VR Headset", "Virtual reality headset for immersive gaming", 300.00, 25),
            ("Game Controller", "Wireless controller for gaming consoles", 40.00, 100)],
        
        7: [("Sofa", "Luxury leather sofa with built-in USB ports", 1200.00, 15),
            ("Dining Table", "Wooden dining table with six chairs", 600.00, 25),
            ("Lamp", "Modern table lamp with adjustable brightness", 45.00, 150),
            ("Coffee Table", "Glass top coffee table for living room", 250.00, 70),
            ("Wall Art", "Framed abstract art for home decor", 80.00, 200)],
        
        8: [("Backpack", "Durable backpack for hiking and traveling", 50.00, 100),
            ("Luggage Set", "3-piece luggage set with TSA lock", 150.00, 30),
            ("Travel Pillow", "Comfortable neck pillow for long flights", 20.00, 150),
            ("Camera", "DSLR camera with zoom lens", 500.00, 10),
            ("Travel Adapter", "Universal plug adapter for global travel", 30.00, 200)],
        
        9: [("Football", "Official size football for training", 25.00, 80),
            ("Basketball", "High-quality basketball for outdoor play", 30.00, 100),
            ("Tennis Racket", "Professional racket for serious players", 100.00, 60),
            ("Baseball Glove", "Soft leather baseball glove for youth", 50.00, 120),
            ("Soccer Cleats", "Premium soccer cleats for performance", 80.00, 70)],
        
        10: [("Blender", "High-speed blender for smoothies", 80.00, 200),
            ("Coffee Maker", "Automatic coffee maker with programmable features", 100.00, 150),
            ("Toaster", "2-slice toaster with adjustable heat settings", 25.00, 100),
            ("Microwave", "Compact microwave for quick meals", 75.00, 80),
            ("Air Fryer", "Healthy air fryer for crisp cooking", 120.00, 50)]
    }

    # Loop through each category and create product entries
    for category_id, products_list in products.items():
        for name, description, price, stock in products_list:
            # Simulating the database function to record a product
            db.record_product(category_id, name, description, price, stock)

def generate_search_histories():
    random_searches = [
        "Laptop", "Phone Case", "Smart Watch", "Headphones", "Keyboard", "Wireless Earbuds",
        "Yoga Mat", "Protein Powder", "Dumbbells", "Treadmill", "Coffee Maker", "Microwave",
        "Guitar", "Piano", "Basketball", "Football", "Running Shoes", "Sunglasses", "Camera",
        "Suitcase", "Travel Adapter", "Air Fryer", "Vegan Recipes", "Cooking Tools", "Home Decor"
    ]

    exclude_user_ids = [10, 20, 30, 40, 50, 60, 70, 80, 90, 99] # users to skip to have no search histories to minic real life cases

    for _ in range(500): # Want 500 searches

        while True:
            user_id = random.randint(1, 100)
            if user_id not in exclude_user_ids:
                break

        # Get the user profile description
        interests = db.get_data(table='User', id=user_id)['profile_description']
        
        # Generate 3 to 5 searches based on the user's interests
        user_searches = []
        
        # Add searches based on user interests
        if "gym" in interests:
            user_searches.extend(["Dumbbells", "Resistance Bands", "Yoga Mat", "Protein Powder", "Treadmill"])
        if "musical" in interests:
            user_searches.extend(["Guitar", "Piano", "Drums", "Headphones", "Violin"])
        if "tech" in interests:
            user_searches.extend(["Smartphone", "Laptop", "Wireless Earbuds", "Keyboard", "Tablet", "Smart Watch"])
        if "books" in interests:
            user_searches.extend(["Fiction", "Non-fiction", "Mystery", "Biography", "Cookbook", "Children's Book"])
        if "movies" in interests:
            user_searches.extend(["Action Movies", "Comedy Movies", "Drama Movies", "Horror Movies", "Documentary"])
        if "cooking" in interests:
            user_searches.extend(["Cookbook", "Kitchen Appliances", "Pots and Pans", "Spices", "Cooking Utensils"])
        if "traveling" in interests:
            user_searches.extend(["Suitcase", "Travel Adapter", "Camera", "Backpack", "Luggage", "Travel Pillow"])
        if "gaming" in interests:
            user_searches.extend(["Video Games", "Gaming Console", "Gaming Mouse", "Gaming Headset", "PC Gaming"])
        if "sports" in interests:
            user_searches.extend(["Football", "Basketball", "Running Shoes", "Soccer Ball", "Tennis Racket"])
        if "photography" in interests:
            user_searches.extend(["Camera", "Lens", "Tripod", "Drone", "Photo Editing Software"])
        
        for _ in range(3):
            user_searches.append(random.choice(random_searches))

        user_searches = random.sample(user_searches, random.randint(1, 3))

        # Record the search history for the user
        for search_query in user_searches:
            db.record_search_history(user_id, search_query)

def generate_recommendations():
    for _ in range(300): # Want 300 recommendations
        user_id = random.randint(1, 100)

        # Get the user profile description
        interests = db.get_data(table='User', id=user_id)['profile_description']
        products = db.search_product(search_keyword=interests, return_as_dict=False)
        try:
            products = random.sample(products, random.randint(1, 3))
        except:
            if len(products) == 0:
                continue
            
        for product in products:
            recommendatino_id = db.record_recommendation(user_id, product.product_id, random.uniform(0.5, 1))
            db.record_recommendation_feedback(recommendatino_id, user_id, random.randint(3, 5))

generate_users()
generate_categories()
generate_products()
generate_search_histories()
generate_recommendations()
