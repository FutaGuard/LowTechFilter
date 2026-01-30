import re
from datetime import datetime, timedelta, timezone
import requests
from glob import glob
import asyncio
import time
from urllib.parse import urlparse

# Domain 驗證相關
DOMAIN_PATTERN = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$", re.IGNORECASE)

filterlist = {
    "abp": [
        "experimental.txt",
        "filter.txt",
        "PureView/news.txt",
        "PureView/news_mobile.txt",
    ],
"hosts": ["hosts.txt", "nofarm.txt", "TWNIC-RPZ.txt", "TW165.txt"],
}
url = "https://filter.futa.gg/"
tz = timezone(timedelta(hours=+8))
today = datetime.now(tz).date()

#  新增 nrd 清單
for files in glob("nrd/past-*.txt"):
    filterlist["hosts"].append(files)


class HEAD:
    abp: str = (
        "[Adblock Plus]\n"
        "! Title: LowTechFilter {name}\n"
        "! Version: {version}\n"
        "! Expires: 1 hour\n"
        "! Homepage: https://t.me/AdBlock_TW\n"
        "! ----------------------------------------------------------------------\n"
    )
    hosts: str = (
        "! FutaHosts\n"
        "! Title: LowTechFilter {name}\n"
        "! URL: <https://github.com/FutaGuard/LowTechFilter>\n"
        "! Version: {version}\n"
        "! --------------------------------------------------\n"
    )


def is_valid_domain(hostname: str) -> bool:
    """檢查是否為合法的完整 domain"""
    if not hostname or len(hostname) > 253:
        return False
    if hostname.startswith(".") or hostname.endswith("."):
        return False
    if ".." in hostname:
        return False
    if not DOMAIN_PATTERN.match(hostname):
        return False
    parts = hostname.split(".")
    if len(parts) < 2:
        return False
    tld = parts[-1]
    if len(tld) < 2 or not tld.isalpha():
        return False
    return True


def strip_bang_comments(text: str) -> str:
    lines = text.splitlines(keepends=True)
    return "".join(line for line in lines if not line.lstrip().startswith("!"))


def update_version(filename: str) -> str:
    pattern = r"(?<=Version: )(\d+\.\d+\.)(\d+)"
    newversion = ""

    r = requests.get(url + filename)
    first = None
    version = None
    if r.status_code != 200:
        pass
    else:
        first = "\n".join(r.text.splitlines()[:5])

    try:
        version = re.findall(pattern, first, re.MULTILINE)[0]
    except:
        # https://www.ptt.cc/bbs/Battlegirlhs/M.1506615677.A.1A4.html
        version = ("2017.0929.", "1")

    dt = datetime.strptime(version[0], "%Y.%m%d.").date()
    newversion = today.strftime("%Y.%m%d.")
    if dt != today:
        newversion += "1"
    else:
        newversion += str(int(version[1]) + 1)
    return newversion


# make hosts formats
async def to_hosts(filename: str, data: str, newversion: str):
    data = data.splitlines()
    newdata = "\n".join(data)
    name = filename.split(".txt")[0].split("_")[0]
    heads: str = HEAD().__getattribute__("hosts")
    newhead = heads.format(name=name + " hosts", version=newversion)
    newfilename = name + "_hosts.txt" if name != "hosts" else "hosts.txt"
    with open(newfilename, "w") as output:
        if name == "hosts":
            pattern = r"(?<=^\|\|)\S+\.\S{2,}(?=\^)"
            newoutput = ""
            for e in re.findall(pattern, newdata, re.MULTILINE):
                if "*" not in e:
                    newoutput += "0.0.0.0 " + e + "\n"
        elif name == "TW165":
            # 只處理沒有 path 的 domain
            domains = []
            for line in data:
                parsed = parse_url(line)
                if not parsed['has_path'] and not parsed['is_ip']:
                    domains.append(parsed['domain'])
            newoutput = "\n".join("0.0.0.0 " + d for d in sorted(set(domains)))
        else:
            newoutput = "\n".join("0.0.0.0 " + e for e in data)
        output.write(newhead)
        output.write(newoutput)


async def to_abp(filename: str, data: str, newversion: str):
    data = data.splitlines()
    newdata = "\n".join(data)
    name = filename.split(".txt")[0].split("_")[0]
    heads: str = HEAD().__getattribute__("abp")
    newhead = heads.format(name=name + " abp", version=newversion)

    with open(name + "_abp.txt", "w") as output:
        if name == "hosts":
            output.write(newhead + newdata)
        elif name == "TW165":
            # 排除 IP，保留完整 URL (domain + path)
            rules = []
            for line in data:
                parsed = parse_url(line)
                if not parsed['is_ip']:
                    rules.append(f"||{parsed['full']}^")
            newoutput = "\n".join(sorted(set(rules)))
            output.write(newhead)
            output.write(newoutput)
        else:
            newoutput = "\n".join(f"||{e}^" for e in data)
            output.write(newhead)
            output.write(newoutput)


def parse_url(url: str) -> dict:
    """解析 URL，返回 domain 和 path 信息"""
    # 移除 http:// 或 https://
    url = url.strip()
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    
    # 分離 domain 和 path
    if '/' in url:
        parts = url.split('/', 1)
        domain = parts[0]
        path = '/' + parts[1]
    else:
        domain = url
        path = ''
    
    # 檢查是否為 IP
    is_ip = bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain))
    
    # 檢查是否為合法 domain
    is_valid = is_valid_domain(domain) if not is_ip else True
    
    return {
        'domain': domain,
        'path': path,
        'has_path': bool(path),
        'is_ip': is_ip,
        'is_valid': is_valid,
        'full': domain + path
    }


async def to_pure_domain(filename: str, data: str):
    data = data.splitlines()
    newdata = "\n".join(data)
    name = filename.split(".txt")[0].split("_")[0]
    with open(name + "_domains.txt", "w") as output:
        if name == "hosts":
            pattern = r"(?<=^\|\|)\S+\.\S{2,}(?=\^)"
            newoutput = "\n".join(re.findall(pattern, newdata, re.MULTILINE))
        elif name == "TW165":
            # 只保留沒有 path 的 domain，與 hosts 格式一致
            domains = []
            for line in data:
                line = line.strip()
                if not line:
                    continue
                parsed = parse_url(line)
                if not parsed['has_path'] and not parsed['is_ip'] and parsed['is_valid']:
                    domains.append(parsed['domain'])
            newoutput = "\n".join(sorted(set(domains)))
        else:
            newoutput = "\n".join(data)
        output.write(newoutput)


async def run():
    import time
    # task = []

    for category in filterlist:
        for filename in filterlist[category]:
            newversion = update_version(filename)

            with open(f"{filename}", "r") as files:
                data = strip_bang_comments(files.read())
                with open(f"{filename}", "w") as output:
                    heads: str = HEAD().__getattribute__(category)
                    newhead = heads.format(
                        name=filename.split(".")[0]
                        .replace("_", " ")
                        .replace("/", " ")
                        .title(),
                        version=newversion,
                    )
                    output.write(newhead)
                    output.write(data)

                # hide farm site from google 轉換 abp
                if filename == "nofarm.txt":
                    domain_list = ""
                    for domains in data.splitlines():
                        if not domains.startswith("!"):
                            domain = domains[2:-1]
                            domain_list += 'google.*##div.g:has(div[data-hveid] a[href*="{domain}"])\n'.format(
                                domain=domain
                            )
                    heads: str = HEAD().__getattribute__("abp")
                    newhead = heads.format(
                        name="hide farm content from google", version=newversion
                    )
                    with open("hide_farm_from_search.txt", "w") as f:
                        f.write(newhead + domain_list)

                if filename == "TW165.txt":
                    # 生成 redirect 格式：只處理沒有 path 的 domain
                    newfilename = "TW165_redirect.txt"
                    heads: str = HEAD().__getattribute__("abp")
                    newhead = heads.format(name="TW165 redirect", version=newversion)
                    with open(newfilename, "w") as f:
                        f.write(newhead)
                        domains = []
                        for line in data.splitlines():
                            parsed = parse_url(line)
                            if not parsed['has_path'] and not parsed['is_ip']:
                                domains.append(parsed['domain'])
                        f.write(
                            "\n".join(
                                f"||{d}^$dnsrewrite=NOERROR;A;34.102.218.71"
                                for d in sorted(set(domains))
                            )
                        )

                if category == "hosts":
                    task = [
                        asyncio.create_task(to_pure_domain(filename, data)),
                        asyncio.create_task(to_abp(filename, data, newversion)),
                        asyncio.create_task(to_hosts(filename, data, newversion)),
                    ]

    await asyncio.gather(*task)


if __name__ == "__main__":
    asyncio.run(run())
