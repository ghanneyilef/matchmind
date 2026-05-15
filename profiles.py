import re

def compute_compatibility(a: dict, b: dict) -> dict:

    # ── 1. Red flags — INSTANT BLOCK ──────────────────────────────
    # Only match against specific text fields to avoid false positives.
    TEXT_FIELDS = ('bio', 'personality', 'social_style', 'communication_style',
                   'romance_trope', 'love_language', 'looking_for', 'travel_style')

    def _profile_text(p: dict) -> str:
        parts = [str(p.get(f, '')) for f in TEXT_FIELDS]
        parts += [str(v) for v in p.get('values', [])]
        parts += [str(h) for h in p.get('hobbies', [])]
        return ' '.join(parts).lower()

    def _word_match(keyword: str, text: str) -> bool:
        """Match whole words only — prevents 'D' matching inside 'adventure' etc."""
        keyword = keyword.strip().lower()
        if len(keyword) < 3:          # ignore very short flags — too noisy
            return False
        return bool(re.search(r'\b' + re.escape(keyword) + r'\b', text))

    b_text = _profile_text(b)
    for flag in a.get('red_flags', []):
        if _word_match(flag, b_text):
            return {'score': 0, 'blocked': flag, 'breakdown': {}}

    a_text = _profile_text(a)
    for flag in b.get('red_flags', []):
        if _word_match(flag, a_text):
            return {'score': 0, 'blocked': flag, 'breakdown': {}}

    # ── 2. Food dealbreaker cross-check ───────────────────────────
    def _food_list(p: dict, key: str):
        v = p.get(key, '')
        if isinstance(v, list):
            return [f.strip().lower() for f in v if f.strip()]
        return [s.strip().lower() for s in str(v).split(',') if s.strip()]

    a_fav  = _food_list(a, 'fav_foods')
    b_deal = _food_list(b, 'food_dealbreaker')
    for food in a_fav:
        if len(food) >= 3 and any(_word_match(food, d) for d in b_deal):
            return {'score': 0, 'blocked': f"food conflict: {food}", 'breakdown': {}}

    b_fav  = _food_list(b, 'fav_foods')
    a_deal = _food_list(a, 'food_dealbreaker')
    for food in b_fav:
        if len(food) >= 3 and any(_word_match(food, d) for d in a_deal):
            return {'score': 0, 'blocked': f"food conflict: {food}", 'breakdown': {}}

    # ── 3. Helpers ─────────────────────────────────────────────────
    def jaccard(l1, l2):
        if isinstance(l1, str): l1 = [l1]
        if isinstance(l2, str): l2 = [l2]
        s1, s2 = set(str(x).lower() for x in l1), set(str(x).lower() for x in l2)
        if not s1 and not s2: return 50
        return len(s1 & s2) / len(s1 | s2) * 100

    def exact(v1, v2):
        return 100 if v1 == v2 else (65 if v1 and v2 else 20)

    def partial(v1, v2):
        if not v1 or not v2: return 20
        v1, v2 = str(v1).lower(), str(v2).lower()
        return 100 if v1 == v2 else (75 if v1 in v2 or v2 in v1 else 30)

    # ── 4. Scoring breakdown ───────────────────────────────────────
    breakdown = {
        'values':         jaccard(a.get('values', []),        b.get('values', [])),
        'life_goals':     partial(a.get('looking_for'),        b.get('looking_for')),
        'hobbies':        jaccard(a.get('hobbies', []),        b.get('hobbies', [])),
        'music':          jaccard(a.get('music_genres', []),   b.get('music_genres', [])),
        'travel':         exact(a.get('travel_style'),         b.get('travel_style')),
        'love_language':  exact(a.get('love_language'),        b.get('love_language')),
        'romance_trope':  exact(a.get('romance_trope'),        b.get('romance_trope')),
        'social_style':   exact(a.get('social_style'),         b.get('social_style')),
        'communication':  exact(a.get('communication_style'),  b.get('communication_style')),
        'wants_children': exact(a.get('wants_children'),       b.get('wants_children')),
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