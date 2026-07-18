import os
import zipfile
import shutil
import json

zip_path = 'all_images.zip'
extract_path = 'unzipped_raw_images'
assets_catalog = 'Assets.xcassets'

os.makedirs(assets_catalog, exist_ok=True)

# 1. Unzip your authentic images on the cloud runner
if os.path.exists(zip_path):
    print("--- UNZIPPING GENUINE APP IMAGES ---")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

# 2. Build the proper directory structure that actool expects
if os.path.exists(extract_path):
    print("--- MAPPING IMAGES INTO COMPILER CATALOG ---")
    for filename in os.listdir(extract_path):
        if filename.lower().endswith('.png'):
            # Parse baseline string name
            base_name = os.path.splitext(filename)[0]
            clean_name = base_name.split('_Normal')[0].split('@')[0]
            
            imageset_dir = f'{assets_catalog}/{clean_name}.imageset'
            os.makedirs(imageset_dir, exist_ok=True)
            
            # Detect resolution scale properties
            scale = '1x'
            if '@2x' in base_name: scale = '2x'
            elif '@3x' in base_name: scale = '3x'
            
            contents_path = f'{imageset_dir}/Contents.json'
            if os.path.exists(contents_path):
                with open(contents_path, 'r') as jf:
                    contents = json.load(jf)
            else:
                contents = {'images': [], 'info': {'version': 1, 'author': 'xcode'}}
                
            contents['images'].append({'idiom': 'universal', 'scale': scale, 'filename': filename})
            
            with open(contents_path, 'w') as jf:
                json.dump(contents, jf)
                
            shutil.copy(os.path.join(extract_path, filename), os.path.join(imageset_dir, filename))
            
    print("Catalog structure built successfully!")
else:
    print("Error: Zip file processing failed.")
