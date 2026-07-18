import os
import zipfile
import shutil
import json

zip_path = 'all_images.zip'
extract_path = 'unzipped_raw_images'
assets_catalog = 'Assets.xcassets'

os.makedirs(assets_catalog, exist_ok=True)

if os.path.exists(zip_path):
    print("--- UNZIPPING APP IMAGES ---")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

if os.path.exists(extract_path):
    print("--- CLEANING AND TRANSLATING TINKERER DATA ---")
    for filename in os.listdir(extract_path):
        if filename.lower().endswith('.png'):
            name_without_ext = os.path.splitext(filename)[0]
            
            # Remove the "_Normal" suffix added by the extraction tool
            clean_name = name_without_ext.replace('_Normal', '')
            
            # Isolate scale properties
            scale = '1x'
            if '@2x' in clean_name:
                scale = '2x'
                clean_name = clean_name.replace('@2x', '')
            elif '@3x' in clean_name:
                scale = '3x'
                clean_name = clean_name.replace('@3x', '')
                
            imageset_dir = f'{assets_catalog}/{clean_name}.imageset'
            os.makedirs(imageset_dir, exist_ok=True)
            
            # Map clean target names
            target_filename = f'{clean_name}.png' if scale == '1x' else f'{clean_name}@{scale}.png'
            
            contents_path = f'{imageset_dir}/Contents.json'
            if os.path.exists(contents_path):
                with open(contents_path, 'r') as jf:
                    contents = json.load(jf)
            else:
                contents = {'images': [], 'info': {'version': 1, 'author': 'xcode'}}
            
            contents['images'].append({
                'idiom': 'universal', 
                'scale': scale, 
                'filename': target_filename
            })
            
            with open(contents_path, 'w') as jf:
                json.dump(contents, jf)
                
            shutil.copy(os.path.join(extract_path, filename), os.path.join(imageset_dir, target_filename))
            
    print("Structural translation completed successfully!")
