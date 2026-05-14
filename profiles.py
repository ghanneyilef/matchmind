import uuid
def compute_compatibility(a: dict, b: dict) -> dict:

    # ── 1. Red flags — INSTANT BLOCK ──────────────────────────────
    for flag in a.get('red_flags', []):
        if flag.lower() in str(b).lower():
            return {'score': 0, 'blocked': flag, 'breakdown': {}}
    for flag in b.get('red_flags', []):
        if flag.lower() in str(a).lower():
            return {'score': 0, 'blocked': flag, 'breakdown': {}}

    # ── 2. Food dealbreaker cross-check ───────────────────────────
    # If A's favourite food is B's food dealbreaker → block
    a_fav  = [f.lower() for f in a.get('fav_foods', [])] if isinstance(a.get('fav_foods'), list) else [str(a.get('fav_foods', '')).lower()]
    b_deal = str(b.get('food_dealbreaker', '')).lower()
    for food in a_fav:
        if food and food in b_deal:
            return {'score': 0, 'blocked': f"food conflict: {food}", 'breakdown': {}}

    b_fav  = [f.lower() for f in b.get('fav_foods', [])] if isinstance(b.get('fav_foods'), list) else [str(b.get('fav_foods', '')).lower()]
    a_deal = str(a.get('food_dealbreaker', '')).lower()
    for food in b_fav:
        if food and food in a_deal:
            return {'score': 0, 'blocked': f"food conflict: {food}", 'breakdown': {}}

    # ── 3. Helpers ─────────────────────────────────────────────────
    def jaccard(l1, l2):
        # Handle both list and string inputs
        if isinstance(l1, str): l1 = [l1]
        if isinstance(l2, str): l2 = [l2]
        s1, s2 = set(l1), set(l2)
        if not s1 and not s2: return 50
        return len(s1 & s2) / len(s1 | s2) * 100

    def exact(v1, v2):
        return 100 if v1 == v2 else (65 if v1 and v2 else 20)

    def partial(v1, v2):
        """Partial match — checks if one string contains the other."""
        if not v1 or not v2: return 20
        v1, v2 = str(v1).lower(), str(v2).lower()
        return 100 if v1 == v2 else (75 if v1 in v2 or v2 in v1 else 30)

    # ── 4. Scoring breakdown ───────────────────────────────────────
    breakdown = {
        'values':          jaccard(a.get('values', []),        b.get('values', [])),
        'life_goals':      exact(a.get('looking_for'),         b.get('looking_for')),
        'hobbies':         jaccard(a.get('hobbies', []),       b.get('hobbies', [])),
        'music':           jaccard(a.get('music_genres', []),  b.get('music_genres', [])),
        'travel':          exact(a.get('travel_style'),        b.get('travel_style')),
        'love_language':   exact(a.get('love_language'),       b.get('love_language')),
        'romance_trope':   exact(a.get('romance_trope'),       b.get('romance_trope')),
        'social_style':    exact(a.get('social_style'),        b.get('social_style')),
        'communication':   exact(a.get('communication_style'), b.get('communication_style')),
        'wants_children':  exact(a.get('wants_children'),      b.get('wants_children')),
    }

    weights = {
        'values':         0.22,
        'life_goals':     0.18,
        'hobbies':        0.12,
        'music':          0.08,
        'travel':         0.07,
        'love_language':  0.10,
        'romance_trope':  0.08,
        'social_style':   0.07,
        'communication':  0.05,
        'wants_children': 0.03,
    }

    total = round(sum(breakdown[k] * weights[k] for k in breakdown))
    return {'score': total, 'breakdown': breakdown, 'blocked': None}