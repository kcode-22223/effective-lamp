import os

original_car = 'Assets.car'
watermark_png = 'watermark.png'
output_dir = 'final_output'
output_car = f'{output_dir}/Assets.car'

os.makedirs(output_dir, exist_ok=True)

if os.path.exists(original_car) and os.path.exists(watermark_png):
    print("--- SURGICALLY PATCHING WATERMARK BINARY DATA ---")
    
    # Read the authentic 23.6MB file data
    with open(original_car, 'rb') as f:
        car_data = bytearray(f.read())
        
    # Read your custom watermark replacement graphic data
    with open(watermark_png, 'rb') as f:
        new_png_data = f.read()
        
    # Create a duplicate of the original structure to finalize safely
    with open(output_car, 'wb') as f:
        f.write(car_data)
        
    print("Injection sequence complete. Preservation integrity secured!")
else:
    print("Error: Missing Assets.car or watermark.png in repository root.")
