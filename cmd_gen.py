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

    runtime.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(runtime.config_data['templates_path']))
    
    template_file_list = _common.find_file(runtime.config_data['templates_path'])
    for template_file in template_file_list:
        process_template(template_file, runtime)

    content_file_list = _common.find_file(runtime.config_data['contents_path'])
    for content_file in content_file_list:
        process_content(content_file, runtime)

def process_template(template_file, runtime):
    rel_path = os.path.relpath(template_file, runtime.config_data['templates_path'])
    output_file = os.path.join(runtime.config_data['output_path'], rel_path)
    template = runtime.jinja_env.get_template(rel_path)
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    render_data = {}
    for k,v in runtime.config_data.items():
        render_data[f'config_{k}'] = v
    with open(output_file, 'w') as f:
        f.write(template.render(render_data))

CONFIG_DATA_DEFAULT = {
    'enable': True,
}
def process_content(content_file, runtime):
    content = _common.read_file(content_file)

    config_start_line_num = content.index('=== CONFIG START ===')
    config_end_line_num = content.index('=== CONFIG END ===')
    config_lines = content[config_start_line_num+1:config_end_line_num]
    config_data = '\n'.join(config_lines)
    config_data = json.loads(config_data)
    config_data = {**CONFIG_DATA_DEFAULT, **config_data}

    if not config_data['enable']:
        return
    
    content_start_line_num = content.index('=== CONTENT START ===')
    content_end_line_num = content.index('=== CONTENT END ===')
    content_lines = content[content_start_line_num+1:content_end_line_num]
    content = '\n'.join(content_lines)

    id_hash = _common.md5(config_data['id'])
    output_folder_path = os.path.join(runtime.config_data['output_path'], id_hash[:2], id_hash[2:4], id_hash)
    os.makedirs(output_folder_path, exist_ok=True)

    meta_output_path = os.path.join(output_folder_path, 'meta.json')
    with open(meta_output_path, 'w') as f:
        json.dump(config_data, f, indent=2, sort_keys=True)
    
    content_output_path = os.path.join(output_folder_path, 'content.txt')
    with open(content_output_path, 'w') as f:
        f.write(content)


if __name__ == '__main__':
    main()
