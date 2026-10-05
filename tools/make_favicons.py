import base64
from PIL import Image

def generate_favicons():
    # 1. Open original primary logo
    orig = Image.open('brand/ivitech-primary.png')
    
    # Bounding box of the V logo without text: [50, 50, 910, 974]
    v_icon = orig.crop((50, 50, 910, 974))
    vw, vh = v_icon.size

    def make_square_favicon(size, fill_ratio=0.86):
        canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        target_h = int(round(size * fill_ratio))
        target_w = int(round(vw * (target_h / vh)))
        scaled_v = v_icon.resize((target_w, target_h), Image.Resampling.LANCZOS)
        offset_x = (size - target_w) // 2
        offset_y = (size - target_h) // 2
        canvas.paste(scaled_v, (offset_x, offset_y), scaled_v)
        return canvas

    # 2. apple-touch-icon.png (180x180)
    apple_icon = make_square_favicon(180, fill_ratio=0.86)
    apple_icon.save('brand/apple-touch-icon.png', 'PNG', optimize=True)
    print('Generated brand/apple-touch-icon.png (180x180)')

    # 3. favicon-32.png (32x32)
    fav_32 = make_square_favicon(32, fill_ratio=0.875)
    fav_32.save('brand/favicon-32.png', 'PNG', optimize=True)
    print('Generated brand/favicon-32.png (32x32)')

    # 4. favicon-16.png (16x16)
    fav_16 = make_square_favicon(16, fill_ratio=0.875)
    fav_16.save('brand/favicon-16.png', 'PNG', optimize=True)
    print('Generated brand/favicon-16.png (16x16)')

    # 5. High-res 512x512 for favicon.svg
    fav_512 = make_square_favicon(512, fill_ratio=0.86)
    fav_512.save('brand/favicon-512.png', 'PNG', optimize=True)

    with open('brand/favicon-512.png', 'rb') as f:
        b64_data = base64.b64encode(f.read()).decode('utf-8')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <image width="512" height="512" href="data:image/png;base64,{b64_data}" />
</svg>
'''
    with open('brand/favicon.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print('Generated brand/favicon.svg (512x512 vector wrapper with embedded high-res lossless PNG)')

if __name__ == '__main__':
    generate_favicons()
