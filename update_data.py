import json, re, os

ICON_MAP = {
    'video_games': 'Gamepad2', 'movies': 'Clapperboard', 'tv_shows': 'Tv', 'memes': 'Laugh', 'people': 'Users',
    'countries': 'Globe', 'school': 'GraduationCap', 'sports': 'Trophy', 'animals': 'PawPrint', 'characters': 'Users',
    'mario_universe': 'Star', 'super_smash_bros': 'Gamepad', 'pok_mon': 'CircleDot',
    'zelda': 'Sword', 'shooter': 'Crosshair', 'fortnite': 'Target', 'minecraft': 'Box',
    'indie_horror': 'Ghost', 'brawl_stars': 'Swords', 'clash_royal': 'Crown',
    'mobile_arcade': 'Gamepad', 'roblox': 'Bot', 'vr': 'Glasses', 'playstation_games': 'Gamepad2',
    'generational': 'Clock', 'brainrot': 'Zap',
    'comedy': 'Popcorn', 'cinephile_favs': 'Award', 'marvel_dc': 'ShieldAlert',
    'sci_fi_fantasy': 'Rocket', 'scifi_fantasy': 'Rocket',
    'horror': 'Skull', 'animated': 'Pencil', 'game_adaptations': 'Gamepad', 'book_adaptations': 'BookOpen',
    'action_thriller': 'Target', 'drama': 'Award', 'crime_mystery': 'Fingerprint', 'animation': 'Pencil',
    'anime': 'Sparkles', 'teen_girls': 'Heart', 'kids': 'Baby', 'reality_documentary': 'Video',
    'social_media': 'Smartphone', 'musicians': 'Music', 'actors_directors': 'Camera', 'athletes': 'Trophy',
    'politicians': 'Flag', 'historical_figures': 'Scroll', 'tech_icons': 'Cpu',
    'artists_writer': 'Palette', 'controversial': 'Flame',
    'disney_pixar': 'Castle', 'star_wars': 'Sword', 'wizarding_world': 'Zap', 'dreamworks_illumination': 'Moon',
    'netflix_prime': 'Tv', 'subjects': 'Book', 'colleges': 'School', 'extracurriculars': 'Activity',
    'stereotypes': 'Theater', 'stem': 'FlaskConical', 'basketball': 'Dribbble', 'football': 'Trophy',
    'soccer': 'Activity', 'net_sports': 'TableTennis', 'water_sports': 'Waves', 'combat_sports': 'Swords',
    'baseball': 'Activity', 'other': 'Plus', 'mammals': 'Dog', 'cold_blooded_animals': 'ThermometerSnowflake',
    'underwater': 'Fish', 'bugs': 'Bug', 'flying': 'Bird',
    'india': 'Flower', 'china': 'Wind', 'united_states': 'Landmark', 'latin_america': 'Music',
    'russia': 'Snowflake', 'japan': 'Mountain', 'italy': 'Pizza', 'france': 'Wine',
    'spain': 'Flame', 'south_korea': 'Smartphone', 'uae': 'Building', 'canada': 'Leaf',
    'uk': 'Crown', 'africa': 'PalmTree'
}

NAME_FIXES = {
    'video_games': 'Video Games', 'pok_mon': 'Pokémon', 'super_smash_bros': 'Super Smash Bros.',
    'indie_horror': 'Indie/Horror', 'clash_royal': 'Clash Royale',
    'mobile_arcade': 'Mobile/Arcade',
    'playstation_games': 'PlayStation Games', 'scifi_fantasy': 'Sci-Fi/Fantasy', 'sci_fi_fantasy': 'Sci-Fi/Fantasy',
    'crime_mystery': 'Crime/Mystery',
    'teen_girls': 'Teen Girls', 'reality_documentary': 'Reality/Documentary', 'marvel_dc': 'Marvel + DC',
    'action_thriller': 'Action/Thriller', 'game_adaptations': 'Game Adaptations', 'book_adaptations': 'Book Adaptations',
    'cinephile_favs': 'Cinephile Favorites', 'artists_writer': 'Artists/Writers', 'disney_pixar': 'Disney & Pixar',
    'dreamworks_illumination': 'DreamWorks & Illumination', 'netflix_prime': 'Netflix & Prime'
}

def gid(n):
    n = n.strip().lower().replace('&', 'and')
    n = re.sub(r'[^a-z0-9]', '_', n)
    return re.sub(r'_+', '_', n).strip('_')

USED_IDS = set()

def get_unique_id(name):
    base_id = gid(name)
    cid = base_id
    counter = 1
    while cid in USED_IDS:
        cid = f"{base_id}_{counter}"
        counter += 1
    USED_IDS.add(cid)
    return cid, base_id

def clean(w):
    w = re.sub(r'\[.*?\]', '', w)
    return w.strip()

def split_words(line):
    def repl(m): return m.group(0).replace(',', '§')
    line = re.sub(r'\[.*?\]', repl, line)
    words = [w.strip() for w in line.split(',') if w.strip()]
    return [clean(w.replace('§', ',')) for w in words if clean(w)]

def parse(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().replace("Sci-Fi/ Fantasy", "Sci-Fi/Fantasy")
    parts = re.split(r'^(.*?) \(CATEGORY\):', content, flags=re.MULTILINE)
    res = []
    USED_IDS.clear()
    for i in range(1, len(parts), 2):
        name, body = parts[i].strip(), parts[i+1].strip()
        cid, base_id = get_unique_id(name)
        obj = {"name": NAME_FIXES.get(base_id, name), "id": cid}
        if base_id in ICON_MAP: obj["icon"] = ICON_MAP[base_id]
        lines = [l.strip() for l in body.split('\n') if l.strip()]
        subs, cur = [], None
        for l in lines:
            if ':' in l and ',' in l and ',' not in l.split(':', 1)[0]:
                if cur: subs.append(cur)
                cur = None
                p = l.split(':', 1)
                sid, s_base_id = get_unique_id(p[0])
                words = split_words(p[1])
                s_obj = {"name": NAME_FIXES.get(s_base_id, p[0].strip()), "id": sid, "words": words}
                if s_base_id in ICON_MAP: s_obj["icon"] = ICON_MAP[s_base_id]
                subs.append(s_obj)
            elif ',' not in l:
                if cur: subs.append(cur)
                sn = l.replace(':', '').strip()
                sid, s_base_id = get_unique_id(sn)
                cur = {"name": NAME_FIXES.get(s_base_id, sn), "id": sid, "words": []}
                if s_base_id in ICON_MAP: cur["icon"] = ICON_MAP[s_base_id]
            else:
                words = split_words(l)
                if cur: cur["words"].extend(words)
                elif not subs: obj.setdefault("words", []).extend(words)
                else: subs[-1]["words"].extend(words)
        if cur: subs.append(cur)
        if subs: obj["categories"] = subs
        res.append(obj)
    return res

if __name__ == "__main__":
    d = os.path.dirname(__file__)
    res = parse(os.path.join(d, 'impasta', 'lol.txt'))
    with open(os.path.join(d, 'impasta', 'data.json'), 'w', encoding='utf-8') as f:
        json.dump({"categories": res}, f, indent=2, ensure_ascii=False)
    print("Updated")
