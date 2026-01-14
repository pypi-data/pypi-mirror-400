"""
手机号码生成器。
支持生成不同国家和运营商的手机号码。
"""

import random
from typing import List, Optional

from ..base import BaseGenerator


class ChinesePhone(BaseGenerator):
    """
    中国手机号码生成器。
    支持三大运营商：移动、联通、电信。
    """

    # 中国移动号段（11位，1开头）
    # 134-139, 147, 150-152, 157-159, 178, 182-184, 187-188, 198
    MOBILE_PREFIXES = [
        "134",
        "135",
        "136",
        "137",
        "138",
        "139",
        "147",
        "150",
        "151",
        "152",
        "157",
        "158",
        "159",
        "178",
        "182",
        "183",
        "184",
        "187",
        "188",
        "198",
    ]

    # 中国联通号段
    # 130-132, 145, 155-156, 166, 171, 175-176, 185-186
    UNICOM_PREFIXES = [
        "130",
        "131",
        "132",
        "145",
        "155",
        "156",
        "166",
        "171",
        "175",
        "176",
        "185",
        "186",
    ]

    # 中国电信号段
    # 133, 149, 153, 173, 177, 180-181, 189, 199
    TELECOM_PREFIXES = [
        "133",
        "149",
        "153",
        "173",
        "177",
        "180",
        "181",
        "189",
        "199",
    ]

    # 所有号段
    ALL_PREFIXES = MOBILE_PREFIXES + UNICOM_PREFIXES + TELECOM_PREFIXES

    # 运营商分组（用于权重控制）
    OPERATOR_GROUPS = {
        "移动": MOBILE_PREFIXES,
        "联通": UNICOM_PREFIXES,
        "电信": TELECOM_PREFIXES,
    }

    # 运营商权重（移动用户最多）
    OPERATOR_WEIGHTS = {
        "移动": 10.0,
        "联通": 6.0,
        "电信": 4.0,
    }

    def __init__(self, operator: Optional[str] = None):
        """
        初始化中国手机号生成器。

        Args:
            operator: 运营商类型，'移动'/'联通'/'电信'，None 表示随机选择
        """
        self.operator = operator

    def _get_prefixes(self) -> List[str]:
        """获取可用的号段前缀"""
        if self.operator:
            if self.operator not in self.OPERATOR_GROUPS:
                raise ValueError(
                    f"Unknown operator: {self.operator}. Available operators: {list(self.OPERATOR_GROUPS.keys())}"
                )
            return self.OPERATOR_GROUPS[self.operator]
        else:
            # 根据权重随机选择运营商
            operators = list(self.OPERATOR_GROUPS.keys())
            weights = [self.OPERATOR_WEIGHTS[op] for op in operators]
            selected_operator = random.choices(operators, weights=weights, k=1)[0]
            return self.OPERATOR_GROUPS[selected_operator]

    def generate(self, operator: Optional[str] = None) -> str:
        """
        生成中国手机号码。

        Args:
            operator: 运营商类型，'移动'/'联通'/'电信'，None 表示随机选择（临时覆盖初始化时的设置）

        Returns:
            str: 生成的11位手机号码
        """
        original_operator = self.operator
        try:
            if operator is not None:
                self.operator = operator

            prefixes = self._get_prefixes()
            prefix = random.choice(prefixes)

            # 生成后8位数字（手机号共11位，前3位是号段）
            suffix = "".join([str(random.randint(0, 9)) for _ in range(8)])

            return prefix + suffix
        finally:
            self.operator = original_operator

    def get_operators(self) -> List[str]:
        """
        获取所有可用的运营商。

        Returns:
            List[str]: 运营商列表
        """
        return list(self.OPERATOR_GROUPS.keys())


class EnglishPhone(BaseGenerator):
    """
    美国手机号码生成器。
    生成美国格式的手机号码（10位数字，格式：XXX-XXX-XXXX）。
    """

    # 美国手机号区号（前3位，不能以0或1开头）
    AREA_CODES = [
        "201",
        "202",
        "203",
        "205",
        "206",
        "207",
        "208",
        "209",
        "210",
        "212",
        "213",
        "214",
        "215",
        "216",
        "217",
        "218",
        "219",
        "224",
        "225",
        "226",
        "228",
        "229",
        "231",
        "234",
        "239",
        "240",
        "242",
        "246",
        "248",
        "250",
        "251",
        "252",
        "253",
        "254",
        "256",
        "260",
        "262",
        "264",
        "267",
        "268",
        "269",
        "270",
        "272",
        "274",
        "276",
        "281",
        "283",
        "284",
        "289",
        "301",
        "302",
        "303",
        "304",
        "305",
        "307",
        "308",
        "309",
        "310",
        "312",
        "313",
        "314",
        "315",
        "316",
        "317",
        "318",
        "319",
        "320",
        "321",
        "323",
        "325",
        "326",
        "327",
        "330",
        "331",
        "332",
        "334",
        "336",
        "337",
        "339",
        "340",
        "341",
        "343",
        "345",
        "346",
        "347",
        "351",
        "352",
        "360",
        "361",
        "364",
        "365",
        "367",
        "368",
        "369",
        "380",
        "385",
        "386",
        "401",
        "402",
        "403",
        "404",
        "405",
        "406",
        "407",
        "408",
        "409",
        "410",
        "412",
        "413",
        "414",
        "415",
        "417",
        "418",
        "419",
        "423",
        "424",
        "425",
        "430",
        "431",
        "432",
        "434",
        "435",
        "437",
        "438",
        "440",
        "441",
        "442",
        "443",
        "445",
        "447",
        "448",
        "450",
        "456",
        "458",
        "463",
        "464",
        "468",
        "469",
        "470",
        "472",
        "473",
        "474",
        "475",
        "478",
        "479",
        "480",
        "484",
        "501",
        "502",
        "503",
        "504",
        "505",
        "507",
        "508",
        "509",
        "510",
        "512",
        "513",
        "515",
        "516",
        "517",
        "518",
        "520",
        "530",
        "531",
        "534",
        "539",
        "540",
        "541",
        "551",
        "559",
        "561",
        "562",
        "563",
        "564",
        "567",
        "570",
        "571",
        "572",
        "573",
        "574",
        "575",
        "580",
        "585",
        "586",
        "601",
        "602",
        "603",
        "605",
        "606",
        "607",
        "608",
        "609",
        "610",
        "612",
        "614",
        "615",
        "616",
        "617",
        "618",
        "619",
        "620",
        "623",
        "626",
        "628",
        "629",
        "630",
        "631",
        "636",
        "640",
        "641",
        "646",
        "647",
        "650",
        "651",
        "657",
        "660",
        "661",
        "662",
        "667",
        "669",
        "670",
        "671",
        "678",
        "679",
        "681",
        "682",
        "684",
        "689",
        "701",
        "702",
        "703",
        "704",
        "706",
        "707",
        "708",
        "712",
        "713",
        "714",
        "715",
        "716",
        "717",
        "718",
        "719",
        "720",
        "724",
        "725",
        "726",
        "727",
        "728",
        "729",
        "730",
        "731",
        "732",
        "734",
        "737",
        "740",
        "743",
        "747",
        "754",
        "757",
        "758",
        "760",
        "762",
        "763",
        "764",
        "765",
        "769",
        "770",
        "772",
        "773",
        "774",
        "775",
        "779",
        "781",
        "785",
        "786",
        "787",
        "801",
        "802",
        "803",
        "804",
        "805",
        "806",
        "807",
        "808",
        "810",
        "812",
        "813",
        "814",
        "815",
        "816",
        "817",
        "818",
        "828",
        "830",
        "831",
        "832",
        "843",
        "845",
        "847",
        "848",
        "850",
        "854",
        "856",
        "857",
        "858",
        "859",
        "860",
        "862",
        "863",
        "864",
        "865",
        "870",
        "872",
        "873",
        "878",
        "901",
        "903",
        "904",
        "906",
        "907",
        "908",
        "909",
        "910",
        "912",
        "913",
        "914",
        "915",
        "916",
        "917",
        "918",
        "919",
        "920",
        "925",
        "928",
        "929",
        "930",
        "931",
        "934",
        "936",
        "937",
        "938",
        "940",
        "941",
        "947",
        "949",
        "951",
        "952",
        "954",
        "956",
        "959",
        "970",
        "971",
        "972",
        "973",
        "978",
        "979",
        "980",
        "984",
        "985",
        "986",
        "989",
    ]

    def __init__(self, format_with_dash: bool = True):
        """
        初始化美国手机号生成器。

        Args:
            format_with_dash: 是否使用连字符格式化（XXX-XXX-XXXX），默认 True
        """
        self.format_with_dash = format_with_dash

    def generate(self, format_with_dash: Optional[bool] = None) -> str:
        """
        生成美国手机号码。

        Args:
            format_with_dash: 是否使用连字符格式化，None 表示使用初始化时的设置

        Returns:
            str: 生成的手机号码（格式：XXX-XXX-XXXX 或 XXXXXXXXXX）
        """
        use_dash = (
            format_with_dash if format_with_dash is not None else self.format_with_dash
        )

        # 选择区号
        area_code = random.choice(self.AREA_CODES)

        # 生成中间3位（不能以0或1开头）
        exchange = str(random.randint(200, 999))

        # 生成后4位
        number = "".join([str(random.randint(0, 9)) for _ in range(4)])

        if use_dash:
            return f"{area_code}-{exchange}-{number}"
        else:
            return f"{area_code}{exchange}{number}"


# 全局实例，用于快速生成
__chinese_phone = ChinesePhone()
__english_phone = EnglishPhone()


def fake_phone(country: Optional[str] = None) -> str:
    """
    快速生成随机手机号码。

    Args:
        country: 国家类型，'chinese' 或 'english'，None 表示随机选择

    Returns:
        str: 生成的手机号码
    """
    if country == "chinese":
        return __chinese_phone.generate()
    elif country == "english":
        return __english_phone.generate()
    else:
        # 随机选择
        return random.choice([__chinese_phone, __english_phone]).generate()
