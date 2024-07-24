import argparse
import jinja2
import json
import os

import _common

def main():
    parser = argparse.ArgumentParser(description='Generate the blog')
    parser.add_argument('--config', type=str, default='config.json', help='config file')

    args = parser.parse_args()

    config_path = args.config
    with open(config_path, 'r') as f:
        config_data = json.load(f)

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(config_data['templates_path']))
    
    template_file_list = _common.find_file(config_data['templates_path'])
    for template_file in template_file_list:
        rel_path = os.path.relpath(template_file, config_data['templates_path'])
        output_file = os.path.join(config_data['output_path'], rel_path)
        process_template(rel_path, output_file, config_data, jinja_env)

def process_template(rel_path, output_file, config_data, jinja_env):
    template = jinja_env.get_template(rel_path)
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    render_data = {}
    for k,v in config_data.items():
        render_data[f'config_{k}'] = v
    with open(output_file, 'w') as f:
        f.write(template.render(render_data))

if __name__ == '__main__':
    main()
