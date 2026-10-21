# ==============================================================================
# MASCOT & STUDY COMPANION CONFIGURATION FRAMEWORK
# 100% English - Customizable Interactive Character Profiles
# ==============================================================================

import json

# ------------------------------------------------------------------------------
# HOW TO ADD OR CUSTOMIZE MASCOTS:
# 1. Duplicate any character block below.
# 2. Give it a unique ID (e.g., 'leo_lion', 'mimi_cat').
# 3. Replace image URLs with your own assets:
#    - Online URLs: "https://your-domain.com/images/leo_idle.png"
#    - Local files: "assets/mascots/leo_idle.png" (or base64 data URIs)
# 4. Customize personality quotes for 'welcome', 'correct', 'wrong', and 'celebrate'.
# ------------------------------------------------------------------------------

MASCOTS = {
    "leo_lion": {
        "id": "leo_lion",
        "name": "Leo the Lion",
        "badge": "🦁",
        "personality": "Brave & Energetic",
        "description": "Roars with courage! Always eager to tackle new challenges.",
        "expressions": {
            "idle": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=LeoLion&backgroundColor=ffeaa7",
            "correct": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=LeoLionHappy&backgroundColor=55efc4",
            "encourage": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=LeoLionThink&backgroundColor=fdcb6e",
            "celebrate": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=LeoLionWin&backgroundColor=fd79a8"
        },
        "quotes": {
            "welcome": [
                "Roar! Ready to conquer new English missions today, champ?",
                "Hello friend! Leo is ready for an awesome learning adventure!",
                "Great to see you! Let's unleash our superpower today!"
            ],
            "correct": [
                "Roaring good job! 🌟",
                "Super work, champ! You nailed it! 💪",
                "Spot on! Your brain is mighty! 🦁",
                "Boom! That was flawless! ⭐",
                "Awesome! Keep that winning streak going! 🚀"
            ],
            "wrong": [
                "Shake it off, champ! You can do this! 🦁",
                "No worries! Great learners learn from every try! 💪",
                "Take a deep breath and try again! You got this! ✨",
                "Almost there! Review the clue and try one more time!"
            ],
            "celebrate": [
                "RAINBOW CHAMPION! You conquered the entire mission! 🏆",
                "Unstoppable! You are truly a superstar today! 🌟"
            ]
        }
    },

    "pandy_panda": {
        "id": "pandy_panda",
        "name": "Pandy the Panda",
        "badge": "🐼",
        "personality": "Clever & Calm",
        "description": "Wise and thoughtful. Loves solving puzzles with patience.",
        "expressions": {
            "idle": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=PandyPanda&backgroundColor=dfe6e9",
            "correct": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=PandyPandaSmart&backgroundColor=81ecec",
            "encourage": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=PandyPandaCalm&backgroundColor=fab1a0",
            "celebrate": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=PandyPandaStar&backgroundColor=a29bfe"
        },
        "quotes": {
            "welcome": [
                "Hello! Let's take it step by step and learn something wonderful!",
                "Welcome back! A calm mind is the sharpest mind. Let's do this!",
                "Pandy is happy to study with you today!"
            ],
            "correct": [
                "Brilliant thinking! 🐼✨",
                "So clever! Perfect answer! 🎋",
                "Wise choice! You figured it out! 🌟",
                "Splendid! Your focus is truly inspiring! 🎯",
                "Clean and sharp! Excellent job! 🌸"
            ],
            "wrong": [
                "Take your time, my friend! Think calmly. 🐼",
                "Mistakes are just stepping stones to wisdom! Try again! ✨",
                "It's okay! Let's examine the options carefully together. 🎋",
                "Patience brings victory! You will get it next time!"
            ],
            "celebrate": [
                "Mastery achieved! You finished the whole mission with grace! 🏆",
                "Pandy is so proud of your brilliant dedication! 🎋🌟"
            ]
        }
    },

    "sparky_robot": {
        "id": "sparky_robot",
        "name": "Sparky the Robot",
        "badge": "🤖",
        "personality": "Tech & Curious",
        "description": "Fueled by curiosity! Loves data, logic, and rapid progress.",
        "expressions": {
            "idle": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=SparkyBot&backgroundColor=74b9ff",
            "correct": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=SparkyOverdrive&backgroundColor=00cec9",
            "encourage": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=SparkyReboot&backgroundColor=ffeaa7",
            "celebrate": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=SparkyUltra&backgroundColor=e84393"
        },
        "quotes": {
            "welcome": [
                "BEEP BOOP! Systems online. Ready to boost your English power!",
                "Greetings, human partner! Sparky is charged and ready to learn!",
                "Calculating success probability... 100%! Let's start!"
            ],
            "correct": [
                "BEEP! 100% Accuracy detected! ⚡",
                "Target acquired and solved! Super smart! 🤖",
                "Processing... Result: EXCELLENT! 🌟",
                "High voltage knowledge! You are on fire! 🔥",
                "Maximum points! Sparky is super impressed! 🚀"
            ],
            "wrong": [
                "Recalibrating! Don't worry, every error is a software upgrade! 🤖",
                "Debug mode activated! Try one more time, you can do it! ⚡",
                "System alert: Keep trying! You are very close! 🔧",
                "Re-scanning... Let's give it another shot!"
            ],
            "celebrate": [
                "MISSION COMPLETE! All data circuits celebrate your victory! 🏆⚡",
                "MAXIMUM LEVEL UNLOCKED! You are an English master! 🚀"
            ]
        }
    },

    "luna_bunny": {
        "id": "luna_bunny",
        "name": "Luna the Bunny",
        "badge": "🐰",
        "personality": "Sweet & Cheerful",
        "description": "Always smiling! Bounces with joy and spreads sunshine.",
        "expressions": {
            "idle": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=LunaBunny&backgroundColor=ffcccc",
            "correct": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=LunaJoy&backgroundColor=fab1a0",
            "encourage": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=LunaHug&backgroundColor=ffeaa7",
            "celebrate": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=LunaParty&backgroundColor=fd79a8"
        },
        "quotes": {
            "welcome": [
                "Yay, you're here! Luna is so excited to learn with you today! 🐰",
                "Hop hop hooray! Let's have the most fun English day ever! 🌸",
                "Hello sunshine! Ready to sparkle and shine?"
            ],
            "correct": [
                "Hooray! That is wonderful! 🐰💖",
                "You did it! Jumping for joy! 🌸✨",
                "Super star! You are so awesome! ⭐",
                "Yay yay yay! That was totally right! 🥕",
                "Magic answer! Keep blooming, little star! 🌼"
            ],
            "wrong": [
                "A big warm hug for you! You can do it, try again! 🐰💕",
                "Don't feel sad! Luna believes in you 100%! 🌸",
                "Take a little hop and try once more! You're almost there! ✨",
                "You're doing great! Let's try one more time together!"
            ],
            "celebrate": [
                "YAY! RAINBOW UNLOCKED! You did the whole mission! 🏆🎉",
                "Luna is dancing with joy for you! You are a true champion! 🐰🌟"
            ]
        }
    },

    "rex_dino": {
        "id": "rex_dino",
        "name": "Rex the Dino",
        "badge": "🦖",
        "personality": "Mighty & Playful",
        "description": "Giant energy and big heart! Loves adventurous quests.",
        "expressions": {
            "idle": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=RexDino&backgroundColor=b2bec3",
            "correct": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=RexDinoMighty&backgroundColor=55efc4",
            "encourage": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=RexDinoCheer&backgroundColor=feca57",
            "celebrate": "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=RexDinoKing&backgroundColor=fdcb6e"
        },
        "quotes": {
            "welcome": [
                "STOMP STOMP! Rex is here! Ready for a colossal mission? 🦖",
                "ROAAAR! Let's crush today's English challenges like a T-Rex!",
                "Greetings, adventurer! Rex has your back all the way!"
            ],
            "correct": [
                "DINO-MITE! Colossal answer! 🦖💥",
                "Mega power! That was incredible! 🌟",
                "Monster brain! Absolutely correct! 🦕",
                "STOMP of victory! You crushed it! ⭐",
                "Jurassic level genius! Keep going! 🌋"
            ],
            "wrong": [
                "Even a T-Rex stumbles sometimes! Stand tall and try again! 🦖",
                "Rex gives you high-fives! You've got the strength, try again! 💪",
                "Shake the dust off! You are tougher than any question! 🌋",
                "Keep stomping forward! The next one is yours!"
            ],
            "celebrate": [
                "COLOSSAL TRIUMPH! You conquered the whole Jurassic quest! 🏆🦖",
                "REX IS ROARING WITH PRIDE! You are the ultimate master! 🌋🌟"
            ]
        }
    }
}

DEFAULT_MASCOT_ID = "leo_lion"

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------
def get_mascot(mascot_id: str) -> dict:
    """Return mascot dict by ID, fallback to default."""
    if not mascot_id:
        return MASCOTS[DEFAULT_MASCOT_ID]
    clean_id = str(mascot_id).replace("mascot:", "").strip().lower()
    return MASCOTS.get(clean_id, MASCOTS[DEFAULT_MASCOT_ID])

def get_all_mascots() -> list:
    """Return list of all mascot objects."""
    return list(MASCOTS.values())

def is_mascot_avatar(avatar_val) -> bool:
    """Check if avatar string is a mascot reference."""
    if not avatar_val:
        return False
    val = str(avatar_val).strip()
    return val.startswith("mascot:") or val in MASCOTS

def parse_student_avatar(avatar_val) -> tuple:
    """
    Parses avatar column from database.
    Returns: (is_mascot: bool, mascot_dict_or_none, image_src: str)
    """
    if not avatar_val:
        m = MASCOTS[DEFAULT_MASCOT_ID]
        return True, m, m["expressions"]["idle"]
    
    val = str(avatar_val).strip()
    if is_mascot_avatar(val):
        m = get_mascot(val)
        return True, m, m["expressions"]["idle"]
    
    # Custom uploaded photo (base64 or direct URL)
    if val.startswith("data:image") or val.startswith("http://") or val.startswith("https://"):
        return False, None, val
    
    # Base64 string without data prefix
    return False, None, f"data:image/jpeg;base64,{val}"

def get_mascot_js_payload(mascot_id: str) -> str:
    """Return JSON string payload for client-side JS reaction logic."""
    m = get_mascot(mascot_id)
    payload = {
        "id": m["id"],
        "name": m["name"],
        "expressions": m["expressions"],
        "quotes": m["quotes"]
    }
    return json.dumps(payload)
