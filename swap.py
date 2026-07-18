import os
import zipfile
import shutil
import json

zip_path = 'all_images.zip'
extract_path = 'unzipped_raw_images'
assets_catalog = 'Assets.xcassets'

os.makedirs(assets_catalog, exist_ok=True)

if os.path.exists(zip_path):
    print("--- UNZIPPING ASSET TINKERER IMAGES ---")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

if os.path.exists(extract_path):
    print("--- TRANSLATING TINKERER FILE NAMES TO APPLE FORMAT ---")
    for filename in os.listdir(extract_path):
        if filename.lower().endswith('.png'):
            # Strip extension
            name_without_ext = os.path.splitext(filename)[0]
            
            # Remove the "_Normal" suffix added by Asset Catalog Tinkerer extraction
            if '_Normal' in name_without_ext:
                clean_name = name_without_ext.split('_Normal')[0]
                # Re-append the scale identifier if it was attached after the _Normal text
                if '@2x' in name_without_ext:
                    clean_name = clean_name.split('@')[0]
                elif '@3x' in name_without_ext:
                    clean_name = clean_name.split('@')[0]
            else:
                clean_name = name_without_ext.split('@')[0]
            
            # Safeguard system asset folder mapping
            imageset_dir = f'{assets_catalog}/{clean_name}.imageset'
            os.makedirs(imageset_dir, exist_ok=True)
            
            # Detect scale properties
            scale = '1x'
            if '@2x' in name_without_ext: scale = '2x'
            elif '@3x' in name_without_ext: scale = '3x'
            
            contents_path = f'{imageset_dir}/Contents.json'
            if os.path.exists(contents_path):
                with open(contents_path, 'r') as jf:
                    contents = json.load(jf)
            else:
                contents = {'images': [], 'info': {'version': 1, 'author': 'xcode'}}
            
            # Map the clean target name and keep uncompressed pixel structures intact
            target_filename = f'{clean_name}.png' if scale == '1x' else f'{clean_name}@{scale}.png'
            contents['images'].append({
                'idiom': 'universal', 
                'scale': scale, 
                'filename': target_filename
            })
            
            with open(contents_path, 'w') as jf:
                json.dump(contents, jf)
                
            shutil.copy(os.path.join(extract_path, filename), os.path.join(imageset_dir, target_filename))
            
    print("Catalog structure successfully translated and matched!")
