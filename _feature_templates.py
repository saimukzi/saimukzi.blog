import jinja2
import json
import os
from urllib.parse import urljoin

import _common
import _feature_base
import _feature_resource

_STEP_DEPENDENCY_LIST = []

def _step_jinja_env_init(runtime):
    runtime.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(runtime.config_data['input_path']))
    runtime.jinja_env.filters['json_encode'] = jinja_filter_json_encode

def _step_jinja_env_ready(runtime):
    pass

_STEP_DEPENDENCY_LIST.append((_feature_base._step_load_config, _step_jinja_env_init))
_STEP_DEPENDENCY_LIST.append((_step_jinja_env_init, _step_jinja_env_ready))
_STEP_DEPENDENCY_LIST.append((_step_jinja_env_ready, _feature_base._step_output_ready))

def _step_init_main_template(runtime):
    runtime.main_template = runtime.jinja_env.get_template('_main.html.template')

_STEP_DEPENDENCY_LIST.append((
    _step_jinja_env_ready,
    _step_init_main_template,
    _feature_base._step_output_ready,
))

# def _step_output(runtime):
#     template_file_list = _common.find_file(runtime.config_data['templates_path'])
#     for template_file in template_file_list:
#         if os.path.basename(template_file)[:1] == '_':
#             return
#         rel_path = os.path.relpath(template_file, runtime.config_data['templates_path'])
#         output_file = os.path.join(runtime.config_data['output_path'], rel_path)
#         template = runtime.jinja_env.get_template(rel_path)
#         os.makedirs(os.path.dirname(output_file), exist_ok=True)
#         render_data = {}
#         for k,v in runtime.config_data.items():
#             render_data[f'config_{k}'] = v
#         with open(output_file, 'wt', encoding='utf-8') as f:
#             f.write(template.render(render_data))

# _STEP_DEPENDENCY_LIST.append((_feature_base._step_output_ready, _step_output))

def _step_resource_suffix_blackset(runtime):
    runtime.resource_suffix_blackset.add('.template')

_STEP_DEPENDENCY_LIST.append((_feature_resource._step_resource_suffix_blackset_init, _step_resource_suffix_blackset))
_STEP_DEPENDENCY_LIST.append((_step_resource_suffix_blackset, _feature_resource._step_resource_suffix_blackset_ready))

# jinja_env functions

def jinja_filter_json_encode(obj):
    return json.dumps(obj)
