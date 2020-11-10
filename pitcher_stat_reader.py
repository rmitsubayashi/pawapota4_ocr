from ocr_reader import OCRReader

class PitcherStatReader:
    def __init__(self, ocr_reader: OCRReader):
        self.ocr_reader = ocr_reader
        self._load_pitches('data/pitches.txt')
        self._load_pitcher_abilities('data/ability_pitcher.txt')

    def _load_pitches(self, file_name):
        file = open(file_name, 'r')
        lines = file.readlines()
        self.pitches = {}
        for line in lines:
            if line[0] == '#':
                continue
            split = line.split(':')
            assert len(split) == 2
            split2 = split[1].split(',')
            split2[-1] = split2[-1].rstrip('\n')
            self.pitches[split[0]] = split2

    def _load_pitcher_abilities(self, file_name):
        file = open(file_name, 'r')
        lines = file.readlines()
        self.pitcher_abilities = []
        for line in lines:
            if line[0] == '#':
                continue
            self.pitcher_abilities.append(line.rstrip('\n'))

    def get_max_velocity(self):
        return self.ocr_reader.detect_num('max_velocity')

    def get_stamina(self):
        return self.ocr_reader.detect_num('stamina')
    
    def get_control(self):
        return self.ocr_reader.detect_num('control')

    def get_pitcher_abilities(self):
        abilities = []
        for ability in self.pitcher_abilities:
            match = self.ocr_reader.match('img/pitcher_ability/ability_p_' + ability + '.png', 0.01)
            if match is not None:
                abilities.append(ability)
        return abilities

    # cannot read two same direction pitches :(
    def get_pitches(self):
        # pitches display is backwards for lefties
        rightie = None
        left_arm = self.ocr_reader.match('img/arm_left.png', 0.01)
        right_arm = self.ocr_reader.match('img/arm_right.png', 0.01)
        if left_arm is not None:
            rightie = False
        elif right_arm is not None:
            rightie = True
        if rightie is None:
            print("could not match pitcher hand")
            return None
        pitches_image = self.ocr_reader.read_dims('pitches')
        straight_name = self._get_straights(pitches_image)
        fork_name, fork_level = self._get_fork(pitches_image)
        curve_name, curve_level = self._get_curve(pitches_image, rightie)
        sinker_name, sinker_level = self._get_sinker(pitches_image, rightie)
        slider_name, slider_level = self._get_slider(pitches_image, rightie)
        shoot_name, shoot_level = self._get_shoot(pitches_image, rightie)
        pitches ={}
        if straight_name is not None:
            pitches[straight_name] = 1
        if fork_name is not None:
            pitches[fork_name] = fork_level
        if slider_name is not None:
           pitches[slider_name] = slider_level
        if curve_name is not None:
            pitches[curve_name] = curve_level
        if shoot_name is not None:
            pitches[shoot_name] = shoot_level
        if sinker_name is not None:
            pitches[sinker_name] = sinker_level

        # original pitches. technically we should identify all types,
        # but pennant mode only has fork based original pitches
        original_pitch_name = self.pitches['original'][0]
        original_pitch = self.ocr_reader.match('img/pitch/pitch_' + original_pitch_name + '.png', 0.05, pitches_image)
        if original_pitch is not None:
            original_level = self._get_fork_level()
            pitches[original_pitch_name] = original_level

        return pitches
        

    
    def _get_straights(self, pitch_image):
        straights = self.pitches['straight']
        for straight_type in straights:
            match = self.ocr_reader.match('img/pitch/pitch_' + straight_type + '.png', 0.05, pitch_image)
            if match is not None:
                return straight_type
        return None

    def _get_fork(self, pitch_image):
        forks = self.pitches['fork']
        fork_match = None
        fork_level = None
        for fork_type in forks:
            match = self.ocr_reader.match('img/pitch/pitch_' + fork_type + '.png', 0.05, pitch_image)
            if match is not None:
                fork_match = fork_type
                break
        if fork_match is not None:
            fork_level = self._get_fork_level()
        return fork_match, fork_level

    def _get_curve(self, pitch_image, rightie):
        curves = self.pitches['curve']
        curve_match = None
        curve_level = None
        for curve_type in curves:
            match = self.ocr_reader.match('img/pitch/pitch_' + curve_type + '.png', 0.01, pitch_image)
            if match is not None:
                curve_match = curve_type
                break
        if curve_match is not None:
            if rightie:
                curve_level = self._get_curve_level()
            else:
                curve_level = self._get_sinker_level()
        return curve_match, curve_level

    def _get_sinker(self, pitch_image, rightie):
        sinkers = self.pitches['sinker']
        sinker_match = None
        sinker_level = None
        for sinker_type in sinkers:
            match = self.ocr_reader.match('img/pitch/pitch_' + sinker_type + '.png', 0.01, pitch_image)
            if match is not None:
                sinker_match = sinker_type
                break
        if sinker_match is not None:
            if rightie:
                sinker_level = self._get_sinker_level()
            else:
                sinker_level = self._get_curve_level()
        return sinker_match, sinker_level

    def _get_slider(self, pitch_image, rightie):
        sliders = self.pitches['slider']
        slider_match = None
        slider_level = None
        for slider_type in sliders:
            match = self.ocr_reader.match('img/pitch/pitch_' + slider_type + '.png', 0.01, pitch_image)
            if match is not None:
                slider_match = slider_type
                break
        if slider_match is not None:
            if rightie:
                slider_level = self._get_slider_level()
            else:
                slider_level = self._get_shoot_level()
        return slider_match, slider_level

    def _get_shoot(self, pitch_image, rightie):
        shoots = self.pitches['shoot']
        shoot_match = None
        shoot_level = None
        for shoot_type in shoots:
            match = self.ocr_reader.match('img/pitch/pitch_' + shoot_type + '.png', 0.01, pitch_image)
            if match is not None:
                shoot_match = shoot_type
                break
        if shoot_match is not None:
            if rightie:
                shoot_level = self._get_shoot_level()
            else:
                shoot_level = self._get_slider_level()
        return shoot_match, shoot_level

    def _get_slider_level(self):
        slider_level = None
        slider_dims = self.ocr_reader.dims['slider']
        start_x = self.ocr_reader.reference_point[0] + int(self.ocr_reader.reference_w * slider_dims[0])
        start_y = self.ocr_reader.reference_point[1] + int(self.ocr_reader.reference_h * slider_dims[1])
        end_x = self.ocr_reader.reference_point[0] + int(self.ocr_reader.reference_w * slider_dims[2])
        # end_y = self.ocr_reader.reference_point[1] + int(self.ocr_reader.reference_h * slider_dims[3])

        for i in range(7):
            x = start_x + int((end_x - start_x) * i / 7)
            y = start_y
            color_bgr = self.ocr_reader.image[y][x]
            if self.ocr_reader._is_whitish(color_bgr):
                slider_level = i
                break
            # image_copy = self.ocr_reader.image.copy()
            # bottom_right = (x + 50, y + 50)
            # cv.rectangle(image_copy, (x,y), bottom_right, 255, 2)
            # plt.subplot(122),plt.imshow(image_copy)
            # plt.title('Location'), plt.xticks([]), plt.yticks([])
            # plt.show()
        # did not detect white => max
        if slider_level is None:
            slider_level = 7

        return slider_level

    def _get_shoot_level(self):
        shoot_level = None
        shoot_dims = self.ocr_reader.dims['shoot']
        start_x = self.ocr_reader.reference_point[0] + int(self.ocr_reader.reference_w * shoot_dims[0])
        start_y = self.ocr_reader.reference_point[1] + int(self.ocr_reader.reference_h * shoot_dims[1])
        end_x = self.ocr_reader.reference_point[0] + int(self.ocr_reader.reference_w * shoot_dims[2])
        # end_y = self.ocr_reader.reference_point[1] + int(self.ocr_reader.reference_h * shoot_dims[3])

        for i in range(7):
            x = start_x - int((start_x - end_x) * i / 7)
            y = start_y
            color_bgr = self.ocr_reader.image[y][x]
            if self.ocr_reader._is_whitish(color_bgr):
                shoot_level = i
                break
            # image_copy = self.ocr_reader.image.copy()
            # bottom_right = (x + 50, y + 50)
            # cv.rectangle(image_copy, (x,y), bottom_right, 255, 2)
            # plt.subplot(122),plt.imshow(image_copy)
            # plt.title('Location'), plt.xticks([]), plt.yticks([])
            # plt.show()
        # did not detect white => max
        if shoot_level is None:
            shoot_level = 7

        return shoot_level
    
    def _get_curve_level(self):
        curve_level = None
        curve_dims = self.ocr_reader.dims['curve']
        start_x = self.ocr_reader.reference_point[0] + int(self.ocr_reader.reference_w * curve_dims[0])
        start_y = self.ocr_reader.reference_point[1] + int(self.ocr_reader.reference_h * curve_dims[1])
        end_x = self.ocr_reader.reference_point[0] + int(self.ocr_reader.reference_w * curve_dims[2])
        end_y = self.ocr_reader.reference_point[1] + int(self.ocr_reader.reference_h * curve_dims[3])

        for i in range(7):
            x = start_x + int((end_x - start_x) * i / 7)
            y = start_y + int((end_y - start_y) * i / 7)
            color_bgr = self.ocr_reader.image[y][x]
            if self.ocr_reader._is_whitish(color_bgr):
                curve_level = i
                break
            # image_copy = self.ocr_reader.image.copy()
            # bottom_right = (x + 50, y + 50)
            # cv.rectangle(image_copy, (x,y), bottom_right, 255, 2)
            # plt.subplot(122),plt.imshow(image_copy)
            # plt.title('Location'), plt.xticks([]), plt.yticks([])
            # plt.show()
        # did not detect white => max
        if curve_level is None:
            curve_level = 7

        return curve_level
    
    def _get_sinker_level(self):
        sinker_level = None
        sinker_dims = self.ocr_reader.dims['sinker']
        start_x = self.ocr_reader.reference_point[0] + int(self.ocr_reader.reference_w * sinker_dims[0])
        start_y = self.ocr_reader.reference_point[1] + int(self.ocr_reader.reference_h * sinker_dims[1])
        end_x = self.ocr_reader.reference_point[0] + int(self.ocr_reader.reference_w * sinker_dims[2])
        end_y = self.ocr_reader.reference_point[1] + int(self.ocr_reader.reference_h * sinker_dims[3])

        for i in range(7):
            x = start_x - int((start_x - end_x) * i / 7)
            y = start_y + int((end_y - start_y) * i / 7)
            color_bgr = self.ocr_reader.image[y][x]
            if self.ocr_reader._is_whitish(color_bgr):
                sinker_level = i
                break
            # image_copy = self.ocr_reader.image.copy()
            # bottom_right = (x + 50, y + 50)
            # cv.rectangle(image_copy, (x,y), bottom_right, 255, 2)
            # plt.subplot(122),plt.imshow(image_copy)
            # plt.title('Location'), plt.xticks([]), plt.yticks([])
            # plt.show()
        # did not detect white => max
        if sinker_level is None:
            sinker_level = 7

        return sinker_level

    def _get_fork_level(self):
        fork_level = None
        fork_dims = self.ocr_reader.dims['fork']
        start_x = self.ocr_reader.reference_point[0] + int(self.ocr_reader.reference_w * fork_dims[0])
        start_y = self.ocr_reader.reference_point[1] + int(self.ocr_reader.reference_h * fork_dims[1])
        # end_x = self.ocr_reader.reference_point[0] + int(self.ocr_reader.reference_w * fork_dims[2])
        end_y = self.ocr_reader.reference_point[1] + int(self.ocr_reader.reference_h * fork_dims[3])
        for i in range(7):
            x = start_x
            y = start_y + int((end_y - start_y) * i / 7)
            color_bgr = self.ocr_reader.image[y][x]
            if self.ocr_reader._is_whitish(color_bgr):
                fork_level = i
                break
            # image_copy = self.ocr_reader.image.copy()
            # bottom_right = (x + 50, y + 50)
            # cv.rectangle(image_copy, (x,y), bottom_right, 255, 2)
            # plt.subplot(122),plt.imshow(image_copy)
            # plt.title('Location'), plt.xticks([]), plt.yticks([])
            # plt.show()
        # did not detect white => max
        if fork_level is None:
            fork_level = 7

        return fork_level
