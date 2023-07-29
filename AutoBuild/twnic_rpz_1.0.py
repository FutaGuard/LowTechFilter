import requests, json
from bs4 import BeautifulSoup

soup = BeautifulSoup(requests.get("https://rpz.twnic.tw/e.html").text, "html.parser")
exec(str(soup.find("script")).split(";")[0].split("const ")[1])
twnic_rpz_1_0_raw = ""
twnic_rpz_1_0_AdGuardHome = ""
for i in rpzdata:
    for datap in i["domains"]:
        twnic_rpz_1_0_raw += datap + "\n"
        twnic_rpz_1_0_AdGuardHome += "||" + datap + "^\n"
with open("TWNIC-RPZ-1.0_RAW.txt","a") as f:
    f.write(twnic_rpz_1_0_raw)
    f.close()
with open("TWNIC-RPZ-1.0_AGH.txt","a") as f:
    f.write(twnic_rpz_1_0_AdGuardHome)
    f.close()
