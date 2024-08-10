import _common
import json
import shutil

_STEP_DEPENDENCY_LIST = []

def _step_init_blog_meta_dict(runtime):
    runtime.blog_meta_dict = {}

# func before it should just init var existence
# func before it should have no dependency to other
def _step_init_done(runtime): pass

_STEP_DEPENDENCY_LIST.append((_step_init_blog_meta_dict, _step_init_done))

def _step_load_config(runtime):
    config_path = runtime.args.config
    with open(config_path, 'r') as f:
        runtime.config_data = json.load(f)
    for k,v in runtime.config_data.items():
        if k.endswith('_path'):
            runtime.config_data[k] = _common.to_native_path(v)

_STEP_DEPENDENCY_LIST.append((_step_init_done, _step_load_config))

def _step_clear_output_path(runtime):
    shutil.rmtree(runtime.config_data['output_path'], ignore_errors=True)

_STEP_DEPENDENCY_LIST.append((_step_load_config, _step_clear_output_path))

def _step_output_ready(runtime):
    pass

_STEP_DEPENDENCY_LIST.append((_step_clear_output_path, _step_output_ready))
