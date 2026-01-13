import re

def parse_string(input_string):
    if "$" in input_string: return "$", [0]
    regex_format1 = r'([A-Za-z0-9]+):(\d+)'
    match = re.match(regex_format1, input_string)
    if match:
        return match.group(1), [int(eval(match.group(2)))]
    else:
        assert False, "Parsing error on "+input_string

def parse_packet_data_delay(input_string):
    if "$" in input_string: return "$", [0]
    regex_format2 = r'([A-Za-z]+)/(\d+,\d+)/(\d+)/([><])'
    match = re.match(regex_format2, input_string)
    if match:
        return match.group(1) + match.group(4), [int(float(match.group(2).replace(',', '.')) * 1e5)]
    else:
        assert False, "Parsing error on "+input_string

def parse_packet_data_size(input_string):
    if "$" in input_string: return "$", [0]
    regex_format2 = r'([A-Za-z]+)/(\d+,\d+)/(\d+)/([><])'
    match = re.match(regex_format2, input_string)
    if match:
        return match.group(1) + match.group(4), [int(eval(match.group(3)))]
    else:
        assert False, "Parsing error on "+input_string


