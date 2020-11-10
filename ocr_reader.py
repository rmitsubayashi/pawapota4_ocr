from os import path
import base64
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import pytesseract
from PIL import Image

class OCRReader:
    def __init__(self):
        self._load_dims('data/dims.txt')

    def _load_dims(self, file_name):
        file = open(file_name, 'r')
        lines = file.readlines()
        self.dims = {}
        for line in lines:
            if line[0] == '#':
                continue
            split = line.split(',')
            assert len(split) == 5
            name = split[0]
            num_arr = []
            for i in split[1:]:
                num_arr.append(float(i))
            self.dims[name] = num_arr

    def set_image(self, image_path):
        self.image = cv.imread(image_path)

    def is_in_frame(self):
        top_left = self.match('img/left.png', 0.1)
        bottom_right = self.match('img/bottom_right_corner.png', 0.1)
        return top_left is not None and bottom_right is not None

    def set_reference_point(self):
        left = self.match('img/left.png', 0.1)
        self.reference_point = self._get_best_match_loc(left)
        # template = cv.imread('img/left.png')
        # _, w, h = template.shape[::-1]
        # print(w)
        # print(h)

        # ran the above code once to get w & h
        self.reference_w = 99
        self.reference_h = 39

    # would have liked to use OCR to extract the name, but Tesseract doesn't recognize the characters :(
    def get_player_name(self):
        img = self.read_dims('name')
        return self._image_to_base64(img)

    def is_pitcher_stats(self):
        match = self.match('img/pitcher_identifier.png', 0.02)
        return match is not None

    def _is_whitish(self, color):
        threshold = 200
        return color[0] > threshold and color[1] > threshold and color[2] > threshold


    def detect_num(self, dim):
        img = self.read_dims(dim)
        matches =[]
        digits = ['zero','one','two','three','four','five','six','seven','eight','nine']
        threshold = 0.07
        for i in range(10):
            match = self.match('img/digit_'+digits[i]+'.png', threshold, img)
            if match is not None:
                locs = self._get_best_match_locs(match, threshold)
                for loc in locs:
                    matches.append((loc[0], i))
        sorted_matches = sorted(matches, key=lambda x: x[0])
        result = 0
        for i in range(len(sorted_matches)):
            result += 10 ** (len(sorted_matches)-1-i) * sorted_matches[i][1]
        return result

    def match(self, template_path, threshold, image=None):
        if image is None:
            image = self.image
        image = image.copy()
        if not path.exists(template_path):
            print('file ' + template_path + ' does not exist')
            return
        template_img = cv.imread(template_path)
        result = cv.matchTemplate(image, template_img, cv.TM_SQDIFF_NORMED)
        flag = False
        min = np.amin(result)
        if min < threshold:
            flag = True

        # debugging code
        # print(template_path + ": " + str(min))
        # _, _, min_loc, _ = cv.minMaxLoc(result)
        # top_left = min_loc
        # _, w,h = template_img.shape[::-1]
        # bottom_right = (top_left[0] + w, top_left[1] + h)
        # cv.rectangle(self.image, top_left, bottom_right, 255, 2)
        # rect = self.image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        # plt.subplot(121),plt.imshow(rect)
        # plt.title('Match'),
        # plt.subplot(122),plt.imshow(self.image)
        # plt.title('Location'), plt.xticks([]), plt.yticks([])
        # plt.show()

        if (flag):
            return result
        else :
            return None
    
    def _get_best_match_loc(self, match):
        # change min to max if the matching method changes
        _, _, min_loc, _ = cv.minMaxLoc(match)
        return min_loc

    # assumes there will be no vertical matches
    # 0  0
    # 
    # X  <- will not be unique
    def _get_best_match_locs(self, match, threshold):
        all_matches = np.where(match <= threshold)
        all_locs = zip(*all_matches[::-1])
        duplicates = []
        new = []
        for loc in all_locs:
            is_duplicate = False
            for d in duplicates:
                if abs(loc[0]-d) < 5:
                    is_duplicate = True
                    break
            if not is_duplicate:
                new.append(loc)
                duplicates.append(loc[0])
        return new
            
        
    
    def read_dims(self, dim_name):
        dims = self.dims[dim_name]
        top_left = (self.reference_point[0] + int(self.reference_w * dims[0]), self.reference_point[1] + int(self.reference_h * dims[1]))
        bottom_right = (top_left[0] + int(self.reference_w * dims[2]), top_left[1] + int(self.reference_h * dims[3]))

        # debugging code
        # rect = self.image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        # cv.rectangle(self.image, top_left, bottom_right, 255, 2)
        # plt.subplot(121),plt.imshow(rect)
        # plt.title('Match'),
        # plt.subplot(122),plt.imshow(self.image)
        # plt.title('Location'), plt.xticks([]), plt.yticks([])
        # plt.show()

        return self.image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

    def _image_to_base64(self, img):
        _, img_arr = cv.imencode('.jpg', img)
        img_bytes = img_arr.tobytes()
        img_b64 = base64.b64encode(img_bytes)
        return img_b64.decode('ASCII')

