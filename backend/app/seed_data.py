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
    {
        "name": "Introductions",
        "chapter": 1,
        "difficulty": "A1",
        "lessons": [
            {
                "name": "Saying your name",
                "description": "Learn how to state your name."
            },
            {
                "name": "Asking someone's name",
                "description": "Learn how to ask for another person's name."
            },
            {
                "name": "Basic Self-Introduction",
                "description": "Practice simple introductions including name, nationality, and occupation."
            },
            {
                "name": "Checkpoint",
                "description": "Test your skills to access the next chapter."
            },
        ]
    },
    {
        "name": "Greetings and Farewells",
        "chapter": 2,
        "difficulty": "A1",
        "lessons": [
            {
                "name": "Common Greetings",
                "description": "Learn standard greetings like 'hello' and time-based ones like 'good morning'."
            },
            {
                "name": "Saying Goodbye",
                "description": "Learn different ways to say farewell."
            },
            {
                "name": "Responding to Greetings",
                "description": "Practice appropriate responses to common greetings."
            },
            {
                "name": "Checkpoint",
                "description": "Test your skills to access the next chapter."
            }
        ]
    },
    {
        "name": "Polite Expressions",
        "chapter": 3,
        "difficulty": "A1",
        "lessons": [
            {
                "name": "Saying Please and Thank You",
                "description": "Learn how and when to use 'please' and 'thank you'."
            },
            {
                "name": "Saying Sorry and Excuse Me",
                "description": "Learn the usage of 'sorry' and 'excuse me' in different situations."
            },
            {
                "name": "Using Polite Phrases",
                "description": "Practice incorporating polite expressions into everyday interactions."
            },
            {
                "name": "Checkpoint",
                "description": "Test your skills to access the next chapter."
            }
        ]
    },
    {
        "name": "Basic Questions and Answers",
        "chapter": 4,
        "difficulty": "A1",
        "lessons": [
            {
                "name": "Yes or No Questions",
                "description": "Learn how to form and answer simple yes/no questions."
            },
            {
                "name": "Asking Who and What",
                "description": "Learn to use 'who' and 'what' to ask basic questions."
            },
            {
                "name": "Asking Where",
                "description": "Learn to use 'where' to ask about location."
            },
            {
                 "name": "Answering Basic Questions",
                 "description": "Practice providing simple answers to common questions."
            },
            {
                "name": "Checkpoint",
                "description": "Test your skills to access the next chapter."
            }
        ]
    },
    {
        "name": "Basic Verbs",
        "chapter": 5,
        "difficulty": "A1",
        "lessons": [
            {
                "name": "Common Action Verbs",
                "description": "Learn basic verbs like 'eat', 'drink', 'go', and 'sleep'."
            },
            {
                "name": "Describing Daily Routines",
                "description": "Use basic verbs to talk about simple daily activities."
            },
            {
                "name": "Asking About Actions",
                "description": "Learn to ask simple questions about what someone is doing."
            },
            {
                "name": "Checkpoint",
                "description": "Test your skills to access the next chapter."
            }
        ]
    },
    {
        "name": "Basic Pronouns",
        "chapter": 6,
        "difficulty": "A1",
        "lessons": [
            {
                "name": "Subject Pronouns",
                "description": "Learn basic pronouns: I, you, he, she, we, they."
            },
            {
                 "name": "Using Pronouns in Sentences",
                 "description": "Practice using pronouns with simple verbs."
            },
             {
                "name": "Checkpoint",
                "description": "Test your skills to access the next chapter."
            }
        ]
    },
     {
        "name": "Numbers",
        "chapter": 7,
        "difficulty": "A1",
        "lessons": [
            {
                "name": "Counting 1 to 10",
                "description": "Learn to recognize and say numbers from one to ten."
            },
            {
                "name": "Using Numbers for Quantity",
                "description": "Practice using numbers 1-10 to indicate quantity."
            },
            {
                 "name": "Saying Phone Numbers (Simple)",
                 "description": "Learn to say digits for basic number sequences like phone numbers."
            },
            {
                "name": "Checkpoint",
                "description": "Test your skills to access the next chapter."
            }
        ]
    },
    {
        "name": "Common Objects",
        "chapter": 8,
        "difficulty": "A1",
        "lessons": [
            {
                "name": "Classroom Objects",
                "description": "Learn the names of common items found in a classroom (pen, book)."
            },
            {
                "name": "Everyday Items",
                "description": "Learn the names of common personal items (bag, phone)."
            },
            {
                "name": "Asking 'What is this?'",
                "description": "Learn how to ask for the name of an object."
            },
            {
                 "name": "Identifying Objects",
                 "description": "Practice naming various common objects."
            },
            {
                "name": "Checkpoint",
                "description": "Test your skills to access the next chapter."
            }
        ]
    },
     {
        "name": "Days of the Week",
        "chapter": 9,
        "difficulty": "A1",
        "lessons": [
            {
                "name": "Naming the Days",
                "description": "Learn the names of the seven days of the week."
            },
            {
                "name": "Asking 'What day is it?'",
                "description": "Learn the question to ask for the current day."
            },
            {
                 "name": "Talking About Days",
                 "description": "Practice saying the day and simple related phrases."
            },
            {
                "name": "Checkpoint",
                "description": "Test your skills to access the next chapter."
            }
        ]
    },
    # {
    #     "name": "Colors",
    #     "chapter": 10,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Naming Basic Colors",
    #             "description": "Learn the names of common colors."
    #         },
    #         {
    #             "name": "Describing Objects with Colors",
    #             "description": "Practice using colors to describe everyday items."
    #         },
    #          {
    #             "name": "Asking About Color",
    #             "description": "Learn how to ask 'What color is it?'."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "Family Members",
    #     "chapter": 11,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Immediate Family Vocabulary",
    #             "description": "Review and expand vocabulary for family (mother, father, sibling)."
    #         },
    #         {
    #              "name": "Talking About Your Family",
    #              "description": "Practice describing your immediate family members."
    #         },
    #         {
    #              "name": "Asking About Someone's Family",
    #              "description": "Learn simple questions to ask about others' families."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "Food and Drinks (Basics)",
    #     "chapter": 12,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Naming Common Foods",
    #             "description": "Learn the names for basic food items like bread and fruit."
    #         },
    #         {
    #             "name": "Naming Common Drinks",
    #             "description": "Learn the names for basic beverages like water."
    #         },
    #         {
    #             "name": "Expressing Likes and Dislikes (Food)",
    #             "description": "Learn simple phrases to say if you like or dislike a food/drink."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    #  {
    #     "name": "Time (Hours and Minutes)",
    #     "chapter": 13,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Asking 'What time is it?'",
    #             "description": "Learn the common question to ask for the time."
    #         },
    #         {
    #             "name": "Telling Time (Hours)",
    #             "description": "Learn how to say the time on the hour (e.g., 3 o'clock)."
    #         },
    #         {
    #              "name": "Telling Time (Hours and Minutes)",
    #              "description": "Learn basic ways to state the time including minutes."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "Weather",
    #     "chapter": 14,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Basic Weather Vocabulary",
    #             "description": "Learn words for common weather conditions (sunny, rainy, hot, cold)."
    #         },
    #         {
    #             "name": "Describing the Weather",
    #             "description": "Practice forming simple sentences about the current weather."
    #         },
    #         {
    #             "name": "Asking About the Weather",
    #             "description": "Learn how to ask 'How is the weather?'."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "Places (Around Town)",
    #     "chapter": 15,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Naming Common Places",
    #             "description": "Learn the names of locations like school, shop, park, and house."
    #         },
    #         {
    #             "name": "Asking 'Where is...?'",
    #             "description": "Learn how to ask for the location of a place."
    #         },
    #          {
    #             "name": "Identifying Places",
    #             "description": "Practice recognizing and naming common places in a town."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "Directions",
    #     "chapter": 16,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Basic Direction Words",
    #             "description": "Learn the words for left, right, and straight."
    #         },
    #         {
    #             "name": "Asking for Simple Directions",
    #             "description": "Learn basic questions to ask for directions."
    #         },
    #         {
    #             "name": "Giving Simple Directions",
    #             "description": "Practice using 'left', 'right', 'straight' to give basic directions."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    #  {
    #     "name": "Shopping (Basics)",
    #     "chapter": 17,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Asking 'How much is it?'",
    #             "description": "Learn the phrase to ask for the price of an item."
    #         },
    #         {
    #             "name": "Saying 'I want this.'",
    #             "description": "Learn a simple phrase to indicate you want to buy something."
    #         },
    #         {
    #             "name": "Basic Shopping Interaction",
    #             "description": "Practice simple phrases used when buying an item."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    #  {
    #     "name": "Adjectives (Describing People and Things)",
    #     "chapter": 18,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Common Descriptive Adjectives",
    #             "description": "Learn basic adjectives like big, small, nice, tall."
    #         },
    #         {
    #             "name": "Describing Objects",
    #             "description": "Practice using adjectives to describe common objects."
    #         },
    #         {
    #             "name": "Describing People",
    #             "description": "Practice using adjectives to describe people simply."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "Daily Routines",
    #     "chapter": 19,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Verbs for Daily Activities",
    #             "description": "Learn verbs related to daily routine: wake up, work, eat, sleep."
    #         },
    #         {
    #             "name": "Describing Your Typical Day",
    #             "description": "Practice talking about your daily schedule in simple terms."
    #         },
    #         {
    #             "name": "Asking About Others' Routines",
    #             "description": "Learn simple questions to ask about someone else's day."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "Likes and Dislikes",
    #     "chapter": 20,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Expressing 'I like'",
    #             "description": "Learn how to say you like something (food, activity)."
    #         },
    #         {
    #             "name": "Expressing 'I don't like'",
    #             "description": "Learn how to say you dislike something."
    #         },
    #         {
    #             "name": "Talking About Preferences",
    #             "description": "Practice discussing simple preferences for hobbies, food, etc."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "Months and Seasons",
    #     "chapter": 21,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Names of the Months",
    #             "description": "Learn the twelve months of the year."
    #         },
    #         {
    #             "name": "Names of the Seasons",
    #             "description": "Learn the four seasons."
    #         },
    #         {
    #             "name": "Saying Dates (Simple)",
    #             "description": "Learn basic ways to mention dates."
    #         },
    #         {
    #              "name": "Talking About Seasons",
    #              "description": "Practice simple sentences related to months and seasons."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    #  {
    #     "name": "Transportation",
    #     "chapter": 22,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Common Transport Vocabulary",
    #             "description": "Learn names for modes of transport like bus, car, bike."
    #         },
    #         {
    #             "name": "Talking About How You Travel",
    #             "description": "Practice saying how you get to places."
    #         },
    #         {
    #             "name": "Asking About Transportation",
    #             "description": "Learn simple questions about travel methods."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    #  {
    #     "name": "Body Parts",
    #     "chapter": 23,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Naming Basic Body Parts",
    #             "description": "Learn vocabulary for head, hand, foot, etc."
    #         },
    #         {
    #             "name": "Identifying Body Parts",
    #             "description": "Practice pointing to and naming basic body parts."
    #         },
    #         {
    #             "name": "Describing Simple Ailments",
    #             "description": "Learn basic phrases like 'My head hurts'."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    #  {
    #     "name": "Clothing",
    #     "chapter": 24,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Common Clothing Items",
    #             "description": "Learn names for clothes like shirt, shoes, hat."
    #         },
    #         {
    #             "name": "Describing What You Wear",
    #             "description": "Practice saying what clothes you are wearing."
    #         },
    #         {
    #              "name": "Identifying Clothes",
    #              "description": "Practice recognizing and naming different clothing items."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "At the Restaurant",
    #     "chapter": 25,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Asking for a Menu",
    #             "description": "Learn the phrase to request a menu."
    #         },
    #         {
    #             "name": "Ordering Food and Drinks",
    #             "description": "Practice simple phrases for ordering (e.g., 'I want...', 'Please bring...')."
    #         },
    #         {
    #             "name": "Basic Restaurant Interaction",
    #             "description": "Role-play a simple restaurant scenario."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "Occupations",
    #     "chapter": 26,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Common Job Titles",
    #             "description": "Learn vocabulary for occupations like teacher, doctor, student."
    #         },
    #         {
    #             "name": "Saying Your Job",
    #             "description": "Practice stating your occupation."
    #         },
    #         {
    #             "name": "Asking 'What do you do?'",
    #             "description": "Learn how to ask someone about their job."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    #  {
    #     "name": "Hobbies and Free Time",
    #     "chapter": 27,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Common Hobby Vocabulary",
    #             "description": "Learn words for hobbies like reading, sports, music."
    #         },
    #         {
    #             "name": "Talking About Your Hobbies",
    #             "description": "Practice discussing what you like to do in your free time."
    #         },
    #         {
    #              "name": "Asking About Hobbies",
    #              "description": "Learn how to ask others about their free time activities."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    #  {
    #     "name": "Animals",
    #     "chapter": 28,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Naming Common Animals",
    #             "description": "Learn the names of animals like dog, cat, bird."
    #         },
    #         {
    #             "name": "Talking About Pets",
    #             "description": "Practice simple sentences about pets (having a pet, liking animals)."
    #         },
    #          {
    #             "name": "Identifying Animals",
    #             "description": "Practice recognizing and naming common animals."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    #  {
    #     "name": "Basic Emotions and Feelings",
    #     "chapter": 29,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Vocabulary for Feelings",
    #             "description": "Learn words to express basic emotions (happy, sad, tired)."
    #         },
    #         {
    #             "name": "Saying How You Feel",
    #             "description": "Practice stating your current feeling."
    #         },
    #         {
    #             "name": "Asking 'How are you feeling?'",
    #             "description": "Learn how to ask about someone's emotional state."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills to access the next chapter."
    #         }
    #     ]
    # },
    # {
    #     "name": "Everyday Life",
    #     "chapter": 30,
    #     "difficulty": "A1",
    #     "lessons": [
    #         {
    #             "name": "Reviewing Daily Activities",
    #             "description": "Consolidate vocabulary and phrases for common routines and tasks."
    #         },
    #         {
    #             "name": "Basic Social Interactions",
    #             "description": "Practice simple conversations covering topics from previous chapters."
    #         },
    #         {
    #             "name": "Communication Basics Recap",
    #             "description": "Review essential questions, answers, and polite expressions."
    #         },
    #         {
    #             "name": "Checkpoint",
    #             "description": "Test your skills and review A1 basics."
    #         }
    #     ]
    # }
]