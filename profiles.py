# profiles.py
import uuid

def compute_compatibility(a: dict, b: dict) -> dict:
    # 1. Red flags check — INSTANT BLOCK
    for flag in a.get('red_flags', []):
        if flag.lower() in str(b).lower():
            return {'score': 0, 'blocked': flag, 'breakdown': {}}
    for flag in b.get('red_flags', []):
        if flag.lower() in str(a).lower():
            return {'score': 0, 'blocked': flag, 'breakdown': {}}

    def jaccard(l1, l2):
        s1, s2 = set(l1), set(l2)
        if not s1 and not s2: return 50
        return len(s1 & s2) / len(s1 | s2) * 100

    def exact(v1, v2):
        return 100 if v1 == v2 else (65 if v1 and v2 else 20)

    breakdown = {
        'values':     jaccard(a.get('values', []),       b.get('values', [])),
        'life_goals': exact(a.get('looking_for'),        b.get('looking_for')),
        'hobbies':    jaccard(a.get('hobbies', []),      b.get('hobbies', [])),
        'music':      jaccard(a.get('music_genres', []), b.get('music_genres', [])),
        'food':       jaccard(a.get('fav_foods', []),    b.get('fav_foods', [])),
        'travel':     exact(a.get('travel_style'),       b.get('travel_style')),
        'love_lang':  exact(a.get('love_language'),      b.get('love_language')),
        'location':   exact(a.get('city'),               b.get('city')),
    }
    weights = {
        'values': 0.25, 'life_goals': 0.20, 'hobbies': 0.15,
        'music':  0.10, 'food': 0.08,       'travel':  0.07,
        'love_lang': 0.10, 'location': 0.05
    }
    total = round(sum(breakdown[k] * weights[k] for k in breakdown))
    return {'score': total, 'breakdown': breakdown, 'blocked': None}