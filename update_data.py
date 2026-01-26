import json
import re
import os

def parse_lol_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    categories = []
    
    # Regex to find blocks starting with "Name (CATEGORY):"
    # We find all matches to determine start and end of sections
    category_regex = re.compile(r'^(.*?) \(CATEGORY\):', re.MULTILINE)
    matches = list(category_regex.finditer(content))
    
    for i, match in enumerate(matches):
        cat_name = match.group(1).strip()
        start_idx = match.end()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(content)
        
        section_content = content[start_idx:end_idx].strip()
        
        cat_id = cat_name.lower().replace(" ", "_").replace("/", "_").replace("&", "and")
        cat_obj = {
            "name": cat_name,
            "id": cat_id
        }
        
        lines = [l.strip() for l in section_content.split('\n') if l.strip()]
        
        if not lines:
            continue

        # Heuristics to determine structure
        
        # Case 1: Video Games style (Line starts with "Subcat: words, words")
        # Check if first few lines generally match "Key: Values"
        is_key_value_lines = False
        colon_count = sum(1 for line in lines if ':' in line)
        if colon_count > len(lines) * 0.5: # If most lines have colons, likely key-value
             is_key_value_lines = True
        
        # Case 2: TV Shows style (Header:\nWords, Header:\nWords)
        # Check if lines ending in ':' are followed by lines without ':'
        is_header_block = False
        if cat_name == "TV Shows": # Explicit check based on known file content, but can be heuristic
            is_header_block = True
            
        # Case 3: Flat list
        
        if is_key_value_lines and not is_header_block:
             cat_obj["categories"] = []
             for line in lines:
                 if ':' in line:
                     parts = line.split(':', 1)
                     sub_name = parts[0].strip()
                     words_str = parts[1].strip()
                     words = [w.strip() for w in words_str.split(',') if w.strip()]
                     
                     sub_id = sub_name.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
                     cat_obj["categories"].append({
                         "name": sub_name,
                         "id": sub_id,
                         "words": words
                     })
                     
        elif is_header_block:
            cat_obj["categories"] = []
            current_sub_name = None
            
            for line in lines:
                if line.endswith(':'):
                    current_sub_name = line[:-1].strip()
                else:
                    if current_sub_name:
                         words = [w.strip() for w in line.split(',') if w.strip()]
                         sub_id = current_sub_name.lower().replace(" ", "_").replace("/", "_").replace("&", "and")
                         cat_obj["categories"].append({
                             "name": current_sub_name,
                             "id": sub_id,
                             "words": words
                         })
                         current_sub_name = None # consume header
            
        else:
            # Flat list
            # Check if comma separated
            all_text_concat = "".join(lines)
            if ',' in all_text_concat:
                words = []
                for line in lines:
                    words.extend([w.strip() for w in line.split(',') if w.strip()])
                cat_obj["words"] = words
            else:
                # Line separated values (Movies)
                cat_obj["words"] = lines
                
        categories.append(cat_obj)
        
    return categories

def main():
    lol_path = os.path.join(os.getcwd(), 'impasta', 'lol.txt')
    json_path = os.path.join(os.getcwd(), 'impasta', 'data.json')
    
    new_categories = parse_lol_txt(lol_path)
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"categories": []}
        
    if "categories" not in data:
        data["categories"] = []
        
    # Append new categories
    data["categories"].extend(new_categories)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    print("Successfully updated data.json")

if __name__ == "__main__":
    main()
