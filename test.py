import json

set = ''
with open('settings.txt','r') as f:
    lines = f.readlines()
    temp = ""
    for line in lines:
        temp += line
    set = json.loads(temp)
    print(lines)
    print(set)
    print(json.dumps(set, sort_keys=True,indent=2, separators=(',', ': ')) )
    
with open('settings.txt','w') as f:
    f.write(json.dumps(set, sort_keys=True,indent=2, separators=(',', ': ')))