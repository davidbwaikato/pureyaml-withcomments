#!/usr/bin/env python3

import os
import sys

from pureyaml.parser import YAMLParser
from pureyaml.nodes import *

#DEBUG=True
DEBUG=False

    
data_test01 = '''---
# Comment 0
'single quote test scalar'
---
"double quote test scalar"
---
# Comment 1 at start of Doc
# Comment 2 at start of Doc
# Comment 3 at start of Doc
text_after_3_comments
---
seqname_example1:
  # comment on new line after hashmap/key
  - 1
  - 2
  - 3
hashname_example1:
  mykey1: myval1
  mykey2: myval2
---
single_word
# Comment at end after single text word
---
# Comment at start of Doc, then named sequence
name:
 - 1
 - 2
another_name: [ 5, 6 ]
---
multline_literal_test: |
  a line that goes 
  on for a long 
  time
multline_literal_test_folded: >
  a line that goes 
  on for a long 
  time
'''

data_test02 = '''
mapkey_seqname_example1:
  # comment on next line after hashmap/key
  - 1
  # comment midway through a sequence
  - 2
  - 3
mapkey_seqname_example2:
  - "abc"
  - "def"
  - "" # comment on empty string val
---
# start of doc comment
seqname_example3:
  - 4
  - 5
  - 6
'''



data_test03 = '''---
# First comment in document
mapkey_seqname_example1:
  - 1   # comment on first line of a sequence
  - 2
  - 3
mapkey_seqname_example2: # comment on line with key
  - abc
  - 'def'
  - "ghi"
---

seqname_example3 # more challenging comment on line with key, before ':'
:
  - 4
  - 5 # comment mid sequence
    # continuing onto another line
  - 6
...
---
# Another doc starting with comment
# over multiple lines
test string
'''    
    


def print_comments(node,indent=0,extra_space='',end=''):
    if node.has_comments():
        comments = node.get_comments()
        if len(comments)>1:
            print(f"{' ' * indent}{extra_space}# {comments}",end=end)
        else:
            print(f"{' ' * indent}{extra_space}# {comments[0]}",end=end)


def print_comments_unfolded(node,indent=0,extra_space=''):
    if node.has_comments():
        comments = node.get_comments()
        num_comments = len(comments)

        for i in range(0,num_comments):
            comment = comments[i]
            if (i == 0):
                if (comment != None):
                    print(f"{extra_space}# {comment}")
                else:
                    print()
            else:
                print(f"{' ' * indent}# {comment}")
        
# Recursive routine that prints out the Abstract Syntax Tree, including comments
def print_ast(node, indent=0):
    
    if isinstance(node, Docs) or isinstance(node, Doc):
        node_class = type(node).__name__
        print(f"{' ' * indent}{node_class}(")
        if (node_class == "Doc"):
            if node.has_comments():
                print(f"{' ' * (indent+2)}",end='')
                print_comments_unfolded(node,indent=indent+2)
        for item in node:
            print_ast(item, indent + 2)
        print(f"{' ' * indent})")

    elif isinstance(node, Map):
        print(f"{' ' * indent}Map(")
        for item_key in node:
            print(f"{' ' * (indent+2)}{item_key.value}:",end='')

            if item_key.has_comments():
                print_comments_unfolded(item_key,indent=indent,extra_space=' ')
            else:
                print()
                
            print_ast(node.get(item_key), indent + 4)
        print(f"{' ' * indent})")

    elif isinstance(node, Sequence):
        node_class = type(node).__name__        
        print(f"{' ' * indent}{node_class}(")
        for item in node:
            print_ast(item, indent + 2)
        print(f"{' ' * indent})")

    elif isinstance(node, Scalar):
        node_class = type(node).__name__
        print(f"{' ' * indent}{node.value} ({node_class})", end='')

        if node.has_comments():
            print_comments_unfolded(node,indent=indent,extra_space=' ')
        else:
            print()        
    else:
        print("**** Warning!")
        print(f"{' ' * indent}UnknownNode(type={type(node)})")
        

        
if __name__ == "__main__":
    pureyaml_optimize = os.environ['PUREYAML_OPTIMIZE']

    print("++++")
    print(f"Parser Mode: PUREYAML_OPTIMIZE={pureyaml_optimize}")
    if (pureyaml_optimize.lower() == "true"):
        print(f"=> Using cached _lextab.py")
    print("++++\n")
    
    # pureyaml debugging on stderr, so flush stdout before running parse
    sys.stdout.flush()

    data_set = [ data_test01, data_test02, data_test03 ]

    for data in data_set:
        
        print("====")
        print("Input YAML file:")
        print("====")
        print(data)
        print("====\n")
        
        if DEBUG:            
            yaml_parser = YAMLParser(debug=True,debuglog=None,errorlog=None,debugfile="debug.out",outputdir=".")
            nodes = yaml_parser.parsedebug(data)
        else:
            yaml_parser = YAMLParser()
            nodes = yaml_parser.parse(data)

        print("====")
        print("Parser return class/data-structure:")
        print("====")
        print(nodes)
        print("====\n")

        print("====")
        print("Prety-print Abstract Syntax Tree:")
        print("====")
        print_ast(nodes)
        print("====\n")
    
        print("/\\" * 40)
        print("\\/" * 40)        
        print()
