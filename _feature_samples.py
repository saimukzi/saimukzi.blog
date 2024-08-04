import _feature_articles

_FUNC_DEPENDENCY_LIST = []

def _func_filter(runtime):
    is_all_sample = True
    for runtime.article in runtime.blog_meta_list:
        if runtime.article['is_sample']: continue
        is_all_sample = False
        break
    if is_all_sample: return

    new_blog_meta_list = []
    for runtime.article in runtime.blog_meta_list:
        if runtime.article['is_sample']: continue
        new_blog_meta_list.append(runtime.article)

    runtime.blog_meta_list = new_blog_meta_list

_FUNC_DEPENDENCY_LIST.append((_feature_articles._func_gen_blog_meta_list, _func_filter, _feature_articles._func_blog_meta_list_ready))
