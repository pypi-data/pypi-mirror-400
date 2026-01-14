from base64 import b64encode
from multiprocessing import Value, Array
from cv2 import imencode
from math import floor
from xy_health_measurement_sdk_configuration.Utility import ConfigUtility


class Utility(ConfigUtility):
    @classmethod
    def assure_adequate_frames(cls, duration, frames_cnt, measurement_duration=None):
        measurement_duration, min_measurement_duration = cls.get_valid_measurement_duration(
            measurement_duration)
        return duration >= measurement_duration and frames_cnt >= floor((cls.get_config(
            'min_frames_cnt')-1) / min_measurement_duration * measurement_duration + 1)

    @classmethod
    def get_valid_measurement_duration(cls, measurement_duration):
        min_measurement_duration = cls.get_config('min_measurement_duration')
        max_measurement_duration = cls.get_config('max_measurement_duration')

        if measurement_duration is None or measurement_duration > max_measurement_duration:
            measurement_duration = max_measurement_duration
        elif measurement_duration < min_measurement_duration:
            measurement_duration = min_measurement_duration

        return measurement_duration, min_measurement_duration

    @staticmethod
    def get_shared_value(shared_value: Value):
        with shared_value.get_lock():
            return shared_value.value

    @staticmethod
    def set_shared_value(shared_value: Value, value):
        with shared_value.get_lock():
            shared_value.value = value

    @staticmethod
    def get_shared_char_array(shared_char_array: Array):
        return shared_char_array[:].decode().strip()

    @staticmethod
    def set_shared_char_array(shared_char_array: Array, value: str):
        length = len(shared_char_array)
        if len(value) > length:
            shared_char_array[:length] = value[:length].encode()
        else:
            shared_char_array[:len(value)] = value.encode()

    @staticmethod
    def serialize_message(message):
        return b64encode(message.SerializeToString()).decode('utf-8')

    @staticmethod
    def convert_frame_to_base64(frame):
        success, encoded_img = imencode('.jpg', frame)
        if not success:
            return False, None
        return success, b64encode(encoded_img.tobytes())
