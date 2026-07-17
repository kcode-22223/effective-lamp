import os
import shutil
import json

# The complete list of names discovered inside your specific file
ALL_DISCOVERED_NAMES = [
    'watermark', 
    'watermark-empty', 
    'watermark-live4-restream', 
    'restream-live4-logo',
    'restream-round-logo',
    'logo', 
    'logo-red-black',
    'gopro_logo',
    'session_logo',
    'hero3_logo',
    'hero5_logo',
    'live4_logo64',
    'vg_logo',
    'vg-logo-small',
    'hplus_logo'
]

os.makedirs('Assets.xcassets', exist_ok=True)

print("--- REPLACING SINGULAR WATERMARK ASSET ---")

for name in ALL_DISCOVERED_NAMES:
    imageset_dir = f'Assets.xcassets/{name}.imageset'
    os.makedirs(imageset_dir, exist_ok=True)
    
    # Generate required asset configuration file
    contents = {
      'images': [{'idiom': 'universal', 'filename': f'{name}.png'}],
      'info': {'version': 1, 'author': 'xcode'}
    }
    with open(f'{imageset_dir}/Contents.json', 'w') as jf:
        json.dump(contents, jf)
    
    # ONLY replace the precise "watermark" image slot
    if name == 'watermark':
        if os.path.exists('watermark.png'):
            print("Target found: Injecting custom image into 'watermark'...")
            shutil.copy('watermark.png', f'{imageset_dir}/{name}.png')
        else:
            print("Error: watermark.png missing from repository root!")
    else:
        # Keeps a safe placeholder for other entries so the compiler generates a valid file
        with open(f'{imageset_dir}/{name}.png', 'wb') as f_dummy:
            f_dummy.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x01\x00\x00\x0c\x00\x01\x04\x1e\xe3\xa8\x00\x00\x00\x00IEND\xaeB`\x82')
