import logging
from multiprocessing import Queue, Value, Array
from ctypes import c_bool, c_char
from blinker import signal
from xy_health_measurement_sdk_configuration.protos.Category_pb2 import All
from xy_health_measurement_sdk_configuration.protos.Validation_pb2 import StartClosedMeasurement, StartRepeatedly
from .MeasurerProcess import MeasurerProcess
from .utilities.SignalProcessor import SignalProcessor as sp
from .utilities.FeatureExtractor import FeatureExtractor as Extractor
from .utilities.Utility import Utility as util


class Measurement(object):
    def __init__(self, app_id, sdk_key, *args, **kwargs):
        """
        kwargs: 可定义参数如下
            {
                'logging_config':{
                    'level': logging.DEBUG,
                    'format': '%(asctime)s - %(levelname)s - %(filename)s[line:%(lineno)d]: %(message)s',
                    'filename': 'log.txt',
                    'filemode': 'w'
                },
                'auth_url': 'https://measurement-auth.xymind.cn/connect/sdk/token',
                'measurement_url': 'https://measurement-web.xymind.cn/measurement/feature',
                'measurement_duration': 30000,
                'min_chunk_timespan': 6000
            }
        """
        logging_config = kwargs.get('logging_config')
        if logging_config:
            logging.basicConfig(**logging_config)

        self.__frame_order = 0
        self.__start_time = None  # 记录第一帧时间
        self.__collected = False  # 数据采集完毕
        self.__started = False  # 已开始测量
        self.__stopped = False  # 测量已停止
        self.__queue = Queue()
        self.__measuring_flag = Value(c_bool, True)  # 正在测量中[状态]
        self.__process = None

        categories = list(args) if args else [All]

        kwargs.update({
            'app_id': app_id,
            'sdk_key': sdk_key,
            'categories': categories,
            'queue': self.__queue,
            'measurement_id': Array(c_char, b' ' * 36, lock=False),
            'measuring_flag': self.__measuring_flag,
            'fire_event': self.__fire_event,
            'handle_error': self.__handle_error,
            'handle_warning': self.__handle_warning
        })
        self.__kwargs = kwargs

        self.__events = self.__init_events(
            'started', 'collected', 'chunk_report_generated', 'whole_report_generated', 'interrupted', 'state_updated',
            'crashed')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        util.set_shared_value(self.__measuring_flag, False)
        self.__collected = True
        self.__queue.close()
        self.__stopped = True

        if self.__process is not None and self.__process.is_alive():
            self.__process.stop()
            self.__process.join()
            self.__process = None

    @property
    def measurement_id(self):
        return util.get_shared_char_array(self.__kwargs['measurement_id'])

    def start(self, frame):
        kwargs = {'message': f'measurement_id:{self.measurement_id} {{}}'}
        if self.__stopped:
            return self.__handle_error(util.generate_error(StartClosedMeasurement, False, **kwargs))

        if self.__started:
            return self.__handle_error(util.generate_error(StartRepeatedly, False, **kwargs))
        self.__started = True

        self.__kwargs['start_frame'] = frame
        self.__process = MeasurerProcess(**self.__kwargs)
        if self.__stopped:
            return
        self.__process.start()


    def enqueue(self, frame, timestamp):
        """
        入队视频帧
        """
        if self.__collected:
            return

        if self.__queue.empty() and not self.__start_time:
            self.__start_time = timestamp

        self.__frame_order += 1
        timestamp -= self.__start_time
        self.__queue.put({'order': self.__frame_order,
                         'timestamp': int(timestamp), 'frame': frame})
        if util.assure_adequate_frames(timestamp, self.__frame_order, self.__kwargs.get('measurement_duration')):
            self.__collected = True
            self.__queue.close()
            self.__fire_event('collected')

    def join(self):
        if self.__process is not None and self.__process.is_alive():
            self.__process.join()
            
        self.stop()

    def stop(self):
        self.__exit__(None, None, None)

    def interrupt(self):
        """
        中断测量
        """
        self.stop()
        self.__fire_event('interrupted')
        logging.warning(f'measurement_id:{self.measurement_id} interrupted')

    def validate(self, frame):
        """
        校验测量条件
        """
        if self.__started or self.__stopped:
            return
        landmarks, _, width, height = sp.detect(frame)
        *position, errors = sp.validate(True, landmarks, width, height)
        warnings = Extractor().validate(
            True, *((0, landmarks, width, height) + tuple(position)))
        return errors + warnings

    def subscribe(self, event, handler):
        """
        订阅事件
        """
        evt = self.__events.get(event)
        if not evt:
            logging.warning(
                f'measurement_id:{self.measurement_id} there is not event with name {event}')
            return

        evt.connect(handler, self)

    def unsubscribe(self, event, handler):
        """
        取消订阅事件
        """
        evt = self.__events.get(event)
        if not evt:
            logging.warning(
                f'measurement_id:{self.measurement_id} there is not event with name {event}')
            return

        evt.disconnect(handler, self)

    def __fire_event(self, event, **kwargs):
        evt = self.__events.get(event)
        if not evt:
            return

        evt.send(self, **kwargs)

    def __handle_error(self, error, exception_config=None, **kwargs):
        message, exception = kwargs.get('message'), kwargs.get('exception')

        if not exception_config:
            interrupted, exception_config, kwargs = util.validate_error(error)

        self.__fire_event('crashed', **exception_config)

        msg = exception_config['msg']
        msg = message.format(msg) if message else msg
        if exception:
            self.stop()
            return logging.critical(f"{msg} {kwargs.get('exception')}", exc_info=True, stack_info=True)
        match exception_config['level']:
            case 'error':
                self.stop()
                logging.error(msg)
            case 'warning':
                logging.warning(msg)
            case _:
                pass
        return exception_config['code']

    def __handle_warning(self, warnings):
        if warnings is None or len(warnings) <= 0:
            return

        states = []
        for warning in warnings:
            _, exception_config, _ = util.validate_error(warning)
            states.append(exception_config)
            level, msg = exception_config['level'], exception_config['msg']

            if level == 'warning':
                logging.warning(msg)
            if level == 'error':
                logging.error(msg)

        self.__fire_event('state_updated', states=states)

    @staticmethod
    def __init_events(*args):
        events = {}
        for evt in args:
            events[evt] = signal(evt)
        return events
