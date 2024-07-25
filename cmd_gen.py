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

    # content_file_list = _common.find_file(runtime.config_data['content_path'])

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

if __name__ == '__main__':
    main()
