import requests, json
from bs4 import BeautifulSoup

rawData = BeautifulSoup(requests.get("https://rpz.twnic.tw/e.html").text, "html.parser")
rpzdata = json.loads(a.split("<script>")[1].split(";")[0].split("= ")[1])
twnic_rpz_1_0_raw = ""
twnic_rpz_1_0_AdGuardHome = ""
for i in rpzdata:
    for datap in i["domains"]:
        twnic_rpz_1_0_raw += datap + "\n"
        twnic_rpz_1_0_AdGuardHome += "||" + datap + "^\n"
with open("TWNIC-RPZ-1.0_RAW.txt","w") as f:
    f.write(twnic_rpz_1_0_raw)
with open("TWNIC-RPZ-1.0_AGH.txt","w") as f:
    f.write(twnic_rpz_1_0_AdGuardHome)
