from copy import deepcopy
from importlib.resources import path as resources_path
from json import load
from re import sub
from .protos.Validation_pb2 import Validation, UnknownError

class ConfigUtility(object):
    with resources_path('xy_health_measurement_sdk_configuration.resources', 'config.json') as config:
        with open(config, 'r', encoding='utf-8') as file:
            __config = load(file)
            __validation = __config['validation']

    @classmethod
    def get_validation(cls, code: Validation):
        # validation子节点配置会在业务中根据情况修改作为返回值
        # 深度拷贝可以防止业务修改影响全局默认配置
        return deepcopy(cls.__validation.get(Validation.Name(code)))

    @classmethod
    def get_config(cls, key):
        return cls.__config[key]

    @staticmethod
    def generate_error(code=None, raising=True, **kwargs):
        """
        kwargs:{
            config: {
                'code': 3016,
                'level': 1,
                'msg': 1
            },
            message: '',
            exception: ex
        }
        obj:
        {
            'config': {
                'code': 3016,
                'level': 1,
                'msg': 1
            },
            'addition': {
                'message': f'failed to authenticate app_id:{app_id} sdk_key:{sdk_key} {exception}',
                'exception': exception
            }
        }
        """
        obj = {'config': kwargs.get('config', {})}
        code = code if code is not None else kwargs['config']['code']
        obj['config']['code'] = code

        addition = {}
        message, exception = kwargs.get('message'), kwargs.get('exception')
        if message:
            addition['message'] = message
        if exception:
            addition['exception'] = exception
        if addition:
            obj['addition'] = addition

        error = ValueError(obj)
        if raising:
            raise error
        return error

    @classmethod
    def validate_error(cls, error: Exception):
        """
        验证是否为中断性错误
        """
        kwargs = error.args[0] if isinstance(error, ValueError) else {'config': {'code': UnknownError}}
        exception_config = cls.__get_validation_args(**kwargs['config'])
        return exception_config['level'] == 'error', exception_config, kwargs.get('addition', {})

    @classmethod
    def __get_validation_args(cls, **kwargs):
        code = kwargs['code']
        exception = cls.get_validation(code)['exception']
        kwargs['msg_cn'] = kwargs.get('msg_cn', kwargs.get('msg', 0))

        for key in exception:
            exception[key] = sub(r'\[(.+?),(.+?)\]', lambda mc: mc.group(kwargs.get(key, 0) + 1), exception[key])
        exception['code'] = code
        return exception