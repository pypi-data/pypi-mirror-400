from reader import PhenixReader
from pathlib import Path
from matplotlib import pyplot as plt

reader = PhenixReader('..\\..\\..\\data\\QB-Hacat-EKAR-H2BmCherry-11012024__2024-11-01T16_56_55-Measurement 1')

# md = reader.get_image_metadata(2, 2, 1)

# print(md['URL'])

image = reader.read_image(2, 2, 1)
print(type(image))
print(image.dtype)

# plt.imshow(image)
# plt.show()

# for image in reader.image_iter_time(2, 2):
#     # print(image.tag)

#     plt.imshow(image)
#     plt.show()

