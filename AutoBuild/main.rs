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
    head.insert(String::from("hosts"), "! FutaHosts\n\
                                       ! LowTechFilter {name}\n\
                                       ! URL: <https://github.com/FutaGuard/LowTechFilter>\n\
                                       ! Version: {version}\n\
                                       ! --------------------------------------------------\n");
    let _url: &str = "https://filter.futa.gg/";

    for category in filterlist {
        println!("{:?}", category);
    }
    // println!("{:?}", filterlist::field_names());
}
