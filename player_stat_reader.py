from fielder_stat_reader import FielderStatReader
from pitcher_stat_reader import PitcherStatReader
from ocr_reader import OCRReader
import json

class PlayerStatReader:
    def __init__(self):
        self._ocr_reader = OCRReader()
        self._pitcher_identifier = PitcherStatReader(self._ocr_reader)
        self._fielder_identifier = FielderStatReader(self._ocr_reader)

    def identify(self, img_path):
        self._ocr_reader.set_image(img_path)
        if (not self._ocr_reader.is_in_frame()):
            return

        self._ocr_reader.set_reference_point()
        img_base64 = self._ocr_reader.get_player_name()
        if (self._ocr_reader.is_pitcher_stats()):
            abilities = self._pitcher_identifier.get_pitcher_abilities()
            velocity = self._pitcher_identifier.get_max_velocity()
            control = self._pitcher_identifier.get_control()
            stamina = self._pitcher_identifier.get_stamina()
            pitches = self._pitcher_identifier.get_pitches()
            data = {
                'name_img': img_base64,
                'type': 'pitcher',
                'velocity': velocity,
                'control': control,
                'stamina': stamina,
                'pitches': pitches,
                'abilities': abilities
            }
        else:
            abilities = self._fielder_identifier.get_fielder_abilities()
            trajectory = self._fielder_identifier.get_trajectory()
            contact = self._fielder_identifier.get_contact()
            power = self._fielder_identifier.get_power()
            legs = self._fielder_identifier.get_legs()
            arm_strength = self._fielder_identifier.get_arm_strength()
            fielding = self._fielder_identifier.get_fielding()
            error_resistance = self._fielder_identifier.get_error_resistance()
            data = {
                'name_img': img_base64,
                'type': 'fielder',
                'trajectory': trajectory,
                'contact': contact,
                'power': power,
                'legs': legs,
                'arm_strength': arm_strength,
                'fielding': fielding,
                'error_resistance': error_resistance,
                'abilities': abilities
            }

        print(json.dumps(data))

        return data
