LANGUAGE_OPTIONS = ["English", "Francais"]
LANGUAGE_CODES = {"English": "en", "Francais": "fr"}


TEXT = {
    "en": {
        "profile_title": "Your profile",
        "stats_title": "Stats",
        "agent_title": "Agent online",
        "agent_status": "Connected - multi-step reasoning",
        "quick_title": "Quick questions",
        "progress_suffix": "questions",
        "profile_done": "Profile complete!",
        "input_placeholder": "Type your answer here...",
        "language_label": "Language",
        "theme_label": "Theme",
        "light": "Light",
        "dark": "Dark",
        "btn_match": "My perfect match?",
        "btn_top1": "My #1 match?",
        "btn_report": "Full report",
        "btn_advice": "First date advice",
        "stats_candidates": "candidates",
        "stats_top_matches": "top matches",
        "done_msg": "Perfect {name}! Your profile is saved. I have **{count} candidates** in the database. Ask me to find your best matches.",
        "fallback_error": "Sorry, I could not process your request. Please try again.",
        "finish_onboarding": "Please finish the onboarding questions first. I will find your matches right after.",
        "quick_match_prompt": "Find my best matches",
        "quick_top1_prompt": "Who is my number one match?",
        "quick_report_prompt": "Generate a full report for my best match",
        "quick_advice_prompt": "Give me first date advice",
    },
    "fr": {
        "profile_title": "Ton profil",
        "stats_title": "Stats",
        "agent_title": "Agent en ligne",
        "agent_status": "Connecte - raisonnement multi-etapes",
        "quick_title": "Questions rapides",
        "progress_suffix": "questions",
        "profile_done": "Profil complet !",
        "input_placeholder": "Ecris ta reponse ici...",
        "language_label": "Langue",
        "theme_label": "Theme",
        "light": "Clair",
        "dark": "Sombre",
        "btn_match": "Mon perfect match ?",
        "btn_top1": "Mon match numero 1 ?",
        "btn_report": "Rapport complet",
        "btn_advice": "Conseils pour le 1er RDV",
        "stats_candidates": "candidats",
        "stats_top_matches": "top matchs",
        "done_msg": "Parfait {name} ! Ton profil est sauvegarde. J'ai **{count} candidats** dans la base. Demande-moi de trouver tes meilleurs matchs.",
        "fallback_error": "Desole, je n'ai pas pu traiter ta demande. Reessaie.",
        "finish_onboarding": "Termine d'abord le questionnaire ! Je trouverai tes matchs juste apres.",
        "quick_match_prompt": "Trouve mes meilleurs matchs",
        "quick_top1_prompt": "Qui est mon match numero 1 ?",
        "quick_report_prompt": "Genere un rapport complet pour mon meilleur match",
        "quick_advice_prompt": "Donne-moi des conseils pour le premier rendez-vous",
    },
}


QUESTIONS_BY_LANGUAGE = {
    "en": {
        "name": "Hey! Welcome to MatchMind. What is your name and how old are you?",
        "gender": "What is your gender? (man / woman / other)",
        "personality": "Are you more introverted, extroverted, or an ambivert?",
        "looking_for": "What are you looking for? (serious relationship / marriage / casual)",
        "hobbies": "What are your favorite hobbies? List what you are passionate about.",
        "music_genres": "Your go-to music genre? What plays on repeat?",
        "netflix_show": "Which Netflix show perfectly matches your vibe?",
        "romance_trope": "Enemies-to-lovers or friends-to-lovers?",
        "social_style": "Clubbing and loud energy, or cozy cafe and board games?",
        "communication_style": "Voice notes or texting?",
        "fav_foods": "Your favorite food? Be specific.",
        "food_dealbreaker": "What food do you absolutely refuse to eat?",
        "travel_style": "Travel style: wild adventure, cultural city-trip, beach relaxation, or luxury?",
        "love_language": "Your love language: words of affirmation, acts of service, physical touch, gifts, or quality time?",
        "values": "The most important values you want in a partner?",
        "red_flags": "Your absolute red flags: things you genuinely cannot accept in a relationship?",
        "relationship_dealbreaker": "What is your biggest relationship dealbreaker?",
        "ideal_first_date": "Describe your ideal first date: where, what, what vibe?",
        "wants_children": "Kids: do you want them, already have them, or is it a hard no?",
        "confession": '"We listen and we do not judge": say one thing about you that surprises people.',
    },
    "fr": {
        "name": "Bienvenue sur MatchMind. Comment tu t'appelles et quel age as-tu ?",
        "gender": "Quel est ton genre ? (homme / femme / autre)",
        "personality": "Tu es plutot introverti, extraverti, ou ambivert ?",
        "looking_for": "Tu cherches quoi ? (relation serieuse / mariage / casual)",
        "hobbies": "Quels sont tes hobbies preferes ?",
        "music_genres": "Ton genre de musique prefere ?",
        "netflix_show": "Quelle serie Netflix correspond le mieux a ton vibe ?",
        "romance_trope": "Enemies-to-lovers ou friends-to-lovers ?",
        "social_style": "Clubbing et grosse energie, ou cafe cozy et jeux de societe ?",
        "communication_style": "Notes vocales ou textos ?",
        "fav_foods": "Ton plat prefere ? Sois specifique.",
        "food_dealbreaker": "Quel aliment refuses-tu absolument de manger ?",
        "travel_style": "Style de voyage : aventure, city-trip culturel, plage, ou luxe ?",
        "love_language": "Ton love language : mots doux, services, toucher, cadeaux, ou quality time ?",
        "values": "Les valeurs les plus importantes chez un partenaire ?",
        "red_flags": "Tes red flags absolus dans une relation ?",
        "relationship_dealbreaker": "Ton plus gros dealbreaker amoureux ?",
        "ideal_first_date": "Decris ton premier date ideal : lieu, activite, vibe.",
        "wants_children": "Les enfants : tu en veux, tu en as deja, ou c'est non ?",
        "confession": '"On ecoute et on ne juge pas" : dis une chose surprenante sur toi.',
    },
}


def language_code(label_or_code: str | None) -> str:
    if label_or_code in TEXT:
        return label_or_code
    return LANGUAGE_CODES.get(label_or_code or "English", "en")


def label_for_language(code: str | None) -> str:
    code = language_code(code)
    return "Francais" if code == "fr" else "English"


def tr(language: str | None, key: str, **kwargs) -> str:
    lang = language_code(language)
    value = TEXT.get(lang, TEXT["en"]).get(key, TEXT["en"].get(key, key))
    return value.format(**kwargs) if kwargs else value


def question_for(language: str | None, questions: list[dict], idx: int) -> str:
    idx = min(max(idx, 0), len(questions) - 1)
    key = questions[idx]["key"]
    return QUESTIONS_BY_LANGUAGE.get(language_code(language), QUESTIONS_BY_LANGUAGE["en"]).get(
        key,
        questions[idx]["q"],
    )
