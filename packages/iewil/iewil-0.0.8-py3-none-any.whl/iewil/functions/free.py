from PIL import Image
import io
import base64
from collections import Counter
from typing import Any, Dict, List

class Free:

    @staticmethod
    def __validate( ok: bool, result: Any = None, message: str = "error" ) -> Dict[str, Any]:
        if not ok:
            return {
                "status": False,
                "message": message
            }

        return {
            "status": True,
            "result": result
        }
    
    @staticmethod
    def Icon(base64_string):
        if "," in base64_string:
            base64_string = base64_string.split(",", 1)[1]

        img_data = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_data))
        
        # Handle palette + transparency
        if img.mode in ("P", "PA") and "transparency" in img.info:
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")

        width, height = img.size
        
        # DETEKSI DIVIDER
        white_dot = 0
        
        for y in range(height):
            row_blue_count = 0
            
            # cari pemisah dalam 1 baris
            for x in range(width):
                if img.mode == "RGBA":
                    r, g, b, a = img.getpixel((x, y))
                    # print(b)
                    if b > 76:
                        white_dot += 1
                else:
                    r, g, b = img.getpixel((x, y))
                    # print(b)
                    if b > 1:
                        white_dot += 1
                        
            # cek total divider/pemisah min 4
            if white_dot > 3:
                break
        
        total_gambar = white_dot + 1
        # print(f"Debug: white_dot = {white_dot}, total_gambar = {total_gambar}")
        
        if total_gambar < 3 or total_gambar > 10:
            return Free.__validate(False, message=f"Jumlah gambar tidak masuk akal ({total_gambar})")
        
        part_width = width / total_gambar
        cropped_sizes = []
        
        # Crop dengan margin
        margin_per_side = 1  # 1 pixel kiri + 1 kanan = total -2
        cropped_width = part_width - (margin_per_side * 2)
        
        for i in range(total_gambar):
            left = round(i * part_width + margin_per_side)
            right = round(left + cropped_width)
            
            if right > width:
                right = width
            if left >= right:
                continue
                
            crop = img.crop((left, 0, right, height))
            
            buf = io.BytesIO()
            # print(buf)
            crop.save(buf, format="PNG", optimize=True)
            # filename = f"potongan_{i+1}.png"
            # crop.save(filename, "PNG")
            # print(f"Disimpan: {filename}")
            size = buf.tell()
            cropped_sizes.append(size)
        #print("Hasil cropped_sizes:", cropped_sizes)
        
        # logika count & pilih
        count = Counter(cropped_sizes)
        min_freq = min(count.values())
        least_sizes = [k for k, v in count.items() if v == min_freq]
        selected_size = min(least_sizes)
        
        # Cari index yang punya selected_size
        for i, size in enumerate(cropped_sizes):
            if size == selected_size:
                x = round(i * part_width + part_width / 2)
                y = round(height / 2)
                result = {
                    #    "urutan_gambar": i + 1,
                        "x": x,
                        "y": y,
                    #    "cropped_sizes": cropped_sizes
                    }
                return Free.__validate(True, result= result)
        return Free.__validate(False, message=f"Ngen")