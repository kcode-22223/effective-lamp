import os
import shutil
import re

# Create required folder
os.makedirs('Assets.xcassets', exist_ok=True)

found_names = set()

# Scan the raw binary file for text names matching asset patterns
if os.path.exists('Assets.car'):
    with open('Assets.car', 'rb') as f:
        content = f.read()
        # Find readable strings inside the binary data
        words = re.findall(b'[a-zA-Z0-9_.-]{3,100}', content)
        for w in words:
            try:
                name_str = w.decode('utf-8')
                # Look for watermark variations or common UI asset name markers
                if 'watermark' in name_str.lower() or 'logo' in name_str.lower():
                    # Clean up trailing file extensions if present in raw strings
                    clean_name = name_str.split('.')[0].split('@')[0]
                    found_names.add(clean_name)
            except:
                pass

print("--- RAW SCANNED ASSET NAMES ---")
if not found_names:
    print("No matching names found. Forcing fallback target name: 'watermark'")
    found_names.add('watermark')
else:
    for name in found_names:
        print(f"Discovered Target Candidate: {name}")

# Rebuild the asset directories using the scanned string names
for name in found_names:
    imageset_dir = f'Assets.xcassets/{name}.imageset'
    os.makedirs(imageset_dir, exist_ok=True)
    
    contents = {
      'images': [{'idiom': 'universal', 'filename': f'{name}.png'}],
      'info': {'version': 1, 'author': 'xcode'}
    }
    with open(f'{imageset_dir}/Contents.json', 'w') as jf:
        import json
        json.dump(contents, jf)
    
    if os.path.exists('watermark.png'):
        print(f"Injecting replacement image into -> {name}")
        shutil.copy('watermark.png', f'{imageset_dir}/{name}.png')
