# LowTechFilter（原 FutaFilter）

一款專為臺灣人設計的廣告阻擋規則。

## 為何叫做 LowTechFilter？

這是致敬[美秀集團](https://streetvoice.com/bisiugroup/)。

## 討論群組

嘿，有使用上的問題嗎？
歡迎到 Telegram 群組上討拍喔。
https://t.me/adblock_tw

## 訂閱網址

### DOM 清單（支援：AdBlock, AdGuard）

> LowTechFilter 專門處理網頁上的 DOM 元素處理。例：側邊廣告欄

- <https://filter.futa.gg/filter.txt>

> 隱藏 Google 搜尋結果裡的
> [農場文](https://content-farm-terminator.blogspot.com/2018/12/about-content-farm-terminator.html)
> 專用清單

- <https://filter.futa.gg/hide_farm_from_search.txt>

> experimental 實驗性清單，公開測試封鎖對策是否對現行服務有影響，無偵錯能力使用者不建議使用。

- <https://filter.futa.gg/experimental.txt>

> PureView 實驗性清單，將網頁不必要的元素去除，只保留最純粹的瀏覽體驗。

- <https://filter.futa.gg/PureView/news.txt>
- （行動裝置版）<https://filter.futa.gg/PureView/news_mobile.txt>

### DNS 清單（支援：AdGuard Home, AdGuard 的 DNS 過濾, Pi-hole, AdAway）

- <https://filter.futa.gg/hosts_abp.txt>
- <https://filter.futa.gg/nofarm_abp.txt>

> 由台灣 165 反詐騙提供

- <https://filter.futa.gg/TW165_abp.txt>

> 由台灣 165 反詐騙提供，並帶有覆寫功能（打開符合規則的網址後會提示已被 165 封鎖）。

- <https://filter.futa.gg/TW165_redirect.txt>

> 由台灣 165 反詐騙提供，純 domain 此為特定用途。

- <https://filter.futa.gg/TW165_domains.txt>

> 從網路上羅列的 NRD 清單，經過整理的版本，NRD (Newly Registered Domain
) 意思是近期註冊的網域，通常新註冊的網域有較高的風險，經常為詐騙集團所用，此清單提供過去 1 天致 30 天的清單
- <https://filter.futa.gg/nrd/past-01day_hosts.txt> （過去 1 天，hosts 格式）
- <https://filter.futa.gg/nrd/past-07day_abp.txt> （過去 7 天，adblock 格式）


| hosts 清單一覽 | LowTechHost                                          | TW165 台灣反詐騙                                     | TW RPZ 阻止解析清單                                      | NoFarm 農場文清單                                     | NRD 清單(過去1天)                                             |
| -------------- | ---------------------------------------------------- | ---------------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| Adblock 語法            | [訂閱連結](https://filter.futa.gg/hosts_abp.txt)     | [訂閱連結](https://filter.futa.gg/TW165_abp.txt)     | [訂閱連結](https://filter.futa.gg/TWNIC-RPZ_abp.txt)     | [訂閱連結](https://filter.futa.gg/nofarm_abp.txt)     | [訂閱連結](https://filter.futa.gg/nrd/past-01day_abp.txt) |
| hosts          | [訂閱連結](https://filter.futa.gg/hosts.txt)   | [訂閱連結](https://filter.futa.gg/TW165_hosts.txt)   | [訂閱連結](https://filter.futa.gg/TWNIC-RPZ_hosts.txt)   | [訂閱連結](https://filter.futa.gg/nofarm_hosts.txt)   | [訂閱連結](https://filter.futa.gg/nrd/past-01day_hosts.txt) |
| 純網域        | [訂閱連結](https://filter.futa.gg/hosts_domains.txt) | [訂閱連結](https://filter.futa.gg/TW165_domains.txt) | [訂閱連結](https://filter.futa.gg/TWNIC-RPZ_domains.txt) | [訂閱連結](https://filter.futa.gg/nofarm_domains.txt) | [訂閱連結](https://filter.futa.gg/nrd/past-01day_domains.txt) |




### Surge 語法

> Surge 專用的語法。

- <https://filter.futa.gg/Surge/filters.txt>

## 如何安裝

請參考 [wiki](https://github.com/FutaGuard/FutaFilter/wiki)

## Q&A

Q: 我用了這個規則之後發現我的噗浪連結打不開了欸！！！！\
A: 請服用這個 [userscript](https://greasyfork.org/en/scripts/40884-plurk-no-redirector)

## 貢獻
本專案歡迎任何人貢獻，但請注意，提交貢獻前請先[閱讀](https://github.com/FutaGuard/LowTechFilter/wiki/%E5%A6%82%E4%BD%95%E8%B2%A2%E7%8D%BB%E6%88%96%E8%AB%8B%E6%B1%82%E6%96%B0%E5%A2%9E%E5%B0%81%E9%8E%96%E8%A6%8F%E5%89%87%EF%BC%9F)，若有任何疑慮，請先開 issue 討論。

## 贊助

[![cloudflare](https://cf-assets.www.cloudflare.com/slt3lc6tev37/7bIgGp4hk4SFO0o3SBbOKJ/b48185dcf20c579960afad879b25ea11/CF_logo_stacked_blktype.jpg)](https://cloudflare.com)
> 由 CloudFlare 提供免費高速 CDN 服務

[![netlify](https://filter-assets.futa.gg/logo-netlify-small-fullcolor-darkmode.png)](https://netlify.com)
> 由 Netlify 提供每日建構

[![Tuta](https://filter-assets.futa.gg/tuta_logotype_rgb.png)](https://tuta.io)
> 由 Tuta.io 提供安全郵件服務，確保成員之間交換資訊安全

歡迎贊助我們，所有贊助金額將完全用做 FutaGuard DNS 運作以及維護清單費用支出。
<https://core.newebpay.com/EPG/futaguard/FMaZ4E>
