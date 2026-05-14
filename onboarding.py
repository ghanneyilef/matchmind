# onboarding.py

QUESTIONS = [
    {'key': 'name',
     'q': 'Hey! Welcome to MatchMind 💘 What is your name and how old are you?'},

    {'key': 'gender',
     'q': 'What is your gender? (homme / femme)'},

    {'key': 'personality',
     'q': 'Are you more introverted, extroverted, or an ambivert?'},

    {'key': 'looking_for',
     'q': 'What are you looking for? (relation sérieuse / mariage / casual)'},

    {'key': 'hobbies',
     'q': 'What are your favorite hobbies? List what you are passionate about.'},

    {'key': 'music_genres',
     'q': 'Your go-to music genre? What plays on repeat?'},

    {'key': 'netflix_show',
     'q': 'Which Netflix show perfectly matches your vibe? 🎬'},

    {'key': 'romance_trope',
     'q': 'Enemies-to-lovers or friends-to-lovers? 💥❤️'},

    {'key': 'social_style',
     'q': 'Clubbing and loud energy 🪩 or cozy café and board games ☕?'},

    {'key': 'communication_style',
     'q': 'Voice notes or texting? 🎙️'},

    {'key': 'fav_foods',
     'q': 'Your favorite food? (ex: pizza, sushi, tacos — be specific 🍕)'},

    {'key': 'food_dealbreaker',
     'q': 'What food do you absolutely refuse to eat? (ex: olives, foie gras — the more specific the better 🚫)'},

    {'key': 'travel_style',
     'q': 'Travel style: wild adventure 🏕️, cultural city-trip 🏛️, beach relaxation 🏖️, or luxury ✈️?'},

    {'key': 'love_language',
     'q': 'Your love language: words of affirmation, acts of service, physical touch, gifts, or quality time? 💬'},

    {'key': 'values',
     'q': 'The most important values you want in a partner? (ex: loyalty, ambition, humour, kindness)'},

    {'key': 'red_flags',
     'q': 'Your absolute red flags — things you genuinely cannot accept in a relationship? 🚩'},

    {'key': 'relationship_dealbreaker',
     'q': 'What is your biggest relationship dealbreaker? The one thing that ends it immediately? 💔'},

    {'key': 'ideal_first_date',
     'q': 'Describe your ideal first date 🌹 — where, what, what vibe?'},

    {'key': 'wants_children',
     'q': 'Kids: do you want them, already have them, or is it a hard no?'},

    {'key': 'confession',
     'q': '"We listen and we don\'t judge" 🤫 — say one thing about you that surprises people.'},
]


def build_bio(profile: dict) -> str:
    """Convert full profile dict into natural text for FAISS embedding."""
    parts = []

    if profile.get('name'):
        parts.append(str(profile['name']))
    if profile.get('gender'):
        parts.append(f"Gender: {profile['gender']}")
    if profile.get('personality'):
        parts.append(f"Personality: {profile['personality']}")
    if profile.get('looking_for'):
        parts.append(f"Seeking: {profile['looking_for']}")
    if profile.get('hobbies'):
        parts.append(f"Hobbies: {profile['hobbies']}")
    if profile.get('music_genres'):
        parts.append(f"Music: {profile['music_genres']}")
    if profile.get('netflix_show'):
        parts.append(f"Netflix vibe: {profile['netflix_show']}")
    if profile.get('romance_trope'):
        parts.append(f"Romance style: {profile['romance_trope']}")
    if profile.get('social_style'):
        parts.append(f"Social style: {profile['social_style']}")
    if profile.get('communication_style'):
        parts.append(f"Communication: {profile['communication_style']}")
    if profile.get('fav_foods'):
        parts.append(f"Favourite food: {profile['fav_foods']}")
    if profile.get('food_dealbreaker'):
        parts.append(f"Food dealbreaker: {profile['food_dealbreaker']}")
    if profile.get('travel_style'):
        parts.append(f"Travel: {profile['travel_style']}")
    if profile.get('love_language'):
        parts.append(f"Love language: {profile['love_language']}")
    if profile.get('values'):
        parts.append(f"Values: {profile['values']}")
    if profile.get('red_flags'):
        parts.append(f"Red flags: {profile['red_flags']}")
    if profile.get('relationship_dealbreaker'):
        parts.append(f"Dealbreaker: {profile['relationship_dealbreaker']}")
    if profile.get('ideal_first_date'):
        parts.append(f"Ideal first date: {profile['ideal_first_date']}")
    if profile.get('wants_children'):
        parts.append(f"Kids: {profile['wants_children']}")
    if profile.get('confession'):
        parts.append(f"Secret: {profile['confession']}")
    # Archetype tags (auto-generated or from database)
    if profile.get('vibe_archetype'):
        parts.append(f"Vibe archetype: {profile['vibe_archetype']}")
    if profile.get('attachment_style'):
        parts.append(f"Attachment style: {profile['attachment_style']}")

    return '. '.join(parts) + '.'