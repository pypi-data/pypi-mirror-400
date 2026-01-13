# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  playwright-helper
# FileName:     template_data.py
# Description:  随机模块数据模块
# Author:       ASUS
# CreateDate:   2025/12/19
# Copyright ©2011-2025. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import re
import random
import string
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


class CountryCode(Enum):
    """国家代码枚举"""
    US = "美国"  # 美国
    CA = "加拿大"  # 加拿大
    GB = "英国"  # 英国
    DE = "德国"  # 德国
    FR = "法国"  # 法国
    IT = "意大利"  # 意大利
    ES = "西班牙"  # 西班牙
    NL = "荷兰"  # 荷兰
    BE = "比利时"  # 比利时
    CH = "瑞士"  # 瑞士
    SE = "瑞典"  # 瑞典
    NO = "挪威"  # 挪威
    DK = "丹麦"  # 丹麦
    FI = "芬兰"  # 芬兰
    PL = "波兰"  # 波兰
    RU = "俄罗斯"  # 俄罗斯
    CN = "中国"  # 中国
    JP = "日本"  # 日本
    KR = "韩国"  # 韩国
    IN = "印度"  # 印度
    AU = "澳大利亚"  # 澳大利亚
    NZ = "新西兰"  # 新西兰
    BR = "巴西"  # 巴西
    MX = "墨西哥"  # 墨西哥
    AR = "阿根廷"  # 阿根廷
    ZA = "南非"  # 南非
    AE = "阿联酋"  # 阿联酋
    SA = "沙特"  # 沙特
    IL = "以色列"  # 以色列
    TR = "土耳其"  # 土耳其
    EG = "埃及"  # 埃及
    SG = "新加坡"  # 新加坡
    MY = "马来西亚"  # 马来西亚
    TH = "泰国"  # 泰国
    ID = "印度尼西亚"  # 印度尼西亚
    PH = "菲律宾"  # 菲律宾
    VN = "越南"  # 越南


@dataclass
class PostalCodeInfo:
    """邮政编码信息"""
    country_code: str
    country_name: str
    format_pattern: str
    regex: str
    example: str
    description: str


@dataclass
class MobileNumberInfo:
    """手机号码信息"""
    country_code: str
    country_name: str
    dialing_code: str
    number_format: str
    number_length: int
    mobile_prefixes: List[str]
    example: str
    description: str


class PostalCodeGenerator:
    """全球邮政编码生成器"""

    def __init__(self):
        # 定义各国邮政编码格式
        self.postal_code_formats: Dict[str, PostalCodeInfo] = {
            # 北美
            'US': PostalCodeInfo(
                country_code='US',
                country_name='美国',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='90210',
                description='5位数字'
            ),
            'CA': PostalCodeInfo(
                country_code='CA',
                country_name='加拿大',
                format_pattern='ANA NAN',
                regex=r'^[A-Z]\d[A-Z] \d[A-Z]\d$',
                example='M5V 2T6',
                description='字母数字交替，中间空格'
            ),

            # 欧洲
            'GB': PostalCodeInfo(
                country_code='GB',
                country_name='英国',
                format_pattern='AAN NAA/AN NAA/AANN NAA/AANA NAA',
                regex=r'^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$',
                example='SW1A 1AA',
                description='复杂格式，多种变体'
            ),
            'DE': PostalCodeInfo(
                country_code='DE',
                country_name='德国',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='10115',
                description='5位数字'
            ),
            'FR': PostalCodeInfo(
                country_code='FR',
                country_name='法国',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='75001',
                description='5位数字'
            ),
            'IT': PostalCodeInfo(
                country_code='IT',
                country_name='意大利',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='00100',
                description='5位数字'
            ),
            'ES': PostalCodeInfo(
                country_code='ES',
                country_name='西班牙',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='28001',
                description='5位数字'
            ),
            'NL': PostalCodeInfo(
                country_code='NL',
                country_name='荷兰',
                format_pattern='NNNN AA',
                regex=r'^\d{4} ?[A-Z]{2}$',
                example='1011 AB',
                description='4位数字+2字母，可选空格'
            ),
            'BE': PostalCodeInfo(
                country_code='BE',
                country_name='比利时',
                format_pattern='NNNN',
                regex=r'^\d{4}$',
                example='1000',
                description='4位数字'
            ),
            'CH': PostalCodeInfo(
                country_code='CH',
                country_name='瑞士',
                format_pattern='NNNN',
                regex=r'^\d{4}$',
                example='8001',
                description='4位数字'
            ),
            'SE': PostalCodeInfo(
                country_code='SE',
                country_name='瑞典',
                format_pattern='NNN NN',
                regex=r'^\d{3} ?\d{2}$',
                example='113 30',
                description='3位数字+2位数字，中间空格'
            ),
            'NO': PostalCodeInfo(
                country_code='NO',
                country_name='挪威',
                format_pattern='NNNN',
                regex=r'^\d{4}$',
                example='0150',
                description='4位数字'
            ),
            'DK': PostalCodeInfo(
                country_code='DK',
                country_name='丹麦',
                format_pattern='NNNN',
                regex=r'^\d{4}$',
                example='1050',
                description='4位数字'
            ),
            'FI': PostalCodeInfo(
                country_code='FI',
                country_name='芬兰',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='00100',
                description='5位数字'
            ),
            'PL': PostalCodeInfo(
                country_code='PL',
                country_name='波兰',
                format_pattern='NN-NNN',
                regex=r'^\d{2}-\d{3}$',
                example='00-001',
                description='2位数字-3位数字'
            ),
            'RU': PostalCodeInfo(
                country_code='RU',
                country_name='俄罗斯',
                format_pattern='NNNNNN',
                regex=r'^\d{6}$',
                example='101000',
                description='6位数字'
            ),

            # 亚洲
            'CN': PostalCodeInfo(
                country_code='CN',
                country_name='中国',
                format_pattern='NNNNNN',
                regex=r'^\d{6}$',
                example='100000',
                description='6位数字'
            ),
            'JP': PostalCodeInfo(
                country_code='JP',
                country_name='日本',
                format_pattern='NNN-NNNN',
                regex=r'^\d{3}-\d{4}$',
                example='100-0001',
                description='3位数字-4位数字'
            ),
            'KR': PostalCodeInfo(
                country_code='KR',
                country_name='韩国',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='03151',
                description='5位数字'
            ),
            'IN': PostalCodeInfo(
                country_code='IN',
                country_name='印度',
                format_pattern='NNNNNN',
                regex=r'^\d{6}$',
                example='110001',
                description='6位数字'
            ),
            'SG': PostalCodeInfo(
                country_code='SG',
                country_name='新加坡',
                format_pattern='NNNNNN',
                regex=r'^\d{6}$',
                example='408600',
                description='6位数字'
            ),
            'MY': PostalCodeInfo(
                country_code='MY',
                country_name='马来西亚',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='50000',
                description='5位数字'
            ),
            'TH': PostalCodeInfo(
                country_code='TH',
                country_name='泰国',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='10100',
                description='5位数字'
            ),
            'ID': PostalCodeInfo(
                country_code='ID',
                country_name='印度尼西亚',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='10110',
                description='5位数字'
            ),
            'PH': PostalCodeInfo(
                country_code='PH',
                country_name='菲律宾',
                format_pattern='NNNN',
                regex=r'^\d{4}$',
                example='1000',
                description='4位数字'
            ),
            'VN': PostalCodeInfo(
                country_code='VN',
                country_name='越南',
                format_pattern='NNNNNN',
                regex=r'^\d{6}$',
                example='100000',
                description='6位数字'
            ),

            # 大洋洲
            'AU': PostalCodeInfo(
                country_code='AU',
                country_name='澳大利亚',
                format_pattern='NNNN',
                regex=r'^\d{4}$',
                example='2000',
                description='4位数字'
            ),
            'NZ': PostalCodeInfo(
                country_code='NZ',
                country_name='新西兰',
                format_pattern='NNNN',
                regex=r'^\d{4}$',
                example='1010',
                description='4位数字'
            ),

            # 南美洲
            'BR': PostalCodeInfo(
                country_code='BR',
                country_name='巴西',
                format_pattern='NNNNN-NNN',
                regex=r'^\d{5}-\d{3}$',
                example='01001-000',
                description='5位数字-3位数字'
            ),
            'AR': PostalCodeInfo(
                country_code='AR',
                country_name='阿根廷',
                format_pattern='ANNNNAAA',
                regex=r'^[A-Z]\d{4}[A-Z]{3}$',
                example='C1000AAA',
                description='字母+4位数字+3字母'
            ),
            'MX': PostalCodeInfo(
                country_code='MX',
                country_name='墨西哥',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='01000',
                description='5位数字'
            ),

            # 非洲和中东
            'ZA': PostalCodeInfo(
                country_code='ZA',
                country_name='南非',
                format_pattern='NNNN',
                regex=r'^\d{4}$',
                example='0001',
                description='4位数字'
            ),
            'AE': PostalCodeInfo(
                country_code='AE',
                country_name='阿联酋',
                format_pattern='',
                regex=r'.*',
                example='',
                description='无邮政编码系统'
            ),
            'SA': PostalCodeInfo(
                country_code='SA',
                country_name='沙特',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='11564',
                description='5位数字'
            ),
            'IL': PostalCodeInfo(
                country_code='IL',
                country_name='以色列',
                format_pattern='NNNNNNN',
                regex=r'^\d{7}$',
                example='9614303',
                description='7位数字'
            ),
            'TR': PostalCodeInfo(
                country_code='TR',
                country_name='土耳其',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='06100',
                description='5位数字'
            ),
            'EG': PostalCodeInfo(
                country_code='EG',
                country_name='埃及',
                format_pattern='NNNNN',
                regex=r'^\d{5}$',
                example='11511',
                description='5位数字'
            ),
        }

        # 国家代码映射
        self.country_names = {
            code: info.country_name for code, info in self.postal_code_formats.items()
        }

        # 特殊生成逻辑
        self.special_generators = {
            'GB': self._generate_uk_postcode,
            'CA': self._generate_ca_postcode,
            'NL': self._generate_nl_postcode,
            'AR': self._generate_ar_postcode,
        }

    @classmethod
    def _generate_uk_postcode(cls) -> str:
        """生成英国邮政编码（复杂格式）"""
        # 英国邮编有多种格式
        formats = [
            # 格式: AN NAA
            lambda: f"{random.choice('ABCDEFGHIJKLMNOPRSTUWYZ')}"
                    f"{random.choice('ABCDEFGHKLMNOPQRSTUVWXY')}"
                    f"{random.randint(1, 9)} "
                    f"{random.choice('ABCDEFGHJKSTUW')}"
                    f"{random.choice('ABCDEFGHJKMNPRSTUVWXY')}"
                    f"{random.choice('ABCDEFGHJKMNPRSTUVWXY')}",
            # 格式: ANN NAA
            lambda: f"{random.choice('ABCDEFGHIJKLMNOPRSTUWYZ')}"
                    f"{random.choice('ABCDEFGHKLMNOPQRSTUVWXY')}"
                    f"{random.randint(10, 99)} "
                    f"{random.choice('ABCDEFGHJKSTUW')}"
                    f"{random.choice('ABCDEFGHJKMNPRSTUVWXY')}"
                    f"{random.choice('ABCDEFGHJKMNPRSTUVWXY')}",
            # 格式: AAN NAA
            lambda: f"{random.choice('ABCDEFGHIJKLMNOPRSTUWYZ')}"
                    f"{random.choice('ABCDEFGHJKLMNOPQRSTUVWXY')}"
                    f"{random.choice('0123456789ABCDEFGHJKLMNOPRSTUVWXY')} "
                    f"{random.randint(0, 9)}"
                    f"{random.choice('ABCDEFGHJKMNPRSTUVWXY')}"
                    f"{random.choice('ABCDEFGHJKMNPRSTUVWXY')}",
        ]
        return random.choice(formats)()

    @classmethod
    def _generate_ca_postcode(cls) -> str:
        """生成加拿大邮政编码"""
        # 格式: A1A 1A1
        first_char = random.choice('ABCEGHJKLMNPRSTVXY')
        first_digit = random.randint(0, 9)
        second_char = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        space = ' '
        third_digit = random.randint(0, 9)
        fourth_char = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        fifth_digit = random.randint(0, 9)
        return f"{first_char}{first_digit}{second_char}{space}{third_digit}{fourth_char}{fifth_digit}"

    @classmethod
    def _generate_nl_postcode(cls) -> str:
        """生成荷兰邮政编码"""
        # 格式: 1234 AB
        numbers = f"{random.randint(1000, 9999)}"
        letters = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        # 随机决定是否加空格
        if random.random() > 0.5:
            return f"{numbers} {letters}"
        return f"{numbers}{letters}"

    def _generate_ar_postcode(self) -> str:
        """生成阿根廷邮政编码"""
        # 格式: A1234BCD
        first_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        numbers = f"{random.randint(1000, 9999)}"
        last_letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
        return f"{first_letter}{numbers}{last_letters}"

    def generate_postal_code(self,
                             country_code: str = 'US',
                             validate: bool = True) -> str:
        """生成指定国家的邮政编码"""
        country_code = country_code.upper()

        if country_code not in self.postal_code_formats:
            raise ValueError(f"不支持的国家代码: {country_code}")

        info = self.postal_code_formats[country_code]

        # 使用特殊生成器
        if country_code in self.special_generators:
            postal_code = self.special_generators[country_code]()
        else:
            # 通用生成逻辑
            postal_code = self._generate_by_format(info.format_pattern)

        # 验证格式
        if validate and not self.validate_postal_code(postal_code, country_code):
            # 如果验证失败，递归生成直到有效
            return self.generate_postal_code(country_code, validate)

        return postal_code

    def _generate_by_format(self, format_pattern: str) -> str:
        """根据格式模式生成邮政编码"""
        result = []
        for char in format_pattern:
            if char == 'N':  # 数字
                result.append(str(random.randint(0, 9)))
            elif char == 'A':  # 大写字母
                result.append(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
            elif char == 'a':  # 小写字母
                result.append(random.choice('abcdefghijklmnopqrstuvwxyz'))
            elif char == ' ':  # 空格
                result.append(' ')
            elif char == '-':  # 连字符
                result.append('-')
            else:  # 其他字符原样保留
                result.append(char)
        return ''.join(result)

    def validate_postal_code(self, postal_code: str, country_code: str) -> bool:
        """验证邮政编码格式"""
        country_code = country_code.upper()

        if country_code not in self.postal_code_formats:
            return False

        # 阿联酋没有邮政编码
        if country_code == 'AE':
            return postal_code == ''

        info = self.postal_code_formats[country_code]

        # 特殊验证规则
        if country_code == 'CA':
            # 加拿大邮政编码特殊验证
            pattern = r'^[ABCEGHJKLMNPRSTVXY]\d[ABCEGHJKLMNPRSTVWXYZ] \d[ABCEGHJKLMNPRSTVWXYZ]\d$'
            return bool(re.match(pattern, postal_code.upper()))

        elif country_code == 'GB':
            # 英国邮政编码特殊验证
            pattern = r'^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$'
            return bool(re.match(pattern, postal_code.upper()))

        elif country_code == 'NL':
            # 荷兰邮政编码特殊验证
            pattern = r'^\d{4} ?[A-Z]{2}$'
            if not re.match(pattern, postal_code.upper()):
                return False
            # 确保第一个数字不是0
            if postal_code[0] == '0':
                return False
            return True

        elif country_code == 'AR':
            # 阿根廷邮政编码特殊验证
            pattern = r'^[A-Z]\d{4}[A-Z]{3}$'
            return bool(re.match(pattern, postal_code.upper()))

        else:
            # 通用正则验证
            return bool(re.match(info.regex, postal_code))

    def get_country_info(self, country_code: str) -> Optional[PostalCodeInfo]:
        """获取国家邮政编码信息"""
        return self.postal_code_formats.get(country_code.upper())

    def generate_multiple(self,
                          country_codes: List[str] = None,
                          count: int = 10) -> List[Dict]:
        """生成多个国家的邮政编码"""
        if country_codes is None:
            country_codes = list(self.postal_code_formats.keys())

        results = []
        for _ in range(count):
            country = random.choice(country_codes)
            postal_code = self.generate_postal_code(country)
            info = self.get_country_info(country)

            results.append({
                'country_code': country,
                'country_name': info.country_name if info else 'Unknown',
                'postal_code': postal_code,
                'format': info.format_pattern if info else '',
                'valid': self.validate_postal_code(postal_code, country)
            })

        return results

    def generate_for_all_countries(self) -> List[Dict]:
        """为所有支持的国家生成邮政编码"""
        results = []
        for country_code, info in self.postal_code_formats.items():
            try:
                postal_code = self.generate_postal_code(country_code)
                results.append({
                    'country_code': country_code,
                    'country_name': info.country_name,
                    'postal_code': postal_code,
                    'format': info.format_pattern,
                    'example': info.example,
                    'description': info.description
                })
            except Exception as e:
                results.append({
                    'country_code': country_code,
                    'country_name': info.country_name,
                    'postal_code': f'Error: {str(e)}',
                    'format': info.format_pattern,
                    'example': info.example,
                    'description': info.description
                })

        return results

    def format_postal_code(self, postal_code: str, country_code: str) -> str:
        """格式化邮政编码（统一格式）"""
        country_code = country_code.upper()

        if not self.validate_postal_code(postal_code, country_code):
            return postal_code

        # 清理输入
        postal_code = postal_code.upper().strip()

        # 特殊国家格式化
        if country_code == 'CA':
            # 加拿大: 确保中间有空格
            if len(postal_code) == 6 and ' ' not in postal_code:
                return f"{postal_code[:3]} {postal_code[3:]}"

        elif country_code == 'NL':
            # 荷兰: 确保4位数字+2字母，中间空格
            postal_code = postal_code.replace(' ', '')
            if len(postal_code) == 6:
                return f"{postal_code[:4]} {postal_code[4:]}"

        elif country_code == 'SE':
            # 瑞典: 确保3位数字+2位数字，中间空格
            postal_code = postal_code.replace(' ', '')
            if len(postal_code) == 5:
                return f"{postal_code[:3]} {postal_code[3:]}"

        elif country_code == 'PL':
            # 波兰: 确保2位数字-3位数字
            postal_code = postal_code.replace('-', '')
            if len(postal_code) == 5:
                return f"{postal_code[:2]}-{postal_code[2:]}"

        elif country_code == 'JP':
            # 日本: 确保3位数字-4位数字
            postal_code = postal_code.replace('-', '')
            if len(postal_code) == 7:
                return f"{postal_code[:3]}-{postal_code[3:]}"

        elif country_code == 'BR':
            # 巴西: 确保5位数字-3位数字
            postal_code = postal_code.replace('-', '')
            if len(postal_code) == 8:
                return f"{postal_code[:5]}-{postal_code[5:]}"

        return postal_code

    def get_postal_code_info(self, postal_code: str) -> Optional[Dict]:
        """根据邮政编码猜测国家信息"""
        # 清理输入
        code = postal_code.strip().upper()

        # 根据特征猜测国家
        for country_code, info in self.postal_code_formats.items():
            if self.validate_postal_code(code, country_code):
                return {
                    'likely_country_code': country_code,
                    'likely_country_name': info.country_name,
                    'format': info.format_pattern,
                    'description': info.description
                }

        return None


def generate_chinese_passport():
    """生成中国护照编号（电子普通护照），E+8位数字（新版电子护照）"""
    # 格式：E + 8位数字
    number = ''.join(random.choices(string.digits, k=8))
    return f"E{number}"


# 示例
def generate_us_passport():
    """生成美国护照编号，美国护照：9位数字"""
    # 格式：9位数字
    return ''.join(random.choices(string.digits, k=9))


def generate_eu_passport():
    """生成欧盟护照编号（以德国为例），2位字母代码 + 7位数字"""
    country_codes = {
        'DE': '德国', 'FR': '法国', 'IT': '意大利',
        'ES': '西班牙', 'NL': '荷兰', 'BE': '比利时'
    }
    country = random.choice(list(country_codes.keys()))
    number = ''.join(random.choices(string.digits, k=7))
    return f"{country}{number}"


class PassportGenerator:
    """护照编号生成器"""

    def __init__(self):
        self.formats = {
            'CN': r'^E\d{8}$',  # 中国
            'US': r'^\d{9}$',  # 美国
            'UK': r'^\d{9}$',  # 英国
            'DE': r'^DE\d{7}$',  # 德国
            'FR': r'^FR\d{7}$',  # 法国
            'AU': r'^[A-Z]\d{7}$',  # 澳大利亚
            'CA': r'^[A-Z]{2}\d{6}$',  # 加拿大
            'JP': r'^[A-Z]{2}\d{7}$',  # 日本
            'KR': r'^[MS]\d{8}$',  # 韩国 (M: 多用途, S: 官方)
            'IN': r'^[A-Z]\d{7}$',  # 印度
        }

    def generate(self, country_code='CN', validate=True):
        """生成指定国家的护照编号"""
        if country_code == 'CN':
            # 中国护照: E + 8位数字
            number = ''.join(random.choices(string.digits, k=8))
            passport = f"E{number}"

        elif country_code == 'US':
            # 美国: 9位数字
            passport = ''.join(random.choices(string.digits, k=9))

        elif country_code == 'UK':
            # 英国: 9位数字
            passport = ''.join(random.choices(string.digits, k=9))

        elif country_code in ['DE', 'FR']:
            # 德国/法国: 国家代码 + 7位数字
            number = ''.join(random.choices(string.digits, k=7))
            passport = f"{country_code}{number}"

        elif country_code == 'AU':
            # 澳大利亚: 字母 + 7位数字
            letter = random.choice(string.ascii_uppercase)
            number = ''.join(random.choices(string.digits, k=7))
            passport = f"{letter}{number}"

        elif country_code == 'CA':
            # 加拿大: 2位字母 + 6位数字
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            number = ''.join(random.choices(string.digits, k=6))
            passport = f"{letters}{number}"

        elif country_code == 'JP':
            # 日本: 2位字母 + 7位数字
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            number = ''.join(random.choices(string.digits, k=7))
            passport = f"{letters}{number}"

        elif country_code == 'KR':
            # 韩国: M/S + 8位数字
            prefix = random.choice(['M', 'S'])  # M: 多用途, S: 官方
            number = ''.join(random.choices(string.digits, k=8))
            passport = f"{prefix}{number}"

        elif country_code == 'IN':
            # 印度: 字母 + 7位数字
            letter = random.choice(string.ascii_uppercase)
            number = ''.join(random.choices(string.digits, k=7))
            passport = f"{letter}{number}"

        else:
            # 默认: 2位字母 + 7位数字
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            number = ''.join(random.choices(string.digits, k=7))
            passport = f"{letters}{number}"

        # 验证格式
        if validate and not self.validate(passport, country_code):
            return self.generate(country_code, validate)

        return passport

    def validate(self, passport_number, country_code='CN'):
        """验证护照编号格式"""
        pattern = self.formats.get(country_code, r'^[A-Z0-9]{6,10}$')
        return bool(re.match(pattern, passport_number))

    def generate_batch(self, country_code='CN', count=10):
        """批量生成护照编号（确保不重复）"""
        passports = set()
        while len(passports) < count:
            passport = self.generate(country_code)
            passports.add(passport)
        return list(passports)


class EmailGenerator:
    """随机电子邮箱生成器"""

    def __init__(self):
        # 世界主流邮箱域名分类
        self.domains = {
            # 国际通用
            'global': [
                'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
                'icloud.com', 'aol.com', 'protonmail.com', 'zoho.com',
                'mail.com', 'yandex.com', 'gmx.com'
            ],
            # 美国
            'us': [
                'comcast.net', 'verizon.net', 'att.net', 'sbcglobal.net',
                'cox.net', 'charter.net', 'earthlink.net', 'bellsouth.net'
            ],
            # 英国
            'uk': [
                'btinternet.com', 'blueyonder.co.uk', 'ntlworld.com',
                'virginmedia.com', 'talktalk.net', 'sky.com'
            ],
            # 德国
            'de': [
                'web.de', 't-online.de', 'gmx.de', 'freenet.de',
                'arcor.de', '1und1.de'
            ],
            # 法国
            'fr': [
                'orange.fr', 'free.fr', 'sfr.fr', 'laposte.net',
                'wanadoo.fr', 'neuf.fr'
            ],
            # 中国
            'cn': [
                'qq.com', '163.com', '126.com', 'sina.com',
                'sohu.com', 'aliyun.com', 'yeah.net', 'foxmail.com'
            ],
            # 日本
            'jp': [
                'docomo.ne.jp', 'ezweb.ne.jp', 'softbank.ne.jp',
                'i.softbank.jp', 'au.com', 'yahoo.co.jp'
            ],
            # 韩国
            'kr': [
                'naver.com', 'daum.net', 'hanmail.net', 'nate.com',
                'kakao.com'
            ],
            # 俄罗斯
            'ru': [
                'mail.ru', 'bk.ru', 'list.ru', 'inbox.ru', 'yandex.ru',
                'rambler.ru'
            ],
            # 印度
            'in': [
                'rediffmail.com', 'indiatimes.com', 'vsnl.com',
                'airtelmail.com', 'jio.com'
            ],
            # 巴西
            'br': [
                'uol.com.br', 'bol.com.br', 'ig.com.br', 'terra.com.br',
                'globo.com', 'r7.com'
            ],
            # 企业域名
            'corporate': [
                'company.com', 'business.com', 'corp.com', 'enterprise.com',
                'firm.com', 'office.com'
            ],
            # 教育机构
            'edu': [
                'edu.com', 'university.edu', 'college.edu', 'school.edu',
                'campus.edu'
            ],
            # 国家顶级域名
            'country_tld': [
                'co.uk',  # 英国
                'de.com',  # 德国
                'fr.com',  # 法国
                'jp.net',  # 日本
                'cn.com',  # 中国
                'ru.com',  # 俄罗斯
                'in.com',  # 印度
                'com.au',  # 澳大利亚
                'co.nz',  # 新西兰
                'co.za',  # 南非
                'com.sg',  # 新加坡
                'com.my',  # 马来西亚
                'com.ph',  # 菲律宾
                'co.id',  # 印度尼西亚
                'com.br',  # 巴西
                'com.mx',  # 墨西哥
                'com.ar',  # 阿根廷
                'com.tr',  # 土耳其
                'co.il',  # 以色列
                'ae.org',  # 阿联酋
                'sa.com'  # 沙特
            ]
        }

        # 常见用户名格式
        self.name_formats = [
            'first.last', 'first_last', 'firstlast',
            'flast', 'firstl', 'f.last', 'first',
            'last.first', 'last_first', 'lastfirst',
            'first.middle.last', 'fmlast', 'first_mlast'
        ]

        # 全球常见名字（用于生成更真实的邮箱）
        self.common_first_names = [
            'alex', 'michael', 'james', 'john', 'david', 'robert', 'william',
            'maria', 'anna', 'sophia', 'emily', 'olivia', 'ava', 'isabella',
            'wei', 'jing', 'ming', 'li', 'zhang', 'wang', 'liu', 'chen',
            'taro', 'hanako', 'yuki', 'sakura', 'kenji', 'hiroshi',
            'raj', 'priya', 'amit', 'anita', 'vikram', 'sanjay',
            'dmitri', 'alexei', 'ivan', 'svetlana', 'natalia', 'olga',
            'juan', 'carlos', 'maria', 'jose', 'luis', 'ana', 'sofia',
            'mohamed', 'ali', 'fatima', 'ahmed', 'hassan', 'amin'
        ]

        self.common_last_names = [
            'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia',
            'miller', 'davis', 'rodriguez', 'martinez', 'hernandez',
            'lopez', 'gonzalez', 'wilson', 'anderson', 'thomas', 'taylor',
            'lee', 'moore', 'jackson', 'martin', 'white', 'harris',
            'thompson', 'wang', 'li', 'zhang', 'chen', 'liu', 'yang',
            'huang', 'zhao', 'zhou', 'wu', 'xu', 'sun', 'ma', 'zhu',
            'hu', 'guo', 'lin', 'he', 'gao', 'sato', 'suzuki', 'takahashi',
            'tanaka', 'watanabe', 'ito', 'yamamoto', 'nakamura',
            'kobayashi', 'kato', 'yoshida', 'yamada', 'sasaki',
            'singh', 'kumar', 'devi', 'patel', 'sharma', 'jha',
            'ivanov', 'petrov', 'sidorov', 'smirnov', 'popov',
            'garcia', 'rodriguez', 'martinez', 'hernandez', 'lopez',
            'gonzalez', 'perez', 'sanchez', 'ramirez', 'torres'
        ]

        # 特殊字符处理
        self.special_chars = ['.', '_', '-']

    def generate_username(self,
                          use_real_name: bool = True,
                          min_length: int = 5,
                          max_length: int = 15,
                          include_numbers: bool = True,
                          include_special: bool = True) -> str:
        """生成随机用户名"""

        if use_real_name and random.random() > 0.3:  # 70%概率使用真实姓名格式
            first = random.choice(self.common_first_names)
            last = random.choice(self.common_last_names)
            format_pattern = random.choice(self.name_formats)

            if format_pattern == 'first.last':
                username = f"{first}.{last}"
            elif format_pattern == 'first_last':
                username = f"{first}_{last}"
            elif format_pattern == 'firstlast':
                username = f"{first}{last}"
            elif format_pattern == 'flast':
                username = f"{first[0]}{last}"
            elif format_pattern == 'firstl':
                username = f"{first}{last[0]}"
            elif format_pattern == 'f.last':
                username = f"{first[0]}.{last}"
            elif format_pattern == 'first':
                username = first
            elif format_pattern == 'last.first':
                username = f"{last}.{first}"
            elif format_pattern == 'last_first':
                username = f"{last}_{first}"
            elif format_pattern == 'lastfirst':
                username = f"{last}{first}"
            elif format_pattern == 'first.middle.last':
                middle = random.choice(self.common_first_names)
                username = f"{first}.{middle[0]}.{last}"
            elif format_pattern == 'fmlast':
                middle = random.choice(self.common_first_names)
                username = f"{first[0]}{middle[0]}{last}"
            elif format_pattern == 'first_mlast':
                middle = random.choice(self.common_first_names)
                username = f"{first}_{middle[0]}{last}"
            else:
                username = f"{first}.{last}"

            # 添加数字
            if include_numbers and random.random() > 0.5:
                username += str(random.randint(1, 99))

        else:  # 随机生成用户名
            length = random.randint(min_length, max_length)
            chars = string.ascii_lowercase

            if include_numbers:
                chars += string.digits

            username = ''.join(random.choices(chars, k=length))

            # 添加特殊字符
            if include_special and random.random() > 0.7:  # 30%概率添加特殊字符
                if '.' in username or random.random() > 0.5:
                    # 不添加点号，或在特定位置添加
                    if '_' not in username and random.random() > 0.5:
                        pos = random.randint(1, len(username) - 1)
                        username = username[:pos] + '_' + username[pos:]
                elif random.random() > 0.5:
                    pos = random.randint(1, len(username) - 1)
                    username = username[:pos] + '.' + username[pos:]

        return username.lower()

    def generate_domain(self,
                        region: Optional[str] = None,
                        domain_type: Optional[str] = None) -> str:
        """生成随机域名"""

        if region and region in self.domains:
            if domain_type and domain_type in ['corporate', 'edu']:
                # 混合企业/教育域名
                all_domains = self.domains.get(domain_type, []) + self.domains.get(region, [])
                return random.choice(all_domains)
            else:
                return random.choice(self.domains[region])

        # 随机选择地区
        if not region:
            regions = list(self.domains.keys())
            # 降低企业/教育域名权重
            weights = [1.0] * len(regions)
            for i, r in enumerate(regions):
                if r in ['corporate', 'edu', 'country_tld']:
                    weights[i] = 0.3

            region = random.choices(regions, weights=weights, k=1)[0]

        return random.choice(self.domains[region])

    def generate_email(self,
                       region: Optional[str] = None,
                       domain: Optional[str] = None,
                       username: Optional[str] = None,
                       use_real_name: bool = True,
                       min_length: int = 5,
                       max_length: int = 15,
                       include_numbers: bool = True,
                       include_special: bool = True) -> str:
        """生成完整的邮箱地址"""

        if username is None:
            username = self.generate_username(
                use_real_name=use_real_name,
                min_length=min_length,
                max_length=max_length,
                include_numbers=include_numbers,
                include_special=include_special
            )

        if domain is None:
            if region and region in self.domains:
                domain = self.generate_domain(region)
            else:
                domain = self.generate_domain(region=None)

        return f"{username}@{domain}"

    def generate_emails(self,
                        count: int = 10,
                        region: Optional[str] = None,
                        unique_domains: bool = False) -> List[str]:
        """批量生成邮箱地址"""
        emails = []
        used_domains = set()

        for _ in range(count):
            if unique_domains and len(used_domains) < len(self.get_all_domains()):
                available_domains = [d for d in self.get_all_domains()
                                     if d not in used_domains]
                domain = random.choice(available_domains) if available_domains else self.generate_domain(region)
                used_domains.add(domain)
            else:
                domain = self.generate_domain(region)

            email = self.generate_email(region=region, domain=domain)
            emails.append(email)

        return emails

    def get_all_domains(self) -> List[str]:
        """获取所有域名"""
        all_domains = []
        for domain_list in self.domains.values():
            all_domains.extend(domain_list)
        return list(set(all_domains))  # 去重

    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def get_email_info(self, email: str) -> dict:
        """解析邮箱信息"""
        if not self.validate_email(email):
            return {"valid": False, "error": "Invalid email format"}

        username, domain = email.split('@')
        region_info = self._guess_region_by_domain(domain)

        return {
            "valid": True,
            "username": username,
            "domain": domain,
            "region": region_info.get('region', 'unknown'),
            "country": region_info.get('country', 'unknown'),
            "type": region_info.get('type', 'commercial')
        }

    def _guess_region_by_domain(self, domain: str) -> dict:
        """根据域名猜测地区"""
        for region, domains in self.domains.items():
            if domain in domains:
                region_names = {
                    'global': 'Global', 'us': 'United States', 'uk': 'United Kingdom',
                    'de': 'Germany', 'fr': 'France', 'cn': 'China', 'jp': 'Japan',
                    'kr': 'South Korea', 'ru': 'Russia', 'in': 'India', 'br': 'Brazil',
                    'corporate': 'Corporate', 'edu': 'Education', 'country_tld': 'Country TLD'
                }
                return {
                    'region': region,
                    'country': region_names.get(region, 'Unknown'),
                    'type': 'corporate' if region == 'corporate' else
                    'education' if region == 'edu' else 'commercial'
                }

        # 根据TLD猜测
        tld = domain.split('.')[-1]
        tld_map = {
            'com': ('global', 'Global'),
            'net': ('global', 'Global'),
            'org': ('global', 'Global'),
            'edu': ('us', 'United States'),
            'gov': ('us', 'United States'),
            'uk': ('uk', 'United Kingdom'),
            'de': ('de', 'Germany'),
            'fr': ('fr', 'France'),
            'jp': ('jp', 'Japan'),
            'cn': ('cn', 'China'),
            'ru': ('ru', 'Russia'),
            'in': ('in', 'India'),
            'br': ('br', 'Brazil'),
            'au': ('au', 'Australia'),
            'ca': ('ca', 'Canada')
        }

        if tld in tld_map:
            region, country = tld_map[tld]
            return {'region': region, 'country': country, 'type': 'country_tld'}

        return {'region': 'unknown', 'country': 'Unknown', 'type': 'unknown'}


class MobileNumberGenerator:
    """全球手机号码生成器"""

    def __init__(self):
        # 定义全球手机号码格式
        self.mobile_formats: Dict[str, MobileNumberInfo] = {
            # 亚洲
            'CN': MobileNumberInfo(
                country_code='CN',
                country_name='中国',
                dialing_code='+86',
                number_format='1XX-XXXX-XXXX',
                number_length=11,
                mobile_prefixes=['130', '131', '132', '133', '134', '135', '136', '137',
                                 '138', '139', '145', '147', '150', '151', '152', '153',
                                 '155', '156', '157', '158', '159', '165', '166', '167',
                                 '170', '171', '172', '173', '174', '175', '176', '177',
                                 '178', '180', '181', '182', '183', '184', '185', '186',
                                 '187', '188', '189', '191', '198', '199'],
                example='+86 138-0013-8000',
                description='11位数字，以1开头'
            ),

            'IN': MobileNumberInfo(
                country_code='IN',
                country_name='印度',
                dialing_code='+91',
                number_format='9XXXX-XXXXX',
                number_length=10,
                mobile_prefixes=['70', '78', '79', '80', '81', '82', '83', '84', '85',
                                 '86', '87', '88', '89', '90', '91', '92', '93', '94',
                                 '95', '96', '97', '98', '99'],
                example='+91 98765-43210',
                description='10位数字，通常以7、8、9开头'
            ),

            'ID': MobileNumberInfo(
                country_code='ID',
                country_name='印度尼西亚',
                dialing_code='+62',
                number_format='8XX-XXXX-XXXX',
                number_length=10,  # 不包括0前缀
                mobile_prefixes=['811', '812', '813', '821', '822', '823', '851', '852',
                                 '853', '881', '882', '885', '886', '887', '888', '889'],
                example='+62 812-3456-7890',
                description='10-12位数字，以08开头（国内拨打）'
            ),

            'JP': MobileNumberInfo(
                country_code='JP',
                country_name='日本',
                dialing_code='+81',
                number_format='90-XXXX-XXXX',
                number_length=10,
                mobile_prefixes=['70', '80', '90'],
                example='+81 90-1234-5678',
                description='10位数字，以070、080、090开头'
            ),

            'KR': MobileNumberInfo(
                country_code='KR',
                country_name='韩国',
                dialing_code='+82',
                number_format='010-XXXX-XXXX',
                number_length=10,
                mobile_prefixes=['010'],
                example='+82 010-1234-5678',
                description='10位数字，以010开头'
            ),

            'VN': MobileNumberInfo(
                country_code='VN',
                country_name='越南',
                dialing_code='+84',
                number_format='9X-XXXX-XXX',
                number_length=9,
                mobile_prefixes=['86', '88', '89', '90', '91', '92', '93', '94', '95',
                                 '96', '97', '98', '99'],
                example='+84 91-234-5678',
                description='9-10位数字，以09、03、07、08开头'
            ),

            'TH': MobileNumberInfo(
                country_code='TH',
                country_name='泰国',
                dialing_code='+66',
                number_format='8-XXXX-XXXX',
                number_length=9,
                mobile_prefixes=['61', '62', '63', '64', '65', '66', '67', '68', '69',
                                 '80', '81', '82', '83', '84', '85', '86', '87', '88',
                                 '89', '90', '91', '92', '93', '94', '95', '96', '97',
                                 '98', '99'],
                example='+66 81-234-5678',
                description='9位数字，以06、08、09开头'
            ),

            'MY': MobileNumberInfo(
                country_code='MY',
                country_name='马来西亚',
                dialing_code='+60',
                number_format='1X-XXX-XXXX',
                number_length=9,
                mobile_prefixes=['10', '11', '12', '13', '14', '15', '16', '17', '18',
                                 '19'],
                example='+60 12-345-6789',
                description='9-10位数字，以01开头'
            ),

            'SG': MobileNumberInfo(
                country_code='SG',
                country_name='新加坡',
                dialing_code='+65',
                number_format='9XXX-XXXX',
                number_length=8,
                mobile_prefixes=['8', '9'],
                example='+65 9123-4567',
                description='8位数字，以8或9开头'
            ),

            'PH': MobileNumberInfo(
                country_code='PH',
                country_name='菲律宾',
                dialing_code='+63',
                number_format='9XX-XXX-XXXX',
                number_length=10,
                mobile_prefixes=['90', '91', '92', '93', '94', '95', '96', '97', '98',
                                 '99'],
                example='+63 912-345-6789',
                description='10位数字，以09开头'
            ),

            'HK': MobileNumberInfo(
                country_code='HK',
                country_name='中国香港',
                dialing_code='+852',
                number_format='5XXX-XXXX',
                number_length=8,
                mobile_prefixes=['5', '6', '9'],
                example='+852 5123-4567',
                description='8位数字，以5、6、9开头'
            ),

            'TW': MobileNumberInfo(
                country_code='TW',
                country_name='中国台湾',
                dialing_code='+886',
                number_format='9XX-XXX-XXX',
                number_length=9,
                mobile_prefixes=['90', '91', '92', '93', '94', '95', '96', '97', '98',
                                 '99'],
                example='+886 912-345-678',
                description='9位数字，以09开头'
            ),

            'MO': MobileNumberInfo(
                country_code='MO',
                country_name='中国澳门',
                dialing_code='+853',
                number_format='6XXXXXX',
                number_length=8,
                mobile_prefixes=['6'],
                example='+853 6123-4567',
                description='8位数字，以6开头'
            ),

            'SA': MobileNumberInfo(
                country_code='SA',
                country_name='沙特阿拉伯',
                dialing_code='+966',
                number_format='5X-XXX-XXXX',
                number_length=9,
                mobile_prefixes=['50', '51', '52', '53', '54', '55', '56', '57', '58',
                                 '59'],
                example='+966 50-123-4567',
                description='9位数字，以05开头'
            ),

            'AE': MobileNumberInfo(
                country_code='AE',
                country_name='阿联酋',
                dialing_code='+971',
                number_format='5X-XXX-XXXX',
                number_length=9,
                mobile_prefixes=['50', '52', '54', '55', '56', '58'],
                example='+971 50-123-4567',
                description='9位数字，以05开头'
            ),

            'IL': MobileNumberInfo(
                country_code='IL',
                country_name='以色列',
                dialing_code='+972',
                number_format='5X-XXX-XXXX',
                number_length=9,
                mobile_prefixes=['50', '52', '53', '54', '55', '58'],
                example='+972 50-123-4567',
                description='9位数字，以05开头'
            ),

            'TR': MobileNumberInfo(
                country_code='TR',
                country_name='土耳其',
                dialing_code='+90',
                number_format='5XX-XXX-XXXX',
                number_length=10,
                mobile_prefixes=['50', '53', '54', '55'],
                example='+90 530-123-4567',
                description='10位数字，以05开头'
            ),

            'IR': MobileNumberInfo(
                country_code='IR',
                country_name='伊朗',
                dialing_code='+98',
                number_format='9XX-XXX-XXXX',
                number_length=10,
                mobile_prefixes=['90', '91', '92', '93'],
                example='+98 912-345-6789',
                description='10位数字，以09开头'
            ),

            # 北美
            'US': MobileNumberInfo(
                country_code='US',
                country_name='美国',
                dialing_code='+1',
                number_format='(XXX) XXX-XXXX',
                number_length=10,
                mobile_prefixes=['201', '202', '203', '205', '206', '207', '208', '209',
                                 '210', '212', '213', '214', '215', '216', '217', '218',
                                 '219', '224', '225', '228', '229', '231', '234', '239',
                                 '240', '248', '251', '252', '253', '254', '256', '260',
                                 '262', '267', '269', '270', '272', '276', '281', '283',
                                 '301', '302', '303', '304', '305', '307', '308', '309',
                                 '310', '312', '313', '314', '315', '316', '317', '318',
                                 '319', '320', '321', '323', '325', '330', '331', '334',
                                 '336', '337', '339', '340', '346', '347', '351', '352',
                                 '360', '361', '364', '380', '385', '386', '401', '402',
                                 '404', '405', '406', '407', '408', '409', '410', '412',
                                 '413', '414', '415', '417', '419', '423', '424', '425',
                                 '430', '432', '434', '435', '440', '442', '443', '445',
                                 '447', '448', '458', '463', '464', '469', '470', '475',
                                 '478', '479', '480', '484', '501', '502', '503', '504',
                                 '505', '507', '508', '509', '510', '512', '513', '515',
                                 '516', '517', '518', '520', '530', '531', '534', '539',
                                 '540', '541', '551', '559', '561', '562', '563', '564',
                                 '567', '570', '571', '573', '574', '575', '580', '585',
                                 '586', '601', '602', '603', '605', '606', '607', '608',
                                 '609', '610', '612', '614', '615', '616', '617', '618',
                                 '619', '620', '623', '626', '628', '629', '630', '631',
                                 '636', '641', '646', '650', '651', '657', '660', '661',
                                 '662', '667', '669', '678', '679', '681', '682', '689',
                                 '701', '702', '703', '704', '706', '707', '708', '712',
                                 '713', '714', '715', '716', '717', '718', '719', '720',
                                 '724', '725', '727', '730', '731', '732', '734', '737',
                                 '740', '743', '747', '752', '754', '757', '760', '762',
                                 '763', '765', '769', '770', '772', '773', '774', '775',
                                 '779', '781', '785', '786', '801', '802', '803', '804',
                                 '805', '806', '808', '810', '812', '813', '814', '815',
                                 '816', '817', '818', '828', '830', '831', '832', '835',
                                 '843', '845', '847', '848', '850', '854', '856', '857',
                                 '858', '859', '860', '862', '863', '864', '865', '870',
                                 '872', '878', '901', '903', '904', '906', '907', '908',
                                 '909', '910', '912', '913', '914', '915', '916', '917',
                                 '918', '919', '920', '925', '928', '929', '930', '931',
                                 '934', '936', '937', '938', '940', '941', '945', '947',
                                 '949', '951', '952', '954', '956', '959', '970', '971',
                                 '972', '973', '975', '978', '979', '980', '984', '985',
                                 '986', '989'],
                example='+1 (212) 555-1234',
                description='10位数字，格式：(XXX) XXX-XXXX'
            ),

            'CA': MobileNumberInfo(
                country_code='CA',
                country_name='加拿大',
                dialing_code='+1',
                number_format='(XXX) XXX-XXXX',
                number_length=10,
                mobile_prefixes=['204', '226', '236', '249', '250', '289', '306', '343',
                                 '365', '367', '403', '416', '418', '431', '437', '438',
                                 '450', '506', '514', '519', '548', '579', '581', '587',
                                 '604', '613', '639', '647', '705', '709', '778', '780',
                                 '782', '807', '819', '825', '867', '873', '902', '905'],
                example='+1 (416) 555-1234',
                description='10位数字，与美国相同格式'
            ),

            'MX': MobileNumberInfo(
                country_code='MX',
                country_name='墨西哥',
                dialing_code='+52',
                number_format='1XX-XXX-XXXX',
                number_length=10,
                mobile_prefixes=['55', '56', '81', '33', '656', '664', '646', '662',
                                 '618', '443', '444', '477', '449', '998', '999', '981',
                                 '983', '984', '985', '986', '987', '988', '921', '924',
                                 '951', '961', '962', '963', '967', '971', '993', '994',
                                 '995', '996', '998', '999'],
                example='+52 55-1234-5678',
                description='10位数字，以1开头'
            ),

            # 欧洲
            'GB': MobileNumberInfo(
                country_code='GB',
                country_name='英国',
                dialing_code='+44',
                number_format='7XXX-XXX-XXX',
                number_length=10,
                mobile_prefixes=['70', '74', '75', '76', '77', '78', '79'],
                example='+44 7123-456-789',
                description='10位数字，以07开头'
            ),

            'DE': MobileNumberInfo(
                country_code='DE',
                country_name='德国',
                dialing_code='+49',
                number_format='151-XXXX-XXXX',
                number_length=10,  # 不包括开头的0
                mobile_prefixes=['151', '152', '157', '159', '160', '162', '163', '170',
                                 '171', '172', '173', '174', '175', '176', '177', '178',
                                 '179'],
                example='+49 151-1234-5678',
                description='10-11位数字，以01开头（国内拨打）'
            ),

            'FR': MobileNumberInfo(
                country_code='FR',
                country_name='法国',
                dialing_code='+33',
                number_format='6 XX XX XX XX',
                number_length=9,
                mobile_prefixes=['6', '7'],
                example='+33 6 12 34 56 78',
                description='9位数字，以06或07开头'
            ),

            'IT': MobileNumberInfo(
                country_code='IT',
                country_name='意大利',
                dialing_code='+39',
                number_format='3XX-XXX-XXXX',
                number_length=10,
                mobile_prefixes=['3'],
                example='+39 345-678-9012',
                description='10位数字，以3开头'
            ),

            'ES': MobileNumberInfo(
                country_code='ES',
                country_name='西班牙',
                dialing_code='+34',
                number_format='6XX-XXX-XXX',
                number_length=9,
                mobile_prefixes=['6', '7'],
                example='+34 612-345-678',
                description='9位数字，以6或7开头'
            ),

            'RU': MobileNumberInfo(
                country_code='RU',
                country_name='俄罗斯',
                dialing_code='+7',
                number_format='9XX-XXX-XX-XX',
                number_length=10,
                mobile_prefixes=['90', '91', '92', '93', '94', '95', '96', '97', '98',
                                 '99'],
                example='+7 912-345-67-89',
                description='10位数字，以9开头'
            ),

            'PL': MobileNumberInfo(
                country_code='PL',
                country_name='波兰',
                dialing_code='+48',
                number_format='5XX-XXX-XXX',
                number_length=9,
                mobile_prefixes=['50', '51', '53', '57', '60', '66', '69', '72', '73',
                                 '78', '79', '88'],
                example='+48 512-345-678',
                description='9位数字，以5、6、7、8开头'
            ),

            'NL': MobileNumberInfo(
                country_code='NL',
                country_name='荷兰',
                dialing_code='+31',
                number_format='6-XXXX-XXXX',
                number_length=9,
                mobile_prefixes=['6'],
                example='+31 6-1234-5678',
                description='9位数字，以06开头（国内拨打）'
            ),

            'BE': MobileNumberInfo(
                country_code='BE',
                country_name='比利时',
                dialing_code='+32',
                number_format='4XX-XX-XX-XX',
                number_length=9,
                mobile_prefixes=['456', '457', '458', '459', '460', '461', '462', '463',
                                 '464', '465', '466', '467', '468', '469', '470', '471',
                                 '472', '473', '474', '475', '476', '477', '478', '479'],
                example='+32 470-12-34-56',
                description='9位数字，以04开头（国内拨打）'
            ),

            'CH': MobileNumberInfo(
                country_code='CH',
                country_name='瑞士',
                dialing_code='+41',
                number_format='7X-XXX-XX-XX',
                number_length=9,
                mobile_prefixes=['76', '77', '78', '79'],
                example='+41 79-123-45-67',
                description='9位数字，以07开头（国内拨打）'
            ),

            'SE': MobileNumberInfo(
                country_code='SE',
                country_name='瑞典',
                dialing_code='+46',
                number_format='7X-XXX-XX-XX',
                number_length=9,
                mobile_prefixes=['70', '72', '73', '76', '79'],
                example='+46 70-123-45-67',
                description='9位数字，以07开头（国内拨打）'
            ),

            'NO': MobileNumberInfo(
                country_code='NO',
                country_name='挪威',
                dialing_code='+47',
                number_format='4XX-XX-XXX',
                number_length=8,
                mobile_prefixes=['4', '9'],
                example='+47 412-34-567',
                description='8位数字，以4或9开头'
            ),

            'DK': MobileNumberInfo(
                country_code='DK',
                country_name='丹麦',
                dialing_code='+45',
                number_format='2X-XX-XX-XX',
                number_length=8,
                mobile_prefixes=['2', '3', '4', '5', '6', '7', '9'],
                example='+45 20-12-34-56',
                description='8位数字'
            ),

            'FI': MobileNumberInfo(
                country_code='FI',
                country_name='芬兰',
                dialing_code='+358',
                number_format='4X-XXX-XX-XX',
                number_length=9,  # 不包括开头的0
                mobile_prefixes=['40', '41', '42', '43', '44', '45', '46', '47', '48',
                                 '49'],
                example='+358 40-123-45-67',
                description='9位数字，以04开头（国内拨打）'
            ),

            'AT': MobileNumberInfo(
                country_code='AT',
                country_name='奥地利',
                dialing_code='+43',
                number_format='6XX-XXXXXX',
                number_length=9,  # 不包括开头的0
                mobile_prefixes=['65', '66', '67', '68', '69'],
                example='+43 650-123456',
                description='9-10位数字，以06开头（国内拨打）'
            ),

            'UA': MobileNumberInfo(
                country_code='UA',
                country_name='乌克兰',
                dialing_code='+380',
                number_format='XX-XXX-XXXX',
                number_length=9,
                mobile_prefixes=['39', '50', '63', '66', '67', '68', '73', '89', '91',
                                 '92', '93', '94', '95', '96', '97', '98', '99'],
                example='+380 50-123-4567',
                description='9位数字，以0开头（国内拨打）'
            ),

            # 南美洲
            'BR': MobileNumberInfo(
                country_code='BR',
                country_name='巴西',
                dialing_code='+55',
                number_format='(XX) 9XXXX-XXXX',
                number_length=11,
                mobile_prefixes=['11', '12', '13', '14', '15', '16', '17', '18', '19',
                                 '21', '22', '24', '27', '28', '31', '32', '33', '34',
                                 '35', '37', '38', '41', '42', '43', '44', '45', '46',
                                 '47', '48', '49', '51', '53', '54', '55', '61', '62',
                                 '63', '64', '65', '66', '67', '68', '69', '71', '73',
                                 '74', '75', '77', '79', '81', '82', '83', '84', '85',
                                 '86', '87', '88', '89', '91', '92', '93', '94', '95',
                                 '96', '97', '98', '99'],
                example='+55 (11) 91234-5678',
                description='11位数字，格式：(XX) 9XXXX-XXXX'
            ),

            'AR': MobileNumberInfo(
                country_code='AR',
                country_name='阿根廷',
                dialing_code='+54',
                number_format='9 XX-XXXX-XXXX',
                number_length=10,
                mobile_prefixes=['9'],
                example='+54 9 11-2345-6789',
                description='10位数字，以9开头'
            ),

            'CO': MobileNumberInfo(
                country_code='CO',
                country_name='哥伦比亚',
                dialing_code='+57',
                number_format='3XX-XXX-XXXX',
                number_length=10,
                mobile_prefixes=['3'],
                example='+57 310-123-4567',
                description='10位数字，以3开头'
            ),

            'PE': MobileNumberInfo(
                country_code='PE',
                country_name='秘鲁',
                dialing_code='+51',
                number_format='9XX-XXX-XXX',
                number_length=9,
                mobile_prefixes=['9'],
                example='+51 912-345-678',
                description='9位数字，以9开头'
            ),

            'CL': MobileNumberInfo(
                country_code='CL',
                country_name='智利',
                dialing_code='+56',
                number_format='9-XXXX-XXXX',
                number_length=9,
                mobile_prefixes=['9'],
                example='+56 9-1234-5678',
                description='9位数字，以9开头'
            ),

            # 非洲
            'NG': MobileNumberInfo(
                country_code='NG',
                country_name='尼日利亚',
                dialing_code='+234',
                number_format='80X-XXX-XXXX',
                number_length=10,
                mobile_prefixes=['70', '80', '81', '90', '91'],
                example='+234 801-234-5678',
                description='10位数字，以070、080、081、090、091开头'
            ),

            'ET': MobileNumberInfo(
                country_code='ET',
                country_name='埃塞俄比亚',
                dialing_code='+251',
                number_format='9XX-XXX-XXX',
                number_length=9,
                mobile_prefixes=['91', '92', '93', '94', '95', '96', '97', '98', '99'],
                example='+251 91-123-4567',
                description='9位数字，以09开头（国内拨打）'
            ),

            'EG': MobileNumberInfo(
                country_code='EG',
                country_name='埃及',
                dialing_code='+20',
                number_format='1X-XXXX-XXXX',
                number_length=10,
                mobile_prefixes=['10', '11', '12'],
                example='+20 10-1234-5678',
                description='10位数字，以01开头（国内拨打）'
            ),

            'ZA': MobileNumberInfo(
                country_code='ZA',
                country_name='南非',
                dialing_code='+27',
                number_format='7X-XXX-XXXX',
                number_length=9,
                mobile_prefixes=['60', '61', '62', '63', '64', '65', '66', '67', '68',
                                 '69', '71', '72', '73', '74', '76', '78', '79', '81',
                                 '82', '83', '84'],
                example='+27 72-123-4567',
                description='9位数字，以07开头（国内拨打）'
            ),

            'KE': MobileNumberInfo(
                country_code='KE',
                country_name='肯尼亚',
                dialing_code='+254',
                number_format='7XX-XXX-XXX',
                number_length=9,
                mobile_prefixes=['70', '71', '72', '73', '74', '75', '76', '77', '78',
                                 '79'],
                example='+254 712-345-678',
                description='9位数字，以07开头（国内拨打）'
            ),

            'GH': MobileNumberInfo(
                country_code='GH',
                country_name='加纳',
                dialing_code='+233',
                number_format='2X-XXX-XXXX',
                number_length=9,
                mobile_prefixes=['20', '24', '26', '27', '28', '29', '30', '31', '32',
                                 '33', '34', '35', '36', '37', '38', '39', '50', '53',
                                 '54', '55', '56', '57', '58', '59'],
                example='+233 20-123-4567',
                description='9位数字，以02开头（国内拨打）'
            ),

            # 大洋洲
            'AU': MobileNumberInfo(
                country_code='AU',
                country_name='澳大利亚',
                dialing_code='+61',
                number_format='4XX-XXX-XXX',
                number_length=9,
                mobile_prefixes=['4'],
                example='+61 412-345-678',
                description='9位数字，以04开头（国内拨打）'
            ),

            'NZ': MobileNumberInfo(
                country_code='NZ',
                country_name='新西兰',
                dialing_code='+64',
                number_format='2X-XXX-XXXX',
                number_length=9,
                mobile_prefixes=['20', '21', '22', '23', '24', '25', '26', '27', '28',
                                 '29'],
                example='+64 21-123-4567',
                description='9位数字，以02开头（国内拨打）'
            ),
        }

        # 运营商映射
        self.operators = {
            'CN': {
                '中国移动': ['134', '135', '136', '137', '138', '139', '147', '150', '151',
                             '152', '157', '158', '159', '165', '172', '178', '182', '183',
                             '184', '187', '188', '198'],
                '中国联通': ['130', '131', '132', '145', '155', '156', '166', '175', '176', '185', '186'],
                '中国电信': ['133', '149', '153', '173', '177', '180', '181', '189', '191', '199'],
                '虚拟运营商': ['170', '171']
            },
            'US': {
                'Verizon': ['201', '202', '203', '205', '206', '207', '208', '209'],
                'AT&T': ['210', '212', '213', '214', '215', '216', '217', '218', '219'],
                'T-Mobile': ['224', '225', '228', '229', '231', '234', '239'],
                'Sprint': ['240', '248', '251', '252', '253', '254', '256', '260']
            },
            'IN': {
                'Airtel': ['98', '99'],
                'Jio': ['70', '96', '97'],
                'Vodafone': ['90', '91', '92', '93'],
                'BSNL': ['94', '95']
            },
            'GB': {
                'Vodafone': ['77'],
                'O2': ['78', '79'],
                'EE': ['76'],
                'Three': ['74']
            },
            'DE': {
                'Telekom': ['151', '152', '157', '159', '160'],
                'Vodafone': ['162', '163', '170'],
                'O2': ['178', '179']
            }
        }

    def generate_mobile_number(self,
                               country_code: str = 'CN',
                               format_type: str = 'international',
                               with_operator: bool = False) -> Dict:
        """生成手机号码"""
        country_code = country_code.upper()

        if country_code not in self.mobile_formats:
            raise ValueError(f"不支持的国家代码: {country_code}")

        info = self.mobile_formats[country_code]

        # 随机选择运营商前缀
        if info.mobile_prefixes:
            prefix = random.choice(info.mobile_prefixes)
        else:
            # 如果没有指定前缀，使用通用规则
            if country_code == 'CN':
                prefix = '13'
            elif country_code == 'US':
                prefix = random.choice(['201', '202', '203'])
            elif country_code == 'GB':
                prefix = '7'
            else:
                prefix = '9'

        # 生成剩余数字
        remaining_length = info.number_length - len(prefix)
        if remaining_length > 0:
            remaining = ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])
            number_without_prefix = prefix + remaining
        else:
            number_without_prefix = prefix

        # 确保总长度正确
        number_without_prefix = number_without_prefix[:info.number_length]

        # 生成不同格式
        formatted_number = self._format_number(number_without_prefix, info, format_type)

        result = {
            'country_code': country_code,
            'country_name': info.country_name,
            'dialing_code': info.dialing_code,
            'full_international': f"{info.dialing_code} {formatted_number}",
            'number': number_without_prefix,
            'formatted': formatted_number,
            'format_type': format_type,
            'length': len(number_without_prefix)
        }

        # 添加运营商信息
        if with_operator:
            operator = self._guess_operator(country_code, number_without_prefix)
            result['operator'] = operator

        return result

    def _format_number(self, number: str, info: MobileNumberInfo, format_type: str) -> str:
        """格式化号码"""
        if format_type == 'international':
            return self._format_international(number, info)
        elif format_type == 'national':
            return self._format_national(number, info)
        elif format_type == 'e164':
            return self._format_e164(number, info)
        elif format_type == 'simple':
            return number
        else:
            return number

    @classmethod
    def _format_international(cls, number: str, info: MobileNumberInfo) -> str:
        """国际格式"""
        if info.country_code == 'CN':
            # 中国: +86 138-0013-8000
            if len(number) == 11:
                return f"{number[:3]}-{number[3:7]}-{number[7:]}"

        elif info.country_code == 'US':
            # 美国: +1 (212) 555-1234
            if len(number) == 10:
                return f"({number[:3]}) {number[3:6]}-{number[6:]}"

        elif info.country_code == 'GB':
            # 英国: +44 7123-456-789
            if len(number) == 10:
                return f"{number[:4]}-{number[4:7]}-{number[7:]}"

        elif info.country_code == 'DE':
            # 德国: +49 151-1234-5678
            if len(number) == 10:
                return f"{number[:3]}-{number[3:7]}-{number[7:]}"

        elif info.country_code == 'FR':
            # 法国: +33 6 12 34 56 78
            if len(number) == 9:
                chunks = [number[i:i + 2] for i in range(0, len(number), 2)]
                if len(chunks[-1]) == 1:  # 处理奇数长度
                    chunks[-2] = chunks[-2] + chunks[-1]
                    chunks = chunks[:-1]
                return ' '.join(chunks)

        elif info.country_code == 'JP':
            # 日本: +81 90-1234-5678
            if len(number) == 10:
                return f"{number[:2]}-{number[2:6]}-{number[6:]}"

        elif info.country_code == 'KR':
            # 韩国: +82 010-1234-5678
            if len(number) == 10:
                return f"{number[:3]}-{number[3:7]}-{number[7:]}"

        elif info.country_code == 'IN':
            # 印度: +91 98765-43210
            if len(number) == 10:
                return f"{number[:5]}-{number[5:]}"

        elif info.country_code == 'BR':
            # 巴西: +55 (11) 91234-5678
            if len(number) == 11:
                return f"({number[:2]}) {number[2:7]}-{number[7:]}"

        elif info.country_code == 'RU':
            # 俄罗斯: +7 912-345-67-89
            if len(number) == 10:
                return f"{number[:3]}-{number[3:6]}-{number[6:8]}-{number[8:]}"

        # 默认格式：每3-4位一组
        if len(number) > 0:
            if len(number) <= 4:
                return number
            elif len(number) <= 7:
                return f"{number[:3]}-{number[3:]}"
            elif len(number) <= 10:
                return f"{number[:3]}-{number[3:6]}-{number[6:]}"
            else:
                return f"{number[:4]}-{number[4:8]}-{number[8:]}"

        return number

    @classmethod
    def _format_national(cls, number: str, info: MobileNumberInfo) -> str:
        """国内格式（添加国内拨打前缀）"""
        if info.country_code == 'CN':
            return number  # 中国国内格式就是11位

        elif info.country_code == 'US':
            return f"({number[:3]}) {number[3:6]}-{number[6:]}"

        elif info.country_code in ['DE', 'FR', 'IT', 'ES', 'GB', 'NL', 'BE', 'CH', 'SE', 'FI', 'AT']:
            # 欧洲国家通常添加0
            return f"0{number}"

        elif info.country_code == 'JP':
            return f"0{number}"

        elif info.country_code == 'KR':
            return number

        elif info.country_code == 'IN':
            return number

        elif info.country_code == 'BR':
            return f"({number[:2]}) {number[2:7]}-{number[7:]}"

        return number

    @classmethod
    def _format_e164(cls, number: str, info: MobileNumberInfo) -> str:
        """E.164格式"""
        # 移除国际拨号前缀中的+
        dialing_code = info.dialing_code.replace('+', '')
        return f"+{dialing_code}{number}"

    def _guess_operator(self, country_code: str, number: str) -> Dict:
        """猜测运营商"""
        if country_code not in self.operators:
            return {"name": "Unknown", "confidence": 0}

        operators = self.operators[country_code]

        for operator, prefixes in operators.items():
            for prefix in prefixes:
                if number.startswith(prefix):
                    confidence = len(prefix) / len(number)
                    return {
                        "name": operator,
                        "confidence": round(confidence, 2),
                        "prefix": prefix
                    }

        return {"name": "Unknown", "confidence": 0}

    def validate_mobile_number(self, number: str, country_code: str) -> Dict:
        """验证手机号码"""
        country_code = country_code.upper()

        if country_code not in self.mobile_formats:
            return {
                "valid": False,
                "error": f"Unsupported country code: {country_code}",
                "country_code": country_code
            }

        info = self.mobile_formats[country_code]

        # 清理号码（移除非数字字符）
        clean_number = re.sub(r'\D', '', number)

        # 移除国际拨号前缀
        dialing_code = info.dialing_code.replace('+', '')
        if clean_number.startswith(dialing_code):
            clean_number = clean_number[len(dialing_code):]

        # 检查长度
        if len(clean_number) != info.number_length:
            return {
                "valid": False,
                "error": f"Invalid length: expected {info.number_length}, got {len(clean_number)}",
                "expected_length": info.number_length,
                "actual_length": len(clean_number),
                "number": clean_number
            }

        # 检查前缀
        valid_prefix = False
        if info.mobile_prefixes:
            for prefix in info.mobile_prefixes:
                if clean_number.startswith(prefix):
                    valid_prefix = True
                    break
        else:
            valid_prefix = True  # 如果没有指定前缀，假设有效

        if not valid_prefix:
            return {
                "valid": False,
                "error": f"Invalid prefix: {clean_number[:3]}",
                "valid_prefixes": info.mobile_prefixes,
                "number": clean_number
            }

        # 格式化为各种格式
        formatted = {
            'international': self._format_international(clean_number, info),
            'national': self._format_national(clean_number, info),
            'e164': self._format_e164(clean_number, info),
            'simple': clean_number
        }

        # 猜测运营商
        operator = self._guess_operator(country_code, clean_number)

        return {
            "valid": True,
            "country_code": country_code,
            "country_name": info.country_name,
            "dialing_code": info.dialing_code,
            "number": clean_number,
            "formatted": formatted,
            "operator": operator,
            "length": len(clean_number)
        }

    def generate_batch(self,
                       count: int = 10,
                       countries: List[str] = None,
                       format_type: str = 'international') -> List[Dict]:
        """批量生成手机号码"""
        if countries is None:
            countries = list(self.mobile_formats.keys())

        results = []
        for _ in range(count):
            country = random.choice(countries)
            try:
                result = self.generate_mobile_number(country, format_type, with_operator=True)
                results.append(result)
            except Exception as e:
                print(f"Error generating for {country}: {e}")

        return results

    def generate_by_region(self,
                           region: str = 'asia',
                           count: int = 5) -> List[Dict]:
        """按地区生成手机号码"""
        regions = {
            'asia': ['CN', 'IN', 'JP', 'KR', 'VN', 'TH', 'MY', 'SG', 'PH', 'ID'],
            'europe': ['GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'CH', 'SE', 'RU'],
            'north_america': ['US', 'CA', 'MX'],
            'south_america': ['BR', 'AR', 'CO', 'PE', 'CL'],
            'africa': ['NG', 'ET', 'EG', 'ZA', 'KE', 'GH'],
            'oceania': ['AU', 'NZ'],
            'middle_east': ['SA', 'AE', 'IL', 'TR', 'IR']
        }

        if region not in regions:
            region = 'asia'

        countries = regions[region]
        return self.generate_batch(count, countries)

    def get_country_info(self, country_code: str) -> Optional[MobileNumberInfo]:
        """获取国家手机号码信息"""
        return self.mobile_formats.get(country_code.upper())

    def get_all_countries(self) -> List[Dict]:
        """获取所有支持的国家信息"""
        countries = []
        for code, info in self.mobile_formats.items():
            countries.append({
                'country_code': code,
                'country_name': info.country_name,
                'dialing_code': info.dialing_code,
                'number_format': info.number_format,
                'number_length': info.number_length,
                'example': info.example
            })
        return countries


@dataclass
class CityInfo:
    """城市信息"""
    name: str
    state: str
    state_abbr: str
    population: int
    latitude: float
    longitude: float
    timezone: str
    is_capital: bool = False
    nickname: Optional[str] = None
    founded_year: Optional[int] = None
    area_sq_miles: Optional[float] = None


class USCityGenerator:
    """美国城市名生成器"""

    def __init__(self):
        # 美国50个州及其缩写
        self.states = {
            'AL': 'Alabama',
            'AK': 'Alaska',
            'AZ': 'Arizona',
            'AR': 'Arkansas',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'HI': 'Hawaii',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'IA': 'Iowa',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'ME': 'Maine',
            'MD': 'Maryland',
            'MA': 'Massachusetts',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MS': 'Mississippi',
            'MO': 'Missouri',
            'MT': 'Montana',
            'NE': 'Nebraska',
            'NV': 'Nevada',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NY': 'New York',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VT': 'Vermont',
            'VA': 'Virginia',
            'WA': 'Washington',
            'WV': 'West Virginia',
            'WI': 'Wisconsin',
            'WY': 'Wyoming'
        }

        # 州首府
        self.state_capitals = {
            'AL': 'Montgomery',
            'AK': 'Juneau',
            'AZ': 'Phoenix',
            'AR': 'Little Rock',
            'CA': 'Sacramento',
            'CO': 'Denver',
            'CT': 'Hartford',
            'DE': 'Dover',
            'FL': 'Tallahassee',
            'GA': 'Atlanta',
            'HI': 'Honolulu',
            'ID': 'Boise',
            'IL': 'Springfield',
            'IN': 'Indianapolis',
            'IA': 'Des Moines',
            'KS': 'Topeka',
            'KY': 'Frankfort',
            'LA': 'Baton Rouge',
            'ME': 'Augusta',
            'MD': 'Annapolis',
            'MA': 'Boston',
            'MI': 'Lansing',
            'MN': 'St. Paul',
            'MS': 'Jackson',
            'MO': 'Jefferson City',
            'MT': 'Helena',
            'NE': 'Lincoln',
            'NV': 'Carson City',
            'NH': 'Concord',
            'NJ': 'Trenton',
            'NM': 'Santa Fe',
            'NY': 'Albany',
            'NC': 'Raleigh',
            'ND': 'Bismarck',
            'OH': 'Columbus',
            'OK': 'Oklahoma City',
            'OR': 'Salem',
            'PA': 'Harrisburg',
            'RI': 'Providence',
            'SC': 'Columbia',
            'SD': 'Pierre',
            'TN': 'Nashville',
            'TX': 'Austin',
            'UT': 'Salt Lake City',
            'VA': 'Richmond',
            'VT': 'Montpelier',
            'WA': 'Olympia',
            'WV': 'Charleston',
            'WI': 'Madison',
            'WY': 'Cheyenne'
        }

        # 美国主要城市数据（包含人口超过10万的城市）
        self.major_cities = {
            # 加利福尼亚州
            'CA': [
                CityInfo('Los Angeles', 'California', 'CA', 3971883, 34.0522, -118.2437, 'Pacific',
                         nickname='City of Angels', founded_year=1781, area_sq_miles=468.7),
                CityInfo('San Diego', 'California', 'CA', 1423851, 32.7157, -117.1611, 'Pacific', founded_year=1769,
                         area_sq_miles=325.2),
                CityInfo('San Jose', 'California', 'CA', 1035317, 37.3382, -121.8863, 'Pacific',
                         nickname='Capital of Silicon Valley', founded_year=1777, area_sq_miles=176.5),
                CityInfo('San Francisco', 'California', 'CA', 883305, 37.7749, -122.4194, 'Pacific',
                         nickname='The City', founded_year=1776, area_sq_miles=46.9),
                CityInfo('Fresno', 'California', 'CA', 542107, 36.7378, -119.7871, 'Pacific', founded_year=1872,
                         area_sq_miles=115.2),
                CityInfo('Sacramento', 'California', 'CA', 524943, 38.5816, -121.4944, 'Pacific', is_capital=True,
                         nickname='City of Trees', founded_year=1849, area_sq_miles=97.9),
                CityInfo('Long Beach', 'California', 'CA', 466742, 33.7701, -118.1937, 'Pacific', founded_year=1888,
                         area_sq_miles=50.3),
                CityInfo('Oakland', 'California', 'CA', 440646, 37.8044, -122.2711, 'Pacific', founded_year=1852,
                         area_sq_miles=55.8),
                CityInfo('Bakersfield', 'California', 'CA', 403455, 35.3733, -119.0187, 'Pacific', founded_year=1869,
                         area_sq_miles=149.2),
                CityInfo('Anaheim', 'California', 'CA', 350365, 33.8366, -117.9143, 'Pacific',
                         nickname='The City of Kindness', founded_year=1857, area_sq_miles=50.8),
                CityInfo('Santa Ana', 'California', 'CA', 332318, 33.7456, -117.8677, 'Pacific', founded_year=1869,
                         area_sq_miles=27.3),
                CityInfo('Riverside', 'California', 'CA', 330063, 33.9806, -117.3755, 'Pacific', founded_year=1870,
                         area_sq_miles=81.1),
                CityInfo('Stockton', 'California', 'CA', 320804, 37.9577, -121.2908, 'Pacific', founded_year=1849,
                         area_sq_miles=61.7),
                CityInfo('Irvine', 'California', 'CA', 307670, 33.6846, -117.8265, 'Pacific', founded_year=1971,
                         area_sq_miles=65.6),
                CityInfo('Chula Vista', 'California', 'CA', 275487, 32.6401, -117.0842, 'Pacific', founded_year=1911,
                         area_sq_miles=49.6),
                CityInfo('Fremont', 'California', 'CA', 230504, 37.5485, -121.9886, 'Pacific', founded_year=1956,
                         area_sq_miles=77.5),
                CityInfo('San Bernardino', 'California', 'CA', 222203, 34.1083, -117.2898, 'Pacific', founded_year=1810,
                         area_sq_miles=59.2),
                CityInfo('Modesto', 'California', 'CA', 218464, 37.6391, -120.9969, 'Pacific', founded_year=1870,
                         area_sq_miles=43.0),
                CityInfo('Fontana', 'California', 'CA', 214547, 34.0922, -117.4350, 'Pacific', founded_year=1913,
                         area_sq_miles=42.4),
                CityInfo('Oxnard', 'California', 'CA', 208881, 34.1975, -119.1771, 'Pacific', founded_year=1903,
                         area_sq_miles=26.9),
                CityInfo('Moreno Valley', 'California', 'CA', 208634, 33.9375, -117.2306, 'Pacific', founded_year=1984,
                         area_sq_miles=51.3),
            ],

            # 德克萨斯州
            'TX': [
                CityInfo('Houston', 'Texas', 'TX', 2325502, 29.7604, -95.3698, 'Central', nickname='Space City',
                         founded_year=1836, area_sq_miles=637.5),
                CityInfo('San Antonio', 'Texas', 'TX', 1547253, 29.4241, -98.4936, 'Central', nickname='Alamo City',
                         founded_year=1718, area_sq_miles=465.4),
                CityInfo('Dallas', 'Texas', 'TX', 1343573, 32.7767, -96.7970, 'Central', founded_year=1841,
                         area_sq_miles=340.9),
                CityInfo('Austin', 'Texas', 'TX', 978908, 30.2672, -97.7431, 'Central', is_capital=True,
                         nickname='Live Music Capital of the World', founded_year=1839, area_sq_miles=305.1),
                CityInfo('Fort Worth', 'Texas', 'TX', 935508, 32.7555, -97.3308, 'Central', nickname='Cowtown',
                         founded_year=1849, area_sq_miles=342.9),
                CityInfo('El Paso', 'Texas', 'TX', 681124, 31.7619, -106.4850, 'Mountain', founded_year=1659,
                         area_sq_miles=256.3),
                CityInfo('Arlington', 'Texas', 'TX', 398112, 32.7357, -97.1081, 'Central', founded_year=1876,
                         area_sq_miles=95.9),
                CityInfo('Corpus Christi', 'Texas', 'TX', 326586, 27.8006, -97.3964, 'Central',
                         nickname='Sparkling City by the Sea', founded_year=1839, area_sq_miles=160.6),
                CityInfo('Plano', 'Texas', 'TX', 287677, 33.0198, -96.6989, 'Central', founded_year=1873,
                         area_sq_miles=71.6),
                CityInfo('Laredo', 'Texas', 'TX', 262491, 27.5306, -99.4803, 'Central', founded_year=1755,
                         area_sq_miles=106.5),
                CityInfo('Lubbock', 'Texas', 'TX', 257141, 33.5779, -101.8552, 'Central', nickname='Hub City',
                         founded_year=1890, area_sq_miles=122.4),
                CityInfo('Garland', 'Texas', 'TX', 246018, 32.9126, -96.6389, 'Central', founded_year=1891,
                         area_sq_miles=57.1),
                CityInfo('Irving', 'Texas', 'TX', 239798, 32.8140, -96.9489, 'Central', founded_year=1903,
                         area_sq_miles=67.0),
                CityInfo('Amarillo', 'Texas', 'TX', 200393, 35.2220, -101.8313, 'Central',
                         nickname='Yellow Rose of Texas', founded_year=1887, area_sq_miles=99.5),
                CityInfo('Grand Prairie', 'Texas', 'TX', 196100, 32.7459, -96.9978, 'Central', founded_year=1863,
                         area_sq_miles=72.1),
                CityInfo('Brownsville', 'Texas', 'TX', 186738, 25.9018, -97.4975, 'Central', founded_year=1848,
                         area_sq_miles=132.3),
                CityInfo('McKinney', 'Texas', 'TX', 199177, 33.1976, -96.6153, 'Central', founded_year=1848,
                         area_sq_miles=66.2),
                CityInfo('Frisco', 'Texas', 'TX', 200490, 33.1554, -96.8225, 'Central', founded_year=1902,
                         area_sq_miles=62.3),
            ],

            # 纽约州
            'NY': [
                CityInfo('New York City', 'New York', 'NY', 8336817, 40.7128, -74.0060, 'Eastern',
                         nickname='The Big Apple', founded_year=1624, area_sq_miles=302.6),
                CityInfo('Buffalo', 'New York', 'NY', 278349, 42.8864, -78.8784, 'Eastern', nickname='The Queen City',
                         founded_year=1789, area_sq_miles=40.4),
                CityInfo('Rochester', 'New York', 'NY', 211328, 43.1566, -77.6088, 'Eastern',
                         nickname='The Flower City', founded_year=1789, area_sq_miles=35.8),
                CityInfo('Yonkers', 'New York', 'NY', 211569, 40.9312, -73.8987, 'Eastern', founded_year=1646,
                         area_sq_miles=18.1),
                CityInfo('Syracuse', 'New York', 'NY', 148620, 43.0481, -76.1474, 'Eastern', nickname='Salt City',
                         founded_year=1825, area_sq_miles=25.1),
                CityInfo('Albany', 'New York', 'NY', 99189, 42.6526, -73.7562, 'Eastern', is_capital=True,
                         founded_year=1686, area_sq_miles=21.4),
            ],

            # 佛罗里达州
            'FL': [
                CityInfo('Jacksonville', 'Florida', 'FL', 949611, 30.3322, -81.6557, 'Eastern', nickname='River City',
                         founded_year=1822, area_sq_miles=747.3),
                CityInfo('Miami', 'Florida', 'FL', 467963, 25.7617, -80.1918, 'Eastern', nickname='The Magic City',
                         founded_year=1896, area_sq_miles=35.9),
                CityInfo('Tampa', 'Florida', 'FL', 399700, 27.9506, -82.4572, 'Eastern', founded_year=1823,
                         area_sq_miles=113.4),
                CityInfo('Orlando', 'Florida', 'FL', 316081, 28.5383, -81.3792, 'Eastern',
                         nickname='The City Beautiful', founded_year=1875, area_sq_miles=110.6),
                CityInfo('St. Petersburg', 'Florida', 'FL', 265098, 27.7676, -82.6403, 'Eastern',
                         nickname='The Sunshine City', founded_year=1888, area_sq_miles=61.7),
                CityInfo('Tallahassee', 'Florida', 'FL', 196068, 30.4383, -84.2807, 'Eastern', is_capital=True,
                         founded_year=1824, area_sq_miles=100.0),
                CityInfo('Fort Lauderdale', 'Florida', 'FL', 182760, 26.1224, -80.1373, 'Eastern',
                         nickname='Venice of America', founded_year=1911, area_sq_miles=34.6),
                CityInfo('Port St. Lucie', 'Florida', 'FL', 204851, 27.2730, -80.3582, 'Eastern', founded_year=1961,
                         area_sq_miles=76.0),
            ],

            # 伊利诺伊州
            'IL': [
                CityInfo('Chicago', 'Illinois', 'IL', 2746388, 41.8781, -87.6298, 'Central', nickname='The Windy City',
                         founded_year=1837, area_sq_miles=227.3),
                CityInfo('Aurora', 'Illinois', 'IL', 180542, 41.7606, -88.3201, 'Central', founded_year=1834,
                         area_sq_miles=44.9),
                CityInfo('Naperville', 'Illinois', 'IL', 149540, 41.7508, -88.1535, 'Central', founded_year=1831,
                         area_sq_miles=39.1),
                CityInfo('Joliet', 'Illinois', 'IL', 150362, 41.5250, -88.0817, 'Central',
                         nickname='City of Steel and Stone', founded_year=1834, area_sq_miles=62.1),
                CityInfo('Rockford', 'Illinois', 'IL', 148655, 42.2711, -89.0937, 'Central', nickname='The Forest City',
                         founded_year=1834, area_sq_miles=61.9),
                CityInfo('Springfield', 'Illinois', 'IL', 114394, 39.7817, -89.6501, 'Central', is_capital=True,
                         nickname='The Flower City', founded_year=1821, area_sq_miles=60.3),
            ],

            # 宾夕法尼亚州
            'PA': [
                CityInfo('Philadelphia', 'Pennsylvania', 'PA', 1584138, 39.9526, -75.1652, 'Eastern',
                         nickname='The City of Brotherly Love', founded_year=1682, area_sq_miles=134.2),
                CityInfo('Pittsburgh', 'Pennsylvania', 'PA', 300431, 40.4406, -79.9959, 'Eastern',
                         nickname='The Steel City', founded_year=1758, area_sq_miles=55.4),
                CityInfo('Allentown', 'Pennsylvania', 'PA', 125845, 40.6084, -75.4902, 'Eastern',
                         nickname='The Queen City', founded_year=1762, area_sq_miles=17.6),
                CityInfo('Erie', 'Pennsylvania', 'PA', 93328, 42.1292, -80.0851, 'Eastern', founded_year=1795,
                         area_sq_miles=19.1),
                CityInfo('Harrisburg', 'Pennsylvania', 'PA', 50099, 40.2732, -76.8867, 'Eastern', is_capital=True,
                         founded_year=1719, area_sq_miles=8.1),
            ],

            # 亚利桑那州
            'AZ': [
                CityInfo('Phoenix', 'Arizona', 'AZ', 1698121, 33.4484, -112.0740, 'Mountain', is_capital=True,
                         nickname='The Valley of the Sun', founded_year=1867, area_sq_miles=517.6),
                CityInfo('Tucson', 'Arizona', 'AZ', 542629, 32.2226, -110.9747, 'Mountain', founded_year=1775,
                         area_sq_miles=241.0),
                CityInfo('Mesa', 'Arizona', 'AZ', 518012, 33.4152, -111.8315, 'Mountain', founded_year=1878,
                         area_sq_miles=136.5),
                CityInfo('Chandler', 'Arizona', 'AZ', 275987, 33.3062, -111.8412, 'Mountain', founded_year=1912,
                         area_sq_miles=64.7),
                CityInfo('Scottsdale', 'Arizona', 'AZ', 258069, 33.4942, -111.9261, 'Mountain', founded_year=1951,
                         area_sq_miles=184.0),
                CityInfo('Gilbert', 'Arizona', 'AZ', 267918, 33.3528, -111.7890, 'Mountain', founded_year=1920,
                         area_sq_miles=68.6),
                CityInfo('Glendale', 'Arizona', 'AZ', 252381, 33.5387, -112.1860, 'Mountain', founded_year=1892,
                         area_sq_miles=61.6),
                CityInfo('Tempe', 'Arizona', 'AZ', 195805, 33.4255, -111.9400, 'Mountain', founded_year=1894,
                         area_sq_miles=39.9),
            ],

            # 俄亥俄州
            'OH': [
                CityInfo('Columbus', 'Ohio', 'OH', 905748, 39.9612, -82.9988, 'Eastern', is_capital=True,
                         nickname='The Discovery City', founded_year=1812, area_sq_miles=217.2),
                CityInfo('Cleveland', 'Ohio', 'OH', 372624, 41.4993, -81.6944, 'Eastern', nickname='The Forest City',
                         founded_year=1796, area_sq_miles=77.7),
                CityInfo('Cincinnati', 'Ohio', 'OH', 309317, 39.1031, -84.5120, 'Eastern', nickname='The Queen City',
                         founded_year=1788, area_sq_miles=77.9),
                CityInfo('Toledo', 'Ohio', 'OH', 270871, 41.6639, -83.5552, 'Eastern', nickname='The Glass City',
                         founded_year=1833, area_sq_miles=80.7),
                CityInfo('Akron', 'Ohio', 'OH', 190469, 41.0814, -81.5190, 'Eastern',
                         nickname='The Rubber Capital of the World', founded_year=1825, area_sq_miles=62.0),
                CityInfo('Dayton', 'Ohio', 'OH', 137644, 39.7589, -84.1916, 'Eastern', nickname='The Gem City',
                         founded_year=1796, area_sq_miles=55.7),
            ],

            # 密歇根州
            'MI': [
                CityInfo('Detroit', 'Michigan', 'MI', 639111, 42.3314, -83.0458, 'Eastern', nickname='Motor City',
                         founded_year=1701, area_sq_miles=138.8),
                CityInfo('Grand Rapids', 'Michigan', 'MI', 201013, 42.9634, -85.6681, 'Eastern',
                         nickname='Furniture City', founded_year=1826, area_sq_miles=44.4),
                CityInfo('Warren', 'Michigan', 'MI', 139387, 42.5145, -83.0147, 'Eastern', founded_year=1837,
                         area_sq_miles=34.4),
                CityInfo('Sterling Heights', 'Michigan', 'MI', 134346, 42.5803, -83.0302, 'Eastern', founded_year=1968,
                         area_sq_miles=36.5),
                CityInfo('Ann Arbor', 'Michigan', 'MI', 123851, 42.2808, -83.7430, 'Eastern', nickname='Tree Town',
                         founded_year=1824, area_sq_miles=28.2),
                CityInfo('Lansing', 'Michigan', 'MI', 118427, 42.7325, -84.5555, 'Eastern', is_capital=True,
                         founded_year=1835, area_sq_miles=36.7),
            ],

            # 印第安纳州
            'IN': [
                CityInfo('Indianapolis', 'Indiana', 'IN', 876384, 39.7684, -86.1581, 'Eastern', is_capital=True,
                         nickname='The Crossroads of America', founded_year=1821, area_sq_miles=361.5),
                CityInfo('Fort Wayne', 'Indiana', 'IN', 267927, 41.0793, -85.1394, 'Eastern',
                         nickname='The Summit City', founded_year=1794, area_sq_miles=110.6),
                CityInfo('Evansville', 'Indiana', 'IN', 117429, 37.9716, -87.5711, 'Central', nickname='River City',
                         founded_year=1812, area_sq_miles=44.2),
                CityInfo('South Bend', 'Indiana', 'IN', 103353, 41.6764, -86.2520, 'Eastern', founded_year=1865,
                         area_sq_miles=41.5),
                CityInfo('Carmel', 'Indiana', 'IN', 101068, 39.9784, -86.1180, 'Eastern', founded_year=1837,
                         area_sq_miles=48.1),
            ],

            # 乔治亚州
            'GA': [
                CityInfo('Atlanta', 'Georgia', 'GA', 506811, 33.7490, -84.3880, 'Eastern', is_capital=True,
                         nickname='The Big Peach', founded_year=1837, area_sq_miles=133.5),
                CityInfo('Augusta', 'Georgia', 'GA', 202096, 33.4709, -81.9748, 'Eastern', founded_year=1736,
                         area_sq_miles=302.5),
                CityInfo('Columbus', 'Georgia', 'GA', 206922, 32.4609, -84.9877, 'Eastern', founded_year=1828,
                         area_sq_miles=216.4),
                CityInfo('Savannah', 'Georgia', 'GA', 147780, 32.0809, -81.0912, 'Eastern', nickname='The Hostess City',
                         founded_year=1733, area_sq_miles=103.1),
                CityInfo('Athens', 'Georgia', 'GA', 127315, 33.9519, -83.3576, 'Eastern', nickname='The Classic City',
                         founded_year=1806, area_sq_miles=118.2),
            ],

            # 北卡罗来纳州
            'NC': [
                CityInfo('Charlotte', 'North Carolina', 'NC', 885708, 35.2271, -80.8431, 'Eastern',
                         nickname='The Queen City', founded_year=1768, area_sq_miles=297.7),
                CityInfo('Raleigh', 'North Carolina', 'NC', 474069, 35.7796, -78.6382, 'Eastern', is_capital=True,
                         nickname='The City of Oaks', founded_year=1792, area_sq_miles=144.8),
                CityInfo('Greensboro', 'North Carolina', 'NC', 299035, 36.0726, -79.7920, 'Eastern',
                         nickname='The Gate City', founded_year=1808, area_sq_miles=131.2),
                CityInfo('Durham', 'North Carolina', 'NC', 285527, 35.9940, -78.8986, 'Eastern', nickname='Bull City',
                         founded_year=1869, area_sq_miles=107.4),
                CityInfo('Winston-Salem', 'North Carolina', 'NC', 249545, 36.0999, -80.2442, 'Eastern',
                         nickname='Twin City', founded_year=1849, area_sq_miles=132.4),
                CityInfo('Fayetteville', 'North Carolina', 'NC', 208501, 35.0527, -78.8784, 'Eastern',
                         founded_year=1762, area_sq_miles=148.7),
            ],

            # 其他重要城市（各州选几个代表性城市）
            'WA': [
                CityInfo('Seattle', 'Washington', 'WA', 776555, 47.6062, -122.3321, 'Pacific',
                         nickname='The Emerald City', founded_year=1851, area_sq_miles=83.9),
                CityInfo('Spokane', 'Washington', 'WA', 228989, 47.6588, -117.4260, 'Pacific',
                         nickname='The Lilac City', founded_year=1871, area_sq_miles=68.7),
                CityInfo('Tacoma', 'Washington', 'WA', 221776, 47.2529, -122.4443, 'Pacific',
                         nickname='The City of Destiny', founded_year=1875, area_sq_miles=49.7),
                CityInfo('Vancouver', 'Washington', 'WA', 190915, 45.6387, -122.6615, 'Pacific', founded_year=1825,
                         area_sq_miles=46.8),
                CityInfo('Olympia', 'Washington', 'WA', 55205, 47.0379, -122.9007, 'Pacific', is_capital=True,
                         founded_year=1859, area_sq_miles=19.7),
            ],

            'MA': [
                CityInfo('Boston', 'Massachusetts', 'MA', 692600, 42.3601, -71.0589, 'Eastern', is_capital=True,
                         nickname='Beantown', founded_year=1630, area_sq_miles=48.3),
                CityInfo('Worcester', 'Massachusetts', 'MA', 206518, 42.2626, -71.8023, 'Eastern',
                         nickname='The Heart of the Commonwealth', founded_year=1673, area_sq_miles=37.4),
                CityInfo('Springfield', 'Massachusetts', 'MA', 155929, 42.1015, -72.5898, 'Eastern',
                         nickname='The City of Firsts', founded_year=1636, area_sq_miles=31.9),
                CityInfo('Cambridge', 'Massachusetts', 'MA', 118927, 42.3736, -71.1097, 'Eastern', founded_year=1630,
                         area_sq_miles=6.4),
                CityInfo('Lowell', 'Massachusetts', 'MA', 115554, 42.6334, -71.3162, 'Eastern', founded_year=1826,
                         area_sq_miles=13.6),
            ],

            'CO': [
                CityInfo('Denver', 'Colorado', 'CO', 727211, 39.7392, -104.9903, 'Mountain', is_capital=True,
                         nickname='The Mile High City', founded_year=1858, area_sq_miles=154.7),
                CityInfo('Colorado Springs', 'Colorado', 'CO', 478221, 38.8339, -104.8214, 'Mountain',
                         founded_year=1871, area_sq_miles=194.5),
                CityInfo('Aurora', 'Colorado', 'CO', 386261, 39.7294, -104.8319, 'Mountain', founded_year=1891,
                         area_sq_miles=154.2),
                CityInfo('Fort Collins', 'Colorado', 'CO', 169810, 40.5853, -105.0844, 'Mountain', founded_year=1864,
                         area_sq_miles=57.2),
                CityInfo('Lakewood', 'Colorado', 'CO', 156798, 39.7047, -105.0814, 'Mountain', founded_year=1889,
                         area_sq_miles=42.9),
            ],

            'TN': [
                CityInfo('Nashville', 'Tennessee', 'TN', 689447, 36.1627, -86.7816, 'Central', is_capital=True,
                         nickname='Music City', founded_year=1779, area_sq_miles=475.9),
                CityInfo('Memphis', 'Tennessee', 'TN', 633104, 35.1495, -90.0490, 'Central', nickname='Bluff City',
                         founded_year=1819, area_sq_miles=294.8),
                CityInfo('Knoxville', 'Tennessee', 'TN', 190740, 35.9606, -83.9207, 'Eastern',
                         nickname='The Marble City', founded_year=1786, area_sq_miles=98.5),
                CityInfo('Chattanooga', 'Tennessee', 'TN', 181099, 35.0456, -85.3097, 'Eastern',
                         nickname='The Scenic City', founded_year=1839, area_sq_miles=142.2),
                CityInfo('Clarksville', 'Tennessee', 'TN', 166722, 36.5298, -87.3595, 'Central', founded_year=1784,
                         area_sq_miles=97.5),
            ],
        }

        # 构建所有城市的列表
        self.all_cities = []
        for state_cities in self.major_cities.values():
            self.all_cities.extend(state_cities)

    def generate_city(self,
                      state: Optional[str] = None,
                      min_population: int = 0,
                      max_population: int = 10000000,
                      include_capitals: bool = True,
                      exclude_capitals: bool = False) -> CityInfo:
        """生成随机城市"""

        if state and state.upper() in self.major_cities:
            # 特定州的城市
            candidates = [city for city in self.major_cities[state.upper()]
                          if min_population <= city.population <= max_population]

            if not include_capitals:
                candidates = [city for city in candidates if not city.is_capital]
            if exclude_capitals:
                candidates = [city for city in candidates if not city.is_capital]
        else:
            # 所有城市
            candidates = [city for city in self.all_cities
                          if min_population <= city.population <= max_population]

            if not include_capitals:
                candidates = [city for city in candidates if not city.is_capital]
            if exclude_capitals:
                candidates = [city for city in candidates if not city.is_capital]

        if not candidates:
            raise ValueError(f"No cities found matching the criteria")

        return random.choice(candidates)

    def generate_city_name(self,
                           state: Optional[str] = None,
                           include_state: bool = False,
                           format_type: str = 'full') -> str:
        """仅生成城市名"""
        city = self.generate_city(state)

        if format_type == 'full':
            if include_state:
                return f"{city.name}, {city.state_abbr}"
            else:
                return city.name
        elif format_type == 'short':
            return city.name
        elif format_type == 'with_state':
            return f"{city.name}, {city.state}"
        else:
            return city.name

    def generate_multiple_cities(self,
                                 count: int = 10,
                                 state: Optional[str] = None,
                                 unique_states: bool = False) -> List[CityInfo]:
        """生成多个城市"""
        cities = []
        used_states = set()

        for _ in range(count):
            if unique_states and state is None:
                # 确保每个州只选一个城市
                available_states = [s for s in self.major_cities.keys()
                                    if s not in used_states]
                if not available_states:
                    break  # 所有州都已使用
                state = random.choice(available_states)
                used_states.add(state)

            city = self.generate_city(state)
            cities.append(city)

            if state is not None:
                # 重置state为None以允许随机选择
                state = None

        return cities

    def generate_capital(self, state: Optional[str] = None) -> CityInfo:
        """生成州首府"""
        if state:
            state_abbr = state.upper()
            if state_abbr in self.state_capitals:
                capital_name = self.state_capitals[state_abbr]
                # 查找首府城市信息
                for city in self.major_cities.get(state_abbr, []):
                    if city.name == capital_name:
                        return city
                # 如果没找到详细信息，创建一个基本对象
                return CityInfo(
                    name=capital_name,
                    state=self.states[state_abbr],
                    state_abbr=state_abbr,
                    population=random.randint(50000, 500000),
                    latitude=random.uniform(25.0, 49.0),
                    longitude=random.uniform(-125.0, -67.0),
                    timezone='Eastern' if state_abbr in ['ME', 'NH', 'VT', 'MA', 'RI', 'CT', 'NY', 'NJ', 'PA', 'DE',
                                                         'MD', 'DC', 'VA', 'WV', 'NC', 'SC', 'GA', 'FL'] else
                    'Central' if state_abbr in ['AL', 'AR', 'IL', 'IA', 'KS', 'KY', 'LA', 'MN', 'MS', 'MO', 'NE', 'ND',
                                                'OK', 'SD', 'TN', 'TX', 'WI'] else
                    'Mountain' if state_abbr in ['AZ', 'CO', 'ID', 'MT', 'NM', 'UT', 'WY'] else 'Pacific',
                    is_capital=True
                )
            else:
                raise ValueError(f"Invalid state abbreviation: {state}")

        # 随机选择一个州的首府
        random_state = random.choice(list(self.state_capitals.keys()))
        return self.generate_capital(random_state)

    def get_cities_by_population(self,
                                 min_pop: int = 0,
                                 max_pop: int = 10000000,
                                 limit: int = 50) -> List[CityInfo]:
        """按人口范围获取城市"""
        filtered = [city for city in self.all_cities
                    if min_pop <= city.population <= max_pop]
        filtered.sort(key=lambda x: x.population, reverse=True)
        return filtered[:limit]

    def get_cities_by_state(self, state: str) -> List[CityInfo]:
        """获取指定州的所有城市"""
        state_abbr = state.upper()
        return self.major_cities.get(state_abbr, [])

    def search_cities(self,
                      name_pattern: str = '',
                      state: Optional[str] = None,
                      min_population: int = 0,
                      max_population: int = 10000000) -> List[CityInfo]:
        """搜索城市"""
        results = []

        search_cities = self.all_cities
        if state:
            state_abbr = state.upper()
            search_cities = self.major_cities.get(state_abbr, [])

        for city in search_cities:
            if (min_population <= city.population <= max_population and
                    name_pattern.lower() in city.name.lower()):
                results.append(city)

        return results

    def generate_city_with_details(self,
                                   state: Optional[str] = None) -> Dict:
        """生成带有详细信息的城市"""
        city = self.generate_city(state)

        return {
            'name': city.name,
            'state': city.state,
            'state_abbr': city.state_abbr,
            'population': city.population,
            'population_formatted': f"{city.population:,}",
            'coordinates': {
                'latitude': city.latitude,
                'longitude': city.longitude
            },
            'timezone': city.timezone,
            'is_state_capital': city.is_capital,
            'nickname': city.nickname,
            'founded_year': city.founded_year,
            'area_sq_miles': city.area_sq_miles,
            'description': self._generate_city_description(city)
        }

    @classmethod
    def _generate_city_description(cls, city: CityInfo) -> str:
        """生成城市描述"""
        descriptions = [
            f"{city.name} is a vibrant city in {city.state} with a population of {city.population:,}.",
            f"Located in {city.state}, {city.name} is known for its rich history and culture.",
            f"{city.name}, {city.state_abbr} is a major urban center with diverse communities.",
            f"The city of {city.name} in {city.state} offers a unique blend of tradition and modernity.",
            f"{city.name} is situated at coordinates {city.latitude:.4f}°N, {city.longitude:.4f}°W.",
        ]

        if city.nickname:
            descriptions.append(f"Often called '{city.nickname}', {city.name} is a key city in {city.state}.")

        if city.is_capital:
            descriptions.append(f"As the capital of {city.state}, {city.name} plays a crucial role in state politics.")

        if city.founded_year:
            descriptions.append(f"Founded in {city.founded_year}, {city.name} has a long and storied history.")

        return random.choice(descriptions)

    def generate_random_state(self) -> Tuple[str, str]:
        """随机生成州"""
        state_abbr = random.choice(list(self.states.keys()))
        return state_abbr, self.states[state_abbr]

    def get_state_info(self, state: str) -> Dict:
        """获取州信息"""
        state_abbr = state.upper()
        if state_abbr not in self.states:
            raise ValueError(f"Invalid state abbreviation: {state}")

        cities = self.major_cities.get(state_abbr, [])
        capital = self.state_capitals.get(state_abbr, 'Unknown')

        return {
            'abbreviation': state_abbr,
            'name': self.states[state_abbr],
            'capital': capital,
            'major_cities_count': len(cities),
            'total_population_estimate': sum(c.population for c in cities),
            'largest_city': max(cities, key=lambda x: x.population).name if cities else 'Unknown'
        }


class StreetType(Enum):
    """街道类型枚举"""
    STREET = "Street"
    AVENUE = "Avenue"
    ROAD = "Road"
    BOULEVARD = "Boulevard"
    DRIVE = "Drive"
    LANE = "Lane"
    COURT = "Court"
    PLACE = "Place"
    TERRACE = "Terrace"
    CIRCLE = "Circle"
    WAY = "Way"
    TRAIL = "Trail"
    PARKWAY = "Parkway"
    HIGHWAY = "Highway"
    FREEWAY = "Freeway"
    EXPRESSWAY = "Expressway"


class Direction(Enum):
    """方向枚举"""
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"
    NORTHEAST = "NE"
    NORTHWEST = "NW"
    SOUTHEAST = "SE"
    SOUTHWEST = "SW"


@dataclass
class StreetName:
    """街道名信息"""
    name: str
    type: StreetType
    direction: Optional[Direction] = None
    suffix: Optional[str] = None
    is_numbered: bool = False


@dataclass
class StreetAddress:
    """街道地址信息"""
    number: int
    street_name: StreetName
    apartment: Optional[str] = None
    city: str = ""
    state: str = ""
    zip_code: str = ""
    full_address: str = ""


class USStreetGenerator:
    """美国街道地址生成器"""

    def __init__(self):
        # 美国常见的街道名前缀
        self.street_prefixes = [
            'Main', 'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth',
            'Ninth', 'Tenth', 'Park', 'Washington', 'Jefferson', 'Lincoln', 'Madison', 'Monroe',
            'Adams', 'Jackson', 'Grant', 'Wilson', 'Roosevelt', 'Kennedy', 'Johnson', 'Nixon',
            'Carter', 'Reagan', 'Bush', 'Clinton', 'Obama', 'Trump', 'Biden', 'Elm', 'Oak',
            'Maple', 'Pine', 'Cedar', 'Birch', 'Walnut', 'Chestnut', 'Hickory', 'Willow',
            'Magnolia', 'Sycamore', 'Poplar', 'Ash', 'Beech', 'Cherry', 'Apple', 'Peach',
            'Pear', 'Orange', 'Lemon', 'Lime', 'River', 'Lake', 'Ocean', 'Sea', 'Mountain',
            'Hill', 'Valley', 'Forest', 'Meadow', 'Field', 'Brook', 'Creek', 'Spring', 'Summer',
            'Winter', 'Autumn', 'Sunset', 'Sunrise', 'Morning', 'Evening', 'Night', 'Day',
            'Moon', 'Star', 'Sky', 'Cloud', 'Rain', 'Snow', 'Wind', 'Storm', 'Lightning',
            'Thunder', 'Rainbow', 'Golden', 'Silver', 'Diamond', 'Ruby', 'Emerald', 'Sapphire',
            'Pearl', 'Crystal', 'Amber', 'Coral', 'Jade', 'Opal', 'Platinum', 'Bronze',
            'Copper', 'Iron', 'Steel', 'Stone', 'Rock', 'Granite', 'Marble', 'Sandstone',
            'Cobblestone', 'Brick', 'Cement', 'Concrete', 'Glass', 'Wood', 'Timber', 'Log',
            'Pioneer', 'Settler', 'Explorer', 'Trailblazer', 'Frontier', 'Homestead', 'Ranch',
            'Farm', 'Orchard', 'Vineyard', 'Garden', 'Greenhouse', 'Barn', 'Stable', 'Pasture',
            'Prairie', 'Plain', 'Plateau', 'Canyon', 'Ravine', 'Gorge', 'Cliff', 'Ridge',
            'Summit', 'Peak', 'Slope', 'Base', 'Foot', 'Shore', 'Beach', 'Coast', 'Harbor',
            'Port', 'Dock', 'Pier', 'Wharf', 'Marina', 'Yacht', 'Sail', 'Anchor', 'Compass',
            'Map', 'Globe', 'World', 'Nation', 'State', 'County', 'Town', 'Village', 'City',
            'Capital', 'Metro', 'Urban', 'Suburban', 'Rural', 'Country', 'International',
            'National', 'Regional', 'Local', 'Community', 'Neighborhood', 'District', 'Ward',
            'Precinct', 'Division', 'Section', 'Quarter', 'Zone', 'Area', 'Territory',
            'Province', 'Department', 'Bureau', 'Office', 'Agency', 'Center', 'Complex',
            'Facility', 'Building', 'Tower', 'Plaza', 'Square', 'Circle', 'Roundabout',
            'Intersection', 'Junction', 'Crossing', 'Overpass', 'Underpass', 'Bridge', 'Tunnel',
            'Highway', 'Expressway', 'Freeway', 'Parkway', 'Turnpike', 'Bypass', 'Beltway',
            'Loop', 'Ring', 'Orbital', 'Radial', 'Diagonal', 'Transverse', 'Longitudinal',
            'Meridian', 'Parallel', 'Equator', 'Tropic', 'Arctic', 'Antarctic', 'Polar',
            'Temperate', 'Tropical', 'Subtropical', 'Desert', 'Oasis', 'Mirage', 'Cactus',
            'Palm', 'Fern', 'Moss', 'Lichen', 'Algae', 'Fungus', 'Mushroom', 'Flower', 'Bud',
            'Bloom', 'Blossom', 'Petal', 'Stem', 'Root', 'Seed', 'Sprout', 'Sapling', 'Tree',
            'Bush', 'Shrub', 'Hedge', 'Lawn', 'Turf', 'Sod', 'Grass', 'Weed', 'Dandelion',
            'Daisy', 'Rose', 'Lily', 'Tulip', 'Iris', 'Orchid', 'Sunflower', 'Daffodil',
            'Carnation', 'Poppy', 'Violet', 'Lavender', 'Lilac', 'Jasmine', 'Honeysuckle',
            'Wisteria', 'Hydrangea', 'Azalea', 'Rhododendron', 'Camellia', 'Gardenia',
            'Magnolia', 'Dogwood', 'Redwood', 'Sequoia', 'Redwood', 'Fir', 'Pine', 'Spruce',
            'Hemlock', 'Cypress', 'Juniper', 'Cedar', 'Yew', 'Holly', 'Ivy', 'Vine', 'Grape',
            'Berry', 'Strawberry', 'Blueberry', 'Raspberry', 'Blackberry', 'Cranberry',
            'Gooseberry', 'Currant', 'Elderberry', 'Boysenberry', 'Loganberry', 'Marionberry',
            'Apple', 'Pear', 'Peach', 'Plum', 'Cherry', 'Apricot', 'Nectarine', 'Fig', 'Date',
            'Prune', 'Raisin', 'Grape', 'Kiwi', 'Mango', 'Papaya', 'Pineapple', 'Coconut',
            'Banana', 'Plantain', 'Avocado', 'Olive', 'Lemon', 'Lime', 'Orange', 'Grapefruit',
            'Tangerine', 'Mandarin', 'Clementine', 'Kumquat', 'Persimmon', 'Pomegranate',
            'Guava', 'Passionfruit', 'Dragonfruit', 'Starfruit', 'Jackfruit', 'Durian',
            'Rambutan', 'Lychee', 'Longan', 'Mangosteen', 'Soursop', 'Breadfruit', 'Carambola',
            'Feijoa', 'Pitanga', 'Sapodilla', 'Sugar', 'Spice', 'Salt', 'Pepper', 'Cinnamon',
            'Nutmeg', 'Clove', 'Ginger', 'Garlic', 'Onion', 'Chive', 'Shallot', 'Leek',
            'Scallion', 'Horseradish', 'Wasabi', 'Mustard', 'Ketchup', 'Mayonnaise', 'Relish',
            'Pickle', 'Olive', 'Caper', 'Anchovy', 'Sardine', 'Tuna', 'Salmon', 'Trout',
            'Bass', 'Perch', 'Walleye', 'Pike', 'Catfish', 'Carp', 'Goldfish', 'Koi',
            'Guppy', 'Betta', 'Angelfish', 'Neon', 'Tetra', 'Barracuda', 'Shark', 'Ray',
            'Dolphin', 'Whale', 'Seal', 'Walrus', 'Manatee', 'Otter', 'Beaver', 'Muskrat',
            'Opossum', 'Raccoon', 'Skunk', 'Badger', 'Weasel', 'Ferret', 'Mink', 'Marten',
            'Fisher', 'Wolverine', 'Otter', 'Mongoose', 'Meerkat', 'Prairie', 'Groundhog',
            'Woodchuck', 'Marmot', 'Chipmunk', 'Squirrel', 'Gopher', 'Mole', 'Shrew', 'Vole',
            'Lemming', 'Hamster', 'Gerbil', 'Guinea', 'Chinchilla', 'Capybara', 'Agouti',
            'Paca', 'Coypu', 'Nutria', 'Beaver', 'Porcupine', 'Hedgehog', 'Tenrec', 'Solenodon',
            'Desman', 'Mole', 'Star', 'Sun', 'Moon', 'Planet', 'Comet', 'Asteroid', 'Meteor',
            'Galaxy', 'Nebula', 'Quasar', 'Pulsar', 'Black', 'White', 'Red', 'Blue', 'Green',
            'Yellow', 'Orange', 'Purple', 'Pink', 'Brown', 'Gray', 'Black', 'White', 'Ivory',
            'Cream', 'Beige', 'Tan', 'Khaki', 'Olive', 'Teal', 'Turquoise', 'Aqua', 'Cyan',
            'Magenta', 'Violet', 'Indigo', 'Lavender', 'Lilac', 'Mauve', 'Maroon', 'Burgundy',
            'Scarlet', 'Crimson', 'Ruby', 'Garnet', 'Amethyst', 'Emerald', 'Jade', 'Peridot',
            'Topaz', 'Citrine', 'Amber', 'Coral', 'Pearl', 'Opal', 'Diamond', 'Platinum',
            'Gold', 'Silver', 'Bronze', 'Copper', 'Iron', 'Steel', 'Tin', 'Lead', 'Zinc',
            'Nickel', 'Aluminum', 'Titanium', 'Tungsten', 'Molybdenum', 'Chromium', 'Vanadium',
            'Manganese', 'Cobalt', 'Cadmium', 'Mercury', 'Arsenic', 'Antimony', 'Bismuth',
            'Selenium', 'Tellurium', 'Polonium', 'Astatine', 'Radon', 'Francium', 'Radium',
            'Actinium', 'Thorium', 'Protactinium', 'Uranium', 'Neptunium', 'Plutonium',
            'Americium', 'Curium', 'Berkelium', 'Californium', 'Einsteinium', 'Fermium',
            'Mendelevium', 'Nobelium', 'Lawrencium', 'Rutherfordium', 'Dubnium', 'Seaborgium',
            'Bohrium', 'Hassium', 'Meitnerium', 'Darmstadtium', 'Roentgenium', 'Copernicium',
            'Nihonium', 'Flerovium', 'Moscovium', 'Livermorium', 'Tennessine', 'Oganesson'
        ]

        # 街道类型及其常见缩写
        self.street_types = {
            StreetType.STREET: ['St', 'Street'],
            StreetType.AVENUE: ['Ave', 'Avenue'],
            StreetType.ROAD: ['Rd', 'Road'],
            StreetType.BOULEVARD: ['Blvd', 'Boulevard'],
            StreetType.DRIVE: ['Dr', 'Drive'],
            StreetType.LANE: ['Ln', 'Lane'],
            StreetType.COURT: ['Ct', 'Court'],
            StreetType.PLACE: ['Pl', 'Place'],
            StreetType.TERRACE: ['Ter', 'Terrace'],
            StreetType.CIRCLE: ['Cir', 'Circle'],
            StreetType.WAY: ['Way'],
            StreetType.TRAIL: ['Trl', 'Trail'],
            StreetType.PARKWAY: ['Pkwy', 'Parkway'],
            StreetType.HIGHWAY: ['Hwy', 'Highway'],
            StreetType.FREEWAY: ['Fwy', 'Freeway'],
            StreetType.EXPRESSWAY: ['Expy', 'Expressway']
        }

        # 方向及其缩写
        self.directions = {
            Direction.NORTH: 'N',
            Direction.SOUTH: 'S',
            Direction.EAST: 'E',
            Direction.WEST: 'W',
            Direction.NORTHEAST: 'NE',
            Direction.NORTHWEST: 'NW',
            Direction.SOUTHEAST: 'SE',
            Direction.SOUTHWEST: 'SW'
        }

        # 美国州及其缩写
        self.states = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
        }

        # 美国主要城市
        self.cities = {
            'CA': ['Los Angeles', 'San Diego', 'San Jose', 'San Francisco', 'Fresno', 'Sacramento',
                   'Long Beach', 'Oakland', 'Bakersfield', 'Anaheim', 'Santa Ana', 'Riverside',
                   'Stockton', 'Irvine', 'Chula Vista', 'Fremont', 'San Bernardino', 'Modesto'],
            'NY': ['New York City', 'Buffalo', 'Rochester', 'Yonkers', 'Syracuse', 'Albany',
                   'New Rochelle', 'Mount Vernon', 'Schenectady', 'Utica', 'White Plains'],
            'TX': ['Houston', 'San Antonio', 'Dallas', 'Austin', 'Fort Worth', 'El Paso',
                   'Arlington', 'Corpus Christi', 'Plano', 'Laredo', 'Lubbock', 'Garland',
                   'Irving', 'Amarillo', 'Grand Prairie', 'Brownsville', 'McKinney', 'Frisco'],
            'FL': ['Jacksonville', 'Miami', 'Tampa', 'Orlando', 'St. Petersburg', 'Tallahassee',
                   'Fort Lauderdale', 'Port St. Lucie', 'Cape Coral', 'Hollywood', 'Gainesville'],
            'IL': ['Chicago', 'Aurora', 'Naperville', 'Joliet', 'Rockford', 'Springfield',
                   'Elgin', 'Waukegan', 'Cicero', 'Champaign', 'Bloomington'],
            'PA': ['Philadelphia', 'Pittsburgh', 'Allentown', 'Erie', 'Harrisburg', 'Reading',
                   'Scranton', 'Bethlehem', 'Lancaster', 'Altoona'],
            'OH': ['Columbus', 'Cleveland', 'Cincinnati', 'Toledo', 'Akron', 'Dayton',
                   'Parma', 'Canton', 'Youngstown', 'Lorain', 'Hamilton'],
            'GA': ['Atlanta', 'Augusta', 'Columbus', 'Savannah', 'Athens', 'Sandy Springs',
                   'Roswell', 'Macon', 'Johns Creek', 'Albany'],
            'NC': ['Charlotte', 'Raleigh', 'Greensboro', 'Durham', 'Winston-Salem', 'Fayetteville',
                   'Cary', 'Wilmington', 'High Point', 'Greenville'],
            'MI': ['Detroit', 'Grand Rapids', 'Warren', 'Sterling Heights', 'Ann Arbor', 'Lansing',
                   'Flint', 'Dearborn', 'Livonia', 'Troy'],
            'NJ': ['Newark', 'Jersey City', 'Paterson', 'Elizabeth', 'Trenton', 'Clifton',
                   'Camden', 'Passaic', 'Union City', 'Bayonne'],
            'VA': ['Virginia Beach', 'Norfolk', 'Chesapeake', 'Richmond', 'Newport News',
                   'Alexandria', 'Hampton', 'Roanoke', 'Portsmouth', 'Suffolk'],
            'WA': ['Seattle', 'Spokane', 'Tacoma', 'Vancouver', 'Bellevue', 'Kent', 'Everett',
                   'Renton', 'Federal Way', 'Yakima'],
            'AZ': ['Phoenix', 'Tucson', 'Mesa', 'Chandler', 'Scottsdale', 'Gilbert', 'Glendale',
                   'Tempe', 'Peoria', 'Surprise'],
            'MA': ['Boston', 'Worcester', 'Springfield', 'Cambridge', 'Lowell', 'Brockton',
                   'New Bedford', 'Quincy', 'Lynn', 'Fall River'],
            'TN': ['Nashville', 'Memphis', 'Knoxville', 'Chattanooga', 'Clarksville', 'Murfreesboro',
                   'Franklin', 'Jackson', 'Johnson City', 'Bartlett'],
            'IN': ['Indianapolis', 'Fort Wayne', 'Evansville', 'South Bend', 'Carmel', 'Bloomington',
                   'Fishers', 'Hammond', 'Gary', 'Lafayette'],
            'MO': ['Kansas City', 'St. Louis', 'Springfield', 'Columbia', 'Independence', "Lee's Summit",
                   "O'Fallon", 'St. Joseph', 'St. Charles', 'Blue Springs'],
            'MD': ['Baltimore', 'Frederick', 'Rockville', 'Gaithersburg', 'Bowie', 'Hagerstown',
                   'Annapolis', 'College Park', 'Salisbury', 'Cumberland'],
            'WI': ['Milwaukee', 'Madison', 'Green Bay', 'Kenosha', 'Racine', 'Appleton', 'Waukesha',
                   'Eau Claire', 'Oshkosh', 'Janesville'],
            'CO': ['Denver', 'Colorado Springs', 'Aurora', 'Fort Collins', 'Lakewood', 'Thornton',
                   'Arvada', 'Westminster', 'Pueblo', 'Centennial'],
            'MN': ['Minneapolis', 'St. Paul', 'Rochester', 'Bloomington', 'Duluth', 'Brooklyn Park',
                   'Plymouth', 'St. Cloud', 'Eagan', 'Woodbury'],
            'SC': ['Charleston', 'Columbia', 'North Charleston', 'Mount Pleasant', 'Rock Hill',
                   'Greenville', 'Summerville', 'Sumter', 'Goose Creek', 'Hilton Head Island'],
            'AL': ['Birmingham', 'Montgomery', 'Mobile', 'Huntsville', 'Tuscaloosa', 'Hoover',
                   'Dothan', 'Auburn', 'Decatur', 'Madison'],
            'LA': ['New Orleans', 'Baton Rouge', 'Shreveport', 'Lafayette', 'Lake Charles',
                   'Kenner', 'Bossier City', 'Monroe', 'Alexandria', 'Houma'],
            'KY': ['Louisville', 'Lexington', 'Bowling Green', 'Owensboro', 'Covington', 'Richmond',
                   'Georgetown', 'Florence', 'Hopkinsville', 'Nicholasville'],
            'OR': ['Portland', 'Salem', 'Eugene', 'Gresham', 'Hillsboro', 'Beaverton', 'Bend',
                   'Medford', 'Springfield', 'Corvallis'],
            'OK': ['Oklahoma City', 'Tulsa', 'Norman', 'Broken Arrow', 'Lawton', 'Edmond',
                   'Moore', 'Midwest City', 'Enid', 'Stillwater']
        }

        # 公寓类型
        self.apartment_types = ['Apt', 'Apartment', 'Unit', 'Suite', 'Ste', '#']

        # 特殊街道名（名人、地标等）
        self.special_streets = [
            'Broadway', 'Wall Street', 'Times Square', 'Sunset Boulevard', 'Rodeo Drive',
            'Michigan Avenue', 'Bourbon Street', 'Beacon Street', 'Pennsylvania Avenue',
            'Lombard Street', 'Abbey Road', 'Cedar Street', 'Elm Street', 'Oak Street',
            'Maple Street', 'Pine Street', 'Chestnut Street', 'Walnut Street', 'Willow Street',
            'Cherry Street', 'Apple Street', 'Peach Street', 'Pear Street', 'Orange Street',
            'Lemon Street', 'Lime Street', 'River Street', 'Lake Street', 'Ocean Street',
            'Sea Street', 'Mountain Street', 'Hill Street', 'Valley Street', 'Forest Street',
            'Meadow Street', 'Field Street', 'Brook Street', 'Creek Street', 'Spring Street',
            'Summer Street', 'Winter Street', 'Autumn Street', 'Sunset Street', 'Sunrise Street',
            'Morning Street', 'Evening Street', 'Night Street', 'Day Street', 'Moon Street',
            'Star Street', 'Sky Street', 'Cloud Street', 'Rain Street', 'Snow Street',
            'Wind Street', 'Storm Street', 'Lightning Street', 'Thunder Street', 'Rainbow Street'
        ]

        # 数字街道（1st, 2nd, 3rd等）
        self.numbered_streets = {
            1: 'First', 2: 'Second', 3: 'Third', 4: 'Fourth', 5: 'Fifth',
            6: 'Sixth', 7: 'Seventh', 8: 'Eighth', 9: 'Ninth', 10: 'Tenth',
            11: 'Eleventh', 12: 'Twelfth', 13: 'Thirteenth', 14: 'Fourteenth', 15: 'Fifteenth',
            16: 'Sixteenth', 17: 'Seventeenth', 18: 'Eighteenth', 19: 'Nineteenth', 20: 'Twentieth',
            21: 'Twenty-First', 22: 'Twenty-Second', 23: 'Twenty-Third', 24: 'Twenty-Fourth',
            25: 'Twenty-Fifth', 26: 'Twenty-Sixth', 27: 'Twenty-Seventh', 28: 'Twenty-Eighth',
            29: 'Twenty-Ninth', 30: 'Thirtieth', 31: 'Thirty-First', 32: 'Thirty-Second',
            33: 'Thirty-Third', 34: 'Thirty-Fourth', 35: 'Thirty-Fifth', 36: 'Thirty-Sixth',
            37: 'Thirty-Seventh', 38: 'Thirty-Eighth', 39: 'Thirty-Ninth', 40: 'Fortieth',
            41: 'Forty-First', 42: 'Forty-Second', 43: 'Forty-Third', 44: 'Forty-Fourth',
            45: 'Forty-Fifth', 46: 'Forty-Sixth', 47: 'Forty-Seventh', 48: 'Forty-Eighth',
            49: 'Forty-Ninth', 50: 'Fiftieth'
        }

        # 邮编前缀（基于州）
        self.zip_prefixes = {
            'AL': ['350', '351', '352', '354', '356', '357', '358', '359', '360', '361', '362', '363', '364', '365',
                   '366', '367', '368'],
            'AK': ['995', '996', '997', '998', '999'],
            'AZ': ['850', '851', '852', '853', '855', '856', '857', '859'],
            'AR': ['716', '717', '718', '719', '720', '721', '722', '723', '724', '725', '726', '727', '728'],
            'CA': ['900', '901', '902', '903', '904', '905', '906', '907', '908', '910', '911', '912', '913', '914',
                   '915', '916', '917', '918', '919', '920', '921', '922', '923', '924', '925', '926', '927', '928',
                   '930', '931', '932', '933', '934', '935', '936', '937', '938', '939', '940', '941', '942', '943',
                   '944', '945', '946', '947', '948', '949', '950', '951', '952', '953', '954', '955', '956', '957',
                   '958', '959'],
            'CO': ['800', '801', '802', '803', '804', '805', '806', '807', '808', '810', '811', '812', '813', '814',
                   '815', '816', '817', '818'],
            'CT': ['060', '061', '062', '063', '064', '065', '066', '067', '068'],
            'DE': ['197', '198', '199'],
            'DC': ['200', '202', '203', '204', '205'],
            'FL': ['320', '321', '322', '323', '324', '325', '326', '327', '328', '329', '330', '331', '332', '333',
                   '334', '335', '336', '337', '338', '339', '340', '341', '342', '344', '346', '347'],
            'GA': ['300', '301', '302', '303', '304', '305', '306', '307', '308', '309', '310', '311', '312', '313',
                   '314', '315', '316', '317', '318', '319'],
            'HI': ['967', '968'],
            'ID': ['832', '833', '834', '835', '836', '837', '838'],
            'IL': ['600', '601', '602', '603', '604', '605', '606', '607', '608', '609', '610', '611', '612', '613',
                   '614', '615', '616', '617', '618', '619', '620', '622', '623', '624', '625', '626', '627', '628',
                   '629'],
            'IN': ['460', '461', '462', '463', '464', '465', '466', '467', '468', '469', '470', '471', '472', '473',
                   '474', '475', '476', '477', '478', '479'],
            'IA': ['500', '501', '502', '503', '504', '505', '506', '507', '508', '509', '510', '511', '512', '513',
                   '514', '515', '516', '520', '521', '522', '523', '524', '525', '526', '527', '528'],
            'KS': ['660', '661', '662', '663', '664', '665', '666', '667', '668', '669', '670', '671', '672', '673',
                   '674', '675', '676', '677', '678', '679'],
            'KY': ['400', '401', '402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413',
                   '414', '415', '416', '417', '418', '420', '421', '422', '423', '424', '425', '426', '427', '428'],
            'LA': ['700', '701', '703', '704', '705', '706', '707', '708', '710', '711', '712', '713', '714'],
            'ME': ['039', '040', '041', '042', '043', '044', '045', '046', '047', '048', '049'],
            'MD': ['206', '207', '208', '209', '210', '211', '212', '214', '215', '216', '217', '218'],
            'MA': ['010', '011', '012', '013', '014', '015', '016', '017', '018', '019', '020', '021', '022', '023',
                   '024', '025', '026', '027'],
            'MI': ['480', '481', '482', '483', '484', '485', '486', '487', '488', '489', '490', '491', '492', '493',
                   '494', '495', '496', '497', '498', '499'],
            'MN': ['550', '551', '553', '554', '555', '556', '557', '558', '559', '560', '561', '562', '563', '564',
                   '565', '566', '567'],
            'MS': ['386', '387', '388', '389', '390', '391', '392', '393', '394', '395', '396', '397'],
            'MO': ['630', '631', '633', '634', '635', '636', '637', '638', '639', '640', '641', '644', '645', '646',
                   '647', '648', '649', '650', '651', '652', '653', '654', '655', '656', '657', '658'],
            'MT': ['590', '591', '592', '593', '594', '595', '596', '597', '598', '599'],
            'NE': ['680', '681', '683', '684', '685', '686', '687', '688', '689', '690', '691', '692', '693'],
            'NV': ['889', '890', '891', '893', '894', '895', '897', '898'],
            'NH': ['030', '031', '032', '033', '034', '035', '036', '037', '038'],
            'NJ': ['070', '071', '072', '073', '074', '075', '076', '077', '078', '079', '080', '081', '082', '083',
                   '084', '085', '086', '087', '088'],
            'NM': ['870', '871', '873', '874', '875', '877', '878', '879', '880', '881', '882', '883', '884'],
            'NY': ['100', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113',
                   '114', '115', '116', '117', '118', '119', '120', '121', '122', '123', '124', '125', '126', '127',
                   '128', '129', '130', '131', '132', '133', '134', '135', '136', '137', '138', '139', '140', '141',
                   '142', '143', '144', '145', '146', '147', '148', '149'],
            'NC': ['270', '271', '272', '273', '274', '275', '276', '277', '278', '279', '280', '281', '282', '283',
                   '284', '285', '286', '287', '288', '289'],
            'ND': ['580', '581', '582', '583', '584', '585', '586', '587', '588', '589'],
            'OH': ['430', '431', '432', '433', '434', '435', '436', '437', '438', '439', '440', '441', '442', '443',
                   '444', '445', '446', '447', '448', '449', '450', '451', '452', '453', '454', '455', '456', '457',
                   '458', '459'],
            'OK': ['730', '731', '733', '734', '735', '736', '737', '738', '739', '740', '741', '743', '744', '745',
                   '746', '747', '748', '749'],
            'OR': ['970', '971', '972', '973', '974', '975', '976', '977', '978', '979'],
            'PA': ['150', '151', '152', '153', '154', '155', '156', '157', '158', '159', '160', '161', '162', '163',
                   '164', '165', '166', '167', '168', '169', '170', '171', '172', '173', '174', '175', '176', '177',
                   '178', '179', '180', '181', '182', '183', '184', '185', '186', '187', '188', '189'],
            'RI': ['028', '029'],
            'SC': ['290', '291', '292', '293', '294', '295', '296', '297', '298', '299'],
            'SD': ['570', '571', '572', '573', '574', '575', '576', '577'],
            'TN': ['370', '371', '372', '373', '374', '375', '376', '377', '378', '379', '380', '381', '382', '383',
                   '384', '385'],
            'TX': ['750', '751', '752', '753', '754', '755', '756', '757', '758', '759', '760', '761', '762', '763',
                   '764', '765', '766', '767', '768', '769', '770', '771', '772', '773', '774', '775', '776', '777',
                   '778', '779', '780', '781', '782', '783', '784', '785', '786', '787', '788', '789', '790', '791',
                   '792', '793', '794', '795', '796', '797', '798', '799'],
            'UT': ['840', '841', '842', '843', '844', '845', '846', '847'],
            'VT': ['050', '051', '052', '053', '054', '055', '056', '057', '058', '059'],
            'VA': ['201', '220', '221', '222', '223', '224', '225', '226', '227', '228', '229', '230', '231', '232',
                   '233', '234', '235', '236', '237', '238', '239', '240', '241', '242', '243', '244', '245', '246'],
            'WA': ['980', '981', '982', '983', '984', '985', '986', '987', '988', '989', '990', '991', '992', '993',
                   '994'],
            'WV': ['247', '248', '249', '250', '251', '252', '253', '254', '255', '256', '257', '258', '259', '260',
                   '261', '262', '263', '264', '265', '266', '267', '268'],
            'WI': ['530', '531', '532', '534', '535', '537', '538', '539', '540', '541', '542', '543', '544', '545',
                   '546', '547', '548', '549'],
            'WY': ['820', '821', '822', '823', '824', '825', '826', '827', '828', '829', '830', '831']
        }

        # 地址编号模式
        self.address_patterns = [
            # 简单模式: 123 Main St
            lambda: f"{random.randint(1, 9999)} {random.choice(self.street_prefixes)} {random.choice(self.street_types[StreetType.STREET])}",

            # 带方向: 123 N Main St
            lambda: f"{random.randint(1, 9999)} {random.choice(list(self.directions.values()))} {random.choice(self.street_prefixes)} {random.choice(self.street_types[StreetType.STREET])}",

            # 数字街道: 123 5th Ave
            lambda: f"{random.randint(1, 9999)} {self.numbered_streets[random.randint(1, 20)]} {random.choice(self.street_types[StreetType.AVENUE])}",

            # 特殊街道: 123 Broadway
            lambda: f"{random.randint(1, 9999)} {random.choice(self.special_streets)}",

            # 带后缀: 123 Main St NW
            lambda: f"{random.randint(1, 9999)} {random.choice(self.street_prefixes)} {random.choice(self.street_types[StreetType.STREET])} {random.choice(['NW', 'NE', 'SW', 'SE'])}",

            # 长格式: 123 North Main Street
            lambda: f"{random.randint(1, 9999)} {random.choice(['North', 'South', 'East', 'West'])} {random.choice(self.street_prefixes)} {random.choice(self.street_types[StreetType.STREET])}",

            # 带公寓: 123 Main St Apt 4B
            lambda: f"{random.randint(1, 9999)} {random.choice(self.street_prefixes)} {random.choice(self.street_types[StreetType.STREET])} {random.choice(self.apartment_types)} {random.randint(1, 30)}{random.choice(['', 'A', 'B', 'C'])}"
        ]

    def generate_street_name(self,
                             include_direction: bool = False,
                             include_suffix: bool = False,
                             use_numbered: bool = False,
                             use_special: bool = False) -> StreetName:
        """生成街道名"""

        # 决定街道类型
        street_type = random.choice(list(self.street_types.keys()))

        # 决定是否使用数字街道
        if use_numbered and random.random() > 0.7:
            number = random.randint(1, 50)
            name = self.numbered_streets[number]
            is_numbered = True
        # 决定是否使用特殊街道
        elif use_special and random.random() > 0.7:
            name = random.choice(self.special_streets)
            is_numbered = False
        else:
            # 随机选择前缀
            name = random.choice(self.street_prefixes)
            is_numbered = False

        # 决定是否包含方向
        direction = None
        if include_direction and random.random() > 0.5:
            direction = random.choice(list(self.directions.keys()))

        # 决定是否包含后缀
        suffix = None
        if include_suffix and random.random() > 0.5:
            suffix = random.choice(['NW', 'NE', 'SW', 'SE', 'Ext', 'Ave'])

        return StreetName(
            name=name,
            type=street_type,
            direction=direction,
            suffix=suffix,
            is_numbered=is_numbered
        )

    def format_street_name(self, street_name: StreetName, format_type: str = 'full') -> str:
        """格式化街道名"""

        # 获取街道类型
        type_variants = self.street_types[street_name.type]
        street_type = random.choice(type_variants) if format_type == 'full' else type_variants[0]

        # 构建基本名称
        name_parts = [street_name.name]

        # 添加方向
        if street_name.direction:
            if format_type == 'full':
                direction_name = street_name.direction.name.title()
                name_parts.append(direction_name)
            else:
                name_parts.append(self.directions[street_name.direction])

        # 添加街道类型
        name_parts.append(street_type)

        # 添加后缀
        if street_name.suffix:
            name_parts.append(street_name.suffix)

        return ' '.join(name_parts)

    @classmethod
    def generate_address_number(cls) -> int:
        """生成地址号码"""
        # 地址号码的概率分布
        rand = random.random()
        if rand < 0.4:  # 40% 小号码 (1-99)
            return random.randint(1, 99)
        elif rand < 0.7:  # 30% 中等号码 (100-999)
            return random.randint(100, 999)
        elif rand < 0.9:  # 20% 大号码 (1000-9999)
            return random.randint(1000, 9999)
        else:  # 10% 特大号码 (10000-99999)
            return random.randint(10000, 99999)

    def generate_apartment(self) -> Optional[str]:
        """生成公寓号"""
        if random.random() > 0.6:  # 40% 的地址有公寓号
            apt_type = random.choice(self.apartment_types)

            # 公寓号格式
            formats = [
                # 数字: Apt 101
                lambda: f"{apt_type} {random.randint(1, 300)}",
                # 字母数字: Apt 2A
                lambda: f"{apt_type} {random.randint(1, 30)}{random.choice(['', 'A', 'B', 'C', 'D'])}",
                # 仅数字: #101
                lambda: f"#{random.randint(1, 300)}",
                # 套间: Suite 200
                lambda: f"Suite {random.randint(100, 500)}",
                # 单位: Unit 3B
                lambda: f"Unit {random.randint(1, 30)}{random.choice(['', 'A', 'B', 'C'])}"
            ]

            return random.choice(formats)()
        return None

    def generate_zip_code(self, state: str = None) -> str:
        """生成邮政编码"""
        if state and state.upper() in self.zip_prefixes:
            prefix = random.choice(self.zip_prefixes[state.upper()])
        else:
            # 随机选择州
            random_state = random.choice(list(self.zip_prefixes.keys()))
            prefix = random.choice(self.zip_prefixes[random_state])

        # 生成后4位
        suffix = f"{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}"

        return f"{prefix}{suffix}"

    def generate_city_state(self, state: str = None) -> Tuple[str, str, str]:
        """生成城市、州和缩写"""
        if state and state.upper() in self.states:
            state_abbr = state.upper()
            state_name = self.states[state_abbr]

            if state_abbr in self.cities:
                city = random.choice(self.cities[state_abbr])
            else:
                # 如果没有该州的城市数据，生成一个虚构的
                city = f"{random.choice(self.street_prefixes)}ville"
        else:
            # 随机选择州
            state_abbr = random.choice(list(self.states.keys()))
            state_name = self.states[state_abbr]

            if state_abbr in self.cities:
                city = random.choice(self.cities[state_abbr])
            else:
                city = f"{random.choice(self.street_prefixes)}ville"

        return city, state_name, state_abbr

    def generate_full_address(self,
                              state: str = None,
                              include_apartment: bool = True,
                              format_type: str = 'full') -> StreetAddress:
        """生成完整地址"""

        # 生成地址号码
        number = self.generate_address_number()

        # 生成街道名
        street_name = self.generate_street_name(
            include_direction=random.random() > 0.5,
            include_suffix=random.random() > 0.7,
            use_numbered=random.random() > 0.7,
            use_special=random.random() > 0.3
        )

        # 生成公寓号
        apartment = None
        if include_apartment:
            apartment = self.generate_apartment()

        # 生成城市和州
        city, state_name, state_abbr = self.generate_city_state(state)

        # 生成邮政编码
        zip_code = self.generate_zip_code(state_abbr)

        # 格式化街道名
        formatted_street = self.format_street_name(street_name, format_type)

        # 构建完整地址
        if format_type == 'full':
            # 完整格式: 123 North Main Street, Apt 4B, Anytown, CA 90210
            address_parts = [f"{number} {formatted_street}"]
            if apartment:
                address_parts.append(f"{apartment}")
            address_parts.append(f"{city}, {state_abbr} {zip_code}")
            full_address = ', '.join(address_parts)
        else:
            # 简洁格式: 123 N Main St, Anytown, CA 90210
            address_parts = [f"{number} {formatted_street}"]
            if apartment:
                address_parts.append(f"{apartment}")
            address_parts.append(f"{city}, {state_abbr} {zip_code}")
            full_address = ', '.join(address_parts)

        return StreetAddress(
            number=number,
            street_name=street_name,
            apartment=apartment,
            city=city,
            state=state_name,
            zip_code=zip_code,
            full_address=full_address
        )

    def generate_address_pattern(self) -> str:
        """使用预定义模式生成地址"""
        return random.choice(self.address_patterns)()

    def generate_multiple_addresses(self,
                                    count: int = 10,
                                    state: str = None,
                                    include_apartment: bool = True) -> List[StreetAddress]:
        """生成多个地址"""
        addresses = []
        for _ in range(count):
            address = self.generate_full_address(state, include_apartment)
            addresses.append(address)
        return addresses

    @classmethod
    def parse_address(cls, address: str) -> Optional[Dict]:
        """解析地址字符串"""
        # 简单的地址解析（实际应用可能需要更复杂的解析）
        patterns = [
            r'(?P<number>\d+)\s+(?P<street>.+?),\s+(?P<city>[^,]+),\s+(?P<state>[A-Z]{2})\s+(?P<zip>\d{5}(?:-\d{4})?)',
            r'(?P<number>\d+)\s+(?P<street>.+?)\s+(?P<apartment>Apt\s+\w+),\s+(?P<city>[^,]+),\s+(?P<state>[A-Z]{2})\s+(?P<zip>\d{5})',
        ]

        for pattern in patterns:
            match = re.match(pattern, address)
            if match:
                return match.groupdict()

        return None

    @classmethod
    def generate_address_variations(cls, base_address: StreetAddress) -> List[str]:
        """生成地址的变体"""
        variations = list()

        # 原始地址
        variations.append(base_address.full_address)

        # 缩写街道类型
        if 'Street' in base_address.full_address:
            variations.append(base_address.full_address.replace('Street', 'St'))
        if 'Avenue' in base_address.full_address:
            variations.append(base_address.full_address.replace('Avenue', 'Ave'))
        if 'Road' in base_address.full_address:
            variations.append(base_address.full_address.replace('Road', 'Rd'))

        # 省略逗号
        variations.append(base_address.full_address.replace(', ', ' '))

        # 小写
        variations.append(base_address.full_address.lower())

        # 大写
        variations.append(base_address.full_address.upper())

        # 添加国家
        variations.append(f"{base_address.full_address}, USA")

        return variations

    def get_state_from_zip(self, zip_code: str) -> Optional[str]:
        """根据邮政编码猜测州"""
        # 提取前3位
        prefix = zip_code[:3]

        for state, prefixes in self.zip_prefixes.items():
            if any(zip_code.startswith(p) for p in prefixes):
                return state

        return None


class NumberingStyle(Enum):
    """门牌号编码风格枚举"""
    SIMPLE = "simple"  # 简单数字: 123
    HYPHENATED = "hyphenated"  # 带连字符: 123-456
    FRACTIONAL = "fractional"  # 分数: 123 1/2
    LETTER_SUFFIX = "letter"  # 字母后缀: 123A
    LETTER_PREFIX = "prefix"  # 字母前缀: A123
    BUILDING = "building"  # 楼号: Building 123
    UNIT = "unit"  # 单元: Unit 123
    SUITE = "suite"  # 套间: Suite 123
    APARTMENT = "apartment"  # 公寓: Apartment 123
    RURAL = "rural"  # 农村地址: RR 123 Box 456
    PO_BOX = "po_box"  # 邮政信箱: PO Box 123
    HISTORICAL = "historical"  # 历史地址: 123 1/2 Main St


class StreetTypeSub(Enum):
    """街道类型（影响门牌号范围）"""
    RESIDENTIAL = "residential"  # 住宅街道
    COMMERCIAL = "commercial"  # 商业街道
    DOWNTOWN = "downtown"  # 市中心
    SUBURBAN = "suburban"  # 郊区
    RURAL = "rural"  # 农村
    HIGHWAY = "highway"  # 高速公路
    BOULEVARD = "boulevard"  # 林荫大道
    AVENUE = "avenue"  # 大道
    STREET = "street"  # 街道
    DRIVE = "drive"  # 车道
    COURT = "court"  # 庭院
    LANE = "lane"  # 小巷
    PLACE = "place"  # 广场
    CIRCLE = "circle"  # 圆形道路
    WAY = "way"  # 小路
    TRAIL = "trail"  # 小径


@dataclass
class HouseNumber:
    """门牌号信息"""
    number: str
    style: NumberingStyle
    street_type: Optional[StreetType] = None
    city_type: Optional[str] = None
    is_commercial: bool = False
    is_multi_unit: bool = False
    description: str = ""


class USHouseNumberGenerator:
    """美国门牌号码生成器"""

    def __init__(self):
        # 不同街道类型的门牌号范围
        self.street_type_ranges = {
            StreetTypeSub.RESIDENTIAL: {
                'min': 1,
                'max': 9999,
                'common_prefixes': [],
                'common_suffixes': ['A', 'B', 'C', 'D', '1/2'],
                'step': 1,
                'density': 'medium'
            },
            StreetTypeSub.COMMERCIAL: {
                'min': 100,
                'max': 9999,
                'common_prefixes': ['Suite', 'Unit', '#', 'Ste', 'Fl', 'Floor'],
                'common_suffixes': [],
                'step': 10,  # 通常商业地址是10的倍数
                'density': 'high'
            },
            StreetTypeSub.DOWNTOWN: {
                'min': 1,
                'max': 200,
                'common_prefixes': [],
                'common_suffixes': ['A', 'B', 'C', '1/2', '2/3', '3/4'],
                'step': 1,
                'density': 'very_high'
            },
            StreetTypeSub.SUBURBAN: {
                'min': 1000,
                'max': 19999,
                'common_prefixes': [],
                'common_suffixes': ['A', 'B'],
                'step': 2,  # 通常郊区房屋间隔较大
                'density': 'low'
            },
            StreetTypeSub.RURAL: {
                'min': 1,
                'max': 999,
                'common_prefixes': ['RR', 'Route', 'Box', 'HC'],
                'common_suffixes': [],
                'step': 1,
                'density': 'very_low'
            },
            StreetTypeSub.HIGHWAY: {
                'min': 1000,
                'max': 99999,
                'common_prefixes': ['Mile', 'MM', 'Exit'],
                'common_suffixes': [],
                'step': 100,
                'density': 'very_low'
            },
            StreetTypeSub.BOULEVARD: {
                'min': 100,
                'max': 9999,
                'common_prefixes': [],
                'common_suffixes': ['NE', 'NW', 'SE', 'SW'],
                'step': 10,
                'density': 'medium'
            },
            StreetTypeSub.AVENUE: {
                'min': 1,
                'max': 500,
                'common_prefixes': [],
                'common_suffixes': ['E', 'W', 'N', 'S'],
                'step': 1,
                'density': 'high'
            },
            StreetTypeSub.STREET: {
                'min': 1,
                'max': 3000,
                'common_prefixes': [],
                'common_suffixes': ['A', 'B', 'C'],
                'step': 2,
                'density': 'medium'
            }
        }

        # 城市类型对门牌号的影响
        self.city_type_ranges = {
            'metropolis': {  # 大都市 (纽约, 洛杉矶)
                'min': 1,
                'max': 9999,
                'fractional_prob': 0.15,  # 分数地址概率
                'letter_suffix_prob': 0.25,
                'multi_unit_prob': 0.4
            },
            'large_city': {  # 大城市
                'min': 1,
                'max': 8000,
                'fractional_prob': 0.08,
                'letter_suffix_prob': 0.15,
                'multi_unit_prob': 0.3
            },
            'medium_city': {  # 中等城市
                'min': 1,
                'max': 5000,
                'fractional_prob': 0.05,
                'letter_suffix_prob': 0.1,
                'multi_unit_prob': 0.2
            },
            'small_city': {  # 小城市
                'min': 1,
                'max': 3000,
                'fractional_prob': 0.02,
                'letter_suffix_prob': 0.05,
                'multi_unit_prob': 0.1
            },
            'town': {  # 城镇
                'min': 1,
                'max': 2000,
                'fractional_prob': 0.01,
                'letter_suffix_prob': 0.03,
                'multi_unit_prob': 0.05
            },
            'village': {  # 村庄
                'min': 1,
                'max': 1000,
                'fractional_prob': 0.005,
                'letter_suffix_prob': 0.01,
                'multi_unit_prob': 0.02
            },
            'rural': {  # 农村
                'min': 1,
                'max': 999,
                'fractional_prob': 0.0,
                'letter_suffix_prob': 0.0,
                'multi_unit_prob': 0.0
            }
        }

        # 门牌号风格的概率分布
        self.style_probabilities = {
            NumberingStyle.SIMPLE: 0.60,  # 60% 简单数字
            NumberingStyle.LETTER_SUFFIX: 0.15,  # 15% 字母后缀
            NumberingStyle.HYPHENATED: 0.10,  # 10% 带连字符
            NumberingStyle.UNIT: 0.05,  # 5% 单元
            NumberingStyle.APARTMENT: 0.03,  # 3% 公寓
            NumberingStyle.SUITE: 0.02,  # 2% 套间
            NumberingStyle.FRACTIONAL: 0.02,  # 2% 分数
            NumberingStyle.LETTER_PREFIX: 0.01,  # 1% 字母前缀
            NumberingStyle.BUILDING: 0.01,  # 1% 楼号
            NumberingStyle.PO_BOX: 0.005,  # 0.5% 邮政信箱
            NumberingStyle.RURAL: 0.005,  # 0.5% 农村地址
        }

        # 特殊数字模式
        self.special_patterns = {
            'all_same': ['111', '222', '333', '444', '555', '666', '777', '888', '999'],
            'sequential': ['123', '234', '345', '456', '567', '678', '789', '890'],
            'repeating': ['101', '202', '303', '404', '505', '606', '707', '808', '909'],
            'palindrome': ['121', '232', '343', '454', '565', '676', '787', '898'],
            'bookend': ['101', '202', '303', '404', '505'],
        }

        # 美国地址编号系统规则
        self.addressing_systems = {
            'standard': {  # 标准编号系统
                'odd_even': True,  # 奇偶分开
                'increment': 2,  # 通常间隔2
                'block_size': 100,  # 每100号一个街区
            },
            'hundred_block': {  # 百位区系统
                'odd_even': True,
                'increment': 2,
                'block_size': 100,
                'description': '常见于网格状城市规划'
            },
            'mile_system': {  # 英里系统（农村）
                'odd_even': False,
                'increment': 1,
                'block_size': 1,
                'description': '农村基于距离的编号'
            },
            'chronological': {  # 按时间顺序
                'odd_even': False,
                'increment': 1,
                'block_size': None,
                'description': '按建设时间编号'
            }
        }

        # 州特定的编号习惯
        self.state_specific_rules = {
            'NY': {  # 纽约
                'fractional_common': True,
                'east_west': True,  # 东/西区分
                'north_south': True,  # 北/南区分
                'description': '曼哈顿有很多分数地址'
            },
            'CA': {  # 加利福尼亚
                'fractional_common': False,
                'east_west': True,
                'north_south': True,
                'description': '基于距离的编号系统'
            },
            'IL': {  # 伊利诺伊
                'fractional_common': False,
                'east_west': True,
                'north_south': True,
                'description': '芝加哥有严格的编号系统'
            },
            'TX': {  # 德克萨斯
                'fractional_common': False,
                'east_west': False,
                'north_south': True,
                'description': '农村地区使用里程编号'
            },
            'FL': {  # 佛罗里达
                'fractional_common': False,
                'east_west': True,
                'north_south': True,
                'description': '基于距离和方向'
            }
        }

        # 字母后缀选项
        self.letter_suffixes = [
            '', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
            'J', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T',
            'U', 'V', 'W', 'X', 'Y', 'Z'
        ]

        # 字母前缀选项
        self.letter_prefixes = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
            'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
            'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
        ]

        # 分数选项
        self.fractions = [
            '1/2', '1/3', '1/4', '1/8',
            '2/3', '3/4',
            '1/2A', '1/2B',
            'A', 'B', 'C'
        ]

        # 单元/公寓前缀
        self.unit_prefixes = [
            'Unit', 'Apt', 'Apartment', 'Suite', 'Ste',
            '#', 'No.', 'Number', 'Rm', 'Room',
            'Office', 'Ofc', 'Fl', 'Floor',
            'Building', 'Bldg', 'Tower', 'Twr'
        ]

    def generate_simple_number(self,
                               street_type: Optional[StreetTypeSub] = None,
                               city_type: str = 'medium_city',
                               use_special_pattern: bool = True) -> str:
        """生成简单门牌号"""

        # 确定范围
        if street_type and street_type in self.street_type_ranges:
            street_info = self.street_type_ranges[street_type]
            min_num = street_info['min']
            max_num = street_info['max']
            step = street_info['step']
        else:
            city_info = self.city_type_ranges[city_type]
            min_num = city_info['min']
            max_num = city_info['max']
            step = 2  # 默认步长

        # 偶尔使用特殊模式
        if use_special_pattern and random.random() < 0.1:
            pattern_type = random.choice(list(self.special_patterns.keys()))
            if self.special_patterns[pattern_type]:
                return random.choice(self.special_patterns[pattern_type])

        # 生成数字
        number = random.randrange(min_num, max_num + 1, step)

        # 确保数字符合奇偶规则（如果适用）
        if street_type and street_type in [StreetType.AVENUE, StreetType.STREET]:
            if random.random() > 0.5:
                # 确保是偶数
                if number % 2 != 0:
                    number += 1
            else:
                # 确保是奇数
                if number % 2 == 0:
                    number += 1

        return str(number)

    def generate_with_letter_suffix(self,
                                    base_number: Optional[str] = None,
                                    street_type: Optional[StreetType] = None,
                                    city_type: str = 'medium_city') -> str:
        """生成带字母后缀的门牌号"""

        if not base_number:
            base_number = self.generate_simple_number(street_type, city_type, use_special_pattern=False)

        # 选择后缀
        suffix = random.choice(self.letter_suffixes)

        # 有时后缀为空
        if suffix == '' and random.random() < 0.3:
            return base_number

        return f"{base_number}{suffix}"

    def generate_with_letter_prefix(self,
                                    base_number: Optional[str] = None,
                                    street_type: Optional[StreetType] = None,
                                    city_type: str = 'medium_city') -> str:
        """生成带字母前缀的门牌号"""

        if not base_number:
            base_number = self.generate_simple_number(street_type, city_type, use_special_pattern=False)

        prefix = random.choice(self.letter_prefixes)

        return f"{prefix}{base_number}"

    def generate_hyphenated(self,
                            street_type: Optional[StreetType] = None,
                            city_type: str = 'medium_city') -> str:
        """生成带连字符的门牌号"""

        # 第一种模式: 123-456
        if random.random() > 0.5:
            num1 = random.randint(1, 999)
            num2 = random.randint(1, 999)
            return f"{num1:03d}-{num2:03d}"

        # 第二种模式: 建筑-单元
        building = random.randint(1, 50)
        unit = random.randint(1, 300)
        return f"{building}-{unit}"

    def generate_fractional(self,
                            base_number: Optional[str] = None,
                            street_type: Optional[StreetType] = None,
                            city_type: str = 'medium_city') -> str:
        """生成分数门牌号"""

        if not base_number:
            base_number = self.generate_simple_number(street_type, city_type, use_special_pattern=False)

        fraction = random.choice(self.fractions)

        return f"{base_number} {fraction}"

    def generate_unit_number(self,
                             street_type: Optional[StreetType] = None,
                             city_type: str = 'medium_city') -> str:
        """生成单元/公寓门牌号"""

        prefix = random.choice(self.unit_prefixes)

        # 决定单元号格式
        if prefix in ['Unit', 'Apt', 'Apartment', 'Suite', 'Ste']:
            # 住宅单元
            if random.random() > 0.7:
                # 带字母: Apt 2A
                unit_num = random.randint(1, 30)
                suffix = random.choice(['', 'A', 'B', 'C', 'D'])
                unit = f"{unit_num}{suffix}".strip()
            else:
                # 纯数字: Apt 101
                unit = str(random.randint(100, 500))

        elif prefix in ['Building', 'Bldg', 'Tower', 'Twr']:
            # 建筑号
            unit = str(random.randint(1, 20))

        elif prefix in ['Fl', 'Floor']:
            # 楼层
            unit = str(random.randint(1, 50))

        else:
            # 其他
            unit = str(random.randint(1, 999))

        return f"{prefix} {unit}"

    @classmethod
    def generate_rural_number(cls) -> str:
        """生成农村地址门牌号"""

        patterns = [
            # 农村路线
            lambda: f"RR {random.randint(1, 10)} Box {random.randint(1, 999)}",
            # 路线号
            lambda: f"Route {random.randint(1, 10)} Box {random.randint(1, 999)}",
            # 农村信箱
            lambda: f"HC {random.randint(1, 99)} Box {random.randint(1, 999)}",
            # 简单农村号
            lambda: f"{random.randint(1, 999)}",
            # 里程标记
            lambda: f"Mile {random.randint(1, 200)}"
        ]

        return random.choice(patterns)()

    @classmethod
    def generate_po_box(cls) -> str:
        """生成邮政信箱号"""

        box_types = ['PO Box', 'P.O. Box', 'Post Office Box', 'Box']
        box_type = random.choice(box_types)

        # 信箱号
        box_number = random.randint(100, 99999)

        return f"{box_type} {box_number}"

    @classmethod
    def generate_historical_number(cls) -> str:
        """生成历史风格门牌号"""

        patterns = [
            # 老式分数地址
            lambda: f"{random.randint(1, 999)} 1/2",
            # 字母后缀
            lambda: f"{random.randint(1, 999)}{random.choice(['A', 'B', 'C'])}",
            # 带"和"的地址
            lambda: f"{random.randint(1, 999)} & {random.randint(1, 999)}",
        ]

        return random.choice(patterns)()

    def generate_house_number(self,
                              style: Optional[NumberingStyle] = None,
                              street_type: Optional[StreetType] = None,
                              city_type: str = 'medium_city',
                              state: Optional[str] = None,
                              is_commercial: bool = False,
                              is_multi_unit: bool = False) -> HouseNumber:
        """生成完整的门牌号"""

        # 如果未指定风格，根据概率随机选择
        if not style:
            styles = list(self.style_probabilities.keys())
            probabilities = list(self.style_probabilities.values())
            style = random.choices(styles, weights=probabilities, k=1)[0]

        # 根据城市类型调整是否为多单元
        city_info = self.city_type_ranges.get(city_type, self.city_type_ranges['medium_city'])
        if not is_multi_unit and random.random() < city_info['multi_unit_prob']:
            is_multi_unit = True

        # 根据州特定规则调整
        state_rules = self.state_specific_rules.get(state, {}) if state else {}

        # 生成门牌号
        number_str = ""
        description = ""

        if style == NumberingStyle.SIMPLE:
            number_str = self.generate_simple_number(street_type, city_type)
            description = "标准门牌号"

        elif style == NumberingStyle.LETTER_SUFFIX:
            number_str = self.generate_with_letter_suffix(None, street_type, city_type)
            description = "带字母后缀的门牌号"

        elif style == NumberingStyle.LETTER_PREFIX:
            number_str = self.generate_with_letter_prefix(None, street_type, city_type)
            description = "带字母前缀的门牌号"

        elif style == NumberingStyle.HYPHENATED:
            number_str = self.generate_hyphenated(street_type, city_type)
            description = "带连字符的门牌号（常见于商业地址）"

        elif style == NumberingStyle.FRACTIONAL:
            # 检查州是否常用分数地址
            if state_rules.get('fractional_common', False) or random.random() < city_info['fractional_prob']:
                number_str = self.generate_fractional(None, street_type, city_type)
                description = "分数地址（常见于历史街区）"
            else:
                # 如果不常用，回退到简单数字
                number_str = self.generate_simple_number(street_type, city_type)
                style = NumberingStyle.SIMPLE
                description = "标准门牌号（替代分数地址）"

        elif style == NumberingStyle.UNIT:
            number_str = self.generate_unit_number(street_type, city_type)
            description = "单元号"
            is_multi_unit = True

        elif style == NumberingStyle.APARTMENT:
            number_str = f"Apt {random.randint(1, 300)}{random.choice(['', 'A', 'B', 'C'])}".strip()
            description = "公寓号"
            is_multi_unit = True

        elif style == NumberingStyle.SUITE:
            number_str = f"Suite {random.randint(100, 2000)}"
            description = "套间号"
            is_commercial = True

        elif style == NumberingStyle.BUILDING:
            number_str = f"Building {random.randint(1, 20)}"
            description = "楼号"

        elif style == NumberingStyle.RURAL:
            number_str = self.generate_rural_number()
            description = "农村地址号"
            street_type = StreetTypeSub.RURAL
            city_type = 'rural'

        elif style == NumberingStyle.PO_BOX:
            number_str = self.generate_po_box()
            description = "邮政信箱号"

        elif style == NumberingStyle.HISTORICAL:
            number_str = self.generate_historical_number()
            description = "历史风格门牌号"

        # 如果是商业地址但还没标记
        if style in [NumberingStyle.SUITE, NumberingStyle.HYPHENATED]:
            is_commercial = True

        # 创建HouseNumber对象
        return HouseNumber(
            number=number_str,
            style=style,
            street_type=street_type,
            city_type=city_type,
            is_commercial=is_commercial,
            is_multi_unit=is_multi_unit,
            description=description
        )

    def generate_batch(self,
                       count: int = 10,
                       style: Optional[NumberingStyle] = None,
                       street_type: Optional[StreetType] = None,
                       city_type: str = 'medium_city',
                       state: Optional[str] = None) -> List[HouseNumber]:
        """批量生成门牌号"""

        numbers = []
        for _ in range(count):
            number = self.generate_house_number(style, street_type, city_type, state)
            numbers.append(number)

        return numbers

    @classmethod
    def generate_for_block(cls,
                           start_number: int = 100,
                           end_number: int = 200,
                           street_type: StreetType = StreetType.STREET,
                           include_fractions: bool = False) -> List[HouseNumber]:
        """生成一个街区的连续门牌号"""

        numbers = []
        current = start_number

        # 确定增量
        increment = 2  # 大多数街道奇偶分开

        while current <= end_number:
            # 决定是否跳过一些号码
            if random.random() < 0.1:  # 10%的概率跳过
                current += increment * random.randint(1, 3)
                continue

            # 决定门牌号风格
            style_choice = random.random()

            if style_choice < 0.7:  # 70% 简单数字
                style = NumberingStyle.SIMPLE
                number_str = str(current)
                description = f"街区连续门牌号 {current}"

            elif style_choice < 0.85:  # 15% 字母后缀
                style = NumberingStyle.LETTER_SUFFIX
                suffix = random.choice(['', 'A', 'B'])
                number_str = f"{current}{suffix}".strip()
                description = f"带后缀的连续门牌号 {current}{suffix if suffix else ''}"

            elif style_choice < 0.95 and include_fractions:  # 10% 分数
                style = NumberingStyle.FRACTIONAL
                fraction = random.choice(['1/2', '1/4', '3/4'])
                number_str = f"{current} {fraction}"
                description = f"分数门牌号 {current} {fraction}"

            else:  # 5% 其他
                style = NumberingStyle.SIMPLE
                number_str = str(current)
                description = f"街区连续门牌号 {current}"

            numbers.append(HouseNumber(
                number=number_str,
                style=style,
                street_type=street_type,
                description=description
            ))

            current += increment

        return numbers

    @classmethod
    def analyze_number(cls, number_str: str) -> Dict:
        """分析门牌号的特征"""

        result = {
            'original': number_str,
            'style': None,
            'is_numeric': False,
            'has_letters': False,
            'has_fraction': False,
            'has_hyphen': False,
            'has_space': False,
            'is_commercial': False,
            'is_multi_unit': False,
            'suggested_street_type': None,
            'parsed_components': {}
        }

        # 清理和标准化
        clean_number = number_str.strip()

        # 检查邮政信箱
        if any(prefix in clean_number.upper() for prefix in ['PO BOX', 'P.O. BOX', 'POST OFFICE BOX']):
            result['style'] = 'po_box'
            result['is_commercial'] = True
            result['suggested_street_type'] = 'PO Box'

        # 检查农村地址
        elif any(prefix in clean_number.upper() for prefix in ['RR', 'ROUTE', 'HC', 'MILE']):
            result['style'] = 'rural'
            result['suggested_street_type'] = 'Rural'

        # 检查单元/公寓
        elif any(prefix in clean_number.split()[0].upper() for prefix in
                 ['UNIT', 'APT', 'APARTMENT', 'SUITE', 'STE', 'BUILDING', 'BLDG', 'FLOOR', 'FL']):
            result['style'] = 'unit'
            result['is_multi_unit'] = True
            result['has_letters'] = any(c.isalpha() for c in clean_number)

        # 检查连字符
        elif '-' in clean_number:
            result['style'] = 'hyphenated'
            result['has_hyphen'] = True
            result['is_commercial'] = True
            parts = clean_number.split('-')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                result['parsed_components'] = {'building': parts[0], 'unit': parts[1]}

        # 检查空格
        elif ' ' in clean_number:
            result['has_space'] = True
            parts = clean_number.split()

            # 检查分数
            if any('/' in part for part in parts):
                result['style'] = 'fractional'
                result['has_fraction'] = True

            # 检查字母后缀
            elif len(parts) > 1 and parts[-1].isalpha():
                result['style'] = 'letter_suffix'
                result['has_letters'] = True
                result['parsed_components'] = {'number': parts[0], 'suffix': parts[1]}

        # 检查纯数字
        elif clean_number.isdigit():
            result['style'] = 'simple'
            result['is_numeric'] = True
            num = int(clean_number)

            # 根据数字大小建议街道类型
            if num < 100:
                result['suggested_street_type'] = 'Downtown'
            elif num < 1000:
                result['suggested_street_type'] = 'Residential'
            elif num < 10000:
                result['suggested_street_type'] = 'Suburban'
            else:
                result['suggested_street_type'] = 'Rural/Highway'

        # 检查字母后缀（无空格）
        elif any(c.isalpha() for c in clean_number):
            result['has_letters'] = True

            # 分离数字和字母
            match = re.match(r'(\d+)([A-Za-z]+)', clean_number)
            if match:
                result['style'] = 'letter_suffix'
                result['parsed_components'] = {'number': match.group(1), 'suffix': match.group(2)}
            else:
                result['style'] = 'letter_prefix'

        # 检查字母前缀
        elif clean_number[0].isalpha():
            result['style'] = 'letter_prefix'
            result['has_letters'] = True

        return result

    def generate_with_context(self,
                              context: str = 'residential',
                              state: Optional[str] = None) -> HouseNumber:
        """根据上下文生成门牌号"""

        contexts = {
            'residential': {
                'street_type': StreetTypeSub.RESIDENTIAL,
                'city_type': 'medium_city',
                'is_commercial': False,
                'is_multi_unit': False,
                'preferred_styles': [NumberingStyle.SIMPLE, NumberingStyle.LETTER_SUFFIX]
            },
            'apartment': {
                'street_type': StreetTypeSub.RESIDENTIAL,
                'city_type': 'metropolis',
                'is_commercial': False,
                'is_multi_unit': True,
                'preferred_styles': [NumberingStyle.APARTMENT, NumberingStyle.UNIT]
            },
            'commercial': {
                'street_type': StreetTypeSub.COMMERCIAL,
                'city_type': 'large_city',
                'is_commercial': True,
                'is_multi_unit': False,
                'preferred_styles': [NumberingStyle.SUITE, NumberingStyle.HYPHENATED]
            },
            'downtown': {
                'street_type': StreetTypeSub.DOWNTOWN,
                'city_type': 'metropolis',
                'is_commercial': True,
                'is_multi_unit': True,
                'preferred_styles': [NumberingStyle.SIMPLE, NumberingStyle.FRACTIONAL]
            },
            'suburban': {
                'street_type': StreetTypeSub.SUBURBAN,
                'city_type': 'town',
                'is_commercial': False,
                'is_multi_unit': False,
                'preferred_styles': [NumberingStyle.SIMPLE, NumberingStyle.LETTER_SUFFIX]
            },
            'rural': {
                'street_type': StreetTypeSub.RURAL,
                'city_type': 'rural',
                'is_commercial': False,
                'is_multi_unit': False,
                'preferred_styles': [NumberingStyle.RURAL, NumberingStyle.SIMPLE]
            },
            'historical': {
                'street_type': StreetTypeSub.STREET,
                'city_type': 'medium_city',
                'is_commercial': False,
                'is_multi_unit': False,
                'preferred_styles': [NumberingStyle.HISTORICAL, NumberingStyle.FRACTIONAL]
            }
        }

        if context not in contexts:
            context = 'residential'

        ctx = contexts[context]
        style = random.choice(ctx['preferred_styles'])

        return self.generate_house_number(
            style=style,
            street_type=ctx['street_type'],
            city_type=ctx['city_type'],
            state=state,
            is_commercial=ctx['is_commercial'],
            is_multi_unit=ctx['is_multi_unit']
        )

    @classmethod
    def validate_number(cls, number_str: str, street_type: str = None) -> Dict:
        """验证门牌号的有效性"""

        result = {
            'number': number_str,
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }

        # 清理输入
        clean_number = number_str.strip()

        if not clean_number:
            result['is_valid'] = False
            result['errors'].append('门牌号不能为空')
            return result

        # 检查邮政信箱格式
        if 'PO' in clean_number.upper() or 'BOX' in clean_number.upper():
            if not re.match(r'^(PO\s+Box|P\.O\.\s+Box|Post\s+Office\s+Box|Box)\s+\d+$', clean_number, re.IGNORECASE):
                result['warnings'].append('邮政信箱格式可能不正确')
            return result

        # 检查农村地址格式
        if any(prefix in clean_number.upper() for prefix in ['RR', 'ROUTE', 'HC']):
            if not re.match(r'^(RR|Route|HC)\s+\d+\s+(Box\s+)?\d+$', clean_number, re.IGNORECASE):
                result['warnings'].append('农村地址格式可能不正确')
            return result

        # 检查单元格式
        if any(prefix in clean_number.upper() for prefix in
               ['UNIT', 'APT', 'APARTMENT', 'SUITE', 'STE', '#']):
            # 基本格式检查
            if not re.match(r'^[A-Za-z#.\s]+\s+[\w/-]+$', clean_number):
                result['warnings'].append('单元号格式可能不正确')
            return result

        # 检查数字部分
        # 提取数字部分
        numbers = re.findall(r'\d+', clean_number)
        if numbers:
            for num in numbers:
                n = int(num)
                if n == 0:
                    result['errors'].append('门牌号不能为0')
                    result['is_valid'] = False
                elif n > 99999:
                    result['warnings'].append('门牌号异常大')
                elif street_type == 'downtown' and n > 200:
                    result['warnings'].append('市中心门牌号通常较小')

        return result


class Gender(Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"


class Ethnicity(Enum):
    """族裔枚举"""
    EUROPEAN = "European"  # 欧洲裔
    AFRICAN_AMERICAN = "African American"  # 非裔美国人
    HISPANIC = "Hispanic"  # 西班牙裔/拉丁裔
    ASIAN = "Asian"  # 亚裔
    NATIVE_AMERICAN = "Native American"  # 原住民
    MIDDLE_EASTERN = "Middle Eastern"  # 中东裔
    MULTIRACIAL = "Multiracial"  # 多种族
    OTHER = "Other"  # 其他


@dataclass
class FirstName:
    """名字信息"""
    name: str
    gender: Gender
    ethnicity: Ethnicity
    meaning: Optional[str] = None
    origin: Optional[str] = None
    popularity_rank: Optional[int] = None
    is_modern: bool = False
    is_traditional: bool = False


@dataclass
class LastName:
    """姓氏信息"""
    name: str
    ethnicity: Ethnicity
    meaning: Optional[str] = None
    origin: Optional[str] = None
    rank_in_us: Optional[int] = None
    is_common: bool = False


@dataclass
class FullName:
    """完整姓名信息"""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    suffix: Optional[str] = None
    gender: Optional[Gender] = None
    ethnicity: Optional[Ethnicity] = None
    full_name: str = ""
    formatted_name: str = ""


class USNameGenerator:
    """美国人名生成器"""

    def __init__(self):
        # 美国常见名字数据库
        self.first_names = {
            # 男性名字
            Gender.MALE: [
                # 欧洲裔男性名字
                FirstName("James", Gender.MALE, Ethnicity.EUROPEAN, "替代者", "Hebrew", 1, is_traditional=True),
                FirstName("John", Gender.MALE, Ethnicity.EUROPEAN, "上帝是仁慈的", "Hebrew", 2, is_traditional=True),
                FirstName("Robert", Gender.MALE, Ethnicity.EUROPEAN, "明亮的名声", "Germanic", 3, is_traditional=True),
                FirstName("Michael", Gender.MALE, Ethnicity.EUROPEAN, "谁像上帝", "Hebrew", 4, is_traditional=True),
                FirstName("William", Gender.MALE, Ethnicity.EUROPEAN, "坚定的保护者", "Germanic", 5,
                          is_traditional=True),
                FirstName("David", Gender.MALE, Ethnicity.EUROPEAN, "心爱的", "Hebrew", 6, is_traditional=True),
                FirstName("Richard", Gender.MALE, Ethnicity.EUROPEAN, "勇敢的统治者", "Germanic", 7,
                          is_traditional=True),
                FirstName("Joseph", Gender.MALE, Ethnicity.EUROPEAN, "他将增加", "Hebrew", 8, is_traditional=True),
                FirstName("Thomas", Gender.MALE, Ethnicity.EUROPEAN, "双胞胎", "Aramaic", 9, is_traditional=True),
                FirstName("Charles", Gender.MALE, Ethnicity.EUROPEAN, "自由人", "Germanic", 10, is_traditional=True),
                FirstName("Christopher", Gender.MALE, Ethnicity.EUROPEAN, "基督的承载者", "Greek", 11,
                          is_traditional=True),
                FirstName("Daniel", Gender.MALE, Ethnicity.EUROPEAN, "上帝是我的法官", "Hebrew", 12,
                          is_traditional=True),
                FirstName("Matthew", Gender.MALE, Ethnicity.EUROPEAN, "上帝的礼物", "Hebrew", 13, is_traditional=True),
                FirstName("Anthony", Gender.MALE, Ethnicity.EUROPEAN, "无价的", "Latin", 14, is_traditional=True),
                FirstName("Donald", Gender.MALE, Ethnicity.EUROPEAN, "世界统治者", "Gaelic", 15, is_traditional=True),
                FirstName("Mark", Gender.MALE, Ethnicity.EUROPEAN, "战神", "Latin", 16, is_traditional=True),
                FirstName("Paul", Gender.MALE, Ethnicity.EUROPEAN, "小的", "Latin", 17, is_traditional=True),
                FirstName("Steven", Gender.MALE, Ethnicity.EUROPEAN, "王冠", "Greek", 18, is_traditional=True),
                FirstName("Andrew", Gender.MALE, Ethnicity.EUROPEAN, "男子气概的", "Greek", 19, is_traditional=True),
                FirstName("Kenneth", Gender.MALE, Ethnicity.EUROPEAN, "英俊的", "Gaelic", 20, is_traditional=True),
                FirstName("Joshua", Gender.MALE, Ethnicity.EUROPEAN, "上帝是拯救", "Hebrew", 21, is_modern=True),
                FirstName("Kevin", Gender.MALE, Ethnicity.EUROPEAN, "英俊的出生", "Gaelic", 22, is_modern=True),
                FirstName("Brian", Gender.MALE, Ethnicity.EUROPEAN, "高贵的", "Gaelic", 23, is_modern=True),
                FirstName("George", Gender.MALE, Ethnicity.EUROPEAN, "农夫", "Greek", 24, is_traditional=True),
                FirstName("Edward", Gender.MALE, Ethnicity.EUROPEAN, "财富守护者", "English", 25, is_traditional=True),

                # 现代流行男性名字
                FirstName("Liam", Gender.MALE, Ethnicity.EUROPEAN, "坚定的保护者", "Irish", 1, is_modern=True),
                FirstName("Noah", Gender.MALE, Ethnicity.EUROPEAN, "休息，安慰", "Hebrew", 2, is_modern=True),
                FirstName("Oliver", Gender.MALE, Ethnicity.EUROPEAN, "橄榄树", "Latin", 3, is_modern=True),
                FirstName("Elijah", Gender.MALE, Ethnicity.EUROPEAN, "我的上帝是耶和华", "Hebrew", 4, is_modern=True),
                FirstName("William", Gender.MALE, Ethnicity.EUROPEAN, "坚定的保护者", "Germanic", 5, is_modern=True),
                FirstName("James", Gender.MALE, Ethnicity.EUROPEAN, "替代者", "Hebrew", 6, is_modern=True),
                FirstName("Benjamin", Gender.MALE, Ethnicity.EUROPEAN, "右手之子", "Hebrew", 7, is_modern=True),
                FirstName("Lucas", Gender.MALE, Ethnicity.EUROPEAN, "来自卢卡尼亚", "Latin", 8, is_modern=True),
                FirstName("Henry", Gender.MALE, Ethnicity.EUROPEAN, "家庭统治者", "Germanic", 9, is_modern=True),
                FirstName("Alexander", Gender.MALE, Ethnicity.EUROPEAN, "人类的保护者", "Greek", 10, is_modern=True),
                FirstName("Mason", Gender.MALE, Ethnicity.EUROPEAN, "石匠", "English", 11, is_modern=True),
                FirstName("Michael", Gender.MALE, Ethnicity.EUROPEAN, "谁像上帝", "Hebrew", 12, is_modern=True),
                FirstName("Ethan", Gender.MALE, Ethnicity.EUROPEAN, "坚固，持久", "Hebrew", 13, is_modern=True),
                FirstName("Daniel", Gender.MALE, Ethnicity.EUROPEAN, "上帝是我的法官", "Hebrew", 14, is_modern=True),
                FirstName("Jacob", Gender.MALE, Ethnicity.EUROPEAN, "取代者", "Hebrew", 15, is_modern=True),
                FirstName("Logan", Gender.MALE, Ethnicity.EUROPEAN, "小空洞", "Gaelic", 16, is_modern=True),
                FirstName("Jackson", Gender.MALE, Ethnicity.EUROPEAN, "杰克之子", "English", 17, is_modern=True),
                FirstName("Levi", Gender.MALE, Ethnicity.EUROPEAN, "加入", "Hebrew", 18, is_modern=True),
                FirstName("Sebastian", Gender.MALE, Ethnicity.EUROPEAN, "尊敬的", "Greek", 19, is_modern=True),
                FirstName("Mateo", Gender.MALE, Ethnicity.EUROPEAN, "上帝的礼物", "Spanish", 20, is_modern=True),
                FirstName("Jack", Gender.MALE, Ethnicity.EUROPEAN, "上帝是仁慈的", "English", 21, is_modern=True),
                FirstName("Owen", Gender.MALE, Ethnicity.EUROPEAN, "年轻的战士", "Welsh", 22, is_modern=True),
                FirstName("Theodore", Gender.MALE, Ethnicity.EUROPEAN, "上帝的礼物", "Greek", 23, is_modern=True),
                FirstName("Aiden", Gender.MALE, Ethnicity.EUROPEAN, "小火", "Gaelic", 24, is_modern=True),
                FirstName("Samuel", Gender.MALE, Ethnicity.EUROPEAN, "上帝已听到", "Hebrew", 25, is_modern=True),

                # 非洲裔美国人男性名字
                FirstName("DeShawn", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "上帝是仁慈的", "American", None,
                          is_modern=True),
                FirstName("Tyrone", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "欧文的土地", "Irish", None,
                          is_modern=True),
                FirstName("Jamal", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "美丽", "Arabic", None, is_modern=True),
                FirstName("Malik", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "国王", "Arabic", None, is_modern=True),
                FirstName("Darnell", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "隐藏的地方", "English", None,
                          is_modern=True),
                FirstName("Terrell", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "雷神的追随者", "French", None,
                          is_modern=True),
                FirstName("Andre", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "男子气概的", "French", None,
                          is_modern=True),
                FirstName("Marquis", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "贵族", "French", None, is_modern=True),
                FirstName("Darius", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "富有", "Persian", None, is_modern=True),
                FirstName("Kareem", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "慷慨的", "Arabic", None, is_modern=True),
                FirstName("Jermaine", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "兄弟", "Latin", None, is_modern=True),
                FirstName("Lamar", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "海洋", "French", None, is_modern=True),
                FirstName("Tremaine", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "石屋", "Cornish", None, is_modern=True),
                FirstName("Desmond", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "来自南曼岛", "Irish", None,
                          is_modern=True),
                FirstName("Quinton", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "女王的庄园", "Latin", None,
                          is_modern=True),
                FirstName("Rashad", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "明智的顾问", "Arabic", None,
                          is_modern=True),
                FirstName("Kendrick", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "皇家统治者", "English", None,
                          is_modern=True),
                FirstName("Demetrius", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "属于得墨忒耳", "Greek", None,
                          is_modern=True),
                FirstName("Tyrone", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "欧文的土地", "Irish", None,
                          is_modern=True),
                FirstName("Malcolm", Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "圣哥伦巴的追随者", "Scottish", None,
                          is_modern=True),

                # 西班牙裔/拉丁裔男性名字
                FirstName("Carlos", Gender.MALE, Ethnicity.HISPANIC, "自由人", "Spanish", None, is_modern=True),
                FirstName("Jose", Gender.MALE, Ethnicity.HISPANIC, "上帝将增加", "Spanish", None, is_modern=True),
                FirstName("Juan", Gender.MALE, Ethnicity.HISPANIC, "上帝是仁慈的", "Spanish", None, is_modern=True),
                FirstName("Miguel", Gender.MALE, Ethnicity.HISPANIC, "谁像上帝", "Spanish", None, is_modern=True),
                FirstName("Antonio", Gender.MALE, Ethnicity.HISPANIC, "无价的", "Spanish", None, is_modern=True),
                FirstName("Francisco", Gender.MALE, Ethnicity.HISPANIC, "法国人", "Spanish", None, is_modern=True),
                FirstName("Luis", Gender.MALE, Ethnicity.HISPANIC, "著名的战士", "Spanish", None, is_modern=True),
                FirstName("Javier", Gender.MALE, Ethnicity.HISPANIC, "新房", "Spanish", None, is_modern=True),
                FirstName("Pedro", Gender.MALE, Ethnicity.HISPANIC, "石头", "Spanish", None, is_modern=True),
                FirstName("Alejandro", Gender.MALE, Ethnicity.HISPANIC, "人类的保护者", "Spanish", None,
                          is_modern=True),
                FirstName("Diego", Gender.MALE, Ethnicity.HISPANIC, "取代者", "Spanish", None, is_modern=True),
                FirstName("Manuel", Gender.MALE, Ethnicity.HISPANIC, "上帝与我们同在", "Spanish", None, is_modern=True),
                FirstName("Ricardo", Gender.MALE, Ethnicity.HISPANIC, "勇敢的统治者", "Spanish", None, is_modern=True),
                FirstName("Fernando", Gender.MALE, Ethnicity.HISPANIC, "勇敢的旅行者", "Spanish", None, is_modern=True),
                FirstName("Rafael", Gender.MALE, Ethnicity.HISPANIC, "上帝已治愈", "Spanish", None, is_modern=True),
                FirstName("Santiago", Gender.MALE, Ethnicity.HISPANIC, "圣詹姆斯", "Spanish", None, is_modern=True),
                FirstName("Andres", Gender.MALE, Ethnicity.HISPANIC, "男子气概的", "Spanish", None, is_modern=True),
                FirstName("Eduardo", Gender.MALE, Ethnicity.HISPANIC, "财富守护者", "Spanish", None, is_modern=True),
                FirstName("Gabriel", Gender.MALE, Ethnicity.HISPANIC, "上帝是我的力量", "Spanish", None,
                          is_modern=True),
                FirstName("Roberto", Gender.MALE, Ethnicity.HISPANIC, "明亮的名声", "Spanish", None, is_modern=True),

                # 亚裔男性名字
                FirstName("Wei", Gender.MALE, Ethnicity.ASIAN, "伟大的", "Chinese", None, is_modern=True),
                FirstName("Jin", Gender.MALE, Ethnicity.ASIAN, "黄金", "Chinese", None, is_modern=True),
                FirstName("Ming", Gender.MALE, Ethnicity.ASIAN, "明亮的", "Chinese", None, is_modern=True),
                FirstName("Takeshi", Gender.MALE, Ethnicity.ASIAN, "武士", "Japanese", None, is_modern=True),
                FirstName("Kenji", Gender.MALE, Ethnicity.ASIAN, "明智的统治者", "Japanese", None, is_modern=True),
                FirstName("Hiroshi", Gender.MALE, Ethnicity.ASIAN, "慷慨的", "Japanese", None, is_modern=True),
                FirstName("Raj", Gender.MALE, Ethnicity.ASIAN, "国王", "Indian", None, is_modern=True),
                FirstName("Amit", Gender.MALE, Ethnicity.ASIAN, "无限的", "Indian", None, is_modern=True),
                FirstName("Sanjay", Gender.MALE, Ethnicity.ASIAN, "胜利的", "Indian", None, is_modern=True),
                FirstName("Min", Gender.MALE, Ethnicity.ASIAN, "敏捷的", "Korean", None, is_modern=True),
                FirstName("Joon", Gender.MALE, Ethnicity.ASIAN, "有才华的", "Korean", None, is_modern=True),
                FirstName("Seung", Gender.MALE, Ethnicity.ASIAN, "胜利的", "Korean", None, is_modern=True),
                FirstName("Duc", Gender.MALE, Ethnicity.ASIAN, "美德", "Vietnamese", None, is_modern=True),
                FirstName("Khanh", Gender.MALE, Ethnicity.ASIAN, "幸福", "Vietnamese", None, is_modern=True),
                FirstName("Phong", Gender.MALE, Ethnicity.ASIAN, "风", "Vietnamese", None, is_modern=True),
            ],

            # 女性名字
            Gender.FEMALE: [
                # 欧洲裔女性名字
                FirstName("Mary", Gender.FEMALE, Ethnicity.EUROPEAN, "苦涩的", "Hebrew", 1, is_traditional=True),
                FirstName("Patricia", Gender.FEMALE, Ethnicity.EUROPEAN, "贵族", "Latin", 2, is_traditional=True),
                FirstName("Jennifer", Gender.FEMALE, Ethnicity.EUROPEAN, "白色的波浪", "Cornish", 3,
                          is_traditional=True),
                FirstName("Linda", Gender.FEMALE, Ethnicity.EUROPEAN, "美丽的", "Spanish", 4, is_traditional=True),
                FirstName("Elizabeth", Gender.FEMALE, Ethnicity.EUROPEAN, "我的上帝是充足的", "Hebrew", 5,
                          is_traditional=True),
                FirstName("Barbara", Gender.FEMALE, Ethnicity.EUROPEAN, "陌生人", "Greek", 6, is_traditional=True),
                FirstName("Susan", Gender.FEMALE, Ethnicity.EUROPEAN, "百合", "Hebrew", 7, is_traditional=True),
                FirstName("Jessica", Gender.FEMALE, Ethnicity.EUROPEAN, "上帝看见", "Hebrew", 8, is_traditional=True),
                FirstName("Sarah", Gender.FEMALE, Ethnicity.EUROPEAN, "公主", "Hebrew", 9, is_traditional=True),
                FirstName("Karen", Gender.FEMALE, Ethnicity.EUROPEAN, "纯洁的", "Greek", 10, is_traditional=True),
                FirstName("Nancy", Gender.FEMALE, Ethnicity.EUROPEAN, "优雅", "Hebrew", 11, is_traditional=True),
                FirstName("Margaret", Gender.FEMALE, Ethnicity.EUROPEAN, "珍珠", "Greek", 12, is_traditional=True),
                FirstName("Betty", Gender.FEMALE, Ethnicity.EUROPEAN, "上帝的誓言", "Hebrew", 13, is_traditional=True),
                FirstName("Sandra", Gender.FEMALE, Ethnicity.EUROPEAN, "人类的保护者", "Greek", 14,
                          is_traditional=True),
                FirstName("Ashley", Gender.FEMALE, Ethnicity.EUROPEAN, "白蜡树林", "English", 15, is_traditional=True),
                FirstName("Dorothy", Gender.FEMALE, Ethnicity.EUROPEAN, "上帝的礼物", "Greek", 16, is_traditional=True),
                FirstName("Kimberly", Gender.FEMALE, Ethnicity.EUROPEAN, "来自皇家堡垒草地", "English", 17,
                          is_traditional=True),
                FirstName("Donna", Gender.FEMALE, Ethnicity.EUROPEAN, "女士", "Italian", 18, is_traditional=True),
                FirstName("Emily", Gender.FEMALE, Ethnicity.EUROPEAN, "竞争者", "Latin", 19, is_traditional=True),
                FirstName("Michelle", Gender.FEMALE, Ethnicity.EUROPEAN, "谁像上帝", "French", 20, is_traditional=True),
                FirstName("Amanda", Gender.FEMALE, Ethnicity.EUROPEAN, "值得爱", "Latin", 21, is_traditional=True),
                FirstName("Helen", Gender.FEMALE, Ethnicity.EUROPEAN, "光", "Greek", 22, is_traditional=True),
                FirstName("Carol", Gender.FEMALE, Ethnicity.EUROPEAN, "自由人", "Germanic", 23, is_traditional=True),
                FirstName("Lisa", Gender.FEMALE, Ethnicity.EUROPEAN, "上帝的誓言", "Hebrew", 24, is_traditional=True),
                FirstName("Maria", Gender.FEMALE, Ethnicity.EUROPEAN, "苦涩的", "Latin", 25, is_traditional=True),

                # 现代流行女性名字
                FirstName("Olivia", Gender.FEMALE, Ethnicity.EUROPEAN, "橄榄树", "Latin", 1, is_modern=True),
                FirstName("Emma", Gender.FEMALE, Ethnicity.EUROPEAN, "完整的", "Germanic", 2, is_modern=True),
                FirstName("Charlotte", Gender.FEMALE, Ethnicity.EUROPEAN, "自由人", "French", 3, is_modern=True),
                FirstName("Amelia", Gender.FEMALE, Ethnicity.EUROPEAN, "工作", "Germanic", 4, is_modern=True),
                FirstName("Sophia", Gender.FEMALE, Ethnicity.EUROPEAN, "智慧", "Greek", 5, is_modern=True),
                FirstName("Isabella", Gender.FEMALE, Ethnicity.EUROPEAN, "上帝的誓言", "Hebrew", 6, is_modern=True),
                FirstName("Ava", Gender.FEMALE, Ethnicity.EUROPEAN, "鸟", "Latin", 7, is_modern=True),
                FirstName("Mia", Gender.FEMALE, Ethnicity.EUROPEAN, "我的", "Italian", 8, is_modern=True),
                FirstName("Evelyn", Gender.FEMALE, Ethnicity.EUROPEAN, "希望的", "English", 9, is_modern=True),
                FirstName("Luna", Gender.FEMALE, Ethnicity.EUROPEAN, "月亮", "Latin", 10, is_modern=True),
                FirstName("Harper", Gender.FEMALE, Ethnicity.EUROPEAN, "竖琴手", "English", 11, is_modern=True),
                FirstName("Camila", Gender.FEMALE, Ethnicity.EUROPEAN, "年轻的仪式仆人", "Latin", 12, is_modern=True),
                FirstName("Gianna", Gender.FEMALE, Ethnicity.EUROPEAN, "上帝是仁慈的", "Italian", 13, is_modern=True),
                FirstName("Abigail", Gender.FEMALE, Ethnicity.EUROPEAN, "父亲的喜悦", "Hebrew", 14, is_modern=True),
                FirstName("Ella", Gender.FEMALE, Ethnicity.EUROPEAN, "完全地", "English", 15, is_modern=True),
                FirstName("Elizabeth", Gender.FEMALE, Ethnicity.EUROPEAN, "我的上帝是充足的", "Hebrew", 16,
                          is_modern=True),
                FirstName("Sofia", Gender.FEMALE, Ethnicity.EUROPEAN, "智慧", "Greek", 17, is_modern=True),
                FirstName("Emily", Gender.FEMALE, Ethnicity.EUROPEAN, "竞争者", "Latin", 18, is_modern=True),
                FirstName("Avery", Gender.FEMALE, Ethnicity.EUROPEAN, "精灵统治者", "English", 19, is_modern=True),
                FirstName("Mila", Gender.FEMALE, Ethnicity.EUROPEAN, "亲爱的", "Slavic", 20, is_modern=True),
                FirstName("Scarlett", Gender.FEMALE, Ethnicity.EUROPEAN, "红色", "English", 21, is_modern=True),
                FirstName("Eleanor", Gender.FEMALE, Ethnicity.EUROPEAN, "光", "Greek", 22, is_modern=True),
                FirstName("Madison", Gender.FEMALE, Ethnicity.EUROPEAN, "马太之子", "English", 23, is_modern=True),
                FirstName("Layla", Gender.FEMALE, Ethnicity.EUROPEAN, "夜晚", "Arabic", 24, is_modern=True),
                FirstName("Penelope", Gender.FEMALE, Ethnicity.EUROPEAN, "织布工", "Greek", 25, is_modern=True),

                # 非洲裔美国人女性名字
                FirstName("LaKeisha", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "最喜爱的", "American", None,
                          is_modern=True),
                FirstName("Shanice", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "上帝是仁慈的", "American", None,
                          is_modern=True),
                FirstName("Latoya", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "胜利的", "Spanish", None,
                          is_modern=True),
                FirstName("Tanisha", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "野心", "Sanskrit", None,
                          is_modern=True),
                FirstName("Keisha", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "最喜爱的", "American", None,
                          is_modern=True),
                FirstName("Tameka", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "甜美的", "Japanese", None,
                          is_modern=True),
                FirstName("Latasha", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "圣诞节", "Latin", None,
                          is_modern=True),
                FirstName("Shaniqua", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "上帝是仁慈的", "American", None,
                          is_modern=True),
                FirstName("Ebony", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "黑木", "English", None, is_modern=True),
                FirstName("Imani", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "信仰", "Arabic", None, is_modern=True),
                FirstName("Nia", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "决心", "Swahili", None, is_modern=True),
                FirstName("Aaliyah", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "最高的，最崇高的", "Arabic", None,
                          is_modern=True),
                FirstName("Jada", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "玉", "Spanish", None, is_modern=True),
                FirstName("Kiara", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "黑暗的", "Irish", None, is_modern=True),
                FirstName("Tiana", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "仙女女王", "Latin", None,
                          is_modern=True),
                FirstName("Monique", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "建议", "French", None, is_modern=True),
                FirstName("Danielle", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "上帝是我的法官", "French", None,
                          is_modern=True),
                FirstName("Brianna", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "高贵的", "Gaelic", None,
                          is_modern=True),
                FirstName("Jasmine", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "茉莉花", "Persian", None,
                          is_modern=True),
                FirstName("Tierra", Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "地球", "Spanish", None, is_modern=True),

                # 西班牙裔/拉丁裔女性名字
                FirstName("Maria", Gender.FEMALE, Ethnicity.HISPANIC, "苦涩的", "Spanish", None, is_modern=True),
                FirstName("Isabella", Gender.FEMALE, Ethnicity.HISPANIC, "上帝的誓言", "Spanish", None, is_modern=True),
                FirstName("Sofia", Gender.FEMALE, Ethnicity.HISPANIC, "智慧", "Spanish", None, is_modern=True),
                FirstName("Camila", Gender.FEMALE, Ethnicity.HISPANIC, "年轻的仪式仆人", "Spanish", None,
                          is_modern=True),
                FirstName("Valentina", Gender.FEMALE, Ethnicity.HISPANIC, "强壮的，健康的", "Spanish", None,
                          is_modern=True),
                FirstName("Valeria", Gender.FEMALE, Ethnicity.HISPANIC, "强壮的", "Spanish", None, is_modern=True),
                FirstName("Luciana", Gender.FEMALE, Ethnicity.HISPANIC, "光", "Spanish", None, is_modern=True),
                FirstName("Ximena", Gender.FEMALE, Ethnicity.HISPANIC, "听者", "Spanish", None, is_modern=True),
                FirstName("Mariana", Gender.FEMALE, Ethnicity.HISPANIC, "苦海", "Spanish", None, is_modern=True),
                FirstName("Victoria", Gender.FEMALE, Ethnicity.HISPANIC, "胜利", "Spanish", None, is_modern=True),
                FirstName("Catalina", Gender.FEMALE, Ethnicity.HISPANIC, "纯洁的", "Spanish", None, is_modern=True),
                FirstName("Gabriela", Gender.FEMALE, Ethnicity.HISPANIC, "上帝是我的力量", "Spanish", None,
                          is_modern=True),
                FirstName("Sara", Gender.FEMALE, Ethnicity.HISPANIC, "公主", "Spanish", None, is_modern=True),
                FirstName("Daniela", Gender.FEMALE, Ethnicity.HISPANIC, "上帝是我的法官", "Spanish", None,
                          is_modern=True),
                FirstName("Lucia", Gender.FEMALE, Ethnicity.HISPANIC, "光", "Spanish", None, is_modern=True),
                FirstName("Julieta", Gender.FEMALE, Ethnicity.HISPANIC, "年轻的", "Spanish", None, is_modern=True),
                FirstName("Martina", Gender.FEMALE, Ethnicity.HISPANIC, "火星的", "Spanish", None, is_modern=True),
                FirstName("Julia", Gender.FEMALE, Ethnicity.HISPANIC, "年轻的", "Spanish", None, is_modern=True),
                FirstName("Paula", Gender.FEMALE, Ethnicity.HISPANIC, "小的", "Spanish", None, is_modern=True),
                FirstName("Emilia", Gender.FEMALE, Ethnicity.HISPANIC, "竞争者", "Spanish", None, is_modern=True),

                # 亚裔女性名字
                FirstName("Mei", Gender.FEMALE, Ethnicity.ASIAN, "美丽的", "Chinese", None, is_modern=True),
                FirstName("Ling", Gender.FEMALE, Ethnicity.ASIAN, "灵魂，铃铛", "Chinese", None, is_modern=True),
                FirstName("Xia", Gender.FEMALE, Ethnicity.ASIAN, "云彩，霞", "Chinese", None, is_modern=True),
                FirstName("Sakura", Gender.FEMALE, Ethnicity.ASIAN, "樱花", "Japanese", None, is_modern=True),
                FirstName("Yuki", Gender.FEMALE, Ethnicity.ASIAN, "雪", "Japanese", None, is_modern=True),
                FirstName("Hana", Gender.FEMALE, Ethnicity.ASIAN, "花", "Japanese", None, is_modern=True),
                FirstName("Priya", Gender.FEMALE, Ethnicity.ASIAN, "心爱的", "Indian", None, is_modern=True),
                FirstName("Anita", Gender.FEMALE, Ethnicity.ASIAN, "优雅的", "Indian", None, is_modern=True),
                FirstName("Maya", Gender.FEMALE, Ethnicity.ASIAN, "幻象", "Indian", None, is_modern=True),
                FirstName("Ji", Gender.FEMALE, Ethnicity.ASIAN, "智慧的", "Korean", None, is_modern=True),
                FirstName("Hye", Gender.FEMALE, Ethnicity.ASIAN, "智慧", "Korean", None, is_modern=True),
                FirstName("Min", Gender.FEMALE, Ethnicity.ASIAN, "敏捷的", "Korean", None, is_modern=True),
                FirstName("Mai", Gender.FEMALE, Ethnicity.ASIAN, "樱桃 blossom", "Vietnamese", None, is_modern=True),
                FirstName("Lan", Gender.FEMALE, Ethnicity.ASIAN, "兰花", "Vietnamese", None, is_modern=True),
                FirstName("Thuy", Gender.FEMALE, Ethnicity.ASIAN, "温和的", "Vietnamese", None, is_modern=True),

            ]
        }

        # 美国常见姓氏数据库
        self.last_names = [
            # 美国最常见姓氏
            LastName("Smith", Ethnicity.EUROPEAN, "金属工匠", "English", 1, is_common=True),
            LastName("Johnson", Ethnicity.EUROPEAN, "约翰之子", "English", 2, is_common=True),
            LastName("Williams", Ethnicity.EUROPEAN, "威尔之子", "English", 3, is_common=True),
            LastName("Brown", Ethnicity.EUROPEAN, "棕色头发或肤色", "English", 4, is_common=True),
            LastName("Jones", Ethnicity.EUROPEAN, "约翰之子", "Welsh", 5, is_common=True),
            LastName("Garcia", Ethnicity.HISPANIC, "熊", "Spanish", 6, is_common=True),
            LastName("Miller", Ethnicity.EUROPEAN, "磨坊主", "English", 7, is_common=True),
            LastName("Davis", Ethnicity.EUROPEAN, "大卫之子", "Welsh", 8, is_common=True),
            LastName("Rodriguez", Ethnicity.HISPANIC, "罗德里戈之子", "Spanish", 9, is_common=True),
            LastName("Martinez", Ethnicity.HISPANIC, "马丁之子", "Spanish", 10, is_common=True),
            LastName("Hernandez", Ethnicity.HISPANIC, "埃尔南多之子", "Spanish", 11, is_common=True),
            LastName("Lopez", Ethnicity.HISPANIC, "狼", "Spanish", 12, is_common=True),
            LastName("Gonzalez", Ethnicity.HISPANIC, "冈萨洛之子", "Spanish", 13, is_common=True),
            LastName("Wilson", Ethnicity.EUROPEAN, "威尔之子", "English", 14, is_common=True),
            LastName("Anderson", Ethnicity.EUROPEAN, "安德鲁之子", "Scandinavian", 15, is_common=True),
            LastName("Thomas", Ethnicity.EUROPEAN, "双胞胎", "Aramaic", 16, is_common=True),
            LastName("Taylor", Ethnicity.EUROPEAN, "裁缝", "English", 17, is_common=True),
            LastName("Moore", Ethnicity.EUROPEAN, "沼泽地", "English", 18, is_common=True),
            LastName("Jackson", Ethnicity.EUROPEAN, "杰克之子", "English", 19, is_common=True),
            LastName("Martin", Ethnicity.EUROPEAN, "战神", "Latin", 20, is_common=True),
            LastName("Lee", Ethnicity.ASIAN, "李树", "Chinese", 21, is_common=True),
            LastName("Perez", Ethnicity.HISPANIC, "彼得之子", "Spanish", 22, is_common=True),
            LastName("Thompson", Ethnicity.EUROPEAN, "汤姆之子", "English", 23, is_common=True),
            LastName("White", Ethnicity.EUROPEAN, "白色头发或肤色", "English", 24, is_common=True),
            LastName("Harris", Ethnicity.EUROPEAN, "哈里之子", "English", 25, is_common=True),
            LastName("Sanchez", Ethnicity.HISPANIC, "圣者", "Spanish", 26, is_common=True),
            LastName("Clark", Ethnicity.EUROPEAN, "书记员", "English", 27, is_common=True),
            LastName("Ramirez", Ethnicity.HISPANIC, "拉米罗之子", "Spanish", 28, is_common=True),
            LastName("Lewis", Ethnicity.EUROPEAN, "著名的战士", "Welsh", 29, is_common=True),
            LastName("Robinson", Ethnicity.EUROPEAN, "罗宾之子", "English", 30, is_common=True),
            LastName("Walker", Ethnicity.EUROPEAN, "布料漂洗工", "English", 31, is_common=True),
            LastName("Young", Ethnicity.EUROPEAN, "年轻的", "English", 32, is_common=True),
            LastName("Allen", Ethnicity.EUROPEAN, "和谐", "Gaelic", 33, is_common=True),
            LastName("King", Ethnicity.EUROPEAN, "国王", "English", 34, is_common=True),
            LastName("Wright", Ethnicity.EUROPEAN, "工匠", "English", 35, is_common=True),
            LastName("Scott", Ethnicity.EUROPEAN, "来自苏格兰", "English", 36, is_common=True),
            LastName("Torres", Ethnicity.HISPANIC, "塔楼", "Spanish", 37, is_common=True),
            LastName("Nguyen", Ethnicity.ASIAN, "原", "Vietnamese", 38, is_common=True),
            LastName("Hill", Ethnicity.EUROPEAN, "山丘", "English", 39, is_common=True),
            LastName("Flores", Ethnicity.HISPANIC, "花", "Spanish", 40, is_common=True),
            LastName("Green", Ethnicity.EUROPEAN, "绿色", "English", 41, is_common=True),
            LastName("Adams", Ethnicity.EUROPEAN, "亚当之子", "English", 42, is_common=True),
            LastName("Nelson", Ethnicity.EUROPEAN, "尼尔之子", "Scandinavian", 43, is_common=True),
            LastName("Baker", Ethnicity.EUROPEAN, "面包师", "English", 44, is_common=True),
            LastName("Hall", Ethnicity.EUROPEAN, "大厅", "English", 45, is_common=True),
            LastName("Rivera", Ethnicity.HISPANIC, "河岸", "Spanish", 46, is_common=True),
            LastName("Campbell", Ethnicity.EUROPEAN, "歪嘴", "Gaelic", 47, is_common=True),
            LastName("Mitchell", Ethnicity.EUROPEAN, "谁像上帝", "English", 48, is_common=True),
            LastName("Carter", Ethnicity.EUROPEAN, "车夫", "English", 49, is_common=True),
            LastName("Roberts", Ethnicity.EUROPEAN, "罗伯特之子", "English", 50, is_common=True),

            # 非裔美国人姓氏
            LastName("Washington", Ethnicity.AFRICAN_AMERICAN, "来自华盛顿", "English", 138, is_common=True),
            LastName("Jefferson", Ethnicity.AFRICAN_AMERICAN, "杰弗里之子", "English", 379, is_common=True),
            LastName("Jackson", Ethnicity.AFRICAN_AMERICAN, "杰克之子", "English", 19, is_common=True),
            LastName("Williams", Ethnicity.AFRICAN_AMERICAN, "威尔之子", "English", 3, is_common=True),
            LastName("Johnson", Ethnicity.AFRICAN_AMERICAN, "约翰之子", "English", 2, is_common=True),
            LastName("Brown", Ethnicity.AFRICAN_AMERICAN, "棕色头发或肤色", "English", 4, is_common=True),
            LastName("Davis", Ethnicity.AFRICAN_AMERICAN, "大卫之子", "Welsh", 8, is_common=True),
            LastName("Jones", Ethnicity.AFRICAN_AMERICAN, "约翰之子", "Welsh", 5, is_common=True),
            LastName("Robinson", Ethnicity.AFRICAN_AMERICAN, "罗宾之子", "English", 30, is_common=True),
            LastName("Harris", Ethnicity.AFRICAN_AMERICAN, "哈里之子", "English", 25, is_common=True),

            # 亚洲裔姓氏
            LastName("Kim", Ethnicity.ASIAN, "黄金", "Korean", 77, is_common=True),
            LastName("Lee", Ethnicity.ASIAN, "李树", "Chinese", 21, is_common=True),
            LastName("Nguyen", Ethnicity.ASIAN, "原", "Vietnamese", 38, is_common=True),
            LastName("Wang", Ethnicity.ASIAN, "国王", "Chinese", 189, is_common=True),
            LastName("Chen", Ethnicity.ASIAN, "古老的", "Chinese", 262, is_common=True),
            LastName("Li", Ethnicity.ASIAN, "李树", "Chinese", 582, is_common=True),
            LastName("Yang", Ethnicity.ASIAN, "杨树", "Chinese", 385, is_common=True),
            LastName("Zhang", Ethnicity.ASIAN, "张开", "Chinese", 411, is_common=True),
            LastName("Liu", Ethnicity.ASIAN, "杀戮", "Chinese", 475, is_common=True),
            LastName("Singh", Ethnicity.ASIAN, "狮子", "Indian", 395, is_common=True),

            # 原住民姓氏
            LastName("Begay", Ethnicity.NATIVE_AMERICAN, "他的儿子", "Navajo", None, is_common=False),
            LastName("Yazzie", Ethnicity.NATIVE_AMERICAN, "小的", "Navajo", None, is_common=False),
            LastName("Benally", Ethnicity.NATIVE_AMERICAN, "他的亲属", "Navajo", None, is_common=False),
            LastName("Tsosie", Ethnicity.NATIVE_AMERICAN, "苗条的", "Navajo", None, is_common=False),
            LastName("Nez", Ethnicity.NATIVE_AMERICAN, "高的", "Navajo", None, is_common=False),
            LastName("Peters", Ethnicity.NATIVE_AMERICAN, "岩石", "Greek", None, is_common=False),
            LastName("Chee", Ethnicity.NATIVE_AMERICAN, "红色的", "Navajo", None, is_common=False),

            # 中东裔姓氏
            LastName("Mohammed", Ethnicity.MIDDLE_EASTERN, "值得赞扬的", "Arabic", None, is_common=False),
            LastName("Ali", Ethnicity.MIDDLE_EASTERN, "崇高的", "Arabic", None, is_common=False),
            LastName("Hassan", Ethnicity.MIDDLE_EASTERN, "英俊的", "Arabic", None, is_common=False),
            LastName("Hussein", Ethnicity.MIDDLE_EASTERN, "英俊的", "Arabic", None, is_common=False),
            LastName("Ahmed", Ethnicity.MIDDLE_EASTERN, "值得赞扬的", "Arabic", None, is_common=False),
            LastName("Khan", Ethnicity.MIDDLE_EASTERN, "王子，领袖", "Persian", None, is_common=False),
            LastName("Malik", Ethnicity.MIDDLE_EASTERN, "国王", "Arabic", None, is_common=False),
        ]

        # 中间名选项
        self.middle_names = {
            Gender.MALE: ["James", "John", "Robert", "Michael", "William", "David", "Richard",
                          "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony"],
            Gender.FEMALE: ["Marie", "Anne", "Lynn", "Elizabeth", "May", "Grace", "Rose", "Jane",
                            "Louise", "Ann", "Kay", "Jean", "Marie", "Claire", "Faith"]
        }

        # 姓名后缀
        self.name_suffixes = ["Jr.", "Sr.", "II", "III", "IV", "V", "PhD", "MD", "Esq.", "CPA"]

        # 美国人口族裔分布（用于随机选择）
        self.ethnicity_distribution = {
            Ethnicity.EUROPEAN: 0.60,  # 60% 欧洲裔
            Ethnicity.HISPANIC: 0.19,  # 19% 西班牙裔/拉丁裔
            Ethnicity.AFRICAN_AMERICAN: 0.13,  # 13% 非裔美国人
            Ethnicity.ASIAN: 0.06,  # 6% 亚裔
            Ethnicity.NATIVE_AMERICAN: 0.01,  # 1% 原住民
            Ethnicity.MIDDLE_EASTERN: 0.01,  # 1% 中东裔
        }

    def generate_first_name(self,
                            gender: Optional[Gender] = None,
                            ethnicity: Optional[Ethnicity] = None,
                            is_modern: bool = False,
                            is_traditional: bool = False) -> FirstName:
        """生成名字"""

        # 如果未指定性别，随机选择
        if gender is None:
            gender = random.choice([Gender.MALE, Gender.FEMALE])

        # 如果未指定族裔，根据分布随机选择
        if ethnicity is None:
            ethnicities = list(self.ethnicity_distribution.keys())
            probabilities = list(self.ethnicity_distribution.values())
            ethnicity = random.choices(ethnicities, weights=probabilities, k=1)[0]

        # 筛选候选名字
        candidates = [name for name in self.first_names[gender]
                      if name.ethnicity == ethnicity]

        # 如果该族裔没有足够名字，放宽族裔限制
        if not candidates:
            candidates = [name for name in self.first_names[gender]]

        # 根据现代/传统偏好筛选
        if is_modern:
            candidates = [name for name in candidates if name.is_modern]
        elif is_traditional:
            candidates = [name for name in candidates if name.is_traditional]

        if not candidates:
            # 如果没有符合条件的名字，返回随机名字
            all_names = []
            for names in self.first_names.values():
                all_names.extend(names)
            return random.choice(all_names)

        return random.choice(candidates)

    def generate_last_name(self,
                           ethnicity: Optional[Ethnicity] = None,
                           is_common: bool = False) -> LastName:
        """生成姓氏"""

        # 筛选候选姓氏
        if ethnicity:
            candidates = [name for name in self.last_names
                          if name.ethnicity == ethnicity]
        else:
            candidates = self.last_names

        # 如果指定常见姓氏
        if is_common:
            candidates = [name for name in candidates if name.is_common]

        if not candidates:
            # 如果没有符合条件的姓氏，返回随机姓氏
            return random.choice(self.last_names)

        return random.choice(candidates)

    def generate_middle_name(self, gender: Gender) -> str:
        """生成中间名"""
        return random.choice(self.middle_names[gender])

    def generate_suffix(self, probability: float = 0.1) -> Optional[str]:
        """生成姓名后缀"""
        if random.random() < probability:
            return random.choice(self.name_suffixes)
        return None

    def generate_full_name(self,
                           gender: Optional[Gender] = None,
                           ethnicity: Optional[Ethnicity] = None,
                           include_middle: bool = False,
                           include_suffix: bool = False,
                           suffix_probability: float = 0.1,
                           format_style: str = 'standard') -> FullName:
        """生成完整姓名"""

        # 生成名字
        first_name_obj = self.generate_first_name(gender, ethnicity)

        # 生成姓氏
        last_name_obj = self.generate_last_name(ethnicity)

        # 生成中间名
        middle_name = None
        if include_middle and random.random() > 0.5:  # 50%的概率有中间名
            middle_name = self.generate_middle_name(first_name_obj.gender)

        # 生成后缀
        suffix = None
        if include_suffix:
            suffix = self.generate_suffix(suffix_probability)

        # 构建完整姓名
        if format_style == 'formal':
            if middle_name and suffix:
                full_name = f"{first_name_obj.name} {middle_name} {last_name_obj.name} {suffix}"
            elif middle_name:
                full_name = f"{first_name_obj.name} {middle_name} {last_name_obj.name}"
            elif suffix:
                full_name = f"{first_name_obj.name} {last_name_obj.name} {suffix}"
            else:
                full_name = f"{first_name_obj.name} {last_name_obj.name}"
        else:  # standard
            if suffix:
                full_name = f"{first_name_obj.name} {last_name_obj.name} {suffix}"
            else:
                full_name = f"{first_name_obj.name} {last_name_obj.name}"

        # 格式化姓名
        if format_style == 'last_first':
            if middle_name:
                formatted_name = f"{last_name_obj.name}, {first_name_obj.name} {middle_name}"
            else:
                formatted_name = f"{last_name_obj.name}, {first_name_obj.name}"
        elif format_style == 'initials':
            initials = f"{first_name_obj.name[0]}."
            if middle_name:
                initials += f"{middle_name[0]}."
            initials += f" {last_name_obj.name}"
            formatted_name = initials
        else:  # standard
            formatted_name = full_name

        return FullName(
            first_name=first_name_obj.name,
            last_name=last_name_obj.name,
            middle_name=middle_name,
            suffix=suffix,
            gender=first_name_obj.gender,
            ethnicity=last_name_obj.ethnicity,
            full_name=full_name,
            formatted_name=formatted_name
        )

    def generate_batch(self,
                       count: int = 10,
                       gender: Optional[Gender] = None,
                       ethnicity: Optional[Ethnicity] = None,
                       include_middle: bool = False) -> List[FullName]:
        """批量生成姓名"""

        names = []
        for _ in range(count):
            name = self.generate_full_name(gender, ethnicity, include_middle)
            names.append(name)

        return names

    def generate_with_pattern(self, pattern: str) -> str:
        """按照指定模式生成姓名"""
        patterns = {
            'alliterative': lambda: self._generate_alliterative_name(),
            'double_first': lambda: self._generate_double_first_name(),
            'hyphenated_last': lambda: self._generate_hyphenated_last_name(),
            'traditional': lambda: self._generate_traditional_name(),
            'modern': lambda: self._generate_modern_name(),
        }

        if pattern in patterns:
            return patterns[pattern]()

        return self.generate_full_name().full_name

    def _generate_alliterative_name(self) -> str:
        """生成头韵姓名（如 Peter Parker）"""
        letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        # 找以该字母开头的名字
        first_candidates = []
        for gender in [Gender.MALE, Gender.FEMALE]:
            for name in self.first_names[gender]:
                if name.name.startswith(letter):
                    first_candidates.append(name)

        # 找以该字母开头的姓氏
        last_candidates = [name for name in self.last_names
                           if name.name.startswith(letter)]

        if first_candidates and last_candidates:
            first = random.choice(first_candidates)
            last = random.choice(last_candidates)
            return f"{first.name} {last.name}"

        return self.generate_full_name().full_name

    def _generate_double_first_name(self) -> str:
        """生成双名（如 Mary Kate）"""
        gender = random.choice([Gender.MALE, Gender.FEMALE])

        first1 = self.generate_first_name(gender)
        first2 = self.generate_first_name(gender)
        last = self.generate_last_name()

        return f"{first1.name}-{first2.name} {last.name}"

    def _generate_hyphenated_last_name(self) -> str:
        """生成连字符姓氏"""
        last1 = self.generate_last_name()
        last2 = self.generate_last_name()

        # 确保两个姓氏不同
        while last2.name == last1.name:
            last2 = self.generate_last_name()

        first = self.generate_first_name()

        return f"{first.name} {last1.name}-{last2.name}"

    def _generate_traditional_name(self) -> str:
        """生成传统姓名"""
        first = self.generate_first_name(is_traditional=True)
        last = self.generate_last_name()

        return f"{first.name} {last.name}"

    def _generate_modern_name(self) -> str:
        """生成现代姓名"""
        first = self.generate_first_name(is_modern=True)
        last = self.generate_last_name()

        return f"{first.name} {last.name}"

    @classmethod
    def get_name_statistics(cls, names: List[str]) -> Dict:
        """分析姓名统计信息"""
        stats = {
            'total': len(names),
            'gender_distribution': {'male': 0, 'female': 0, 'unisex': 0},
            'ethnicity_distribution': {},
            'most_common_first': {},
            'most_common_last': {},
            'name_lengths': {'first': [], 'last': []}
        }

        for name_str in names:
            # 简单解析姓名
            parts = name_str.split()
            if len(parts) >= 2:
                first = parts[0]
                last = parts[-1]

                # 记录长度
                stats['name_lengths']['first'].append(len(first))
                stats['name_lengths']['last'].append(len(last))

                # 统计姓氏
                stats['most_common_last'][last] = stats['most_common_last'].get(last, 0) + 1

        return stats

    @classmethod
    def validate_name(cls, name_str: str) -> Dict:
        """验证姓名有效性"""
        result = {
            'name': name_str,
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }

        if not name_str or not name_str.strip():
            result['is_valid'] = False
            result['errors'].append('姓名不能为空')
            return result

        parts = name_str.strip().split()

        if len(parts) < 2:
            result['warnings'].append('通常需要名和姓')

        # 检查每个部分
        for i, part in enumerate(parts):
            if not part:
                result['errors'].append(f'第{i + 1}部分为空')
                result['is_valid'] = False

            # 检查是否包含数字
            if any(char.isdigit() for char in part):
                result['warnings'].append(f'第{i + 1}部分包含数字: {part}')

            # 检查特殊字符
            if re.search(r'[^\w\s-]', part):
                result['warnings'].append(f'第{i + 1}部分包含特殊字符: {part}')

        return result

    def generate_celebrity_name(self) -> str:
        """生成名人风格的姓名"""
        celebrity_patterns = [
            # 单名名人
            lambda: random.choice(["Beyoncé", "Madonna", "Cher", "Prince", "Rihanna"]),
            # 全名反转
            lambda: f"{self.generate_last_name().name} {self.generate_first_name().name}",
            # 中间名作为姓
            lambda: f"{self.generate_first_name().name} {self.generate_middle_name(random.choice([Gender.MALE, Gender.FEMALE]))}",
            # 艺名
            lambda: f"The {random.choice(['Weeknd', 'Rock', 'Game', 'Dream', 'Artist'])}",
        ]

        return random.choice(celebrity_patterns)()


if __name__ == '__main__':
    generator = EmailGenerator()
    for i in range(10):
        print(generator.generate_email())
    generator = PassportGenerator()
    for i in range(10):
        print(generator.generate(country_code="CN"))
    generator = PostalCodeGenerator()
    test_countries = ['US', 'GB', 'CN', 'JP', 'DE', 'CA', 'FR', 'AU', 'BR', 'IN']

    for country in test_countries:
        postal_code = generator.generate_postal_code(country)
        info = generator.get_country_info(country)
        print(f"{info.country_name:10s} ({country}): {postal_code:15s} 格式: {info.format_pattern}")

    multiple = generator.generate_multiple(country_codes=['US', 'GB', 'CN', 'JP'], count=5)
    for item in multiple:
        print(f"{item['country_name']:10s}: {item['postal_code']}")

    # 生成单个手机号码
    generator = MobileNumberGenerator()
    result = generator.generate_mobile_number('CN')  # 中国手机号
    print(result['full_international'])  # +86 138-0013-8000
    print(result['number'])  # 13800138000

    result = generator.generate_mobile_number('US')  # 美国手机号
    print(result['full_international'])  # +1 (212) 555-1234

    generator = USCityGenerator()

    # 生成随机城市
    city = generator.generate_city()
    print(f"{city.name}, {city.state_abbr}")  # Winston-Salem, NC

    # 仅生成城市名
    city_name = generator.generate_city_name()  # Houston
    print(city_name)

    generator = USStreetGenerator()
    # 示例1: 生成基本地址
    print("1. 基本地址示例:")
    for _ in range(5):
        address = generator.generate_full_address()
        print(f"  • {address.full_address}")

    # 示例2: 生成特定州的地址
    print("\n2. 加利福尼亚州地址:")
    for _ in range(3):
        address = generator.generate_full_address('CA')
        print(f"  • {address.full_address}")

    generator = USHouseNumberGenerator()
    print(generator.generate_house_number().number)

    generator = USNameGenerator()

    test_cases = [
        (Gender.MALE, Ethnicity.EUROPEAN, "欧洲裔男性"),
        (Gender.FEMALE, Ethnicity.EUROPEAN, "欧洲裔女性"),
        (Gender.MALE, Ethnicity.AFRICAN_AMERICAN, "非裔男性"),
        (Gender.FEMALE, Ethnicity.AFRICAN_AMERICAN, "非裔女性"),
        (Gender.MALE, Ethnicity.HISPANIC, "西班牙裔男性"),
        (Gender.FEMALE, Ethnicity.HISPANIC, "西班牙裔女性"),
        (Gender.MALE, Ethnicity.ASIAN, "亚裔男性"),
        (Gender.FEMALE, Ethnicity.ASIAN, "亚裔女性")
    ]

    for gender, ethnicity, description in test_cases:
        name = generator.generate_full_name(gender, ethnicity)
        print(f"  {description:15s}: {name.full_name}, {name.last_name}, {name.first_name}")
