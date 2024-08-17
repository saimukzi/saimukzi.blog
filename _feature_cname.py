import os

import _feature_base

_STEP_DEPENDENCY_LIST = []

def _step_output(runtime):
    if 'cname' in runtime.config_data:
        cname_path = os.path.join(runtime.config_data['output_path'], 'CNAME')
        with open(cname_path, 'w') as f:
            f.write(runtime.config_data['cname'])
            f.write('\n')

_STEP_DEPENDENCY_LIST.append((_feature_base._step_output_ready, _step_output))
