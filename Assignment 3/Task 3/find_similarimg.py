import os
from PIL import Image, ImageDraw, UnidentifiedImageError
import torchvision.models as models
import torchvision.transforms as transforms
import torch.nn as nn

from annoy import AnnoyIndex

images_folder=r'C:\Users\KARTIKEY\my first repo\GanForge\PetImages\Dog'
images=os.listdir(images_folder)

weights=models.ResNet18_Weights.IMAGENET1K_V1
model= models.resnet18(weights=weights)
model.fc=nn.Identity()

model.eval()
transform=transforms.Compose([transforms.Resize((224,224)),transforms.ToTensor()])

annoy_index=AnnoyIndex(512,'angular')
annoy_index.load('dog_index.ann')

image_grid=Image.new('RGB',(1000,1000))

for i in range(len(images)):
    image_path= os.path.join(images_folder, images[i])
    try:
        image=Image.open(image_path)
    except UnidentifiedImageError:
        print(f"\nWarning: Skipping '{images[i]}' - UnidentifiedImageError (likely corrupted or invalid image file).")
    except Exception as e:
        # Catch any other potential errors during image opening
        print(f"\nWarning: Skipping '{images[i]}' - Error opening image: {e}")
        continue
        
    input_tensor= transform(image).unsqueeze(0)

    if input_tensor.shape[1]==3:
      output_tensor = model(input_tensor)

      nns= annoy_index.get_nns_by_vector(output_tensor[0], 24)

      image=image.resize((200,200))
      image_draw=ImageDraw.Draw(image)
      image_draw.rectangle([(0,0), (200,200)], outline='red', width=8)
      image_grid.paste(image, ((0,0,)))

      for j in range(24):
        search_img=Image.open(os.path.join(images_folder, images[nns[j]]))
        search_img= search_img.resize((200,200))
        image_grid.paste(search_img, (200 * ((j+1)%5),200 *((j+1)//5)))
      image_grid.save(f'ImageDump/image_{i}.png')
