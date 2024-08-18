#!/usr/bin/env python3

from pureyaml.parser import YAMLParser

DEBUG=True

# Test the ConfigLexer class
if __name__ == "__main__":
    data = '''---
# Comment 0
'single quote test scalar' # comment at end of line
---
"double quote test scalar"
---
# Comment at start, on own 1
# Comment at start, on own 2
# Comment at start, on own 3
---
# Comment at start of Doc, then named sequence
name:
 - 1
 - 2
---
literal
'''

if DEBUG:    
    yaml_parser = YAMLParser(debug=True,debuglog=None,errorlog=None,debugfile="debug.out",outputdir=".")
    nodes = yaml_parser.parsedebug(data)
else:
    yaml_parser = YAMLParser()
    nodes = yaml_parser.parse(data)

print(nodes)

if DEBUG:
    print("----")
    print("YAMLParser() constructor debug info in:")
    print("  ./debug.out")
    print("----")
    
