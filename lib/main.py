import re
import sys

def extract_data(log_line):
    """
    Extracts data from a given log line, handling both standard and malformed lines.

    Args:
      log_line: The log line string.

    Returns:
      A dictionary containing the extracted data or None if the line is malformed.
    """

    standard_pattern = re.compile(
        r'(?P<ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<date_time>[^\]]+)\]'
        r' "(?P<request_method>\w+) (?P<request_path>[^"]+) HTTP/\d+\.\d+"'
        r' (?P<status_code>\d+) (?P<response_size>\d+|-) "(?P<referer>.*?)"'
        r' "(?P<user_agent>.*?)"'
    )
    
    malformed_pattern = re.compile(
         r'(?P<ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<date_time>[^\]]+)\]'
         r' "(?P<request>.*?)"'
         r' (?P<status_code>\d+) (?P<response_size>\d+|-) "(?P<referer>.*?)"'
         r' "(?P<user_agent>.*?)"'
    )

    match = standard_pattern.match(log_line)

    if match:
        return {"type": "standard", "data": match.groupdict()}
    else:
        match = malformed_pattern.match(log_line)
        if match:
            return {"type": "malformed", "data": match.groupdict()}
        else:
            return None

for line in sys.stdin :
    print(extract_data(line))
    