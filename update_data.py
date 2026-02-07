import json, re, os

ICON_MAP = {
    'video_games': 'Gamepad2', 'movies': 'Clapperboard', 'tv_shows': 'Tv', 'memes': 'Laugh', 'people': 'Users',
    'mario_universe': 'Star', 'super_smash_bros': 'Gamepad', 'pokemon': 'CircleDot', 'pokmon': 'CircleDot',
    'zelda': 'Sword', 'shooter': 'Crosshair', 'fortnite': 'Target', 'minecraft': 'Box', 'indie_horror': 'Sprout',
    'brawl_stars': 'Swords', 'clash_royal': 'Crown', 'mobile_arcade': 'Smartphone', 'roblox': 'Bot', 'vr': 'Glasses',
    'playstation_games': 'Gamepad2', 'generational': 'Clock', 'characters': 'Users', 'brainrot': 'Zap',
    'comedy': 'Popcorn', 'cinephile_favs': 'Award', 'marveldc': 'ShieldAlert', 'scifi_fantasy': 'Rocket',
    'horror': 'Skull', 'animated': 'Pencil', 'game_adaptations': 'Gamepad', 'book_adaptations': 'BookOpen',
    'action_thriller': 'Target', 'drama': 'Award', 'crime_mystery': 'Fingerprint', 'animation': 'Pencil',
    'anime': 'Sparkles', 'teen_girls': 'Heart', 'kids': 'Baby', 'reality_documentary': 'Video',
    'social_media': 'Smartphone', 'musicians': 'Music', 'actors_directors': 'Camera', 'athletes': 'Trophy',
    'politicians': 'Flag', 'historical_figures': 'Scroll', 'tech_icons': 'Cpu', 'artists_writer': 'Palette',
}

NAME_FIXES = {
    'video_games': 'Video Games', 'pokmon': 'Pokémon', 'pokemon': 'Pokémon', 'super_smash_bros': 'Super Smash Bros.',
    'indie_horror': 'Indie/Horror', 'clash_royal': 'Clash Royale', 'mobile_arcade': 'Mobile/Arcade',
    'playstation_games': 'PlayStation Games', 'scifi_fantasy': 'Sci-Fi/Fantasy', 'crime_mystery': 'Crime/Mystery',
    'teen_girls': 'Teen Girls', 'reality_documentary': 'Reality/Documentary', 'marveldc': 'Marvel+DC',
    'action_thriller': 'Action/Thriller', 'game_adaptations': 'Game Adaptations', 'book_adaptations': 'Book Adaptations',
    'cinephile_favs': 'Cinephile Favorites',
}

def gid(n):
    n = n.strip().lower().replace('&', 'and').replace('/', '_').replace('-', '_')
    n = re.sub(r'[^a-z0-9\s_]', '', n)
    return re.sub(r'\s+', '_', n)

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
    for i in range(1, len(parts), 2):
        name, body = parts[i].strip(), parts[i+1].strip()
        cid = gid(name)
        obj = {"name": NAME_FIXES.get(cid, name), "id": cid}
        if cid in ICON_MAP: obj["icon"] = ICON_MAP[cid]
        lines = [l.strip() for l in body.split('\n') if l.strip()]
        subs, cur = [], None
        for l in lines:
            if ':' in l and ',' in l and ',' not in l.split(':', 1)[0]:
                if cur: subs.append(cur)
                cur = None
                p = l.split(':', 1)
                sid = gid(p[0])
                words = split_words(p[1])
                s_obj = {"name": NAME_FIXES.get(sid, p[0].strip()), "id": sid, "words": words}
                if sid in ICON_MAP: s_obj["icon"] = ICON_MAP[sid]
                subs.append(s_obj)
            elif ',' not in l:
                if cur: subs.append(cur)
                sn = l.replace(':', '').strip()
                sid = gid(sn)
                cur = {"name": NAME_FIXES.get(sid, sn), "id": sid, "words": []}
                if sid in ICON_MAP: cur["icon"] = ICON_MAP[sid]
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
