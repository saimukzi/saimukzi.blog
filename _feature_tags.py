import _feature_articles
import _feature_base
import json
import os

_STEP_DEPENDENCY_LIST = []

def _step_gen_tag_id_to_data_dict(runtime):
    runtime.tag_id_to_data_dict = {}
    for article_meta in runtime.article_meta_list:
        for tag in article_meta['tags']:
            if tag not in runtime.tag_id_to_data_dict:
                runtime.tag_id_to_data_dict[tag] = {
                    'tag_id': tag,
                    'article_id_list': [],
                }
            runtime.tag_id_to_data_dict[tag]['article_id_list'].append(article_meta['id'])

def _step_tag_id_to_data_dict_ready(runtime):
    pass

_STEP_DEPENDENCY_LIST.append((_feature_articles._step_article_meta_list_ready, _step_gen_tag_id_to_data_dict, _step_tag_id_to_data_dict_ready))

def _step_meta_tag_data_list(runtime):
    tag_data_list = runtime.article_meta_list
    tag_data_list = map(lambda x: x['tags'], tag_data_list)
    tag_data_list = sum(tag_data_list, [])
    value_to_count_dict = {}
    for tag in tag_data_list:
        value_to_count_dict[tag] = value_to_count_dict.get(tag, 0) + 1
    tag_data_list = set(tag_data_list)
    tag_data_list = map(lambda x: {'tag_id': x, 'count': value_to_count_dict[x]}, tag_data_list)
    tag_data_list = sorted(tag_data_list, key=lambda x: (-x['count'], x['tag_id']))
    tag_data_list = list(tag_data_list)
    runtime.blog_meta_dict['tag_data_list'] = tag_data_list

_STEP_DEPENDENCY_LIST.append((_feature_base._step_init_done, _step_meta_tag_data_list))
_STEP_DEPENDENCY_LIST.append((_feature_articles._step_article_meta_list_ready, _step_meta_tag_data_list))
_STEP_DEPENDENCY_LIST.append((_step_meta_tag_data_list, _feature_base._step_output_ready))

def _step_output(runtime):
    os.makedirs(os.path.join(runtime.config_data['output_path'], 'tags'), exist_ok=True)
    for tag_data in runtime.tag_id_to_data_dict.values():
        tag_id = tag_data['tag_id']
        tag_output_path = os.path.join(runtime.config_data['output_path'], 'tags', f'{tag_id}.json')
        with open(tag_output_path, 'w') as f:
            json.dump(tag_data, f, indent=2, sort_keys=True)

_STEP_DEPENDENCY_LIST.append((_step_tag_id_to_data_dict_ready, _step_output))
_STEP_DEPENDENCY_LIST.append((_feature_base._step_output_ready, _step_output))
