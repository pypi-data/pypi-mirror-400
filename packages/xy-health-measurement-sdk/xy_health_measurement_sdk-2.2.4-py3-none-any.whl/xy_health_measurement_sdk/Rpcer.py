import logging
from requests import post
from base64 import b64decode
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import threading
from google.protobuf.json_format import MessageToDict, MessageToJson
from signalrcore.hub_connection_builder import HubConnectionBuilder
from xy_health_measurement_sdk_configuration.protos.Report_pb2 import HrReport, Report
from xy_health_measurement_sdk_configuration.protos.Validation_pb2 import ServiceCommunicationError, AuthenticationFailure, ServiceError
from .utilities.Utility import Utility as util


class Rpcer(object):
    def __init__(self, **kwargs):
        self.__categories = kwargs['categories']
        self.__fire_event = kwargs['fire_event']
        self.__hub_connection = None

        token = self.__authenticate(kwargs.get('auth_url', util.get_config('auth_url')),
                                    kwargs['app_id'], kwargs['sdk_key'])
        logging_level = kwargs.get(
            'logging_config', {}).get('level', logging.INFO)
        self.__hub_connection = (HubConnectionBuilder().with_url(
            kwargs.get('measurement_url', util.get_config('measurement_url')),
            options={'headers': {'authorization': f'Bearer {token}'}}).configure_logging(
            logging_level).with_automatic_reconnect(
            {'type': 'raw', 'keep_alive_interval': 10, 'reconnect_interval': 5, 'max_attempts': 5}).build())
        self.__hub_connection.on_open(
            lambda: logging.debug('connection opened and handshake received ready to send messages'))
        self.__hub_connection.on_close(lambda: print('connection closed'))
        self.__hub_connection.on_error(lambda data: util.generate_error(
            ServiceCommunicationError, exception=data.error,
            message=f'measurement_id:{self.measurement_id} websocket connection error:{data.error}'))
        self.__hub_connection.on('ReceiveMeasurementId', self.__started)
        self.__hub_connection.on(
            'ReceiveMeasurementHrReport', self.__chunk_report_generated)
        self.__hub_connection.on(
            'ReceiveMeasurementResult', self.__whole_report_generated)
        self.__hub_connection.on('HandleError', self.__handle_server_error)
        self.__measurement_id = kwargs['measurement_id']
        self.__measuring_flag = kwargs['measuring_flag']
        # 添加线程池
        self.__executor = ThreadPoolExecutor(max_workers=2)
        # 添加锁以确保线程安全
        self.__connection_lock = threading.Lock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__hub_connection:
            self.__hub_connection.stop()
        # 关闭线程池
        if hasattr(self, '__executor'):
            self.__executor.shutdown(wait=True)

    def __del__(self):
        if not self.__hub_connection:
            return
        self.__hub_connection.stop()

    @property
    def measurement_id(self):
        return util.get_shared_char_array(self.__measurement_id)

    def start(self, frame):
        try:
            self.__hub_connection.start()
            while not self.__hub_connection.ready:
                sleep(0.1)

            self.__hub_connection.send('CreateMeasurement', [
                                       {'firstFrame': frame, 'categories': self.__categories}])
        except Exception as ex:
            util.generate_error(ServiceCommunicationError, exception=ex,
                                message=f'failed to create measurement firstFrame:{frame},categories:{self.__categories}')

    def stop(self):
        self.__exit__(None, None, None)

    def push_physiology_chunk(self, chunk, callback=None):
        def _send_chunk():
            try:
                # 使用锁保护对hub_connection的访问
                with self.__connection_lock:
                    if self.__hub_connection and self.__hub_connection.ready:
                        self.__hub_connection.send('ProcessPhysiologyChunkResult', [
                                                {'chunkData': chunk}])
                    else:
                        raise Exception("Hub connection is not ready")
            except Exception as ex:
                util.set_shared_value(self.__measuring_flag, False)
                error = util.generate_error(ServiceCommunicationError,raising=False, exception=ex,
                                          message=f'{self.measurement_id} failed to push physiology chunk {chunk}')
                if callback:
                    callback(error=error, exception=ex)
        
        return self.__executor.submit(_send_chunk)

    def push_emotion_chunk(self, chunk, callback=None):
        def _send_chunk():
            try:
                # 使用锁保护对hub_connection的访问
                with self.__connection_lock:
                    if self.__hub_connection and self.__hub_connection.ready:
                        self.__hub_connection.send('ProcessEmotionChunkResult', [
                                                {'chunkData': chunk}])
                    else:
                        raise Exception("Hub connection is not ready")
            except Exception as ex:
                util.set_shared_value(self.__measuring_flag, False)
                error = util.generate_error(ServiceCommunicationError,raising=False, exception=ex,
                                          message=f'{self.measurement_id} failed to push emotion chunk {chunk}')
                if callback:
                    callback(error=error, exception=ex)
        
        return self.__executor.submit(_send_chunk)

    def report_error(self, error_type, description=None):
        # websocket未就绪 记日志但不上报错误
        if not self.__hub_connection.ready:
            logging.debug(
                f'measurement_id:{self.measurement_id} failed to report error while the connection is not ready')
            return

        obj = {'eventType': error_type}
        if description is not None:
            obj['description'] = description

        try:
            # 使用锁保护对hub_connection的访问
            with self.__connection_lock:
                self.__hub_connection.send('CreateEvent', [obj])
        except Exception as ex:
            # 上报错误出错，记日志不再触发异常事件，避免异常循环
            logging.debug(
                f'measurement_id:{self.measurement_id} failed to report error because of a network error {ex}.')

    def __authenticate(self, url, app_id, sdk_key):
        code, message = AuthenticationFailure, f'failed to authenticate app_id:{app_id} sdk_key:{sdk_key} {{}}'
        try:
            response = post(url, data=f'appId={app_id}&sdkKey={sdk_key}',
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})
            response_body = eval(response.text)
            if response.ok:
                return response_body.get('access_token')

            util.generate_error(code, message=message.format(
                f"{response_body.get('error')} {response_body.get('error_description')}"))
        except ValueError as error:
            raise error
        except Exception as ex:
            util.generate_error(code, exception=ex, message=message.format(ex))

    def __started(self, measurement_id):
        util.set_shared_char_array(self.__measurement_id, measurement_id[0])
        self.__fire_event('started', measurement_id=self.measurement_id)
        logging.debug(f'measurement_id:{self.measurement_id} started')

    def __chunk_report_generated(self, report):
        rpt = HrReport()
        rpt.ParseFromString(b64decode(report[0]))
        rpt_obj = MessageToDict(rpt, including_default_value_fields=True)
        self.__fire_event('chunk_report_generated', report=rpt_obj)
        logging.debug(
            f'measurement_id:{self.measurement_id} received chunk report {MessageToJson(rpt, including_default_value_fields=True)}')

    def __whole_report_generated(self, report):
        rpt = Report()
        rpt.ParseFromString(b64decode(report[0]))
        rpt_obj = MessageToDict(rpt, including_default_value_fields=True)
        self.__fire_event('whole_report_generated', report=rpt_obj)
        logging.debug(
            f'measurement_id:{self.measurement_id} received whole report {MessageToJson(rpt, including_default_value_fields=True)}')
        util.set_shared_value(self.__measuring_flag, False)

    def __handle_server_error(self, error):
        util.generate_error(
            ServiceError, message=f'measurement_id:{self.measurement_id} {{}} {error[0].message}')