import os
import io
import sys
import threading
import copy
import warnings

from . import cfg_loader
from .hierarchy_match import best_match
from .py_tools import create_instance_from_string
import logging.config

log_root_dir = os.environ.get("APP_LOG_DIR") or os.path.join(os.getcwd(), "logs")
log_global_level = os.environ.get('APP_LOG_LEVEL', 'INFO')
log_global_fmt = os.getenv('APP_LOG_FMT', 'log_fmt_3')
log_global_error_fmt = os.getenv('APP_LOG_ERROR_FMT', 'error_fmt')

root_handlers_type = os.getenv('APP_LOG_TYPE', 'console')
root_handlers = set()
for root_handler_type in root_handlers_type.split(','):
    if root_handler_type == 'file':
        root_handlers.add('log_file')
        root_handlers.add('error_file')
    else:
        root_handlers.add(root_handler_type)
root_handlers = list(root_handlers)
def_cfg = {
    "log_level": log_global_level,
    "log_dir": log_root_dir,
    "log_fmt": log_global_fmt,
    "log_error_fmt": log_global_error_fmt,
    "log_root_handlers": root_handlers
}
ori_stdout = sys.stdout
ori_stdout_imp_str = f"{__name__}.ori_stdout"
ori_stderr = sys.stderr
ori_stderr_imp_str = f"{__name__}.ori_stderr"

ori_logger_getLogger = logging.getLogger

# language=yaml
def_formatters_yaml = """
formatters:
  log_fmt_0:
    format: '%(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'
    
  log_fmt_1:
    format: '[%(asctime)s,%(msecs)03d] - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'
    
  log_fmt_2:
    format: '[%(asctime)s,%(msecs)03d]  [%(levelname)-8s] %(name)s - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'
    
  log_fmt_3:
    format: '[%(asctime)s,%(msecs)03d] [%(levelname)-8s] [%(process)d] [%(threadName)s] %(name)s - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'
    
  log_fmt_4:
    format: "[%(asctime)s,%(msecs)03d] [%(levelname)-8s] [%(process)d] [%(threadName)s] %(name)s - %(module)s.%(funcName)s (%(filename)s:%(lineno)d) - %(message)s"
    datefmt: '%Y-%m-%d %H:%M:%S'

  error_fmt:
    format: "[%(asctime)s,%(msecs)03d] [%(levelname)-8s] [%(process)d] [%(threadName)s] %(name)s - %(module)s.%(funcName)s (%(filename)s:%(lineno)d) - %(message)s"
    datefmt: '%Y-%m-%d %H:%M:%S'
"""
# language=yaml
tpl_filters_yaml = """
filters: {}
"""
# language=yaml
tpl_handlers_yaml = """
handlers:
  # 控制台：输出 >= INFO 的日志
  console:
    class: logging.StreamHandler
    level: ${init_cfg.log_level}
    formatter: ${init_cfg.log_fmt}
    stream: ext://sys.stdout
    # stream: ext://logging_patch.ori_stdout

  # 普通日志文件：INFO 及以上，按天滚动
  log_file:
    class: logging.handlers.TimedRotatingFileHandler
    level: ${init_cfg.log_level}
    formatter: ${init_cfg.log_fmt}
    filename: ${init_cfg.log_dir}/{log_name}.log
    when: midnight        # 每天午夜滚动
    interval: 1
    backupCount: 30       # 保留30天
    encoding: utf-8

  # 错误日志文件：只记录 ERROR 及以上，按天滚动
  error_file:
    class: logging.handlers.TimedRotatingFileHandler
    level: ERROR
    formatter: ${init_cfg.log_fmt}
    filename: ${init_cfg.log_dir}/error.log
    when: midnight
    interval: 1
    backupCount: 30
    encoding: utf-8
  
  file:
    class: logging.handlers.RotatingFileHandler
    level: ${init_cfg.log_level}
    formatter: ${init_cfg.log_fmt}
    filename: ${init_cfg.log_dir}/{log_name.path_1l}.log
    maxBytes: 1_000_000_000  # 1 GB
    backupCount: 5
    encoding: utf-8
    
  file_in_dir:
    class: logging.handlers.RotatingFileHandler
    level: ${init_cfg.log_level}
    formatter: ${init_cfg.log_fmt}
    filename: ${init_cfg.log_dir}/${log_name.path_2l_left}.log
    maxBytes: 1_000_000_000  # 1 GB
    backupCount: 5
    encoding: utf-8
    
  string_kafka:
    class: aabd.base.patched_logging.KafkaStringHandler
    level: ${init_cfg.log_level}
    formatter: ${init_cfg.log_fmt}

"""
# language=yaml
def_cfg_without_formatter_yaml = """
version: 1
disable_existing_loggers: false  # 关键！设为 false 避免第三方库日志被禁用

# =============== 处理器（Handlers） ===============
handlers:
  # 控制台：输出 >= INFO 的日志
  console:
    tpl_name: console

  # 普通日志文件：INFO 及以上，按天滚动
  log_file:
    tpl_name: log_file
    filename: ${init_cfg.log_dir}/info.log

  # 错误日志文件：只记录 ERROR 及以上，按天滚动
  error_file:
    tpl_name: error_file
  

# =============== 日志器（Loggers） ===============
loggers:
  # 主应用 logger
  app:
    level: ${init_cfg.log_level}
    handlers: []
  sys.stdout:
    level: INFO
    handlers: ${init_cfg.log_root_handlers}
    propagate: False
  sys.stderr:
    level: ERROR
    handlers: ${init_cfg.log_root_handlers}
    propagate: False
# =============== 根日志器（Root Logger） ===============
root:
  level: ${init_cfg.log_level}
  handlers: ${init_cfg.log_root_handlers}
"""

# language=yaml
default_tpl_yaml = """
loggers:
  task_tpl:
    pattern: tasks.*
    handlers: 
      log_file:
        tpl_name: file_in_dir
    level: ${init_cfg.log_level}
    propagate: True
"""


class KafkaStringHandler(logging.Handler):
    def __init__(self, servers, topic, username=None, password=None):
        from aabd.mq.kafka_client import KafkaProducer
        super().__init__()
        self.kafka_producer = KafkaProducer(servers, username, password)
        self.topic = topic

    def emit(self, record):
        try:
            # self.format() 会自动处理 exc_info、stack_info 等
            full_message = self.format(record)
            self.kafka_producer.send_message_async(self.topic, full_message)
        except:
            self.handleError(record)


class LoggerWriter:
    def __init__(self, logger_writer):
        self.logger_writer = logger_writer

    def write(self, message):
        if message != '\n':
            self.logger_writer(message)

    def flush(self):
        pass

    def isatty(self):
        pass


logger_templates = None


def _reform_cfg(cfg):
    use_handlers = []
    use_handlers.extend(cfg.get('root', {}).get('handlers', []))
    for _, logger in cfg.get("loggers", {}).items():
        use_handlers.extend(logger.get('handlers', []))

    del_handler_keys = []
    for handler_key, _ in cfg.get('handlers', {}).items():
        del_handler_keys.append(handler_key) if handler_key not in use_handlers else None
    for k in del_handler_keys:
        del cfg['handlers'][k]

    use_filters = []

    for handler_key, handler in cfg.get('handlers', {}).items():
        file_name = handler.get('filename', None)
        if file_name is not None:
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
        use_filters.extend(handler.get('filters', []))
    del_filter_keys = []
    for filter_key, _ in cfg.get('filters', {}).items():
        del_filter_keys.append(filter_key) if filter_key not in use_filters else None
    for k in del_filter_keys:
        del cfg['filters'][k]

    return cfg


def _replace_sys_stream(handlers):
    for handler_key, handler in handlers.items():
        if handler.get('class', None) == 'logging.StreamHandler' and isinstance(handler['stream'], str):
            handler['stream'] = handler['stream'].replace('sys.stdout', ori_stdout_imp_str).replace(
                'sys.stderr', ori_stderr_imp_str)


def _parse_tpl(cfg, tpl, init_cfg):
    tpl_filters = tpl.get("filters")
    update_filters = {}
    for key, filter in cfg.get("filters", {}).items():
        tpl_name = filter.pop('tpl_name', None)
        if tpl_name is None:
            continue
        update_filters[key] = cfg_loader.merge_omega_conf(tpl_filters.get(tpl_name, {}), filter,
                                                          to_container=False)
    for k, h in update_filters.items():
        cfg['filters'][k] = h

    tpl_handlers = tpl.get("handlers")
    update_handlers = {}
    for key, handler in cfg.get("handlers", {}).items():
        tpl_name = handler.pop('tpl_name', None)
        if tpl_name is None:
            continue
        update_handlers[key] = cfg_loader.merge_omega_conf(tpl_handlers.get(tpl_name, {}), handler,
                                                           to_container=False)
    for k, h in update_handlers.items():
        cfg['handlers'][k] = h

    for _, handler in tpl.get("handlers", {}).items():
        update_filters = {}
        for key, filter in handler.get("filters", {}).items():
            tpl_name = filter.pop('tpl_name', None)
            if tpl_name is None:
                continue
            update_filters[key] = cfg_loader.merge_omega_conf(tpl_filters.get(tpl_name, {}), filter,
                                                              to_container=False)
        for k, f in update_filters.items():
            handler['filters'][k] = f

    for _, logger in tpl.get("loggers", {}).items():
        update_handlers = {}
        for key, handler in logger.get("handlers", {}).items():
            tpl_name = handler.pop('tpl_name', None)
            if tpl_name is None:
                continue
            update_handlers[key] = cfg_loader.merge_omega_conf(tpl_handlers.get(tpl_name, {}), handler,
                                                               to_container=False)
        for k, h in update_handlers.items():
            logger['handlers'][k] = h

    cfg_dict = cfg_loader.merge_omega_conf(init_cfg, cfg)
    cfg_dict = _reform_cfg(cfg_dict)
    _replace_sys_stream(cfg_dict['handlers'])

    tpl_omega = cfg_loader.merge_omega_conf(tpl, init_cfg, to_container=False)
    _replace_sys_stream(tpl_omega['handlers'])

    return cfg_dict, tpl_omega


def _log_name_to_name_config(log_name: str):
    name_list = log_name.split('.')
    path_nl = os.path.join(*name_list)
    if len(name_list) >= 2:
        path_2l_left = os.path.join('.'.join(name_list[:-1]), name_list[-1])
        path_2l_right = os.path.join(name_list[0], '.'.join(name_list[1:]))
        path_2l_last2 = os.path.join(name_list[-2], name_list[-1])
    else:
        path_2l_left = os.path.join(log_name, log_name)
        path_2l_right = os.path.join(log_name, log_name)
        path_2l_last2 = os.path.join(log_name, log_name)
    return {"log_name": {
        'path_1l': log_name,
        'path_nl': path_nl,
        'path_2l_left': path_2l_left,
        'path_2l_right': path_2l_right,
        'path_2l_last2': path_2l_last2
    }}


def init_logging_by_config(cfg, tpl, **kwargs):
    init_config = {"init_cfg": cfg_loader.merge_omega_conf(def_cfg, kwargs)}

    def_formatters = cfg_loader.load_yaml(io.StringIO(def_formatters_yaml), to_container=False)
    tpl_handlers = cfg_loader.load_yaml(io.StringIO(tpl_handlers_yaml), to_container=False)
    tpl_filters = cfg_loader.load_yaml(io.StringIO(tpl_filters_yaml), to_container=False)
    def_cfg_without_formatter = cfg_loader.load_yaml(io.StringIO(def_cfg_without_formatter_yaml),
                                                     to_container=False)
    default_tpl = cfg_loader.load_yaml(io.StringIO(default_tpl_yaml), to_container=False)

    if cfg is None:
        env_cfg = {}
    elif isinstance(cfg, str):
        env_cfg = cfg_loader.load_yaml(cfg, to_container=False)
    else:
        env_cfg = cfg

    if tpl is None:
        env_tpl = {}
    elif isinstance(tpl, str):
        env_tpl = cfg_loader.load_yaml(tpl, to_container=False)
    else:
        env_tpl = tpl

    tpl_cfg_omega = cfg_loader.merge_omega_conf(def_formatters, tpl_handlers, tpl_filters,
                                                default_tpl, env_tpl,
                                                to_container=False)

    cfg_cfg_omega = cfg_loader.merge_omega_conf(def_cfg_without_formatter,
                                                {'formatters': tpl_cfg_omega.get('formatters', {}),
                                                 'filters': tpl_cfg_omega.get('filters', {})},
                                                env_cfg,
                                                to_container=False)
    cfg, tpl = _parse_tpl(cfg_cfg_omega, tpl_cfg_omega, init_config)
    global logger_templates
    logger_templates = tpl
    logging.config.dictConfig(cfg)


def init_logging(env=None, **kwargs):
    env_cfg = cfg_loader.load_yaml_by_name_with_env('log_cfg', env=env, to_container=False)
    cfg = cfg_loader.merge_omega_conf(env_cfg, cfg_loader.load_env_vars_to_dict('APP_LOG_CFG_'),
                                      to_container=False)

    env_tpl = cfg_loader.load_yaml_by_name_with_env('log_tpl', env=env, to_container=False)
    tpl = cfg_loader.merge_omega_conf(env_tpl, cfg_loader.load_env_vars_to_dict('APP_LOG_TPL_'),
                                      to_container=False)
    init_logging_by_config(cfg, tpl, **kwargs)


def set_global_logger(**kwargs):
    init_logging()


loggers = {}

get_logger_lock = threading.Lock()


def getLogger(name):
    return get_logger(name)


def get_logger(name):
    with get_logger_lock:
        if name in loggers:
            return loggers[name]

        logger = logging.getLogger(name)
        loggers[name] = logger

        if logger_templates is None:
            return logger
        logger_templates_merged = cfg_loader.merge_omega_conf(logger_templates, _log_name_to_name_config(name))
        tpl_loggers = logger_templates_merged.get("loggers", None)
        tpl_formatters = logger_templates_merged.get("formatters")
        if tpl_loggers is None or len(tpl_loggers) == 0:
            return logger

        logger_patterns = [v.get("pattern", None) for k, v in tpl_loggers.items()]
        loggers_list = [v for k, v in tpl_loggers.items()]
        best_tpl_idx = best_match(name, logger_patterns)
        if best_tpl_idx is None:
            return logger
        tpl_logger = loggers_list[best_tpl_idx]
        logger.setLevel(tpl_logger.get("level", def_cfg["log_level"]))
        if (propagate := tpl_logger.get("propagate", None)) is not None:
            logger.propagate = propagate

        for tpl_handle_key, tpl_handle in tpl_logger.get("handlers", {}).items():
            class_name = tpl_handle.pop("class", None)

            level = tpl_handle.pop("level", def_cfg["log_level"])
            formatter_name = tpl_handle.pop("formatter", None)
            filters = tpl_handle.pop("filters", None)
            filename = tpl_handle.get("filename", None)
            if filename is not None:
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            handler = create_instance_from_string(class_name, **tpl_handle)
            handler.setLevel(level)
            if filters is not None:
                for _, filter_c in filters.items():
                    filter_config = copy.deepcopy(filter_c)
                    class_name = filter_config.pop("()")
                    if class_name is not None:
                        filter = create_instance_from_string(class_name, **filter_config)
                    else:
                        filter = logging.Filter(**filter_config)
                    handler.addFilter(filter)

            if formatter_name is not None:
                formatter = tpl_formatters.get(formatter_name, None)
                if formatter is None:
                    continue
                formatter = copy.deepcopy(formatter)
                class_name = formatter.pop('()', None)
                if class_name is not None:
                    formatter = create_instance_from_string(class_name, **formatter)
                else:
                    formatter['fmt'] = formatter.pop('format', None)
                    formatter = logging.Formatter(**formatter)
                handler.setFormatter(formatter)

            logger.addHandler(handler)
        return logger


def get_set_once_logger(name="app", **kwargs):
    warnings.warn(
        "get_set_once_logger() is deprecated and will be removed in a future version. Use get_logger() replace.",
        DeprecationWarning,
        stacklevel=2  # 让警告指向调用者的位置，而不是本函数内部
    )
    return get_logger(name)


def patch_logging_get_logger():
    logging.getLogger = get_logger


def adapt_sys_out():
    sys.stdout = LoggerWriter(logging.getLogger("sys.stdout").info)
    sys.stderr = LoggerWriter(logging.getLogger("sys.stderr").error)


if __name__ == '__main__':
    adapt_sys_out()
    init_logging()
    import logging

    lg = logging.getLogger("a")
    lg.info("hello world i")
    lg.warning("hello world w")
    lg.debug("hello world d")
    lg.error("hello world e")
    print("hello world c")
    print(111, file=sys.stderr)

    get_logger("tasks.123")
    task123_logger = get_logger("tasks.123.1")

    task123_logger.info('task123')
    task123_logger.info('task123')
    task123_logger.info('task123')
    task123_logger.info('task1233')
    logging.info('task1234')
    print(__name__)
    kafka_logger = get_logger('kafka.111')
    kafka_logger.info('kafka')
    try:
        a = 1/0
    except:
        kafka_logger.exception('kafka_exception')
