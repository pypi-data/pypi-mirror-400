import os
import json
import time
import datetime
import random
import functools
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from dateutil.relativedelta import relativedelta

import requests
import requests.adapters
from requests.exceptions import ConnectTimeout, ConnectionError, ProxyError

from .utils import random_sleep, dict_to_pretty_string_py

RETRY = requests.adapters.Retry(
    total=3,  # 允许的重试总次数，优先于其他计数
    read=3,  # 重试读取错误的次数
    connect=3,  # 重试多少次与连接有关的错误（请求发送到远程服务器之前引发的错误）
    backoff_factor=0.3,  # 休眠时间： {backoff_factor} * (2 ** ({重试总次数} - 1))
    status_forcelist=[403, 408, 500, 502, 504],  # 强制重试的状态码
)

# 重试次数
DEFAULT_RETRIES = 2


class BaseClient:
    def __init__(self, retry=None, retries=None):
        """
        API接口的基础类

        # 来自
        >>> from spider_utils.client import BaseSpiderClient

        """
        self._session = requests.session()

        # 默认超时时间 https://2.python-requests.org//zh_CN/latest/user/advanced.html#timeout
        self.timeout = 5

        # 重试次数
        if retries is None:
            self.retries = DEFAULT_RETRIES
        else:
            self.retries = retries

        self.params = {}
        self.parse_data = {}
        self.load_count = 0

        # 删除SSL验证
        self._session.verify = False
        urllib3.disable_warnings(InsecureRequestWarning)

        # 添加会话自动重试
        if retry is None:
            adapter_with_retry = requests.adapters.HTTPAdapter(max_retries=RETRY)
        else:
            adapter_with_retry = requests.adapters.HTTPAdapter(max_retries=retry)
        self._session.mount('http://', adapter_with_retry)
        self._session.mount('https://', adapter_with_retry)

    def set_proxy(self, proxy):
        """ 设置 http 和 https 代理或者 sock5代理（requests 已经可以支持 socks 代理）

        因为由 :any:`SpiderClient` 生成的爬虫类对象和本对象使用同一session，
        所以设置代理后，对所有由当前对象生成的爬虫对象均会使用设置的代理。

        ..  note:: 如果需要使用 socks 代理，需要安装 pysocks

            ``sudo pip install pysocks>=1.5.6,!=1.5.7``

        :param str|unicode proxy: 形如 'http://user:pass@10.10.1.10:3128/'
          或者 'socks5://user:pass@host:port'。
          传入 None 表示清除代理设置。
        :return: None
        """
        if proxy is None:
            self._session.proxies.clear()
        else:
            self._session.proxies.update({'http': proxy, 'https': proxy})

    def set_headers(self, headers):
        """
        设置 headers（全局），如果是 None，清除数据

        :return: None
        """
        if headers is None:
            self._session.headers.clear()
        else:
            self._session.headers.update(headers)

    def get_headers(self):
        """
        获取 headers（全局）

        :return: Dict(headers)
        """
        return dict(self._session.headers)

    def set_cookies(self, cookies):
        """
        设置 cookies（全局），如果是 None，清除数据

        :return: None
        """
        if cookies is None:
            self._session.cookies.clear()
        else:
            self._session.cookies.update(cookies)

    def get_cookies(self):
        """
        获取 cookies（全局）

        :return: Dict(cookies)
        """
        return requests.utils.dict_from_cookiejar(self._session.cookies)

    def set_params(self, params):
        """
        设置 params（全局），如果是 None，清除数据

        :return: None
        """
        if params is None:
            self.params = {}
        else:
            self.params.update(params)

    def get(self, url, **kwargs):
        r"""发送GET请求。 返回响应对象。

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        kwargs.setdefault('timeout', self.timeout)

        # 合并 params
        params = dict(self.params)
        if 'params' in kwargs:
            params.update(kwargs['params'])
            del kwargs['params']

        return self._session.get(url, params=params, **kwargs)

    def download(self, url, dst, **kwargs):
        """
        下载文件
        """

        req = self.get(url, **kwargs)

        with open(dst, 'ab') as f:
            f.write(req.content)

        file_size = os.path.getsize(dst)
        # 检查文件大小判断是否下载成功
        if file_size >= int(req.headers['content-length']):
            return file_size
        else:
            os.remove(dst)

    def load_page(self, url, **kwargs):

        self.parse_data = {}
        self.load_count += 1
        print(f'[{self.load_count:05}] Starting {url}')

        for i in range(self.retries):
            try:
                r = self.get(url, **kwargs)
                random_sleep()
            except (ConnectTimeout, ConnectionError) as e:
                print(f'错误 {e}')
            else:
                return r

    def api(self, method, url, params=None, data=None):
        """
        开发时用的测试某个 API 返回的 JSON 用的便捷接口。

        :param str|unicode method: HTTP 方式， GET or POST or OPTION, etc。
        :param str|unicode url: API 地址。
        :param dict params: GET 参数。
        :param dict data: POST 参数。
        :return: 访问结果。
        :rtype: request.Response
        """
        return self._session.request(method, url, params, data)

    def __repr__(self):
        repr_info = [f"<------------------------------ {type(self).__name__} ------------------------------>",
                     f"timeout = {self.timeout}",
                     f"headers = {dict_to_pretty_string_py(self.get_headers())}",
                     f"cookies = {dict_to_pretty_string_py(self.get_cookies())}",
                     f"params = {dict_to_pretty_string_py(self.params)}",
                     f"<------------------------------ {type(self).__name__} ------------------------------>"]
        return '\n'.join(repr_info)
