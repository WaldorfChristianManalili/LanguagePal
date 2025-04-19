from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin"),
        "learning_language": "Japanese",
        "openai_thread_id": None,
        "is_active": True,
    },
]

CATEGORIES = [
    # A1
    {"name": "Introduce Yourself"},
    {"name": "Describe People"},
    {"name": "Order Food"},
    {"name": "Order Food and Drink"},
    {"name": "Talk About Countries"},
    {"name": "Ask for Directions"},
    {"name": "Describe Belongings"},
    {"name": "Talk About Neighbors"},
    {"name": "Tell Time"},
    {"name": "Get Help When Traveling"},
]

SENTENCES = [
    # Introduce Yourself
    {"text": "My name is Anna.", "category_name": "Introduce Yourself"},
    {"text": "I am a student.", "category_name": "Introduce Yourself"},
    {"text": "Nice to meet you!", "category_name": "Introduce Yourself"},

    # Describe People
    {"text": "She has long hair.", "category_name": "Describe People"},
    {"text": "He is very tall.", "category_name": "Describe People"},
    {"text": "They are friendly.", "category_name": "Describe People"},

    # Order Food
    {"text": "I would like sushi.", "category_name": "Order Food"},
    {"text": "Can I get a sandwich?", "category_name": "Order Food"},
    {"text": "One ramen, please.", "category_name": "Order Food"},

    # Order Food and Drink
    {"text": "I’ll have a coffee and a croissant.", "category_name": "Order Food and Drink"},
    {"text": "Can I order tea and cake?", "category_name": "Order Food and Drink"},
    {"text": "I'd like orange juice with my breakfast.", "category_name": "Order Food and Drink"},

    # Talk About Countries
    {"text": "I am from Brazil.", "category_name": "Talk About Countries"},
    {"text": "Are you from Italy?", "category_name": "Talk About Countries"},
    {"text": "He is Japanese.", "category_name": "Talk About Countries"},

    # Ask for Directions
    {"text": "Where is the bus stop?", "category_name": "Ask for Directions"},
    {"text": "How do I get to the station?", "category_name": "Ask for Directions"},
    {"text": "Is it far from here?", "category_name": "Ask for Directions"},

    # Describe Belongings
    {"text": "This is my phone.", "category_name": "Describe Belongings"},
    {"text": "The bag is blue.", "category_name": "Describe Belongings"},
    {"text": "That’s her laptop.", "category_name": "Describe Belongings"},

    # Talk About Neighbors
    {"text": "My neighbor is kind.", "category_name": "Talk About Neighbors"},
    {"text": "They live next door.", "category_name": "Talk About Neighbors"},
    {"text": "Our neighbors have a dog.", "category_name": "Talk About Neighbors"},

    # Tell Time
    {"text": "It is ten o’clock.", "category_name": "Tell Time"},
    {"text": "The train is at 7:30.", "category_name": "Tell Time"},
    {"text": "What time is it?", "category_name": "Tell Time"},

    # Get Help When Traveling
    {"text": "Can you help me, please?", "category_name": "Get Help When Traveling"},
    {"text": "I lost my passport.", "category_name": "Get Help When Traveling"},
    {"text": "I need a doctor.", "category_name": "Get Help When Traveling"},
]
