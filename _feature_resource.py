import jinja2
import os
import shutil
from urllib.parse import urljoin

import _common
import _feature_base
# import _feature_templates
import _global

_STEP_DEPENDENCY_LIST = []

def _step_resource_suffix_blackset_init(runtime):
    runtime.resource_suffix_blackset = set()

def _step_resource_suffix_blackset_ready(runtime):
    pass

_STEP_DEPENDENCY_LIST.append((_step_resource_suffix_blackset_init, _step_resource_suffix_blackset_ready))

def _step_gen_file_list(runtime):
    input_path = runtime.config_data['input_path']
    input_resource_file_list = _common.find_file(input_path)
    input_resource_file_list = filter(lambda x: not is_black(x, runtime), input_resource_file_list)
    input_resource_file_list = list(input_resource_file_list)
    runtime.input_resource_file_list = input_resource_file_list

def _step_input_resource_file_list_ready(runtime):
    pass

_STEP_DEPENDENCY_LIST.append((_feature_base._step_load_config,_step_gen_file_list))
_STEP_DEPENDENCY_LIST.append((_step_resource_suffix_blackset_ready,_step_gen_file_list))
_STEP_DEPENDENCY_LIST.append((_step_gen_file_list,_step_input_resource_file_list_ready))

def _step_scan_res(runtime):
    runtime.article_res_fn_to_url = {}
    runtime.article_res_output_list = []
    for res_path in runtime.input_resource_file_list:
        dot_idx = res_path.rfind('.')
        if dot_idx == -1:
            file_suffix = ''
        else:
            file_suffix = res_path[dot_idx:]
        file_md5 = _common.md5_file(res_path)
        key = 'article_res.'+file_md5+file_suffix
        output_folder_path = _global.db_path(key, runtime)
        output_path = os.path.join(output_folder_path, 'bin'+file_suffix)
        runtime.article_res_output_list.append((res_path, output_path))
        output_rel_path = os.path.relpath(output_path, runtime.config_data['output_path'])
        output_rel_url = _common.to_rel_url(output_rel_path)
        output_url = urljoin(runtime.config_data['base_url'], output_rel_url)
        input_rel_path = os.path.relpath(res_path, runtime.config_data['input_path'])
        runtime.article_res_fn_to_url[input_rel_path] = output_url

def _step_article_res_fn_to_url_ready(runtime):
    pass

def _step_article_res_output_list_ready(runtime):
    pass

_STEP_DEPENDENCY_LIST.append((_feature_base._step_load_config, _step_scan_res))
_STEP_DEPENDENCY_LIST.append((_step_input_resource_file_list_ready, _step_scan_res))
_STEP_DEPENDENCY_LIST.append((_step_scan_res, _step_article_res_fn_to_url_ready))
_STEP_DEPENDENCY_LIST.append((_step_scan_res, _step_article_res_output_list_ready))
_STEP_DEPENDENCY_LIST.append((_step_article_res_fn_to_url_ready, _feature_base._step_output_ready))
_STEP_DEPENDENCY_LIST.append((_step_article_res_output_list_ready, _feature_base._step_output_ready))

def _step_output_res(runtime):
    for res_path, output_path in runtime.article_res_output_list:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if os.path.exists(output_path):
            assert(_common.is_file_equal(res_path, output_path))
        else:
            shutil.copy(res_path, output_path)

_STEP_DEPENDENCY_LIST.append((_feature_base._step_output_ready, _step_output_res))

def _step_jinja_env(runtime):
    runtime.jinja_env.filters['res'] = jinja_filter_res

@jinja2.pass_context
def jinja_filter_res(context, input_path):
    runtime = context['runtime']
    res_base_absnpath = context['res_base_absnpath']
    input_absnpath = os.path.join(res_base_absnpath, input_path)
    assert(os.path.commonprefix([input_absnpath, runtime.config_data['input_path']]) == runtime.config_data['input_path'])
    input_relpath = os.path.relpath(input_absnpath, runtime.config_data['input_path'])
    output_url = runtime.article_res_fn_to_url[input_relpath]
    return output_url

_STEP_DEPENDENCY_LIST.append((
    '_feature_templates._step_jinja_env_init',
    _step_jinja_env,
    '_feature_templates._step_jinja_env_ready',
))

# Helper functions

def is_black(path, runtime):
    for suffix in runtime.resource_suffix_blackset:
        if path.endswith(suffix):
            return True
    return False
