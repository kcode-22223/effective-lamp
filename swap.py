import json
import os
import shutil

catalog_path = 'extracted_raw/catalog.json'

if os.path.exists(catalog_path):
    with open(catalog_path) as f:
        data = json.load(f)
        
        print("--- LIST OF ALL DETECTED IMAGES IN APP ---")
        for item in data:
            if 'Name' in item and item.get('RenditionType') == 'Bitmap':
                name = item['Name']
                print(f"Found Asset Name: {name}") # This will print names to your GitHub log
                
                imageset_dir = f'Assets.xcassets/{name}.imageset'
                os.makedirs(imageset_dir, exist_ok=True)
                
                # Generate Apple metadata
                contents = {
                  'images': [{'idiom': 'universal', 'filename': f'{name}.png'}],
                  'info': {'version': 1, 'author': 'xcode'}
                }
                with open(f'{imageset_dir}/Contents.json', 'w') as jf:
                    json.dump(contents, jf)
                
                # Inject watermark or write transparent 1x1 fallback
                # Using .lower() and 'in' to catch variations like "Watermark_Logo" or "watermark@2x"
                if 'watermark' in name.lower() and os.path.exists('watermark.png'):
                    print(f"-> SUCCESS: Matching watermark file found! Injecting into {name}...")
                    shutil.copy('watermark.png', f'{imageset_dir}/{name}.png')
                else:
                    with open(f'{imageset_dir}/{name}.png', 'wb') as f_dummy:
                        f_dummy.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x01\x00\x00\x0c\x00\x01\x04\x1e\xe3\xa8\x00\x00\x00\x00IEND\xaeB`\x82')
