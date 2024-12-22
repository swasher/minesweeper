from PIL import Image
from pathlib import Path
import shutil

dir = 'asset_tk'
f = '8.png'

p = dir / Path(f)

image = Image.open(p)
new_image = image.resize((20, 20))
new_image.save(p)