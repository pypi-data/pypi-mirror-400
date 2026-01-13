import os
from pathlib import Path
from omegaconf import OmegaConf
from .path_util import list_files, to_absolute_path_str
import warnings


def load_yaml_dir(path, overridden=None, override=None):
    warnings.warn(
        "load_yaml_dir() is deprecated and will be removed in a future version. "
        "Use load_by_deep_dir() instead.",
        DeprecationWarning,
        stacklevel=2  # 让警告指向调用者的位置，而不是本函数内部
    )
    return load_yaml_by_deep_dir(path, overridden, override)


def load_yaml(yaml, overridden=None, override=None, resolve=True, to_container=True):
    if not isinstance(yaml, list):
        yaml = [yaml]
    configs = []
    if overridden is not None:
        configs.append(overridden)
    if len(yaml) > 0:
        configs.extend(OmegaConf.load(y) for y in yaml)
    if override is not None:
        configs.append(override)
    if len(configs) == 0:
        return {}
    else:
        omega_confs = OmegaConf.merge(*configs)
        if to_container:
            return OmegaConf.to_container(omega_confs, resolve=resolve)
        else:
            return omega_confs


def load_yaml_by_files(yaml_paths, overridden=None, override=None, resolve=True, to_container=True):
    return load_yaml(yaml_paths, overridden, override, resolve, to_container)


def load_by_file(yaml_path, overridden=None, override=None, resolve=True, to_container=True):
    return load_yaml_by_files([yaml_path], overridden, override, resolve, to_container)


def load_yaml_by_file_with_env(yaml_path, env=None, overridden=None, override=None, resolve=True, to_container=True):
    config_paths = []
    if os.path.exists(yaml_path):
        config_paths.append(yaml_path)
    env = env or os.environ.get('ENV', None)
    if env is not None:
        p = Path(yaml_path)
        env_config_path = p.with_name(p.stem + f'.{env}' + p.suffix)
        if os.path.exists(env_config_path):
            config_paths.append(env_config_path)

    return load_yaml_by_files(config_paths, overridden, override, resolve, to_container)


def load_yaml_by_name(yaml_name, overridden=None, override=None, resolve=True, to_container=True):
    config_paths = []
    if (path := to_absolute_path_str(f"{yaml_name}.yml")) is not None:
        config_paths.append(path)
    if (path := to_absolute_path_str(f"{yaml_name}.yaml")) is not None:
        config_paths.append(path)

    return load_yaml_by_files(config_paths, overridden, override, resolve, to_container)


def load_yaml_by_name_with_env(yaml_name, env=None, overridden=None, override=None, resolve=True, to_container=True):
    configs = []
    if overridden is not None:
        configs.append(overridden)
    configs.append(load_yaml_by_name(yaml_name, to_container=False))
    env = env or os.environ.get('ENV', None)
    if env is not None:
        configs.append(load_yaml_by_name(f"{yaml_name}.{env}", to_container=False))
    if override is not None:
        configs.append(override)

    omega_confs = OmegaConf.merge(*configs)
    if to_container:
        return OmegaConf.to_container(omega_confs, resolve=resolve)
    else:
        return omega_confs


def load_yaml_by_deep_dir(dir_path, overridden=None, override=None, resolve=True, to_container=True):
    yaml_files = list_files(dir_path, suffixes=['.yaml', '.yml'])
    return load_yaml_by_files(sorted(yaml_files), overridden, override, resolve, to_container)


def load_yaml_by_dir(dir_path, overridden=None, override=None, resolve=True, to_container=True):
    yaml_files = [f.as_posix() for f in Path(dir_path).iterdir() if
                  f.is_file() and f.suffix.lower() in {'.yml', '.yaml'}]
    return load_yaml_by_files(sorted(yaml_files), overridden, override, resolve, to_container)


def load_yaml_by_dir_with_env(dir_path, env=None, overridden=None, override=None, resolve=True, to_container=True):
    configs = []
    if overridden is not None:
        configs.append(overridden)
    configs.append(load_yaml_by_dir(dir_path, to_container=False))
    env = env or os.environ.get('ENV', None)
    if env is not None:
        configs.append(load_yaml_by_dir(f"{dir_path}/{env}", to_container=False))
    if override is not None:
        configs.append(override)
    omega_confs = OmegaConf.merge(*configs)
    if to_container:
        return OmegaConf.to_container(omega_confs, resolve=resolve)
    else:
        return omega_confs


def merge_omega_conf(*configs, resolve=True, to_container=True):
    omega_confs = OmegaConf.merge(*configs)
    if to_container:
        return OmegaConf.to_container(omega_confs, resolve=resolve)
    else:
        return omega_confs


def load_env_vars_to_dict(prefix, dict_split_char='__'):
    """
    读取以指定前缀开头的环境变量，并将其转换为小写、嵌套的字典。

    :param prefix: 环境变量前缀（例如 "APP_"）
    :param dict_split_char: 分隔符
    :return: 转换后的嵌套字典
    """
    # 确保前缀是大写的，避免大小写问题
    prefix = prefix.upper()
    result = {}

    for key, value in os.environ.items():
        if key.startswith(prefix):
            # 去掉前缀部分并转为小写
            stripped_key = key[len(prefix):].lower()
            # 使用双下划线分割各个部分
            parts = stripped_key.split(dict_split_char)

            current_level = result
            for part in parts[:-1]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

            # 尝试将字符串值解析为Python数据类型
            try:
                namespace = {}
                exec(f'data={value}', namespace)
                data = namespace['data']
            except:
                data = value  # 如果解析失败则保留原始字符串

            # 设置最终值
            current_level[parts[-1]] = data

            # 如果parts长度为1，则直接设置在result上
            if len(parts) == 1:
                result[stripped_key] = data

    return result
