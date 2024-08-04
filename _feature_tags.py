import _feature_articles
import _feature_base
import json
import os

_FUNC_DEPENDENCY_LIST = []

def _func_gen_tag_id_to_data_dict(runtime):
    runtime.tag_id_to_data_dict = {}
    for article_meta in runtime.article_meta_list:
        for tag in article_meta['tags']:
            if tag not in runtime.tag_id_to_data_dict:
                runtime.tag_id_to_data_dict[tag] = {
                    'tag_id': tag,
                    'article_id_list': [],
                }
            runtime.tag_id_to_data_dict[tag]['article_id_list'].append(article_meta['id'])

def _func_tag_id_to_data_dict_ready(runtime):
    pass

_FUNC_DEPENDENCY_LIST.append((_feature_articles._func_article_meta_list_ready, _func_gen_tag_id_to_data_dict, _func_tag_id_to_data_dict_ready))

def _func_output(runtime):
    os.makedirs(os.path.join(runtime.config_data['output_path'], 'tags'), exist_ok=True)
    for tag_data in runtime.tag_id_to_data_dict.values():
        tag_id = tag_data['tag_id']
        tag_output_path = os.path.join(runtime.config_data['output_path'], 'tags', f'{tag_id}.json')
        with open(tag_output_path, 'w') as f:
            json.dump(tag_data, f, indent=2, sort_keys=True)

_FUNC_DEPENDENCY_LIST.append((_func_tag_id_to_data_dict_ready, _func_output))
_FUNC_DEPENDENCY_LIST.append((_feature_base._func_output_ready, _func_output))
