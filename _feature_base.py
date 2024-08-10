import _common
import json
import os
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

def _step_reset_output_folder(runtime):
    shutil.rmtree(runtime.config_data['output_path'], ignore_errors=True)
    os.makedirs(runtime.config_data['output_path'])

_STEP_DEPENDENCY_LIST.append((_step_load_config, _step_reset_output_folder))

def _step_output_ready(runtime):
    pass

_STEP_DEPENDENCY_LIST.append((_step_reset_output_folder, _step_output_ready))

def _step_output_blog_meta(runtime):
    blog_meta_path = os.path.join(runtime.config_data['output_path'], 'blog_meta.json')
    with open(blog_meta_path, 'w') as f:
        json.dump(runtime.blog_meta_dict, f, indent=2, sort_keys=True)

_STEP_DEPENDENCY_LIST.append((_step_output_ready, _step_output_blog_meta))
