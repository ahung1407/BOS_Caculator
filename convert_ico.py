from PIL import Image, ImageOps

def get_bounding_box(img):
    # Attempt to use alpha channel first
    if img.mode in ('RGBA', 'LA'):
        alpha = img.split()[-1]
        bbox = alpha.getbbox()
        # If the image is not purely a solid rectangle of alpha, return its bbox
        if bbox and (bbox[2] - bbox[0] < img.width or bbox[3] - bbox[1] < img.height):
            return bbox
    
    # If solid background, assume white
    gray = img.convert("L")
    inverted = ImageOps.invert(gray)
    return inverted.getbbox()

img = Image.open("image.png")
img_rgba = img.convert("RGBA")

bbox = get_bounding_box(img_rgba)
if bbox:
    img_rgba = img_rgba.crop(bbox)

width, height = img_rgba.size
# Give a 10% margin
max_dim = int(max(width, height) * 1.15)

# Center the cropped image in a square transparent background
square_img = Image.new("RGBA", (max_dim, max_dim), (255, 255, 255, 0))
x_offset = (max_dim - width) // 2
y_offset = (max_dim - height) // 2
square_img.paste(img_rgba, (x_offset, y_offset))

square_img.save("calculator.ico", format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("Converted and perfectly padded logo_tools1.png to calculator.ico")
