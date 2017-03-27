import re
import base64
import html
from bs4 import BeautifulSoup
import quopri

_email_utf8_encoded_string = re.compile(r'.*(\=\?UTF\-8\?B\?(.*)\?=).*')
_email_address = re.compile(r'[a-zA-Z0-9._%+\-"]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9_-]{2,}')
_ip = re.compile(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
_domain = re.compile(r'(((?=[a-zA-Z0-9-]{1,63}\.)[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,63})')
_url_regex = r'(((?:(?:https?|ftp)://)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_:\?]*)#?(?:[\.\!\/\\\w:%\?&;=-]*))?(?<!=))'
_url = re.compile(_url_regex)
_url_b = re.compile(_url_regex.encode())
_md5 = re.compile(r'^[a-fA-F0-9]{32}$')
_sha1 = re.compile(r'^[a-fA-F0-9]{40}$')
_sha256 = re.compile(r'^[a-fA-F0-9]{64}$')
_sha512 = re.compile(r'^[a-fA-F0-9]{128}$')
_strings = re.compile(b'[^\x00-\x1F\x7F-\xFF]{4,}')

def decode_utf_b64_string(value):
    match = _email_utf8_encoded_string.match(value)
    
    if match:
        # Match the full encoded portion of the string. Ex: =?UTF-8?B?TsKqOTE4NzM4Lmh0bWw=?=
        encoded_string_full = match.group(1)
        
        # Match just the base64 portion of the string. Ex: TsKqOTE4NzM4Lmh0bWw=
        encoded_string_base64 = match.group(2)
        
        # Decode the base64.
        decoded_string_base64 = base64.b64decode(encoded_string_base64).decode("utf-8")
        
        # Set the return value equal to the original encoded value, but replace the
        # full encoded portion of the string with the decoded base64.
        return value.replace(encoded_string_full, decoded_string_base64)
    else:
        return value

def find_urls(value):
    is_str = isinstance(value, str)
    is_bin = not is_str

    if is_str:
        regex_pattern = _url
    else:
        regex_pattern = _url_b

    urls = regex_pattern.findall(value)

    if not is_str:
        unescaped_urls = [html.unescape(url[0].decode('ascii', errors='ignore')) for url in urls]
    else:
        unescaped_urls = [html.unescape(url[0]) for url in urls]
    
    cleaned_urls = set()
    
    # Try to convert what we were given to soup and search for URLs.
    if is_bin:
        decoded_value = value.decode("utf-8", errors="ignore")
    else:
        decoded_value = value
    unquoted = quopri.decodestring(decoded_value)
    soup = BeautifulSoup(unquoted, "html.parser")
    tags = soup.find_all(href=True)
    for tag in tags:
        url = tag["href"]
        url = re.sub("\s+", "", url)
        unescaped_urls.append(url)

    # Check for embedded URLs inside other URLs.
    for url in unescaped_urls:
        cleaned_urls.add(url)
        
        for chunk in url.split("http://"):
            if chunk:
                if not chunk.startswith("http://") and not chunk.startswith("https://") and not chunk.startswith("ftp://"):
                    if is_url("http://" + chunk, bin=is_bin):
                        cleaned_urls.add("http://" + chunk)

        for chunk in url.split("https://"):
            if chunk:
                if not chunk.startswith("http://") and not chunk.startswith("https://") and not chunk.startswith("ftp://"):
                    if is_url("https://" + chunk, bin=is_bin):
                        cleaned_urls.add("https://" + chunk)
                    
        for chunk in url.split("ftp://"):
            if chunk:
                if not chunk.startswith("http://") and not chunk.startswith("https://") and not chunk.startswith("ftp://"):
                    if is_url("ftp://" + chunk, bin=is_bin):
                        cleaned_urls.add("ftp://" + chunk)

    return sorted(list(cleaned_urls))
    
def find_strings(value):
    matches = _strings.findall(value)
    return [str(s, 'utf-8') for s in matches]

def find_ip_addresses(value):
    return _ip.findall(value)

def find_domains(value):
    return _domain.findall(value)

def is_md5(value):
    try:
        if _md5.match(value):
            return True
        else:
            return False
    except TypeError:
        return False
    
def is_url(value, bin=False):
    try:
        if bin:
            if _url_b.match(value):
                return True
            else:
                return False
        else:
            if _url.match(value):
                return True
            else:
                return False
    except TypeError:
        return False
    
def is_sha1(value):
    try:
        if _sha1.match(value):
            return True
        else:
            return False
    except TypeError:
        return False
    
def is_sha256(value):
    try:
        if _sha256.match(value):
            return True
        else:
            return False
    except TypeError:
        return False

def is_sha512(value):
    try:
        if _sha512.match(value):
            return True
        else:
            return False
    except TypeError:
        return False

def is_ip(value):
    try:
        if _ip.match(value):
            return True
        else:
            return False
    except TypeError:
        return False
    
def is_domain(value):
    try:
        if _domain.match(value):
            return True
        else:
            return False
    except TypeError:
        return False
