# onboarding.py

QUESTIONS = [
    {'key': 'name',          'q': 'Hey! Welcome to MatchMind 💘 What is your name and how old are you?'},
    {'key': 'personality',   'q': 'Are you more introverted, extroverted, or an ambivert?'},
    {'key': 'looking_for',   'q': 'What are you looking for — serious relationship, marriage, or casual?'},
    {'key': 'hobbies',       'q': 'What are your favorite hobbies? List what you are passionate about.'},
    {'key': 'music_genres',  'q': 'Your go-to music genre? What plays on repeat?'},
    {'key': 'pets',          'q': 'Cat person, dog person, or neither?'},
    {'key': 'fav_books',     'q': 'A book, series, or film that left a mark on you?'},
    {'key': 'fav_foods',     'q': 'Your favorite food? And what do you absolutely refuse to eat?'},
    {'key': 'travel_style',  'q': 'Travel style: wild adventure, cultural city-trip, beach relaxation, or luxury?'},
    {'key': 'love_language', 'q': 'Your love language: words, acts of service, touch, gifts, or quality time?'},
    {'key': 'values',        'q': 'The most important values you want in a partner?'},
    {'key': 'red_flags',     'q': 'Your absolute red flags — things you genuinely cannot accept?'},
    {'key': 'wants_children','q': 'Kids: do you want them, already have them, or is it a hard no?'},
    {'key': 'religion',      'q': 'Does religion play a role in your relationships?'},
    {'key': 'secret',        'q': 'One last thing about you that most people do not know 😉'},
]


def build_bio(profile: dict) -> str:
    """Convert full profile dict into a natural text string for FAISS embedding."""
    parts = []
    if profile.get('name'):          parts.append(str(profile['name']))
    if profile.get('personality'):   parts.append(f"Personality: {profile['personality']}")
    if profile.get('looking_for'):   parts.append(f"Seeking: {profile['looking_for']}")
    if profile.get('hobbies'):       parts.append(f"Hobbies: {profile['hobbies']}")
    if profile.get('music_genres'):  parts.append(f"Music: {profile['music_genres']}")
    if profile.get('fav_books'):     parts.append(f"Books/Series: {profile['fav_books']}")
    if profile.get('fav_foods'):     parts.append(f"Food: {profile['fav_foods']}")
    if profile.get('travel_style'):  parts.append(f"Travel: {profile['travel_style']}")
    if profile.get('love_language'): parts.append(f"Love language: {profile['love_language']}")
    if profile.get('values'):        parts.append(f"Values: {profile['values']}")
    if profile.get('red_flags'):     parts.append(f"Dealbreakers: {profile['red_flags']}")
    if profile.get('secret'):        parts.append(str(profile['secret']))
    # Gen Z tags
    if profile.get('vibe_archetype'):   parts.append(f"Vibe: {profile['vibe_archetype']}")
    if profile.get('attachment_style'): parts.append(f"Attachment: {profile['attachment_style']}")
    if profile.get('romance_trope'):    parts.append(f"Romance style: {profile['romance_trope']}")
    return '. '.join(parts) + '.'