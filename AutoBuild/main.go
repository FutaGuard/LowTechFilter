package main

import (
	"log"
	"reflect"
	"time"
)

type FilterList struct {
	abp   []string
	hosts []string
}

type HEAD struct {
	abp   string
	hosts string
}

func main() {

	filterlist := &FilterList{
		[]string{"experimental.txt", "filter.txt"},
		[]string{"hosts.txt", "nofarm_hosts.txt"}}

	heads := HEAD{
		abp: "[Adblock Plus]\n" +
			"! Title: LowTechFilter {name}\n" +
			"! Version: {version}\n" +
			"! Expires: 1 hour\n" +
			"! Homepage: https://t.me/AdBlock_TW\n" +
			"! ----------------------------------------------------------------------\n",
		hosts: "! FutaHosts\n" +
			"! LowTechFilter {name}\n" +
			"! URL: <https://github.com/FutaGuard/LowTechFilter>\n" +
			"! Version: {version}\n" +
			"! --------------------------------------------------\n",
	}
	url := "https://filter.futa.gg/"
	log.Println(url)
	log.Println(heads)

	location, _ := time.LoadLocation("Asia/Taipei")
	now := time.Now().In(location)
	log.Println(now)

	//fields := reflect.VisibleFields(reflect.TypeOf(filterlist))
	v := reflect.ValueOf(filterlist).Elem()
	log.Println(v.FieldByName("abp").s)
	//for _, field := range fields {
	//	data := reflect.Indirect(v).FieldByName(field.Name)
	//	log.Println(data)
	//}
	log.Println(v)
	menu := map[string][]string{
		"abp":   {"experimental.txt", "filter.txt"},
		"hosts": {"hosts.txt", "nofarm_hosts.txt"},
	}
	for category, data := range menu {
		log.Println(category, data)
	}
	//log.Println(menu)
}
