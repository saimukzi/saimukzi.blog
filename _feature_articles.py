import json
import os
import shutil
from urllib.parse import urljoin

import _common
import _feature_base
import _feature_resource
import _global

_STEP_DEPENDENCY_LIST = []

def _step_gen_article_file_list(runtime):
    article_dir = runtime.config_data['input_path']
    article_file_list = _common.find_file(article_dir)
    article_file_list = list(filter(lambda x: x.endswith('.article.txt'), article_file_list))
    runtime.article_file_list = article_file_list

def _step_article_file_list_ready(runtime):
    pass

_STEP_DEPENDENCY_LIST.append((_feature_base._step_load_config, _step_gen_article_file_list))
_STEP_DEPENDENCY_LIST.append((_step_gen_article_file_list, _step_article_file_list_ready))
_STEP_DEPENDENCY_LIST.append((_step_article_file_list_ready, _feature_base._step_output_ready))

def _step_gen_article_meta_list(runtime):
    runtime.article_meta_list = []
    for article_path in runtime.article_file_list:
        article_meta = get_article_data(article_path)['meta']
        if not article_meta['enable']:
            continue
        runtime.article_meta_list.append(article_meta)

def _step_article_meta_list_ready(runtime):
    pass

_STEP_DEPENDENCY_LIST.append((_step_gen_article_file_list, _step_gen_article_meta_list))
_STEP_DEPENDENCY_LIST.append((_step_gen_article_meta_list, _step_article_meta_list_ready))
_STEP_DEPENDENCY_LIST.append((_step_article_meta_list_ready, _feature_base._step_output_ready))

def _step_output_article(runtime):
    for article_meta in runtime.article_meta_list:
        article_data = get_article_data(article_meta['_path'])
        article_meta = article_data['meta']

        output_folder_path = _global.db_path('article.'+article_meta['id'], runtime)
        os.makedirs(output_folder_path, exist_ok=True)

        # output meta
        meta_output_path = os.path.join(output_folder_path, 'meta.json')
        with open(meta_output_path, 'w') as f:
            json.dump(article_meta, f, indent=2, sort_keys=True)

        # process article_content
        article_content = article_data['content']
        render_data = {
            'res_base_absnpath': os.path.dirname(article_meta['_path']),
            'article_meta_data': article_meta,
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
        
        # output html
        render_data['res_base_absnpath'] = runtime.config_data['input_path']
        article_id = article_meta['id']
        article_html_output_path = os.path.join(runtime.config_data['output_path'], 'articles', f'{article_id}.html')
        os.makedirs(os.path.dirname(article_html_output_path), exist_ok=True)
        with open(article_html_output_path, 'wt', encoding='utf-8') as f:
            f.write(runtime.main_template.render(render_data))

_STEP_DEPENDENCY_LIST.append((_feature_base._step_output_ready, _step_output_article))

def _step_resource_suffix_blackset(runtime):
    runtime.resource_suffix_blackset.add('.article.txt')

_STEP_DEPENDENCY_LIST.append((_feature_resource._step_resource_suffix_blackset_init, _step_resource_suffix_blackset))
_STEP_DEPENDENCY_LIST.append((_step_resource_suffix_blackset, _feature_resource._step_resource_suffix_blackset_ready))

# Helper functions

ARTICLE_META_DEFAULT = {
    'enable': True,
    'is_sample': False,
    'tags': [],
}
def get_article_data(article_path):
    article = _common.read_file(article_path)
    article_meta_start_line_num = article.index('=== META START ===')
    article_meta_end_line_num = article.index('=== META END ===')
    article_meta_lines = article[article_meta_start_line_num+1:article_meta_end_line_num]
    article_meta = '\n'.join(article_meta_lines)
    article_meta = json.loads(article_meta)
    article_meta = {**ARTICLE_META_DEFAULT, **article_meta}
    article_meta['_path'] = article_path

    article_start_line_num = article.index('=== CONTENT START ===')
    article_end_line_num = article.index('=== CONTENT END ===')
    article_lines = article[article_start_line_num+1:article_end_line_num]
    article_content = '\n'.join(article_lines)
    
    return {
        'meta': article_meta,
        'content': article_content,
    }
