import os
import shutil

# Target list found directly from your log results
TARGET_NAMES = [
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

# Ensure asset container exists
os.makedirs('Assets.xcassets', exist_ok=True)

print("--- INJECTING TARGETED GRAPHICS ---")

for name in TARGET_NAMES:
    imageset_dir = f'Assets.xcassets/{name}.imageset'
    os.makedirs(imageset_dir, exist_ok=True)
    
    # Generate required asset configuration file
    contents = {
      'images': [{'idiom': 'universal', 'filename': f'{name}.png'}],
      'info': {'version': 1, 'author': 'xcode'}
    }
    with open(f'{imageset_dir}/Contents.json', 'w') as jf:
        import json
        json.dump(contents, jf)
    
    # Inject your new watermark image into the target slot
    if os.path.exists('watermark.png'):
        print(f"Successfully modified -> {name}")
        shutil.copy('watermark.png', f'{imageset_dir}/{name}.png')
    else:
        # Fallback empty image byte string just in case
        with open(f'{imageset_dir}/{name}.png', 'wb') as f_dummy:
            f_dummy.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x01\x00\x00\x0c\x00\x01\x04\x1e\xe3\xa8\x00\x00\x00\x00IEND\xaeB`\x82')
