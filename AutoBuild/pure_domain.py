import re

with open('../hosts.txt', 'r') as files:
    data = files.read().splitlines()
    newdata = '\n'.join(data[5:])
    desc = '\n'.join(x.replace('!', '#') for x in data[:5]) + '\n'
    
    with open('../domains.txt', 'w') as output:
        pattern = r'(?<=^\|\|)\S+\.\S{2,}(?=\^)'
        desc += '\n'.join(re.findall(pattern, newdata, re.MULTILINE))
        output.write(desc)
