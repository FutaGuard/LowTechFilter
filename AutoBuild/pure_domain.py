with open('../hosts.txt', 'r') as files:
    data = files.read().splitlines()
    output = '\n'.join(e for e in list(filter(lambda x: not x.startswith('/') and not x.startswith('! regex'), data)))
    with open('../domains.txt', 'w') as newoutput:
        newoutput.write(output)
