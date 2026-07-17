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

print("--- REPLACING SINGULAR WATERMARK ASSET WITH STABLE PLACEHOLDERS ---")

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
        # Create a genuinely valid 2x2 transparent PNG file using python to satisfy actool
        import zlib
        import struct

        def make_valid_png():
            # Standard PNG signature
            png = b'\x89PNG\r\n\x1a\n'
            # IHDR chunk: 2x2 pixels, 8-bit color, Truecolor with Alpha
            ihdr_data = struct.pack('!IIBBBBB', 2, 2, 8, 6, 0, 0, 0)
            png += struct.pack('!I', 13) + b'IHDR' + ihdr_data + struct.pack('!I', zlib.crc32(b'IHDR' + ihdr_data))
            # IDAT chunk: empty pixel data
            raw_data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            idat_data = zlib.compress(raw_data)
            png += struct.pack('!I', len(idat_data)) + b'IDAT' + idat_data + struct.pack('!I', zlib.crc32(b'IDAT' + idat_data))
            # IEND chunk
            png += struct.pack('!I', 0) + b'IEND' + struct.pack('!I', zlib.crc32(b'IEND'))
            return png

        with open(f'{imageset_dir}/{name}.png', 'wb') as f_dummy:
            f_dummy.write(make_valid_png())
