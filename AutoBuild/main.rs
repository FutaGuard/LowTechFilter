extern crate chrono;
extern crate fancy_regex;
extern crate reqwest;
use chrono::{NaiveDate, Utc};
use fancy_regex::{Captures, Regex};
use std::collections::HashMap;
// use std::fmt::{Debug, Write};
use std::any::type_name;
use std::fs::File;
use std::io::prelude::*;
use std::io::Write;
use std::path::Path;
// use std::fmt::format;

fn type_of<T>(_: T) -> &'static str {
    type_name::<T>()
}

fn main() {
    let mut filterlist = HashMap::new();
    // let mut head = HashMap::new();
    filterlist.insert(String::from("abp"), ["experimental.txt", "filter.txt"]);
    filterlist.insert(String::from("hosts"), ["hosts.txt", "nofarm_hosts.txt"]);

    let _url: &str = "https://filter.futa.gg/";
    let now: chrono::DateTime<Utc> = Utc::now();

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

            // "1983 Apr 13 12:09:14.274 +0000", "%Y %b %d %H:%M:%S%.3f %z"
            let dt = NaiveDate::parse_from_str(version.0, "%Y.%m%d.").unwrap();
            let today = now.date_naive();
            let mut newversion = now.format("%Y.%m%d.").to_string().to_owned();
            if dt != today {
                newversion.push_str("1");
                // println!("not today {:?}", newversion);
            } else {
                let index = version.1.to_string().parse::<i32>().unwrap() + 1;
                newversion.push_str(&index.to_string());
            }

            let mut name: Vec<&str> = text.split(".").collect();
            let name = name[0];
            let mut output = match category.0.as_str() {
                "hosts" => {
                    format!(
                        "! FutaHosts\n\
                    ! LowTechFilter {name}\n\
                    ! URL: <https://github.com/FutaGuard/LowTechFilter>\n\
                    ! Version: {version}\n\
                    ! --------------------------------------------------\n",
                        name = name,
                        version = newversion
                    )
                }
                "abp" => {
                    format!(
                        "[Adblock Plus]\n\
                    ! Title: LowTechFilter {name}\n\
                    ! Version: {version}\n\
                    ! Expires: 1 hour\n\
                    ! Homepage: https://t.me/AdBlock_TW\n\
                    ! ----------------------------------------------------------------------\n",
                        name = name,
                        version = newversion
                    )
                }
                _ => {
                    continue;
                }
            };
            // open and ready to write
            let path = Path::new(text);
            let display = path.display(); // Option 用
            let mut file = match File::open(&path) {
                Err(why) => panic!("couldn't open {}: {:?}", display, why),
                Ok(file) => file,
            };

            let mut reader = String::new();
            match file.read_to_string(&mut reader) {
                Err(why) => panic!("couldn't read {}: {:?}", display, why),
                Ok(..) => println!("{:?}", reader),
            };

            output.push_str(&reader);
            let mut file = match File::create(&path) {
                Err(why) => panic!("couldn't create {}: {:?}", display, why),
                Ok(file) => file,
            };
            match file.write_all(output.as_bytes()) {
                Err(why) => {
                    panic!("couldn't write to {}: {:?}", display, why)
                },
                _ => {},
            }
        }
    }
}
