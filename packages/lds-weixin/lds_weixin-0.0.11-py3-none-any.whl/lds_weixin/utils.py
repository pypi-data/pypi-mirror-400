import os
import json
import time
import datetime
import random
import functools
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from dateutil.relativedelta import relativedelta


def dict_to_pretty_string_py(the_dict):
    if not the_dict:
        return "{}"
    return json.dumps(the_dict, sort_keys=True, indent=4, separators=(',', ': '))


def random_sleep(start=1, end=3, debug=True):
    """
    随机延迟，因为如果你访问了很多页面，你的 ip 可能会被封。
    """
    sleep_time = random.randint(start, end)
    if debug:
        print('随机延迟：%s 秒......' % sleep_time)
    time.sleep(sleep_time)


def get_now(fmt="%Y-%m-%d %H:%M:%S"):
    """
    获取当前日期和时间
    :return: 格式 2018-11-28 15:03:08
    """
    return datetime.datetime.now().strftime(fmt)


def get_past_time(now_time: datetime.datetime, amount, period='days', start_of_day=False):
    """
    获取过去的时间，可选择是否将时间设定为零点

    :param now_time: 当前时间 一般使用 datetime.datetime.now()
    :param amount: 要回溯的数量，比如几天、几周或几个月前
    :param period: 时间类型，支持 'days', 'weeks', 或 'months'
    :param start_of_day: 布尔值，是否将时间设定为零点，默认不设定
    :return: 计算得到的日期和时间
    """

    if period == 'days':
        past_time = now_time - datetime.timedelta(days=amount)
    elif period == 'weeks':
        past_time = now_time - datetime.timedelta(weeks=amount)
    elif period == 'months':
        past_time = now_time - relativedelta(months=amount)
    else:
        raise ValueError("无效的时间段。使用 'days'、'weeks' 或 'months'")

    if start_of_day:
        past_time = past_time.replace(hour=0, minute=0, second=0, microsecond=0)

    return past_time


def timestamp_to_date(time_stamp, format_string="%Y-%m-%d %H:%M:%S", tz=None, is_str=True):
    """
    将 Unix 时间戳(10位)转换为时间字符串，默认为 2018-01-23 01:23:45 格式
    """
    d = datetime.datetime.fromtimestamp(float(time_stamp), tz)
    if is_str:
        date_str = d.strftime(format_string)
        return date_str
    return d


def date_to_timestamp(date, format_string="%Y-%m-%d %H:%M:%S"):
    """
    将时间字符串转换为 Unix 时间戳(10位)，时间字符串默认为 2018-01-23 01:23:45 格式
    """
    time_array = time.strptime(date, format_string)
    time_stamp = int(time.mktime(time_array))
    return time_stamp


def second_to_time_str(seconds):
    """
    秒转换为人类阅读的时间显示，用来显示已用时间
    例如：'1小时1分1.099秒'
    """
    time_str = ''
    hour = '%01d小时' % (seconds / 3600)
    minute = '%01d分' % ((seconds % 3600) / 60)

    if hour != '0小时':
        time_str += hour

    if minute != '0分':
        time_str += minute

    # seconds
    time_str += '%01d.%03d秒' % (seconds % 60, (seconds % 1) * 1000)

    return time_str


class Timer:
    """
    计时器，可以当装饰器或者用 with 来对代码计时

    # 例子：
        >>> import time
        >>> def papapa(t):
        >>>     time.sleep(t)
        >>> with Timer() as timer:
        >>>     papapa(1)
        运行时间 1.000 秒
        >>> @Timer.time_it
        >>> def papapa(t):
        >>>     time.sleep(t)
        >>> papapa(1)
        papapa 运行时间 1.001 秒
    """

    def __init__(self, name=None):
        self.start = time.time()

        # 我们添加一个自定义的计时名称
        if isinstance(name, str):
            self.name = name + ' '
        else:
            self.name = ''

        print(f'{get_now()} 开始运行 {self.name}', )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running_time()
        return exc_type is None

    @staticmethod
    def time_it(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            print(f'{get_now()} 开始运行 {func.__name__}', )
            result = func(*args, **kwargs)
            print(f'{get_now()} 结束运行 {func.__name__}，运行时间 {second_to_time_str(time.time() - start)}', )
            return result

        return wrapper

    def running_time(self):
        stop = time.time()
        cost = stop - self.start
        print(f'{get_now()} 结束运行 {self.name}，运行时间 {second_to_time_str(cost)}', )


def generate_table(headers, rows):
    """
    创建微信全机器人的表格

    | 姓名 | 调休假 | 应调 | 调节后 | 检查 |
    | :--- | :---: | :---: | :---: | ---: |
    | 张三 | 1 | 3 | 4 | OK |
    | 李四 | 2 | 4 | 2 | 调整后数据不对 |
    """
    # 创建表头行
    header_row = "| " + " | ".join(headers) + " |"

    # 创建对齐格式行
    alignment_list = []
    for i in range(len(headers)):
        if i == 0:
            alignment_list.append(":---")
        elif i == len(headers) - 1:
            alignment_list.append("---:")
        else:
            alignment_list.append(":---:")

    alignment_row = "| " + " | ".join(alignment_list) + " |"

    # 创建数据行
    data_rows = ["| " + " | ".join(row) + " |" for row in rows]

    # 合并表头和数据行
    table = "\n".join([header_row, alignment_row] + data_rows)
    return table
