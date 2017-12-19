import os

from use_ssd import UseSSD

useSSD = UseSSD()

img_dirname = 'files'

for filename in os.listdir(img_dirname):
    if not filename.lower().endswith(('.jpg', '.jpeg')):
        continue

    useSSD.process_img(img_dirname + '/' + filename, 0.5, 'processed_imgs')

