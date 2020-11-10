from ocr_reader import OCRReader

class FielderStatReader:
    def __init__(self, ocr_reader: OCRReader):
        self.ocr_reader = ocr_reader
        self._load_fielder_abilities('data/ability_fielder.txt')

    def _load_fielder_abilities(self, file_name):
        file = open(file_name, 'r')
        lines = file.readlines()
        self.fielder_abilities = []
        for line in lines:
            if line[0] == '#':
                continue
            self.fielder_abilities.append(line.rstrip('\n'))

    def get_trajectory(self):
        return self.ocr_reader.detect_num('trajectory')

    def get_contact(self):
        return self.ocr_reader.detect_num('contact')

    def get_power(self):
        return self.ocr_reader.detect_num('power')
    
    def get_legs(self):
        return self.ocr_reader.detect_num('legs')

    def get_arm_strength(self):
        return self.ocr_reader.detect_num('arm_strength')
    
    def get_fielding(self):
        return self.ocr_reader.detect_num('fielding')

    def get_error_resistance(self):
        return self.ocr_reader.detect_num('error_resistance')

    def get_fielder_abilities(self):
        abilities = []
        for ability in self.fielder_abilities:
            match = self.ocr_reader.match('img/fielder_ability/ability_f_' + ability + '.png', 0.01)
            if match is not None:
                abilities.append(ability)
        return abilities