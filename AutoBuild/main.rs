use fancy_regex::{Captures, Regex};
use reqwest;
use std::collections::HashMap;

fn main() {
    let mut filterlist = HashMap::new();
    let mut head = HashMap::new();
    filterlist.insert(String::from("abp"), ["experimental.txt", "filter.txt"]);
    filterlist.insert(String::from("hosts"), ["hosts.txt", "nofarm_hosts.txt"]);

    head.insert(String::from("abp"), "[Adblock Plus]\n
                                     ! Title: LowTechFilter {name}\n
                                     ! Version: {version}\n
                                     ! Expires: 1 hour\n
                                     ! Homepage: https://t.me/AdBlock_TW\n
                                     ! ----------------------------------------------------------------------\n");
    head.insert(
        String::from("hosts"),
        "! FutaHosts\n\
                                       ! LowTechFilter {name}\n\
                                       ! URL: <https://github.com/FutaGuard/LowTechFilter>\n\
                                       ! Version: {version}\n\
                                       ! --------------------------------------------------\n",
    );
    let _url: &str = "https://filter.futa.gg/";

    for category in filterlist {
        for text in category.1 {
            let mut resp = reqwest::blocking::get(_url.to_owned() + text).unwrap();
            if resp.status().is_success() {
            } else {
                panic!("Something else happened. Status: {:?}", resp.status());
            }
            let resp = resp.text().unwrap();

            let re = Regex::new(r"(?<=Version: )(\d+\.\d+\.)(\d+)").unwrap();
            let captures = re.captures(&resp).unwrap();

            let mut version: (&str, &str) = match captures {
                None => ("2017.0929.", "1"),
                _ => (
                    captures.as_ref().unwrap().get(1).unwrap().as_str(),
                    captures.as_ref().unwrap().get(2).unwrap().as_str(),
                ),
            };
            println!("{:?}", version)
        }
    }
}
