domain_list = ''
with open('../nofarm_hosts.txt', 'r') as files:
    for domains in files.read().split('\n'):
        if domains:
            domain = domains[2:-1]
            domain_list += 'google.*##div.g:has(a[href*="{domain}"])\n'.format(
                domain=domain
            )

with open('../hide_farm_from_search.txt', 'w') as files:
    files.write(domain_list)
