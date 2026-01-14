from __future__ import annotations

import datetime
from pathlib import Path
from random import choices, choice
from typing import Any, Dict, Iterable, Optional, Tuple, Union

import numpy as np
import pandas as pd

from ._constants import sample_order
from ._paths import pet_home, make_output_xlsx, open_in_file_manager


def gen_iid(init: int = 220151000, number: int = 40) -> pd.Series:
    """
    Generate student IDs (学号) as an increasing integer sequence.
    """
    if not isinstance(init, int):
        init = 240151000
    return pd.Series(data=range(init, init + number))


def gen_name(xm: Optional[Union[Tuple[str, str], list]] = None, number: int = 40) -> pd.Series:
    """
    Generate Chinese names.

    xm can be:
      - None / "" / invalid: generate random 2~3 character names
      - [姓字符串, 名字符串]: draw from provided character pools
    """
    if xm in ("", None) or not isinstance(xm, (list, tuple)) or len(xm) < 2:
        x = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦',
             '尤', '许', '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏', '陶', '姜', '戚', '谢', '邹', '喻',
             '柏', '水', '窦', '章', '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦', '昌', '马', '苗', '凤',
             '花', '方', '俞', '任', '袁', '柳', '酆', '鲍', '史', '唐', '费', '廉', '岑', '薛', '雷', '贺', '倪', '汤',
             '滕', '殷', '罗', '毕', '郝', '邬', '安', '常', '乐', '于', '时', '傅', '皮', '卞', '齐', '康', '伍', '余',
             '元', '卜', '顾', '孟', '平', '黄', '和', '穆', '萧', '尹', '姚', '邵', '湛', '汪', '祁', '毛', '禹', '狄',
             '米', '贝', '明', '臧', '计', '伏', '成', '戴', '谈', '宋', '茅', '庞', '熊', '纪', '舒', '屈', '项', '祝',
             '董', '梁', '杜', '阮', '蓝', '闵', '席', '季', '麻', '强', '贾', '路', '娄', '危', '江', '童', '颜', '郭',
             '梅', '盛', '林', '刁', '钟', '徐', '邱', '骆', '高', '夏', '蔡', '田', '樊', '胡', '凌', '霍', '虞', '万',
             '支', '柯', '昝', '管', '卢', '莫', '经', '房', '裘', '缪', '干', '解', '应', '宗', '丁', '宣', '贲', '邓',
             '郁', '单', '杭', '洪', '包', '诸', '左', '石', '崔', '吉', '钮', '龚', '程', '嵇', '邢', '滑', '裴', '陆',
             '荣', '翁', '荀', '羊', '於', '惠', '甄', '曲', '家', '封', '芮', '羿', '储', '靳', '汲', '邴', '糜', '松',
             '井', '段', '富', '巫', '乌', '焦', '巴', '弓', '牧', '隗', '山', '谷', '车', '侯', '宓', '蓬', '全', '郗',
             '班', '仰', '秋', '仲', '伊', '宫', '宁', '仇', '栾', '暴', '甘', '钭', '历', '戎', '祖', '武', '符', '刘',
             '景', '詹', '束', '龙', '叶', '幸', '司', '韶', '郜', '黎', '蓟', '溥', '印', '宿', '白', '怀', '蒲', '邰',
             '从', '鄂', '索', '咸', '籍', '赖', '卓', '蔺', '屠', '蒙', '池', '乔', '阳', '郁', '胥', '能', '苍', '双',
             '闻', '莘', '党', '翟', '谭', '贡', '劳', '逄', '姬', '申', '扶', '堵', '冉', '宰', '郦', '雍', '郤', '璩',
             '桑', '桂', '濮', '牛', '寿', '通', '边', '扈', '燕', '冀', '姓', '浦', '尚', '农', '温', '别', '庄']
        m = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀英',
             '霞', '平', '刚', '桂英', '俊', '琳', '玲', '丹', '萍', '鹏', '华', '红', '玉兰', '飞', '桂兰', '英', '梅',
             '鑫', '辉', '玉梅', '浩', '建华', '慧', '建国', '亮', '建军', '艳丽', '莉', '文', '建', '婷婷', '玉珍', '晶',
             '敏', '冬梅', '文', '浩然', '思雨', '梓涵', '子轩', '宇航', '佳怡', '雨欣', '欣怡', '明轩', '子涵', '浩宇',
             '欣妍', '梓豪', '浩然', '浩翔', '雨婷', '梓轩', '诗涵', '雨菲', '浩东', '雨涵']
        xm = (''.join(x), ''.join(m))

    last = xm[0]
    first = xm[1]
    # Choose 1 char for surname, 1-2 chars for given name
    names = [choice(last) + ''.join(choices(first, k=choice([1, 2]))) for _ in range(number)]
    return pd.Series(names)


def gen_int_series(init: Union[int, Iterable[int], list] = 0, number: int = 40) -> pd.Series:
    if isinstance(init, int):
        low, high = init, init + 100
    elif isinstance(init, (list, tuple)) and len(init) >= 2:
        low, high = int(init[0]), int(init[1])
    else:
        low, high = 0, 100
    return pd.Series(np.random.randint(low, high + 1, size=number))


def gen_float_series(init: Union[float, Iterable[float], list] = 0.0, number: int = 40) -> pd.Series:
    if isinstance(init, (int, float)):
        low, high = float(init), float(init) + 100.0
    elif isinstance(init, (list, tuple)) and len(init) >= 2:
        low, high = float(init[0]), float(init[1])
    else:
        low, high = 0.0, 100.0
    vals = np.random.uniform(low, high, size=number)
    return pd.Series(np.round(vals, 2))


def gen_date_time_series(init: Any = None, number: int = 40) -> pd.Series:
    # init can be [start, end] strings; default last 365 days
    if isinstance(init, (list, tuple)) and len(init) >= 2:
        start, end = init[0], init[1]
        dt = pd.date_range(start=start, end=end, periods=number)
    else:
        end = pd.Timestamp.now()
        start = end - pd.Timedelta(days=365)
        dt = pd.date_range(start=start, end=end, periods=number)
    return pd.Series(dt)


def gen_date_series(init: Any = None, number: int = 40) -> pd.Series:
    return gen_date_time_series(init=init, number=number).dt.date


def gen_time_series(init: Any = None, number: int = 40) -> pd.Series:
    return gen_date_time_series(init=init, number=number).dt.time


def gen_category_series(init: Any = None, number: int = 40) -> pd.Series:
    if isinstance(init, (list, tuple)) and len(init) > 0:
        categories = list(init)
    elif isinstance(init, str) and init:
        categories = list(init)
    else:
        categories = ["A", "B", "C"]
    return pd.Series([choice(categories) for _ in range(number)])


func_dict = {
    "iid": gen_iid,
    "n": gen_name,
    "i": gen_int_series,
    "f": gen_float_series,
    "d": gen_date_series,
    "t": gen_time_series,
    "dt": gen_date_time_series,
    "c": gen_category_series,
}


def add_noise(df: pd.DataFrame, noise: float = 0.1, repeat: int = 2) -> pd.DataFrame:
    """
    Add missing values and duplicates to simulate dirty data.
    noise: probability of setting a cell to None.
    repeat: number of times to duplicate the dataset before shuffling.
    """
    if repeat and repeat > 1:
        df = pd.concat([df] * int(repeat), ignore_index=True)
        # Shuffle back to roughly original size distribution
        df = df.sample(frac=1 / int(repeat)).reset_index(drop=True)

    if noise and noise > 0:
        # Apply noise per-column for stability.
        n_rows = len(df)
        for col in df.columns:
            mask = np.random.rand(n_rows) < float(noise)
            df.loc[mask, col] = None
    return df


def generator(order: Dict[str, Any] = sample_order,
              number: int = 40,
              dst: Optional[Union[str, Path]] = None,
              noise: float = 0.0,
              repeat: int = 1) -> pd.DataFrame:
    """
    Generate a dataset according to an 'order' dict.

    order keys use the pattern: "列名.类型码"
      - iid: student id series
      - n: name series
      - i: int series
      - f: float series
      - dt/d/t: datetime/date/time
      - c: category series
    """
    df = pd.DataFrame()
    for k, v in order.items():
        col_name, code = k.split(".")
        func = func_dict.get(code)
        if func is None:
            raise ValueError(f"Unknown generator code: {code!r} (column {k!r})")
        df[col_name] = func(v, number=number)

    if noise and noise > 0.0:
        df = add_noise(df, noise=float(noise), repeat=int(repeat) if repeat else 1)

    if dst is not None:
        dst_path = Path(dst)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(dst_path, index=False)
        print(f"Dataset is generated in {dst_path} !!!")

    return df


def show_order_sample() -> None:
    from pprint import pprint
    pprint(sample_order)


def gen_sample_series(number: int = 40, dst: Optional[Union[str, Path]] = None, noise: float = 0.0, repeat: int = 1) -> pd.Series:
    """
    Generate a simple score Series indexed by name.

    Supports textbook parameters:
      - number: number of rows
      - dst: optional output Excel filename
      - noise: missing value ratio
      - repeat: duplicate-and-shuffle factor
    """
    order = {"姓名.n": "", "成绩.i": ""}
    if dst is None:
        dst = make_output_xlsx("generated_sample_series")
    df = generator(order, number=number, dst=dst, noise=noise, repeat=repeat)

    if repeat and repeat > 1:
        df = pd.concat([df] * int(repeat))
        df = df.sample(frac=1 / int(repeat)).reset_index(drop=True)

    df = df.set_index("姓名")
    # Set some scores to None as noise
    if noise and noise > 0:
        n = len(df)
        mask = np.random.rand(n) < float(noise)
        df.loc[mask, "成绩"] = None

    return df["成绩"]


def gen_sample_dataframe(sample_order: Dict[str, Any] = sample_order,
                         number: int = 40,
                         dst: Optional[Union[str, Path]] = None,
                         noise: float = 0.0,
                         repeat: int = 1) -> pd.DataFrame:
    """
    Generate a DataFrame according to `sample_order`.
    """
    print("*" * max(10, int(number)))
    from pprint import pprint
    print("订单格式：")
    pprint(sample_order)
    print("*" * max(10, int(number)))

    if dst is None:
        dst = make_output_xlsx("generated_sample_dataframe")
    df = generator(order=sample_order, number=number, dst=dst, noise=noise, repeat=repeat)
    # Convenience: open working folder
    open_in_file_manager(pet_home)
    return df


def gen_sample_dataframe_12(number: int = 40, dst: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """
    Chapter 12 dedicated DataFrame generator (stable column structure used in the textbook).
    """
    order = {
        '考号.i': [151000, 789000],
        '姓名.n': '',
        '性别.c': ['男', '女'],
        '报名时间.dt': ['1/1/2023 00:00', '12/31/2023 23:59'],
        '年龄.i': [18, 28],
        '政治面貌.c': ['党员', '团员', '群众', '其它'],
        '专业.c': ['物联网工程', '网络工程', '计算机科学与技术', '通信工程', '软件工程', '信息安全'],
        '学校.c': ['北京大学', '复旦大学', '上海交通大学', '华东理工大学', '中山大学', '上海师范大学', '南京大学', '南京师范大学', '同济大学'],
        '政治成绩.i': [40, 80],
        '英语成绩.i': [40, 80],
        '英语类别.c': ['英语一', '英语二'],
        '数学成绩.i': [40, 80],
        '专业课一.i': [40, 80],
        '专业课二.i': [40, 80],
        '总分.i': [320, 450],
        '是否录取.c': ['否', '是'],
    }
    if dst is None:
        dst = make_output_xlsx("generated_sample_dataframe_12")
    df = generator(order=order, number=number, dst=dst)
    return df


def gen_zmt_series(start: str = '1/1/2024', end: str = '12/31/2025', freq: str = 'M', data_range: Tuple[float, float] = (1000, 80000)) -> pd.Series:
    """
    Generate a time series representing self-media income.
    """
    date_rng = pd.date_range(start=start, end=end, freq=freq)
    data = np.random.uniform(*data_range, len(date_rng))
    data = np.round(data, decimals=2)
    return pd.Series(data, index=date_rng, name='净收入')
