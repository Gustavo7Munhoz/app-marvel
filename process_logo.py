import os
from PIL import Image, ImageOps

input_path = r"C:\Users\gustavomunhoz-ieg\.gemini\antigravity\brain\6b868cba-daa6-446f-a070-7fc970c0d061\.user_uploaded\media_1790774950672.png"
output_res_dir = r"C:\Users\gustavomunhoz-ieg\AndroidStudioProjects\Marvel\app\src\main\res"

try:
    img = Image.open(input_path).convert("RGBA")
    
    # 1. Base White Logo
    r, g, b, a = img.split()
    rgb_image = Image.merge('RGB', (r,g,b))
    
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] < 100 and item[1] < 100 and item[2] < 100 and item[3] > 0:
            new_data.append((255, 255, 255, item[3]))
        else:
            new_data.append((255, 255, 255, 0))

    app_logo = Image.new("RGBA", img.size)
    app_logo.putdata(new_data)
    
    # 2. Create the App Icon
    icon_size = 1024
    icon_canvas = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
    
    logo_size = 650 # Larger logo since no text
    logo_for_icon = app_logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    
    # Center perfectly
    offset = (icon_size - logo_size) // 2
    icon_canvas.paste(logo_for_icon, (offset, offset), logo_for_icon)
    
    # Save foreground
    icon_canvas.save(os.path.join(output_res_dir, "drawable", "ic_launcher_foreground.png"))
    
    for size, name in [(48, "mdpi"), (72, "hdpi"), (96, "xhdpi"), (144, "xxhdpi"), (192, "xxxhdpi")]:
        folder = os.path.join(output_res_dir, f"mipmap-{name}")
        os.makedirs(folder, exist_ok=True)
        
        legacy_icon = Image.new("RGBA", (size, size), (10, 11, 16, 255))
        scaled_fg = icon_canvas.resize((size, size), Image.Resampling.LANCZOS)
        legacy_icon.paste(scaled_fg, (0, 0), scaled_fg)
        
        legacy_icon.save(os.path.join(folder, "ic_launcher.png"))
        legacy_icon.save(os.path.join(folder, "ic_launcher_round.png"))
        
    print("Success")
except Exception as e:
    print(f"Error: {e}")
