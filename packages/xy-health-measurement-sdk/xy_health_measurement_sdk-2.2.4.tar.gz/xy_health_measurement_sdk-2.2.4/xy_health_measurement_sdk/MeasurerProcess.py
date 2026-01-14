import logging
from time import sleep
from multiprocessing import Process, Queue, Value
from xy_health_measurement_sdk_configuration.protos.Validation_pb2 import ReportTimeout, InvalidStartFrame
from .Rpcer import Rpcer
from .utilities.FeatureExtractor import FeatureExtractor
from .utilities.SignalProcessor import SignalProcessor as sp
from .utilities.Utility import Utility as util


class MeasurerProcess(Process):
    def __init__(self, **kwargs):
        super().__init__()
        logging_config = kwargs.get('logging_config')
        if logging_config:
            logging.basicConfig(**logging_config)

        self.__queue: Queue = kwargs['queue']
        self.__start_frame = kwargs['start_frame']
        self.__measuring_flag: Value = kwargs['measuring_flag']
        self.__handle_error = kwargs['handle_error']
        self.__handle_warning = kwargs['handle_warning']
        self.__rpcer = None

        try:
            self.__rpcer = Rpcer(**kwargs)
            self.__extractor = FeatureExtractor(**kwargs)
        except ValueError as error:
            interrupted, config, addition = util.validate_error(error)
            self.stop(interrupted, error, config, **addition)
            if interrupted:
                return
        except Exception as ex:
            self.stop(exception=ex)
            return

    def run(self):
        self.__creat_measurement()
        self.__process_frames()
        self.__wait_report()

    @property
    def measurement_id(self):
        return self.__rpcer.measurement_id

    def __creat_measurement(self):
        """
        创建测量
        """
        image = None
        try:
            success, image = util.convert_frame_to_base64(self.__start_frame)
            if not success:
                util.generate_error(InvalidStartFrame)
            landmarks, _, width, height = sp.detect(self.__start_frame)
            sp.validate(False, landmarks, width, height)
        except ValueError as error:
            interrupted, config, addition = util.validate_error(error)
            self.stop(interrupted, error, config, **addition)
            if interrupted:
                return
        except Exception as ex:
            return self.stop(exception=ex)

        self.__rpcer.start(image.decode('utf-8'))

    def __process_frames(self):
        """
        处理视频帧
        """
        frame_order = 0

        def format_message(suffix):
            return {
                'message': f"measurement_id:{self.measurement_id} frame_order:{frame_order}{' ' + suffix if suffix else suffix} {{}}"}

        try:
            while util.get_shared_value(self.__measuring_flag):
                # 检出视频帧
                if self.__queue.empty() or not self.measurement_id:
                    sleep(0.1)
                    continue

                frame_obj = self.__queue.get()
                frame = frame_obj['frame']
                frame_order = frame_obj['order']
                frame_features = None

                # 校验视频帧
                try:
                    frame_features = landmarks, _, width, height = sp.detect(
                        frame)
                    *position, _ = sp.validate(False, landmarks, width, height)
                    warnings = self.__extractor.validate(False,
                                                         *((frame_order, landmarks, width, height) + tuple(position)))
                    if len(warnings) > 0:
                        self.__handle_warning(warnings)
                except ValueError as error:
                    interrupted, config, addition = util.validate_error(error)
                    self.stop(interrupted, error, config, **
                    addition, **format_message(''))
                    if interrupted:
                        return
                except Exception as ex:
                    return self.stop(exception=ex, **format_message(ex))

                frame_timestamp = frame_obj['timestamp']
                logging.debug(format_message(
                    f'start to process frame {frame_timestamp}')['message'])
                status = self.__extractor.process_frame(
                    frame, frame_timestamp, *frame_features)

                match status:
                    case 0:  # 无chunk
                        continue
                    case 1:  # 阶段性chunk
                        chunk_no, chunk = self.__extractor.chunk
                        self.__rpcer.push_physiology_chunk(
                            util.serialize_message(chunk), callback=self.stop)
                        logging.debug(
                            f'measurement_id:{self.measurement_id} packaged chunk {chunk_no}')
                    case 2:  # 完整chunk
                        self.__rpcer.push_physiology_chunk(
                            util.serialize_message(self.__extractor.physiology_chunk), callback=self.stop)
                        self.__rpcer.push_emotion_chunk(
                            util.serialize_message(self.__extractor.emotion_chunk), callback=self.stop)
                        logging.debug(
                            f'measurement_id:{self.measurement_id} finished packaging all chunks')
                        break
                    case _:
                        return self.stop(**format_message('invalid extraction status'))
        except Exception as ex:
            # 异常中断测量
            self.stop(exception=ex, **format_message(ex.args[0]))

    def __wait_report(self):
        """
        等待健康报告
        """
        waited_time, interval = 0, 0.2
        while util.get_shared_value(self.__measuring_flag):
            sleep(interval)
            waited_time += interval

            timeout = util.get_validation(ReportTimeout)['timeout']
            if waited_time < timeout:
                continue
            return self.stop(
                error=util.generate_error(ReportTimeout, False,
                                          message=f'measurement_id:{self.measurement_id} {{}} {timeout}'))

        # self.__accomplish()

    def stop(self, interrupted=True, error=None, exception_config=None, **kwargs):
        if error is not None or kwargs:
            code = self.__handle_error(error, exception_config, **kwargs)
            if self.__rpcer:
                self.__rpcer.report_error(code)
        if interrupted and self.__rpcer:
            self.__rpcer.stop()