fn main() {
    struct FilterList<'a> {
        abp: Vec<&'a str>,
        hosts: Vec<&'a str>,
    }
    struct HEAD<'a> {
        abp: &'a str,
        hosts: &'a str,
    }

    let filterlist = FilterList {
        abp: vec!["experimental.txt", "filter.txt"],
        hosts: vec!["hosts.txt", "nofarm_hosts.txt"],
    };
    let url: &str = "https://filter.futa.gg/";
    let head = HEAD {
        abp: "[Adblock Plus]\n
             ! Title: LowTechFilter {name}\n
             ! Version: {version}\n
             ! Expires: 1 hour\n
             ! Homepage: https://t.me/AdBlock_TW\n
             ! ----------------------------------------------------------------------\n",
        hosts: "! FutaHosts\n\
               ! LowTechFilter {name}\n\
               ! URL: <https://github.com/FutaGuard/LowTechFilter>\n\
               ! Version: {version}\n\
               ! --------------------------------------------------\n",
    };
    println!("{:?}", head.hosts);
    for val in head {
        println!("{:?}", val)
    }
    // println!("{:?}", filterlist::field_names());
}
