import argparse
import jinja2
import json
import os
import shutil
import types

import _common

def main():
    parser = argparse.ArgumentParser(description='Generate the blog')
    parser.add_argument('--config', type=str, default='config.json', help='config file')

    args = parser.parse_args()

    runtime = types.SimpleNamespace()

    config_path = args.config
    with open(config_path, 'r') as f:
        runtime.config_data = json.load(f)

    shutil.rmtree(runtime.config_data['output_path'], ignore_errors=True)

    runtime.tag_id_to_data_dict = {}

    runtime.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(runtime.config_data['templates_path']))
    
    template_file_list = _common.find_file(runtime.config_data['templates_path'])
    for template_file in template_file_list:
        process_template(template_file, runtime)

    runtime.main_template = runtime.jinja_env.get_template('_main.html')

    article_file_list = _common.find_file(runtime.config_data['articles_path'])
    for article_file in article_file_list:
        process_article(article_file, runtime)
    
    os.makedirs(os.path.join(runtime.config_data['output_path'], 'tags'), exist_ok=True)
    for tag_data in runtime.tag_id_to_data_dict.values():
        process_tag(tag_data, runtime)

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

CONFIG_DATA_DEFAULT = {
    'enable': True,
}

def process_article(article_file, runtime):
    article_data = get_article_data(article_file)
    article_config_data = article_data['config']
    article_content = article_data['content']

    if not article_config_data['enable']:
        return

    id_hash = _common.md5(article_config_data['id'])
    output_folder_path = os.path.join(runtime.config_data['output_path'], id_hash[:2], id_hash[2:4], id_hash)
    os.makedirs(output_folder_path, exist_ok=True)

    meta_output_path = os.path.join(output_folder_path, 'meta.json')
    with open(meta_output_path, 'w') as f:
        json.dump(article_config_data, f, indent=2, sort_keys=True)
    
    article_txt_output_path = os.path.join(output_folder_path, 'article.txt')
    with open(article_txt_output_path, 'wt', encoding='utf-8') as f:
        f.write(article_content)
    
    # output article
    article_id = article_config_data['id']
    article_html_output_path = os.path.join(runtime.config_data['output_path'], 'articles', f'{article_id}.html')
    os.makedirs(os.path.dirname(article_html_output_path), exist_ok=True)
    render_data = {
        'article_config_data': article_config_data,
        'article_content': article_content,
        'config': runtime.config_data,
    }
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
    article_config_start_line_num = article.index('=== CONFIG START ===')
    article_config_end_line_num = article.index('=== CONFIG END ===')
    article_config_lines = article[article_config_start_line_num+1:article_config_end_line_num]
    article_config_data = '\n'.join(article_config_lines)
    article_config_data = json.loads(article_config_data)
    article_config_data = {**CONFIG_DATA_DEFAULT, **article_config_data}

    article_start_line_num = article.index('=== ARTICLE START ===')
    article_end_line_num = article.index('=== ARTICLE END ===')
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

if __name__ == '__main__':
    main()
