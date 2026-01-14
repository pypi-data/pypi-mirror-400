from shutil import copy
import os


for i, style_id in enumerate([1, 2, 4, 5, 7, 8, 9]):
    os.makedirs(f"/mnt/nas1/duanzhongjie.dzj/dev6_zimagebase/Z-Image-Omni-Base-i2L/assets/style/{i}", exist_ok=True)
    for file_name in os.listdir(f"data/style/{style_id}"):
        copy(f"data/style/{style_id}/{file_name}", f"/mnt/nas1/duanzhongjie.dzj/dev6_zimagebase/Z-Image-Omni-Base-i2L/assets/style/{i}/{file_name}")
    image_id = 0
    for file_name in sorted(os.listdir(f"data/style_out/1")):
        if file_name.startswith(f"image_lora_{style_id}_"):
            copy(f"data/style_out/1/{file_name}", f"/mnt/nas1/duanzhongjie.dzj/dev6_zimagebase/Z-Image-Omni-Base-i2L/assets/style/{i}/image_{image_id}.jpg")
            image_id += 1
