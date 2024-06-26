from pathlib import Path
from matplotlib.image import imread, imsave

def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray

class Img:
    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        self.path = Path(path)
        self.data = rgb2gray(imread(path)).tolist()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def apply_blur(self, blur_level=16):
        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2

        result = []
        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result
        return self.save_img()

    def find_contours(self):
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j - 1] - row[j]))
            self.data[i] = res
        return self.save_img()

    def rotate(self):
        pass

    def add_salt_and_pepper_noise(self):
        pass

    def concatenate(self, other_img, direction='horizontal'):
        pass

    def segment(self, threshold=100):
        segmented_data = []
        for row in self.data:
            segmented_row = []
            for pixel in row:
                segmented_row.append(255 if pixel > threshold else 0)
            segmented_data.append(segmented_row)

        self.data = segmented_data
        return self.save_img()

# Example usage
if __name__ == "__main__":
    image_path = '/home/asyas/PycharmProjects/ImageProcessingService/bb.jpg'
    img_instance = Img(image_path)
    img_instance.segment()
    img_instance.save_img()
