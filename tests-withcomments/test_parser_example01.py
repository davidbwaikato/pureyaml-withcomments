
import ply.lex as lex
import ply.yacc as yacc

#from pureyaml.grammar.tokens import YAMLTokens
from pureyaml.grammar.productions import YAMLProductions

from pureyaml.parser import YAMLParser


# Test the ConfigLexer class
if __name__ == "__main__":
    data = '''---
# Comment 0
'single quote test scalar'
---
"double quote test scalar"
---
# Comment at start, on own
---
# Comment at start of Doc, then named sequence
name:
 - 1
 - 2
---
literal
'''


#parser = YAMLParser(debug=False)
#parser = YAMLParser(debug=True)
yaml_parser = YAMLParser(debug=True,debuglog=None,errorlog=None,debugfile="debug.out",outputdir=".")

#yaml_productions = YAMLProductions()
###yaml_parser = YAMLProductions(debug=True,debuglog=None,errorlog=None,debugfile="debug.out",outputdir=".")

#yaml_parser = yacc(tabmodule='pureyaml.grammar._parsetab')


#print(yaml_parser.tokenize(data))

#nodes = yaml_parser.parsedebug(data)
nodes = yaml_parser.parse(data)

print(type(nodes))
print(nodes)

