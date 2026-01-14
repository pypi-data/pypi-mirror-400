import datetime
import json
import re
from dataclasses import dataclass, field
from typing import Union, List, Optional, Dict, Callable, TYPE_CHECKING

from loguru import logger
from parsel import Selector

from ._internal import _join_url
from .lazy import LazyLoader

if TYPE_CHECKING:
    import dateparser
    import pandas as pd
else:
    dateparser = LazyLoader("dateparser")  # type: ignore
    pd = LazyLoader("pandas")  # type: ignore


@dataclass
class AttachmentsAndImagesResult:
    """
    封装附件和图片的结果
    """
    file_urls: List[str] = field(default_factory=list)  # 文件链接列表
    file_names: List[str] = field(default_factory=list)  # 文件名称列表
    image_urls: List[str] = field(default_factory=list)  # 图片链接列表
    image_names: List[str] = field(default_factory=list)  # 图片名称列表


def get_column_list(text: str, xpath: str, str_add_head: str = '', str_add_tail: str = '', auto_wash: bool = True) -> \
        list[str]:
    if isinstance(text, str):
        selector = Selector(text=text)
        value_list = selector.xpath(xpath).getall()
        if auto_wash:
            value_new_list = []
            for value in value_list:
                value = value.replace(' ', '').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('\t', '')
                value_new_list.append(str_add_head + value + str_add_tail)
            return list(value_new_list)
        else:
            return value_list
    else:
        return []


def get_column(text: str, xpath: str, str_add_head: str = '', str_add_tail: str = '', auto_wash: bool = True) -> str:
    if isinstance(text, str):
        selector = Selector(text=text)
        value_list = selector.xpath(xpath).getall()
        if auto_wash:
            result = []
            for value in value_list:
                value = value.replace(' ', '').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('\t',
                                                                                                               '').replace(
                    '\u3000', '')
                result.append(value)
            result_result = str_add_head + ''.join(result) + str_add_tail

            return result_result
        else:
            return ''.join(value_list)


def get_content(text: str, xpath_expression: str, auto_space: bool = True) -> str:
    """
    获取正文内容，并忽略style、script标签
    :param text: HTML文本
    :param xpath_expression: XPath表达式
    :param auto_space: 是否自动去除空格（True：去除所有空格，False：保留单个空格）
    :return: 清理后的文本内容
    """
    if not text:
        return ''

    selector = Selector(text=text)

    # 移除style和script标签
    for style in selector.xpath(xpath_expression + '//style'):
        style.drop()
    for script in selector.xpath(xpath_expression + '//script'):
        script.drop()

    # 提取内容并拼接
    contents = selector.xpath(xpath_expression).xpath('string(.)').getall()
    content = ''.join(contents).strip() \
        .replace('\r', '') \
        .replace('\n', '') \
        .replace('\xa0', '') \
        .replace('\t', '') \
        .strip()

    if auto_space:
        content = content.replace(' ', '')
    else:
        content = re.sub(r' +', ' ', content)

    return content


def xpath_kv(selector: Union[Selector, str], item_xpath: str, key_xpath: str, value_xpath: str) -> list[
    tuple[str, str]]:
    if isinstance(selector, str):
        selector = Selector(text=selector)
    item_list = selector.xpath(item_xpath)
    result = []
    for item_selector in item_list:
        name = ''.join(item_selector.xpath(key_xpath).getall()).strip().replace('\n', ' ').replace('\t', ' ').replace(
            '\r', ' ').replace(' ', '').replace('\xa0', '')
        v = item_selector.xpath(value_xpath).get()
        value = v if v else ''
        item = (name, value)
        result.append(item)
    return result

class Att:
    file_extensions = ['.rar', '.zip', '.7z', '.tar', '.gz', '.docx', '.doc', '.xlsx', '.xls', '.pdf', '.txt', '.csv',
                       '.et', '.ceb']
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']


    @staticmethod
    def _handel_att_json(item_list: list[tuple[str, str]], base_url) -> str:
        result = {}
        i = 0
        for name, href in item_list:
            href = _join_url(base_url, href)
            fj = f'{name}|{href}'
            if fj not in result.values():
                i += 1
                result[f'fj{i}'] = fj
        if not result:
            return ""
        else:
            return json.dumps(result, ensure_ascii=False, separators=(',', ':'))

    @staticmethod
    def get_attachments(text: Union[Selector, str], xpath_expression: str, file_ext: Union[list, str] = '', image=False, base_url='', handel=False) -> Union[list[tuple[str, str]], str]:
        file_extensions = Att.file_extensions.copy()
        image_extensions = Att.image_extensions.copy()
        if isinstance(text, str):
            text = Selector(text=text)
        if file_ext:
            if isinstance(file_ext, str):
                file_ext = [file_ext]
            file_extensions += file_ext
        if image:
            file_extensions += image_extensions
        # 添加大写后缀
        file_extensions += [ext.upper() for ext in file_extensions]
        pattern = re.compile(r'(?:' + '|'.join(re.escape(e) for e in file_extensions) + r')(?=[?]|$)')
        file_extensions_xpath = ' or '.join(
            f'contains(@href,"{ext}")'
            # f'substring(@href, string-length(@href) - {len(ext) - 1}) = "{ext}"'
            for ext in file_extensions
        )
        file_a_xpath = f'{xpath_expression}//a[{file_extensions_xpath}]'
        file_result = xpath_kv(text, file_a_xpath, 'string(.)', './@href')
        file_result = [
            (name, href) for name, href in file_result
            if href and pattern.search(href)
        ]
        if handel: return Att._handel_att_json(file_result, base_url)
        return file_result

    @staticmethod
    def get_images(text: Union[Selector, str], xpath_expression: str, image_ext: Union[list, str] = '', base_url='', handel=False) -> Union[list[tuple[str, str]], str]:
        image_extensions = Att.image_extensions.copy()
        if image_ext:
            if isinstance(image_ext, str):
                image_ext = [image_ext]
            image_extensions += image_ext
        image_extensions += [ext.upper() for ext in image_extensions]
        pattern = re.compile(r'(?:' + '|'.join(re.escape(e) for e in image_extensions) + r')(?=[?]|$)')
        image_extensions_xpath = ' or '.join(
            f'contains(@src,"{ext}")'
            # f'substring(@src, string-length(@src) - {len(ext) - 1}) = "{ext}"'
            for ext in image_extensions
        )
        image_img_xpath = f'{xpath_expression}//img[{image_extensions_xpath}]'
        image_result = xpath_kv(text, image_img_xpath, './@alt', './@src')
        image_result = [
            (name, href) for name, href in image_result
            if href and pattern.search(href)
        ]
        if handel: return Att._handel_att_json(image_result, base_url)

        return image_result

def get_attachments_and_images(text: str, xpath_expression: str, file_ext: Union[list, str] = '') -> AttachmentsAndImagesResult:
    """
    获取正文中的附件和图片链接及名称
    :param text: HTML文本
    :param xpath_expression: XPath表达式
    :param file_ext: 额外的文件后缀（可选）
    :return: AttachmentsAndImagesResult 对象，包含文件链接、文件名称、图片链接、图片名称
    """
    selector = Selector(text=text)
    file_urls = []
    file_names = []
    file_result = Att.get_attachments(selector, xpath_expression, file_ext)
    for file in file_result:
        file_names.append(file[0])
        file_urls.append(file[1])
    image_urls = []
    image_names = []
    image_result = Att.get_images(selector, xpath_expression, file_ext)
    for image in image_result:
        image_names.append(image[0])
        image_urls.append(image[1])
    return AttachmentsAndImagesResult(
        file_urls=file_urls,
        file_names=file_names,
        image_urls=image_urls,
        image_names=image_names
    )


def get_p_list(xpath: str, text: str) -> list[str]:
    """
    获取这一级所有 p 标签的 content
    :param xpath: XPath 表达式
    :param text: HTML 文本
    :return: 清理后的 p 标签内容列表
    """
    selector = Selector(text=text)
    p_tags = selector.xpath(xpath).getall()
    ps = []
    for p in p_tags:
        # 使用 Selector 解析每个 p 标签的内容
        p_content = Selector(text=p).xpath('string(.)').get().strip() \
            .replace(' ', '') \
            .replace('\r', '') \
            .replace('\n', '') \
            .replace('\xa0', '') \
            .replace('\t', '') \
            .replace(' ', '')
        ps.append(p_content)
    return ps


def get_p_value(p_list: list[str], *keys: str) -> Optional[str]:
    """
    从 p_list 中查找以任意一个 key 开头的内容，并返回匹配的值
    """
    for p in p_list:
        for key in keys:
            if re_match := re.search(f'^{key}(.*)', p):
                return re_match.group(1).strip()
    return None


def parse_date(date_str: str) -> Union[datetime.datetime, None]:
    """
    动态解析日期字符串(严格模式)
    :param date_str:
    :return:
    """
    if not date_str:
        return None

    return dateparser.parse(str(date_str), settings={'STRICT_PARSING': True})


def parse_table(
        trs: List[str],
        header_str: Optional[str] = None,
        skip_line: Optional[int] = None,
        nested: bool = False,
        column_mapper: Optional[Dict[str, str]] = None,
        multi_header: bool = False,
        skip_empty_rows: bool = True,
        cell_formatter: Optional[Callable[[str], str]] = None
) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
    """
        解析 HTML 表格，支持嵌套表格、自定义列名映射、多表头行
        :param trs: 表格里的 tr 标签数组
        :param header_str: 判断表头的字符串
        :param skip_line: 跳过指定行数
        :param nested: 是否解析嵌套表格
        :param column_mapper: 自定义列名映射规则
        :param multi_header: 是否支持多行表头
        :param skip_empty_rows: 是否跳过空行
        :param cell_formatter: 自定义单元格内容格式化函数
        :return: 解析后的表格数据（字典列表）
        """

    if not trs:
        return []

    # 跳过指定行数
    if skip_line and skip_line > 0:
        trs = trs[skip_line:]

    # 检查表头下标
    header_index = -1
    for i, tr in enumerate(trs):
        if header_str and header_str in tr:
            header_index = i
            break
    if header_index == -1:
        return []

    # 获取表头
    header_trs = [trs[header_index]]
    if multi_header:
        # 如果支持多行表头，继续向上查找表头行
        for i in range(header_index - 1, -1, -1):
            if any(tag in trs[i] for tag in ['<th>', '<td>']):
                header_trs.insert(0, trs[i])
            else:
                break

    columns = []
    for header_tr in header_trs:
        header_selector = Selector(text=header_tr)
        header_tds = header_selector.xpath('//td | //th').getall()
        current_columns = [
            Selector(text=td).xpath('string(.)').get().strip()
            .replace(' ', '')
            .replace('\r', '')
            .replace('\n', '')
            .replace('\xa0', '')
            .replace('\t', '')
            for td in header_tds
        ]
        if not columns:
            columns = current_columns
        else:
            # 合并多行表头
            columns = [f"{col1}_{col2}" if col2 else col1 for col1, col2 in zip(columns, current_columns)]

    # 自定义列名映射
    if column_mapper:
        columns = [column_mapper.get(col, col) for col in columns]

    # 解析表格内容
    result = []
    for tr in trs[header_index + 1:]:
        content_selector = Selector(text=tr)
        content_tds = content_selector.xpath('//td').getall()

        if len(content_tds) != len(columns):  # 如果列数不匹配，跳过该行
            continue

        item = {}
        for i, td in enumerate(content_tds):
            td_selector = Selector(text=td)
            td_text = (td_selector.xpath('string(.)').get().strip()
                       .replace('\r', '')
                       .replace('\n', '')
                       .replace('\xa0', '')
                       .replace('\t', ''))

            # 自定义单元格内容格式化
            if cell_formatter:
                td_text = cell_formatter(td_text)

            # 解析嵌套表格
            if nested and '<table' in td:
                nested_tables = td_selector.xpath('//table').getall()
                if nested_tables:
                    td_text = parse_table(nested_tables, header_str=header_str, nested=True)

            item[columns[i]] = td_text

        # 跳过空行
        if skip_empty_rows and all(not value for value in item.values()):
            continue

        result.append(item)

    return result


def parse_excel(path, header_str, merge=False):
    try:
        p = pd.read_excel(path)
    except Exception as e:
        logger.error(e)
        return []
    # header_str = '案件名称'
    # 获取表头那一行
    header_index = -1

    if header_str in p.columns:
        columns = p.columns
        header_index = 0
    else:
        for i, v in enumerate(p.values):
            if header_str in v:
                header_index = i
                break
        columns = p.values[header_index]
    if header_index == -1:
        return []
    result = []
    for v in p.values[header_index + 1:]:
        item = {}
        for i, column in enumerate(columns):
            item[column] = v[i]
        result.append(item)

    return result


def parse_excel_v2(path, header_str: Union[list[str], str]):
    # 如果header_str是字符串，则调用parse_excel
    if not isinstance(header_str, list):
        return parse_excel(path, header_str)
    if len(header_str) < 2:
        return []

    try:
        df = pd.read_excel(path, header=None)
    except Exception as e:
        logger.error(e)
        return []

    # 查找最后一个表头的索引
    last_header = header_str[-1]
    last_index = next((i for i, row in enumerate(df.values) if last_header in row), -1)

    if last_index == -1:
        return []

    # 验证表头行是否包含header_str中的元素
    header_start_index = last_index - len(header_str) + 1
    if header_start_index < 0 or not all(any(header_str[j] in str(cell) for cell in df.iloc[idx]) for j, idx in
                                         enumerate(range(header_start_index, last_index + 1))):
        columns = df.iloc[last_index].tolist()
    else:
        # 前向填充表头行
        header_df = df.iloc[header_start_index:last_index + 1].ffill(axis=0)
        # 取最后一行作为真正的表头
        columns = header_df.iloc[-1].tolist()

    # 生成结果列表
    result = []
    for row in df.values[last_index + 1:]:
        item = {col: value for col, value in zip(columns, row)}
        result.append(item)

    return result
