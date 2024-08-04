import argparse
import importlib
import jinja2
import json
import os
import shutil
import types
from urllib.parse import urljoin

import _common

MY_PATH = os.path.abspath(__file__)

def main():
    parser = argparse.ArgumentParser(description='Generate the blog')
    parser.add_argument('--config', type=str, default='config.json', help='config file')

    args = parser.parse_args()

    runtime = types.SimpleNamespace()
    runtime.args = args

    my_dir = os.path.dirname(MY_PATH)
    feature_py_list = os.listdir(my_dir)
    feature_py_list = filter(lambda x: x.startswith('_feature_'), feature_py_list)
    feature_py_list = filter(lambda x: x.endswith('.py'), feature_py_list)
    feature_py_list = map(lambda x: x[:-3], feature_py_list)
    feature_py_list = list(feature_py_list)
    runtime.module_id_to_module_dict = {}
    for feature_py in feature_py_list:
        runtime.module_id_to_module_dict[feature_py[9:]] = importlib.import_module(feature_py)

    # init modules
    runtime.func_key_to_func_dict = {}
    runtime.func_dependency_0_to_1_set_dict = {}
    runtime.func_dependency_1_to_0_set_dict = {}
    for module in runtime.module_id_to_module_dict.values():
        for func_name in dir(module):
            if func_name.startswith('_func_'):
                func = getattr(module, func_name)
                func_key = get_func_key(func)
                runtime.func_key_to_func_dict[func_key] = func
                runtime.func_dependency_0_to_1_set_dict[func_key] = set()
                runtime.func_dependency_1_to_0_set_dict[func_key] = set()
        if hasattr(module, '_FUNC_DEPENDENCY_LIST'):
            func_dependency_list = getattr(module, '_FUNC_DEPENDENCY_LIST')
            for func_dependency in func_dependency_list:
                for i in range(len(func_dependency)-1):
                    func0_key = get_func_key(func_dependency[i])
                    func1_key = get_func_key(func_dependency[i+1])
                    runtime.func_dependency_0_to_1_set_dict[func0_key].add(func1_key)
                    runtime.func_dependency_1_to_0_set_dict[func1_key].add(func0_key)
    
    runtime.ready_func_set = set()
    for func1_key, func0_set in runtime.func_dependency_1_to_0_set_dict.items():
        if len(func0_set) == 0:
            runtime.ready_func_set.add(func1_key)
    
    runtime.done_func_key_set = set()
    while len(runtime.ready_func_set) > 0:
        func_key = runtime.ready_func_set.pop()
        func = runtime.func_key_to_func_dict[func_key]
        func(runtime)
        runtime.done_func_key_set.add(func_key)
        for func1_key in runtime.func_dependency_0_to_1_set_dict.get(func_key):
            runtime.func_dependency_1_to_0_set_dict[func1_key].remove(func_key)
            if len(runtime.func_dependency_1_to_0_set_dict[func1_key]) == 0:
                runtime.ready_func_set.add(func1_key)

    assert(len(runtime.done_func_key_set) == len(runtime.func_key_to_func_dict))

    runtime.tag_id_to_data_dict = {}
    runtime.sample_only = True
    runtime.article_res_fn_to_url = {}

    runtime.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(runtime.config_data['templates_path']))
    runtime.jinja_env.filters['json_encode'] = jinja_filter_json_encode
    runtime.jinja_env.filters['url'] = jinja_filter_url

    template_file_list = _common.find_file(runtime.config_data['templates_path'])
    for template_file in template_file_list:
        process_template(template_file, runtime)

    runtime.main_template = runtime.jinja_env.get_template('_main.html')

    article_file_list = _common.find_file(runtime.config_data['articles_path'])

    article_res_file_list = list(filter(lambda x: not x.endswith('.txt'), article_file_list))
    for article_res_file in article_res_file_list:
        process_article_res_file_0(article_res_file, runtime)

    article_blog_file_list = list(filter(lambda x: x.endswith('.txt'), article_file_list))
    for article_blog_file in article_blog_file_list:
        process_article_blog_file_0(article_blog_file, runtime)
    for article_blog_file in article_blog_file_list:
        process_article_blog_file_1(article_blog_file, runtime)
    
    os.makedirs(os.path.join(runtime.config_data['output_path'], 'tags'), exist_ok=True)
    for tag_data in runtime.tag_id_to_data_dict.values():
        process_tag(tag_data, runtime)

def get_func_key(func):
    return f'{func.__module__}.{func.__name__}'

def process_template(template_file, runtime):
    if os.path.basename(template_file)[:1] == '_':
        return
    rel_path = os.path.relpath(template_file, runtime.config_data['templates_path'])
    output_file = os.path.join(runtime.config_data['output_path'], rel_path)
    template = runtime.jinja_env.get_template(rel_path)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    render_data = {}
    for k,v in runtime.config_data.items():
        render_data[f'config_{k}'] = v
    with open(output_file, 'wt', encoding='utf-8') as f:
        f.write(template.render(render_data))

def process_article_res_file_0(article_file, runtime):
    dot_idx = article_file.rfind('.')
    if dot_idx == -1:
        file_suffix = ''
    else:
        file_suffix = article_file[dot_idx:]
    file_md5 = _common.md5_file(article_file)
    key = 'article_res.'+file_md5+file_suffix
    output_folder_path = db_path(key, runtime)
    output_path = os.path.join(output_folder_path, 'bin'+file_suffix)
    os.makedirs(output_folder_path, exist_ok=True)
    if os.path.exists(output_path):
        assert(_common.is_file_equal(article_file, output_path))
    else:
        shutil.copy(article_file, output_path)
    output_rel_path = os.path.relpath(output_path, runtime.config_data['output_path'])
    output_rel_url = _common.to_rel_url(output_rel_path)
    output_url = urljoin(runtime.config_data['base_url'], output_rel_url)
    # output_local_uri = _common.local_path_to_abs_uri(output_path)
    # config_output_local_uri = _common.local_path_to_abs_uri(runtime.config_data['output_path'])
    # print(output_path)
    input_rel_path = os.path.relpath(article_file, runtime.config_data['articles_path'])
    runtime.article_res_fn_to_url[input_rel_path] = output_url

CONFIG_DATA_DEFAULT = {
    'enable': True,
    'is_sample': False,
}

def process_article_blog_file_0(article_file, runtime):
    article_data = get_article_data(article_file)
    article_config_data = article_data['config']

    if not article_config_data['enable']:
        return

    # process is_sample
    if not article_config_data['is_sample']:
        runtime.sample_only = False

def process_article_blog_file_1(article_file, runtime):
    article_data = get_article_data(article_file)
    article_config_data = article_data['config']
    article_content = article_data['content']

    if not article_config_data['enable']:
        return

    if not runtime.sample_only and article_config_data['is_sample']:
        return

    output_folder_path = db_path('article.'+article_config_data['id'], runtime)
    os.makedirs(output_folder_path, exist_ok=True)

    # output meta
    meta_output_path = os.path.join(output_folder_path, 'meta.json')
    with open(meta_output_path, 'w') as f:
        json.dump(article_config_data, f, indent=2, sort_keys=True)
    
    # process article_content
    render_data = {
        'article_file_path': article_file,
        'article_config_data': article_config_data,
        'config': runtime.config_data,
        'runtime': runtime,
    }
    article_content = runtime.jinja_env.from_string(article_content)
    article_content = article_content.render(render_data)
    render_data['article_content'] = article_content

    # output content txt
    content_txt_output_path = os.path.join(output_folder_path, 'content.txt')
    with open(content_txt_output_path, 'wt', encoding='utf-8') as f:
        f.write(article_content)

    # output article html
    article_id = article_config_data['id']
    article_html_output_path = os.path.join(runtime.config_data['output_path'], 'articles', f'{article_id}.html')
    os.makedirs(os.path.dirname(article_html_output_path), exist_ok=True)
    with open(article_html_output_path, 'wt', encoding='utf-8') as f:
        f.write(runtime.main_template.render(render_data))
    
    # process tags
    tag_list = article_config_data.get('tags', [])
    for tag_id in tag_list:
        tag_data = runtime_get_or_init_tag(runtime, tag_id)
        tag_data['article_id_list'].append(article_id)

def process_tag(tag_data, runtime):
    tag_id = tag_data['id']
    tag_output_path = os.path.join(runtime.config_data['output_path'], 'tags', f'{tag_id}.json')
    with open(tag_output_path, 'w') as f:
        json.dump(tag_data, f, indent=2, sort_keys=True)


def get_article_data(article_file):
    article = _common.read_file(article_file)
    article_config_start_line_num = article.index('=== META START ===')
    article_config_end_line_num = article.index('=== META END ===')
    article_config_lines = article[article_config_start_line_num+1:article_config_end_line_num]
    article_config_data = '\n'.join(article_config_lines)
    article_config_data = json.loads(article_config_data)
    article_config_data = {**CONFIG_DATA_DEFAULT, **article_config_data}

    article_start_line_num = article.index('=== CONTENT START ===')
    article_end_line_num = article.index('=== CONTENT END ===')
    article_lines = article[article_start_line_num+1:article_end_line_num]
    article_content = '\n'.join(article_lines)
    
    return {
        'config': article_config_data,
        'content': article_content,
    }

def runtime_get_or_init_tag(runtime, tag_id):
    if tag_id not in runtime.tag_id_to_data_dict:
        runtime.tag_id_to_data_dict[tag_id] = {
            'id': tag_id,
            'article_id_list': [],
        }
    return runtime.tag_id_to_data_dict[tag_id]

def jinja_filter_json_encode(obj):
    return json.dumps(obj)

@jinja2.pass_context
def jinja_filter_url(context, input_relpath, ttype='articles'):
    assert(ttype in ['articles', 'templates'])
    runtime = context['runtime']
    if ttype == 'articles':
        article_file_path = context['article_file_path']
        article_file_folder_path = os.path.dirname(article_file_path)
        input_abspath = os.path.join(article_file_folder_path, input_relpath)
        assert(os.path.commonprefix([input_abspath, runtime.config_data['articles_path']]) == runtime.config_data['articles_path'])
        input_relpath = os.path.relpath(input_abspath, runtime.config_data['articles_path'])
        output_url = runtime.article_res_fn_to_url[input_relpath]
        return output_url
    elif ttype == 'templates':
        output_url = urljoin(runtime.config_data['base_url'], input_relpath)
        return output_url
    assert(False)

def db_path(key, runtime):
    key_hash = _common.md5(key)
    return os.path.join(runtime.config_data['output_path'], 'db', key_hash[:2], key_hash[2:4], key_hash)

if __name__ == '__main__':
    main()
