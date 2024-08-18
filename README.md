# pureyaml-withcomments

Yet Another YAML Parser, in pure python ... extended to include
comments as part of the Abstract Syntax Tree, rather than ignoring
them at the lexical tokenizing stage.  This variant of the parser has
been developed for programmers who want to take account -- for
analysis purposes -- of the comments that are included in a YAML file.

The README file documents how to use the extended feature.  For all
other details, refer to the original [README-orig](README-orig.rst)
file.

As things currently stand, this fork of the code is intended for
developers.  You will need to configure/install it for yourself
using _pip_.  It is suggested you do this in a python3 virtual
environment.  For instanceL

```
python3 -mvenv python3-for-yamlcomments
source ./python3-for-yamlcomments/bin/activate

git clone --recurse-submodules https://github.com/davidbwaikato/pureyaml-withcomments.git 

cd pureyaml-withcomments

pip install -e .

pip install ply

# At the time of testing, version of ply was 3.11.  If looking to match
# to this version, then:
pip install ply==3.11


export PUREYAML_OPTIMIZE=false

```

