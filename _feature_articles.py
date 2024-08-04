import json
import os
import shutil
from urllib.parse import urljoin

import _common
import _feature_base
import _feature_resource
import _global

_FUNC_DEPENDENCY_LIST = []

def _func_gen_article_file_list(runtime):
    article_dir = runtime.config_data['input_path']
    article_file_list = _common.find_file(article_dir)
    article_file_list = list(filter(lambda x: x.endswith('.txt'), article_file_list))
    runtime.article_file_list = article_file_list

def _func_article_file_list_ready(runtime):
    pass

_FUNC_DEPENDENCY_LIST.append((_feature_base._func_load_config, _func_gen_article_file_list))
_FUNC_DEPENDENCY_LIST.append((_func_gen_article_file_list, _func_article_file_list_ready))
_FUNC_DEPENDENCY_LIST.append((_func_article_file_list_ready, _feature_base._func_output_ready))

def _func_gen_blog_meta_list(runtime):
    runtime.blog_meta_list = []
    for blog_path in runtime.article_file_list:
        blog_meta = get_blog_data(blog_path)['meta']
        if not blog_meta['enable']:
            continue
        runtime.blog_meta_list.append(blog_meta)

def _func_blog_meta_list_ready(runtime):
    pass

_FUNC_DEPENDENCY_LIST.append((_func_gen_article_file_list, _func_gen_blog_meta_list))
_FUNC_DEPENDENCY_LIST.append((_func_gen_blog_meta_list, _func_blog_meta_list_ready))
_FUNC_DEPENDENCY_LIST.append((_func_blog_meta_list_ready, _feature_base._func_output_ready))

def _func_output_blog(runtime):
    for blog_meta in runtime.blog_meta_list:
        blog_data = get_blog_data(blog_meta['_path'])
        blog_meta = blog_data['meta']

        output_folder_path = _global.db_path('article.'+blog_meta['id'], runtime)
        os.makedirs(output_folder_path, exist_ok=True)

        # output meta
        meta_output_path = os.path.join(output_folder_path, 'meta.json')
        with open(meta_output_path, 'w') as f:
            json.dump(blog_meta, f, indent=2, sort_keys=True)

        # process blog_content
        blog_content = blog_data['content']
        render_data = {
            'blog_meta_data': blog_meta,
            'config': runtime.config_data,
            'runtime': runtime,
        }
        blog_content = runtime.jinja_env.from_string(blog_content)
        blog_content = blog_content.render(render_data)
        render_data['blog_content'] = blog_content

        # output content txt
        content_txt_output_path = os.path.join(output_folder_path, 'content.txt')
        with open(content_txt_output_path, 'wt', encoding='utf-8') as f:
            f.write(blog_content)
        
        # output html
        blog_id = blog_meta['id']
        blog_html_output_path = os.path.join(runtime.config_data['output_path'], 'articles', f'{blog_id}.html')
        os.makedirs(os.path.dirname(blog_html_output_path), exist_ok=True)
        with open(blog_html_output_path, 'wt', encoding='utf-8') as f:
            f.write(runtime.main_template.render(render_data))

_FUNC_DEPENDENCY_LIST.append((_feature_base._func_output_ready, _func_output_blog))

def _func_resource_suffix_blackset(runtime):
    runtime.resource_suffix_blackset.add('.txt')

_FUNC_DEPENDENCY_LIST.append((_feature_resource._func_resource_suffix_blackset_init, _func_resource_suffix_blackset))
_FUNC_DEPENDENCY_LIST.append((_func_resource_suffix_blackset, _feature_resource._func_resource_suffix_blackset_ready))

# Helper functions

BLOG_META_DEFAULT = {
    'enable': True,
    'is_sample': False,
    'tags': [],
}
def get_blog_data(blog_path):
    blog = _common.read_file(blog_path)
    blog_meta_start_line_num = blog.index('=== META START ===')
    blog_meta_end_line_num = blog.index('=== META END ===')
    blog_meta_lines = blog[blog_meta_start_line_num+1:blog_meta_end_line_num]
    blog_meta = '\n'.join(blog_meta_lines)
    blog_meta = json.loads(blog_meta)
    blog_meta = {**BLOG_META_DEFAULT, **blog_meta}
    blog_meta['_path'] = blog_path

    blog_start_line_num = blog.index('=== CONTENT START ===')
    blog_end_line_num = blog.index('=== CONTENT END ===')
    blog_lines = blog[blog_start_line_num+1:blog_end_line_num]
    blog_content = '\n'.join(blog_lines)
    
    return {
        'meta': blog_meta,
        'content': blog_content,
    }
