from pathlib import Path
from matplotlib.image import imread, imsave
from PIL import Image

def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray

class Img:
    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        self.path = path
        self.data = rgb2gray(imread(path)).tolist()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def segment(self, threshold=100):
        # Open the image
        with open(self.path, 'rb') as f:
            image = Image.open(f)
            image_width, image_height = image.size

            # Create a new image for segmented pixels
            segmented_image = Image.new('L', (image_width, image_height))

            # Load pixel data
            pixels = image.load()
            segmented_pixels = segmented_image.load()


            # Segment the image based on threshold
            for y in range(image_height):
                for x in range(image_width):
                    pixel_value = pixels[x, y][0]
                    segmented_pixels[x, y] = 255 if pixel_value > threshold else 0



            # Display the segmented image
            segmented_image.show()

# Example usage
if __name__ == "__main__":
    image_path = '/home/asyas/PycharmProjects/ImageProcessingService/bb.jpg'
    img_instance = Img(image_path)
    img_instance.segment()
    img_instance.save_img()
