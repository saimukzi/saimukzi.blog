import _common
import json
import shutil

_FUNC_DEPENDENCY_LIST = []

def _func_init_blog_meta_dict(runtime):
    runtime.blog_meta_dict = {}

# func before it should just init var existence
# func before it should have no dependency to other
def _func_init_done(runtime): pass

_FUNC_DEPENDENCY_LIST.append((_func_init_blog_meta_dict, _func_init_done))

def _func_load_config(runtime):
    config_path = runtime.args.config
    with open(config_path, 'r') as f:
        runtime.config_data = json.load(f)
    for k,v in runtime.config_data.items():
        if k.endswith('_path'):
            runtime.config_data[k] = _common.to_native_path(v)

_FUNC_DEPENDENCY_LIST.append((_func_init_done, _func_load_config))

def _func_clear_output_path(runtime):
    shutil.rmtree(runtime.config_data['output_path'], ignore_errors=True)

_FUNC_DEPENDENCY_LIST.append((_func_load_config, _func_clear_output_path))

def _func_output_ready(runtime):
    pass

_FUNC_DEPENDENCY_LIST.append((_func_clear_output_path, _func_output_ready))
