package main

func main() {

	type FilterList struct {
		abp   []string
		hosts []string
	}
	filterlist := FilterList{
		[]string{"experimental.txt", "filter.txt"},
		[]string{"hosts.txt", "nofarm_hosts.txt"}}

	//fmt.Println(filterlist)
}
