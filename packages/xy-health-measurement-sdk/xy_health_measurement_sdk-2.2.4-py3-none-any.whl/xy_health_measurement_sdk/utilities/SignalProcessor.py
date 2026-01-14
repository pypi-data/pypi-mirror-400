import cv2
import mediapipe as mp
from importlib.resources import path as resources_path
from enum import Enum
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import FaceLandmarkerOptions, FaceLandmarker
from xy_health_measurement_sdk_configuration.protos.Validation_pb2 import TooSmallImage, FaceLost, FaceOutOfBoundary
from .Utility import Utility as util


class FacialPosition(Enum):
    """
    人脸位置枚举
    """
    LEFT_FACE = 0
    RIGHT_FACE = 1
    NOSE = 2


class SignalProcessor(object):
    # 初始化mediapipe
    with resources_path('xy_health_measurement_sdk.resources', 'face_landmarker.task') as task:
        __options = FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=task),
                                          output_face_blendshapes=True, num_faces=1)

    @classmethod
    def detect(cls, frame):
        """
        特征提取
        """
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        return cls.__detect_image(mp_image)

    @classmethod
    def detect_file(cls, file):
        mp_image = mp.Image.create_from_file(file)
        return cls.__detect_image(mp_image)

    @classmethod
    def __detect_image(cls, image):
        # 图像特征提取
        with FaceLandmarker.create_from_options(cls.__options) as landmarker:
            detection = landmarker.detect(image)
            return detection.face_landmarks[0] if len(
                detection.face_landmarks) > 0 else None, list(
                map(lambda b: b.score, detection.face_blendshapes[0])) if len(
                detection.face_blendshapes) > 0 else None, image.width, image.height

    @classmethod
    def validate(cls, verify_requirements_only=False, *args):
        """
        数据校验(error)
        """
        landmarks, width, height = args
        errors = []

        # 校验图像尺寸
        image_size_validation = util.get_validation(TooSmallImage)
        if image_size_validation:
            longer_side = width if width > height else height
            shorter_side = width + height - longer_side
            if longer_side < image_size_validation['min_height'] or shorter_side < image_size_validation['min_width']:
                errors.append(util.generate_error(
                    TooSmallImage, not verify_requirements_only))

        # 校验是否存在人脸
        if not landmarks:
            errors.append(util.generate_error(
                FaceLost, not verify_requirements_only))

        # 查找人脸区域坐标，需要特别注意的是，mediapipe提取landmarks中x/y为相对于图像尺寸的比例，x*width、y*height 之后得到的才是绝对坐标
        min_x, min_y, max_x, max_y = width, height, 0, 0
        for landmark in landmarks:
            if landmark.x < min_x:
                min_x = landmark.x
            if landmark.x > max_x:
                max_x = landmark.x
            if landmark.y < min_y:
                min_y = landmark.y
            if landmark.y > max_y:
                max_y = landmark.y

        # 校验人脸边界
        if util.get_validation(FaceOutOfBoundary):
            if len(landmarks) < 478 or min_x < 0 or min_y < 0 or max_x > width or max_y > height:
                errors.append(util.generate_error(
                    FaceOutOfBoundary, not verify_requirements_only))

        return min_x, min_y, max_x, max_y, errors
