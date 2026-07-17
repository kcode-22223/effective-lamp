import os
import shutil
import json
import re
import struct
import zlib

os.makedirs('Assets.xcassets', exist_ok=True)
all_discovered_names = set()

# 1. Scan the binary of your Assets.car to harvest all 152 true internal asset names
if os.path.exists('Assets.car'):
    with open('Assets.car', 'rb') as f:
        content = f.read()
        words = re.findall(b'[a-zA-Z0-9_.-]{3,100}', content)
        for w in words:
            try:
                name_str = w.decode('utf-8')
                # Filter out standard system words, keeping structural asset names
                if any(x in name_str.lower() for x in ['logo', 'watermark', 'btn', 'icon', 'bg', 'image', 'asset', 'view', 'cell']):
                    clean_name = name_str.split('.')[0].split('@')[0]
                    all_discovered_names.add(clean_name)
            except:
                pass

# Safety fallbacks for the crucial known keys from the log
known_keys = ['watermark', 'watermark-empty', 'watermark-live4-restream', 'restream-live4-logo', 'restream-round-logo', 'logo', 'logo-red-black', 'gopro_logo', 'session_logo', 'hero3_logo', 'hero5_logo', 'live4_logo64', 'vg_logo', 'vg-logo-small', 'hplus_logo']
for key in known_keys:
    all_discovered_names.add(key)

print(f"--- GENERATING STABLE STRUCTURES FOR {len(all_discovered_names)} ASSETS ---")

# Function to construct a structurally perfect 2x2 transparent PNG that passes Apple's validation
def make_valid_png():
    png = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('!IIBBBBB', 2, 2, 8, 6, 0, 0, 0)
    png += struct.pack('!I', 13) + b'IHDR' + ihdr_data + struct.pack('!I', zlib.crc32(b'IHDR' + ihdr_data))
    raw_data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    idat_data = zlib.compress(raw_data)
    png += struct.pack('!I', len(idat_data)) + b'IDAT' + idat_data + struct.pack('!I', zlib.crc32(b'IDAT' + idat_data))
    png += struct.pack('!I', 0) + b'IEND' + struct.pack('!I', zlib.crc32(b'IEND'))
    return png

valid_dummy_png = make_valid_png()

# 2. Build the exact compilation hierarchy 
for name in all_discovered_names:
    imageset_dir = f'Assets.xcassets/{name}.imageset'
    os.makedirs(imageset_dir, exist_ok=True)
    
    contents = {
      'images': [{'idiom': 'universal', 'filename': f'{name}.png'}],
      'info': {'version': 1, 'author': 'xcode'}
    }
    with open(f'{imageset_dir}/Contents.json', 'w') as jf:
        json.dump(contents, jf)
    
    # Check if this asset is the specific target watermark
    if name == 'watermark':
        if os.path.exists('watermark.png'):
            print("Found watermark! Swapping in your custom image...")
            shutil.copy('watermark.png', f'{imageset_dir}/{name}.png')
        else:
            print("Error: watermark.png was not found in the root directory.")
    else:
        # Write the perfectly valid dummy file to satisfy the compiler pipeline
        with open(f'{imageset_dir}/{name}.png', 'wb') as f_dummy:
            f_dummy.write(valid_dummy_png)

print("Mapping sequence complete.")
