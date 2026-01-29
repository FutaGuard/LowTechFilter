import re
from datetime import datetime, timedelta, timezone
import requests
from glob import glob
import asyncio
import time

filterlist = {
    "abp": [
        "experimental.txt",
        "filter.txt",
        "PureView/news.txt",
        "PureView/news_mobile.txt",
    ],
    "hosts": ["hosts.txt", "nofarm.txt", "TW165.txt", "TWNIC-RPZ.txt"],
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

        else:
            newoutput = "\n".join(f"||{e}^" for e in data)
            output.write(newhead)
            output.write(newoutput)


async def to_pure_domain(filename: str, data: str):
    data = data.splitlines()
    newdata = "\n".join(data)
    name = filename.split(".txt")[0].split("_")[0]
    with open(name + "_domains.txt", "w") as output:
        if name == "hosts":
            pattern = r"(?<=^\|\|)\S+\.\S{2,}(?=\^)"
            newoutput = "\n".join(re.findall(pattern, newdata, re.MULTILINE))
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
                    newfilename = "TW165-redirect.txt"
                    heads: str = HEAD().__getattribute__("abp")
                    newhead = heads.format(name="TW165 redirect", version=newversion)
                    with open(newfilename, "w") as f:
                        f.write(newhead)
                        f.write(
                            "".join(
                                f"||{e}^$dnsrewrite=NOERROR;A;34.102.218.71\n"
                                for e in data.splitlines()
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
