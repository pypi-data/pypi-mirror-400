import ctypes
from base64 import b64decode
from importlib.resources import path as resources_path
from xy_health_measurement_sdk_configuration.protos.Chunk_pb2 import PhysiologyChunk, EmotionChunk, Feature
from xy_health_measurement_sdk_configuration.protos.Category_pb2 import Physiology, HeartRate
from xy_health_measurement_sdk_configuration.protos.Validation_pb2 import UnknownError, TooLowFps, InappropriateDistance, YawOutOfRange, PitchOutOfRange, \
    FaceWobble
from .Utility import Utility as util


class FeatureExtractor(object):
    """
    视频帧分析器
    用于分析视频帧得到RGB颜色通过数据，并组装Chunk
    """

    # C++ SDK初始化
    with resources_path('xy_health_measurement_sdk.resources', 'libmeasurement.so') as lib:
        library = ctypes.cdll.LoadLibrary(lib)

        __process_frame = library.processFrame
        __process_frame.argtypes = [
            ctypes.c_char_p,  # image
            ctypes.POINTER(ctypes.c_float),  # faceLandmarks
            ctypes.POINTER(ctypes.c_float),  # faceBlendShapes
            ctypes.c_int,  # featureExtractor
            ctypes.c_char_p,  # frameResult
            ctypes.c_int,  # frameResultSize
        ]
        __process_frame.restype = None

    @classmethod
    def _process_frame(cls, frame, *args):
        landmarks, blend_shapes, width, height = args
        lms = []
        for lm in landmarks:
            lms.append(lm.x * width)
            lms.append(lm.y * height)

        frame_result_size = 800 * 20
        frame_result = None
        try:
            success, image = util.convert_frame_to_base64(frame)
            if not success:
                util.generate_error(
                    UnknownError, message='failed to encode frame to base64')
            lms = (ctypes.c_float * len(lms))(*lms)
            bss = (ctypes.c_float * len(blend_shapes))(*blend_shapes)
            frame_result = ctypes.create_string_buffer(frame_result_size)
            cls.__process_frame(image, lms, bss, 1,
                                frame_result, frame_result_size)
            feature = Feature()
            feature.ParseFromString(b64decode(frame_result.value.decode()))
            return feature
        except Exception as ex:
            util.generate_error(code=UnknownError,
                                message=f'exception occurred during physiology measurement with whole_report : {ex}',
                                exception=ex)
        finally:
            if frame_result is not None:
                ctypes.memset(frame_result, 0, frame_result_size)

    def __init__(self, **kwargs):
        self.__measurement_duration,_ = util.get_valid_measurement_duration(
            kwargs.get('measurement_duration'))

        min_chunk_timespan = util.get_config('min_chunk_timespan')
        custom_chunk_timespan = kwargs.get(
            'min_chunk_timespan', min_chunk_timespan)
        self.__min_chunk_timespan = min_chunk_timespan if custom_chunk_timespan < min_chunk_timespan else (
            self.__measurement_duration if custom_chunk_timespan > self.__measurement_duration else custom_chunk_timespan)

        # 滑动chunk最小帧数（避免帧率过低时每次滑动帧数过少，频繁组装chunk）
        self.__chunk_frame_span = util.get_config('chunk_frame_span')

        self.__min_fps = util.get_validation(TooLowFps)['min_fps']

        self.__time_stamps = []  # 用于chunk滑动窗口
        self.__chunk = None  # 阶段性Chunk
        self.__chunk_no = 0  # 当前测量chunk编号
        self.__physiology_chunk = PhysiologyChunk()
        self.__emotion_chunk = EmotionChunk()
        self.__sliding_window = kwargs.get('sliding_window', [])  # 视频帧校验滑动窗口
        self.__wobbling_cnt = kwargs.get('wobbling_cnt', 0)  # 人脸晃动累计次数
        self.__skewing_cnt = kwargs.get('skewing_cnt', 0)  # 人脸角度偏移累计次数
        self.__warnings = {}  # 告警统计

    @property
    def chunk(self):
        """
        阶段性chunk
        """
        return self.__chunk_no, self.__chunk

    @property
    def physiology_chunk(self):
        """
        完整chunk
        """
        return self.__physiology_chunk

    @property
    def emotion_chunk(self):
        return self.__emotion_chunk

    @property
    def sliding_window(self):
        return self.__sliding_window

    @sliding_window.setter
    def sliding_window(self, value):
        self.__sliding_window = value

    @property
    def wobbling_cnt(self):
        return self.__wobbling_cnt

    @wobbling_cnt.setter
    def wobbling_cnt(self, value):
        self.__wobbling_cnt = value

    @property
    def skewing_cnt(self):
        return self.__skewing_cnt

    @skewing_cnt.setter
    def skewing_cnt(self, value):
        self.__skewing_cnt = value

    def validate(self, verify_requirements_only=False, *args):
        """
        数据校验(warning)
        verify_requirements_only: 仅用于（测量前）测量条件验证
        args: frame_order, landmarks, width, height, min_x, min_y, max_x, max_y
        """

        self.__warnings.clear()
        self.__validate_distance(*args)
        self.__validate_skewing(*args[:4])
        if verify_requirements_only:
            self.__skewing_cnt = 0
        else:
            self.__validate_wobble(*args[4:])

        return list(self.__warnings.values())

    def process_frame(self, frame, timestamp, *args):
        """
        处理视频帧并组装chunk
        :param frame: 原始视频帧
        :param timestamp: 当前视频帧相对时间戳
        :return: chunk状态， 0:未组装, 1:阶段性chunk, 2:最后一个阶段性chunk + 完整chunk（）
        """

        # 记录时间戳
        self.__time_stamps.append(timestamp)

        feature = self._process_frame(frame, *args)
        # 记录视频帧颜色通道数据到physiology_chunk
        self.__physiology_chunk.reds.append(feature.red)
        self.__physiology_chunk.greens.append(feature.green)
        self.__physiology_chunk.blues.append(feature.blue)
        self.__physiology_chunk.timeStamps.append(timestamp)
        self.__emotion_chunk.features.append(feature)

        # 判断测量时长是否超时并满足结束帧数要求
        if util.assure_adequate_frames(timestamp, len(self.__physiology_chunk.timeStamps), self.__measurement_duration):
            # 测量结束 计算完整chunk帧率
            self.__physiology_chunk.fps = len(
                self.__physiology_chunk.timeStamps) / self.__physiology_chunk.timeStamps[-1] * 1000
            self.__physiology_chunk.category = Physiology
            if self.__physiology_chunk.fps < self.__min_fps:
                util.generate_error(TooLowFps)
            return 2

        # 每30帧尝试组装chunk
        if len(self.__time_stamps) % self.__chunk_frame_span != 0:
            return 0

        # 判断滑动窗口
        if self.__time_stamps[-1] - self.__time_stamps[0] < self.__min_chunk_timespan:
            return 0

        # 组装阶段性chunk
        self.__package_chunk()
        return 1

    def __package_chunk(self):
        """
        组装阶段性chunk
        """

        # 滑动窗口
        origin_len = len(self.__time_stamps)
        while self.__time_stamps[-1] - self.__time_stamps[0] > self.__min_chunk_timespan:
            if self.__time_stamps[-1] - self.__time_stamps[1] < self.__min_chunk_timespan:
                break
            self.__time_stamps.pop(0)

        # 查找当前窗口头部索引
        __index = list(self.__physiology_chunk.timeStamps).index(
            self.__time_stamps[0])

        # 组装chunk。从完整chunk中截取当前滑动窗口内容并组装为阶段性chunk
        self.__chunk = PhysiologyChunk()
        self.__chunk.reds.extend(self.__physiology_chunk.reds[__index:])
        self.__chunk.greens.extend(self.__physiology_chunk.greens[__index:])
        self.__chunk.blues.extend(self.__physiology_chunk.blues[__index:])
        self.__chunk.timeStamps.extend(self.__time_stamps)
        self.__chunk.fps = len(
            self.__time_stamps) / (self.__time_stamps[-1] - self.__time_stamps[0]) * 1000
        self.__chunk.category = HeartRate

        # 确保每次chunk组装完毕后窗口滑动步长至少是30帧倍数，即至少每30帧组装一个chunk。
        # 可以有效避免帧率过低时滑动步长太小或帧率过高时滑动步长太大，频繁组装chunk。
        # 如帧率过低只出队1帧即满足滑动窗口要求，本次chunk组装完毕后，仅需入队一帧即可满足30整除且大于滑动窗口长度，进而出现滑动一帧便组装chunk
        # 如帧率过高出队31帧后满足滑动窗口要求，本次chunk组装完毕后，仅需入队一帧即可满足30整除且大于滑动窗口长度，进而出现滑动一帧便组装chunk
        remainder = (origin_len - len(self.__time_stamps)
                     ) % self.__chunk_frame_span
        if remainder > 0:
            self.__time_stamps = self.__time_stamps[self.__chunk_frame_span - remainder:]

        self.__chunk_no += 1

    def __validate_distance(self, *args):
        """
        校验测量距离
        """
        # 校验测量距离（太远或太近）
        distance_config = util.get_validation(InappropriateDistance)
        if not distance_config:
            return

        frame_order, _, _, _, min_x, min_y, max_x, max_y = args

        # 间隔帧数
        if frame_order - 1 % distance_config['interval'] != 0:
            return  # 直接return返回值是None，无法区分暂不校验与校验通过

        # 计算人脸区域面积占比
        face_ratio = (max_x - min_x) * (max_y - min_y)
        config = {'code': InappropriateDistance, 'level': 0, 'msg': 0}
        if face_ratio < distance_config['min_ratio']:
            self.__warnings[InappropriateDistance] = util.generate_error(
                raising=False, config=config)
        if face_ratio > distance_config['max_ratio']:
            config['msg'] = 1
            self.__warnings[InappropriateDistance] = util.generate_error(
                raising=False, config=config)

    def __validate_skewing(self, *args):
        """
        校验人脸角度偏移
        """
        yaw_config, pitch_config = util.get_validation(
            YawOutOfRange), util.get_validation(PitchOutOfRange)
        if not yaw_config and not pitch_config:
            return

        # 容许角度偏移总次数
        max_failed_times = 0
        if yaw_config:
            max_failed_times += yaw_config['max_failed_times']
        if pitch_config:
            max_failed_times += pitch_config['max_failed_times']

        frame_order, landmarks, width, height = args
        # pitch, yaw, _ = get_head_pose_angles(landmarks, width, height) # 计算角度不准确暂停使用
        pitch, yaw = 0, 0

        if frame_order - 1 % yaw_config['interval'] == 0 and yaw_config and abs(yaw) > yaw_config['yaw_angle']:
            self.__skewing_cnt += 1
            interrupting = self.__skewing_cnt >= max_failed_times
            self.__warnings[YawOutOfRange] = util.generate_error(raising=interrupting, config={
                'code': YawOutOfRange,
                'level': 1 if interrupting else 0,
                'msg': 0 if yaw > yaw_config['yaw_angle'] else 1
            })

        if frame_order - 1 % pitch_config['interval'] == 0 and pitch_config and abs(pitch) > pitch_config[
                'pitch_angle']:
            self.__skewing_cnt += 1
            interrupting = self.__skewing_cnt >= max_failed_times
            self.__warnings[PitchOutOfRange] = util.generate_error(raising=interrupting, config={
                'code': PitchOutOfRange,
                'level': 1 if interrupting else 0,
                'msg': 0 if pitch > pitch_config['pitch_angle'] else 1
            })

    def __validate_wobble(self, *args):
        """
        校验人脸晃动
        当前帧与15帧之前对比图像重叠比例，从第16帧开始每帧检测
        """
        wobbling_config = util.get_validation(FaceWobble)
        if not wobbling_config:
            return

        self.__sliding_window.append(args)

        if len(self.__sliding_window) <= wobbling_config['interval']:
            return

        pre_position = self.__sliding_window.pop(0)
        overlap_area_ratio = self.__calculate_overlap_area_ratio(
            pre_position, args)

        if overlap_area_ratio >= wobbling_config['min_overlapping_ratio']:
            return

        self.__wobbling_cnt += 1
        if self.__wobbling_cnt < wobbling_config['max_failed_times']:
            self.__warnings[FaceWobble] = util.generate_error(
                FaceWobble, False)
            return

        util.generate_error(config={'code': FaceWobble, 'level': 1})

    @staticmethod
    def __calculate_overlap_area_ratio(position_a, position_b):
        """
        计算两个矩形的重叠部分面占比。

        参数:
        - Ax1, Ay1: 矩形A的左上角坐标
        - ax2, Ay2: 矩形A的右下角坐标
        - Bx1, By1: 矩形B的左上角坐标
        - Bx2, By2: 矩形B的右下角坐标

        返回:
        - 重叠部分的面积
        """

        (ax1, ay1, ax2, ay2), (bx1, by1, bx2, by2) = position_a, position_b

        # 计算重叠部分的坐标
        overlap_x1 = max(ax1, bx1)
        overlap_y1 = max(ay1, by1)
        overlap_x2 = min(ax2, bx2)
        overlap_y2 = min(ay2, by2)

        # 计算重叠部分的宽度和高度
        overlap_width = overlap_x2 - overlap_x1
        overlap_height = overlap_y2 - overlap_y1

        # 计算重叠部分的面积
        overlap_area = max(0, overlap_width) * max(0, overlap_height)

        # 计算最新矩形的面积
        newest_area = (bx2 - bx1) * (by2 - by1)

        return overlap_area / newest_area
