import os
import shutil
import json

extracted_dir = 'extracted_assets'
assets_catalog = 'Assets.xcassets'

os.makedirs(assets_catalog, exist_ok=True)

# Look through the real assets unpacked by acextract
if os.path.exists(extracted_dir):
    print("--- SCANNING GENUINE IMAGES FROM CAR ---")
    for root, dirs, files in os.walk(extracted_dir):
        for filename in files:
            if filename.lower().endswith('.png'):
                # Isolate the clean asset key
                base_name = os.path.splitext(filename)[0]
                clean_name = base_name.split('@')[0]
                
                imageset_dir = f'{assets_catalog}/{clean_name}.imageset'
                os.makedirs(imageset_dir, exist_ok=True)
                
                # IF it matches the watermark target, drop in your custom image
                if clean_name == 'watermark':
                    if os.path.exists('watermark.png'):
                        print(f"Injecting replacement -> {filename}")
                        shutil.copy('watermark.png', f'{imageset_dir}/{filename}')
                else:
                    # Otherwise, copy the original file over completely untouched
                    print(f"Preserving original -> {filename}")
                    shutil.copy(os.path.join(root, filename), f'{imageset_dir}/{filename}')

    # Create the standard Apple configurations required for compilation
    for folder in os.listdir(assets_catalog):
        folder_path = f'{assets_catalog}/{folder}'
        if os.path.isdir(folder_path):
            found_files = [f for f in os.listdir(folder_path) if f != 'Contents.json']
            if found_files:
                images_entry = []
                for f in found_files:
                    scale = '1x'
                    if '@2x' in f: scale = '2x'
                    elif '@3x' in f: scale = '3x'
                    images_entry.append({'idiom': 'universal', 'scale': scale, 'filename': f})
                
                contents = {'images': images_entry, 'info': {'version': 1, 'author': 'xcode'}}
                with open(f'{folder_path}/Contents.json', 'w') as jf:
                    json.dump(contents, jf)
else:
    print("Error: Native extraction directory not found.")
