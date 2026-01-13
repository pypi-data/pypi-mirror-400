# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 10:18
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 10:18
# Thanks for your comments!

def check_post_params(params, must_list, must_type=None, is_or=False):
    if not isinstance(must_list, list):
        return True
    if is_or:
        for field in must_list:
            if field in params:
                return True
        return "lack %s" % ','.join(must_list)
    if isinstance(params, list):
        for p in params:
            p_result = check_post_params(p, must_list)
            if isinstance(p_result, str):
                return p_result
    if isinstance(params, dict):
        for attr in must_list:
            if attr not in params:
                return 'lack %s' % attr
    if must_type and isinstance(must_type, dict):
        for k, v in must_type.items():
            if not isinstance(params.get(k), v):
                return "%s type error, need %s" % (k, str(v))
    return True
