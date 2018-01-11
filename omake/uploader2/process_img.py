import os

from use_ssd import UseSSD

useSSD = UseSSD()

img_dirname = 'files'

for filename in os.listdir(img_dirname):
    if not filename.lower().endswith(('.jpg', '.jpeg')):
        continue

    result = useSSD.has_category(img_dirname + '/' + filename, 'Cat', 0.5)
    print('%s: %s' % (filename, result))

