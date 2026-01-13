# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from functools import wraps
from typing import Callable, Optional, Sequence, Tuple, TypeVar, cast

from flask import current_app, flash, redirect, request, url_for
from flask_login import login_user

from airflow.settings import APPKEY

import time
import base64
import hmac

T = TypeVar("T", bound=Callable)

def generate_token(key, expire=3600):
    r'''
        @Args:
            key: str (用户给定的key，需要用户保存以便之后验证token,每次产生token时的key 都可以是同一个key)
            expire: int(最大有效时间，单位为s)
        @Return:
            state: str
    '''
    ts_str = str(time.time() + expire)
    ts_byte = ts_str.encode("utf-8")
    sha1_tshexstr  = hmac.new(key.encode("utf-8"),ts_byte,'sha1').hexdigest()
    token = ts_str+':'+sha1_tshexstr
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")

def certify_token(key, token):
    r'''
        @Args:
            key: str
            token: str
        @Returns:
            boolean
    '''
    try:
        token_str = base64.urlsafe_b64decode(token).decode('utf-8')
        token_list = token_str.split(':')
        if len(token_list) != 2:
            return False
        ts_str = token_list[0]
        if float(ts_str) < time.time():
            # token expired
            return False
        known_sha1_tsstr = token_list[1]
        sha1 = hmac.new(key.encode("utf-8"),ts_str.encode('utf-8'),'sha1')
        calc_sha1_tsstr = sha1.hexdigest()
        if calc_sha1_tsstr != known_sha1_tsstr:
            # token certification failed
            return False
        # token certification success
        return True
    except Exception as e:
        print(str(e.args))
        return False

def has_access(permissions: Optional[Sequence[Tuple[str, str]]] = None) -> Callable[[T], T]:
    """Factory for decorator that checks current user's permissions against required permissions."""

    def requires_access_decorator(func: T):
        @wraps(func)
        def decorated(*args, **kwargs):
            appbuilder = current_app.appbuilder
            if appbuilder.sm.check_authorization(permissions, request.args.get('dag_id', None)):
                return func(*args, **kwargs)
            else:
                if request.method == 'GET' and request.args.get("user") and request.args.get("EmbedToken"):
                    username = request.args.get("user")
                    token = request.args.get("EmbedToken")
                    if certify_token(APPKEY + username, token):
                        user = appbuilder.sm.auth_user_remote_user(username)
                        if user is None:
                            access_denied = 'auth fail, no user setup'
                        else:
                            login_user(user)
                            return redirect(request.args.get("next") or url_for("Airflow.index"))
                    else:
                        access_denied = 'token auth fail'
                else:
                    access_denied = "Access is Denied"
                flash(access_denied, "danger")

            return redirect(
                url_for(
                    appbuilder.sm.auth_view.__class__.__name__ + ".login",
                    next=request.url,
                )
            )

        return cast(T, decorated)

    return requires_access_decorator

