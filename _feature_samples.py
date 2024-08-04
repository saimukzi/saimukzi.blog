import _feature_articles

_FUNC_DEPENDENCY_LIST = []

def _func_filter(runtime):
    is_all_sample = True
    for runtime.article in runtime.article_meta_list:
        if runtime.article['is_sample']: continue
        is_all_sample = False
        break
    if is_all_sample: return

    new_article_meta_list = []
    for runtime.article in runtime.article_meta_list:
        if runtime.article['is_sample']: continue
        new_article_meta_list.append(runtime.article)

    runtime.article_meta_list = new_article_meta_list

_FUNC_DEPENDENCY_LIST.append((_feature_articles._func_gen_article_meta_list, _func_filter, _feature_articles._func_article_meta_list_ready))
