import re
import typing as t
from .chunk import chunkwise


def load(data: str, preserve_comments: bool = False):
    out_dict = {}
    out_list = []
    
    def backward_list():
        assert (
            info['nested_list']['parent_chain'] and
            info['level'] > 0
        )
        info['nested_list']['innerest_list'] = (
            info['nested_list']['parent_chain'].pop()
        )
        info['level'] -= 1
    
    def insert_child_list():
        if info['nested_list']['innerest_list'] is None:
            info['nested_list']['innerest_list'] = []
            info['nested_list']['complete_list'].append(
                info['nested_list']['innerest_list']
            )
            info['nested_list']['parent_chain'].append(
                info['nested_list']['complete_list']
            )
        else:
            info['nested_list']['innerest_list'].append([])
            info['nested_list']['parent_chain'].append(
                info['nested_list']['innerest_list']
            )
            info['nested_list']['innerest_list'] = (
                info['nested_list']['innerest_list'][0]
            )
    
    def get_key(text: str):
        if is_quoted(text):
            return text[1:-1]
        return text
    
    def is_complete():
        pass
    
    def is_comment(text):
        return text.startswith('#')
    
    def is_empty():
        return item == ''
    
    def is_key_only(text: str):
        return text.rstrip().endswith(':')
    
    def is_kv_pair(text: str):
        pass
    
    def is_list(text: str):
        return text.startswith('- ')
    
    def is_quoted(text):
        pass
    
    flag = 'START'
    info = {
        'level': 0,
        'nested_list': {
            'complete_list': [],
            'parent_chain': [],
            'innerest_list': None,
        },
    }
    for last, curr, next in chunkwise(data.splitlines(), 3, 1):
        if flag == 'START':
            if is_list(curr):
                item = curr[2:]
                flag = 'TOP_LIST'
                info['level'] = 1
                while True:
                    if is_list(item):
                        item = item[2:]
                        info['level'] += 1
                        insert_child_list()
                    else:
                        break
                if is_comment(item):
                    raise Exception(curr)
                elif is_empty():
                    info['nested_list']['innerest_list'].append(None)
                
            while True:
                if is_list(curr):
                    temp1 = curr[2:]
                    if temp2 is None:
                        temp2 = [temp1]
                else:
                    break
            if is_list(curr):
                if is_key_only(curr):
                    ctx['key'] = get_key(curr[2:-1])
                elif is_kv_pair(curr):
                    pass
            
        if is_comment(curr):
            continue
    
    for line in data.splitlines():
        if flag == 'DEFAULT':
            if line.startswith('- '):
                item = line[2:].rstrip()
                out_list.append(item)
                flag = 'TOP_LIST'
                
        if line.startswith('# '):
            continue
        if line.startswith(('"', "'")):
            next_quote_pos = 1 + line[1:].index(line[0])
            assert line[next_quote_pos + 1] == ':'
            key = line[1:next_quote_pos]
            val = line[next_quote_pos + 1:]
            if _is_quoted(val):
                val = _strip_quotes(val)
        if line.startswith('-'):
            pass


def _is_quoted(text):
    pass


# noinspection PyTypeChecker
def _split_top_dicts(lines: t.Tuple[str, ...]) -> t.Iterator[t.Iterable[str]]:
    flag = 'START'
    temp = {'lines': [], 'ruler': 0}
    
    def analyze_key(text: str):
        if text.rstrip().endswith(': |'):
            return 'textarea'
        return 'normal'
    
    def analyze_value(text: str):
        if text[0] == '-':
            pass
    
    def is_comment(text: str):
        return text.startswith('#')
    
    def is_complete_kv_pair(text: str):
        if text.rstrip().endswith((':', ': |')):
            return False
        else:
            assert ':' in text
            return True
    
    def is_empty(text: str):
        return text.strip() == ''
    
    def is_new_item(text: str):
        if text.strip():
            if text[0]:
                if text[:2] == '- ':
                    raise Exception(text)
                return True
        return False
    
    def submit():
        yield from temp['lines']
        temp['lines'].clear()
    
    for curr, next in chunkwise(lines, 2):
        if is_comment(curr):
            continue
    
        if flag == 'START':
            if not is_empty(curr):
                if is_complete_kv_pair(curr):
                    yield (curr,)
                else:
                    temp['lines'].append(curr)
                    if analyze_key(curr) == 'textarea':
                        flag = 'TEXTAREA'
                    else:
                        flag = 'START_SEEKING_VALUE'
            continue
        
        if flag == 'TEXTAREA':
            temp['lines'].append(curr)
            if is_new_item(next):
                assert len(temp['lines']) > 1
                yield temp['lines']
                temp['lines'].clear()
                flag = 'START'
            continue
            
        if flag == 'START_SEEKING_VALUE':
            if not is_empty(curr):
                if line[0] == '-':
                    assert line[1] == ' '
                    temp['lines'].append(line)
                    temp['ruler'] = len(line[1:]) - len(line[1:].lstrip()) + 1
                    flag = 'SEEK_LIST'
                elif line[0] == ' ':
                    temp['ruler'] = len(line) - len(line.lstrip())
                    temp['lines'].append(line)
                    flag = 'SEEK_VALUE'
                else:
                    yield temp['lines']
                    temp['lines'].clear()
                    
                    if is_complete_kv_pair(curr):
                        yield (curr,)
                        flag = 'START'
                    else:
                        temp['lines'].append(curr)
                        if analyze_key(curr) == 'textarea':
                            flag = 'TEXTAREA'
                        else:
                            flag = 'START_SEEKING_VALUE'
            continue
            
        if flag == 'SEEK_LIST':
            if line.strip():
                if line[0] == '-':
                    assert line[1] == ' '
                    temp['lines'].append(line)
                elif line[0] == ' ':
                    indent = len(line) - len(line.lstrip())
                    assert indent == temp['ruler']
                    temp['lines'].append(line)
                else:
                    yield temp['lines']
                    temp['lines'].clear()
                    
                    if line.rstrip().endswith(':'):
                        temp['lines'].append(line)
                        flag = 'START_SEEKING_VALUE'
                    else:
                        assert ':' in line
                        yield line
                        flag = 'START'
            continue
            
        if flag == 'SEEK_VALUE':
            if line.strip():
                if line[0] == ' ':
                    indent = len(line) - len(line.lstrip())
                    assert indent >= temp['ruler']
                    temp['lines'].append(line)
                else:
                    yield temp['lines']
                    temp['lines'].clear()
                    
                    if line.rstrip().endswith(':'):
                        temp['lines'].append(line)
                        flag = 'START_SEEKING_VALUE'
                    else:
                        assert ':' in line
                        yield line
                        flag = 'START'
            continue


def _strip_quotes(text: str):
    pass
