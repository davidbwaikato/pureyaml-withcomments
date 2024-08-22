# coding=utf-8
"""Yaml grammar production rules."""
from __future__ import absolute_import

import sys

import re
from textwrap import dedent

from .tokens import YAMLTokens, YAMLCommentedScalarToken
from .utils import strict, fold
from ..nodes import *  # noqa

WITHCOMMENTS_PRODUCTIONS_DEBUG=False
#WITHCOMMENTS_PRODUCTIONS_DEBUG=True

# noinspection PyIncorrectDocstring,PyMethodMayBeStatic
class YAMLProductions(YAMLTokens):
    # PARSER
    # ===================================================================
    @strict(Docs)
    def p_docs__last(self, p):
        """
        docs    : doc
                | doc DOC_END
        """
        p[0] = Docs(p[1])

    @strict(Docs)
    def p_docs__init(self, p):
        """
        docs    : docs doc
        """
        p[0] = p[1] + Docs(p[2])

    @strict(Doc)
    def p_doc__indent(self, p):
        """
        doc : DOC_START doc DOC_END
            | DOC_START doc
            | INDENT doc DEDENT
        """
        p[0] = p[2]

    @strict(Doc)
    def p_doc(self, p):
        """
        doc : collection
            | scalar
        """
        # ****
        doc_node = Doc(p[1])
        if YAMLTokens.StartOfDocComments:
            doc_node.set_comments(YAMLTokens.StartOfDocComments)

        YAMLTokens.StartOfDocComments = None
        YAMLTokens.MostRecentScalarNode = None
        YAMLTokens.MostRecentScalarToken = None
            
        p[0] = doc_node
            

    def p_doc_scalar_collection_ignore(self, p):
        """
        scalar      : ignore_indent_dedent  scalar
        """

        p[0] = p[2]

    @strict(Sequence, Map)
    def p_collection(self, p):
        """
        collection  : sequence
                    | map
                    | flow_collection
        """
        p[0] = p[1]
        
    @strict(Map)
    def p_map__last(self, p):
        """
        map : map_item
        """
        p[0] = Map(p[1])

    @strict(Map)
    def p_map__init(self, p):
        """
        map : map map_item
        """
        p[0] = p[1] + Map(p[2])

    @strict(tuple)
    def p_map_item(self, p):
        """
        map_item    : map_item_key map_item_value
        """
        p[0] = p[1], p[2]
        
    @strict(tuple)
    def p_map_item__compact_scalar(self, p):
        """
        map_item    : B_MAP_COMPACT_KEY scalar B_MAP_VALUE scalar DEDENT
        """
        p[0] = p[2], p[4]

    @strict(Scalar)
    def p_map_item_key__complex_key_scalar(self, p):
        """
        map_item_key    : B_MAP_KEY         scalar
        """
        p[0] = p[2]

    @strict(Scalar)
    def p_map_item_key(self, p):
        """
        map_item_key    : scalar
        """
        p[0] = p[1]

    @strict(Map, Sequence)
    def p_map_item___key_value__collection(self, p):
        """
        map_item_key    :  B_MAP_KEY    INDENT collection DEDENT
        map_item_value  :  B_MAP_VALUE  INDENT collection DEDENT
        """
        p[0] = p[3]

    @strict(Map, Sequence)
    def p_map_item_value__flow_collection(self, p):
        """
        map_item_value  :  B_MAP_VALUE flow_collection
        """
        p[0] = p[2]

    @strict(Scalar)
    def p_map_item_value__scalar(self, p):
        """
        map_item_value  : B_MAP_VALUE scalar
        """
        p[0] = p[2]

    @strict(Scalar)
    def p_map_item_value__scalar_indented(self, p):
        """
        map_item_value  : B_MAP_VALUE INDENT scalar DEDENT
        """
        p[0] = p[3]

    @strict(Sequence)
    def p_map_item_value__sequence_no_indent(self, p):
        """
        map_item_value  : B_MAP_VALUE sequence
        """
        p[0] = p[2]

    # @strict(Null)
    # def p_map_item_value_empty(self, p):
    #     """
    #     map_item_value  : B_MAP_VALUE empty
    #     """
    #     p[0] = Null(None)

    @strict(Sequence)
    def p_sequence__last(self, p):
        """
        sequence    : sequence_item
        """
        p[0] = Sequence(p[1])

    @strict(Sequence)
    def p_sequence__init(self, p):
        """
        sequence    : sequence sequence_item
        """
        p[0] = p[1] + Sequence(p[2])

    @strict(Scalar)
    def p_sequence_item__scalar(self, p):
        """
        sequence_item   : B_SEQUENCE_START scalar
        """
        p[0] = p[2]
        
    # @strict(Null)
    # def p_sequence_item_scalar_empty(self, p):
    #     """
    #     sequence_item   : B_SEQUENCE_START empty
    #     """
    #     p[0] = Null(None)

    @strict(Map, Sequence)
    def p_sequence_item__collection(self, p):
        """
        sequence_item   : B_SEQUENCE_START INDENT collection DEDENT
        """
        p[0] = p[3]

    @strict(Map, Sequence)
    def p_map_item__key__map_item_value__sequence_item__compact_collection(self, p):
        """
        map_item_key    : B_MAP_COMPACT_KEY         collection DEDENT
        map_item_value  : B_MAP_COMPACT_VALUE       collection DEDENT
        sequence_item   : B_SEQUENCE_COMPACT_START  collection DEDENT
        """
        p[0] = p[2]

    @strict(Map, Sequence)
    def p_sequence_item__flow_collection(self, p):
        """
        sequence_item   : B_SEQUENCE_START flow_collection
        """
        p[0] = p[2]

    @strict(Str)
    def p_scalar__doublequote(self, p):
        """
        scalar  : DOUBLEQUOTE_START SCALAR DOUBLEQUOTE_END
        """
        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print(f"**** <p_scalar> (\"double-quote\") {p[2]}",file=sys.stderr)
            
        #scalar = re.sub('\n\s+', ' ', str(p[2]))
        # p[0] = Str(scalar.replace('\\"', '"'))
        # ****
        wrapped_scalar_token2 = p[2]
        scalar2a = wrapped_scalar_token2.get_value()
        scalar2b = re.sub('\n\s+', ' ', scalar2a)
        scalar2c = scalar2b.replace('\\"', '"')
        wrapped_scalar_token2c = YAMLCommentedScalarToken.WrapAsString(scalar2c,wrapped_scalar_token2.lineno)
        p[0] = Str(wrapped_scalar_token2c)

        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print("----",file=sys.stderr)


    @strict(Str)
    def p_scalar__singlequote(self, p):
        """
        scalar  : SINGLEQUOTE_START SCALAR SINGLEQUOTE_END
        """
        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print(f"**** <p_scalar> ('single-quote') {p[2]}",file=sys.stderr)
        # ****
        #p[0] = Str(str(p[2]).replace("''", "'"))
        wrapped_scalar_token2 = p[2]
        scalar2a = wrapped_scalar_token2.get_value()
        scalar2b = scalar2a.replace("''", "'")
        wrapped_scalar_token2b = YAMLCommentedScalarToken.WrapAsString(scalar2b,wrapped_scalar_token2.lineno)
        p[0] = Str(wrapped_scalar_token2b)

        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print("----",file=sys.stderr)

        
    @strict(Str)
    def p_scalar__quote_empty(self, p):
        """
        scalar  : DOUBLEQUOTE_START DOUBLEQUOTE_END
                | SINGLEQUOTE_START SINGLEQUOTE_END
        """
        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print(f"**** <p_scalar> (empty quote string)",file=sys.stderr)
        # ****
        #p[0] = Str('')
        #p[0] = ScalarDispatch('', cast='str')

        wrapped_scalar = YAMLCommentedScalarToken.WrapAsString('',p.lexer.lineno)
        p[0] = Str(wrapped_scalar)

        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print("----",file=sys.stderr)

    @strict(Scalar)
    def p_scalar__explicit_cast(self, p):
        """
        scalar  : CAST_TYPE scalar
        """
        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print(f"**** <p_scalar> (explicit cast p[1]) {p[2]}",file=sys.stderr)

        p[0] = ScalarDispatch(p[2].raw_value, cast=p[1])

        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print("----",file=sys.stderr)

    @strict(Scalar)
    def p_scalar(self, p):
        """
        scalar  : SCALAR
        """
        # ****
        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print(f"**** <p_scalar> (default rule) type = {p[1]}",file=sys.stderr)

        wrapped_scalar_token1 = p[1]
        scalar_node1 = ScalarDispatch(wrapped_scalar_token1)
        YAMLTokens.MostRecentScalarNode = scalar_node1
        YAMLTokens.MostRecentScalarToken = None
        p[0] = scalar_node1

        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print("----",file=sys.stderr)

    @strict(Str)
    def p_scalar__literal(self, p):
        """
        scalar  : B_LITERAL_START scalar_group B_LITERAL_END
        """
        scalar_group = ''.join(p[2])
        p[0] = ScalarDispatch('%s\n' % dedent(scalar_group).replace('\n\n\n', '\n'), cast='str')

    @strict(Str)
    def p_scalar__folded(self, p):
        """
        scalar  : B_FOLD_START scalar_group B_FOLD_END
        """
        scalar_group = ''.join(p[2])
        folded_scalar = fold(dedent(scalar_group)).rstrip()
        p[0] = ScalarDispatch('%s\n' % folded_scalar, cast='str')

    @strict(Str)
    def p_scalar__indented_flow(self, p):
        """
        scalar  : INDENT scalar_group DEDENT
        """
        scalar_group = '\n'.join(p[2])
        folded_scalar = fold(dedent(scalar_group))
        p[0] = ScalarDispatch(folded_scalar, cast='str')

    @strict(Str)
    def p_scalar__string_indented_multi_line(self, p):
        """
        scalar  : scalar INDENT SCALAR DEDENT
        """
        scalar = '\n'.join([p[1].value, p[3]])

        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print(f"**** <p_scalar> (indended multi-line) {fold(scalar)}", file=sys.stderr)

        p[0] = ScalarDispatch(fold(scalar), cast='str')

        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print("----",file=sys.stderr)
        

    @strict(tuple)
    def p_scalar_group(self, p):
        """
        scalar_group    : SCALAR
                        | scalar_group SCALAR
        """
        if len(p) == 2:
            if WITHCOMMENTS_PRODUCTIONS_DEBUG:
                print(f"**** <p_scalar_group> (single entry) {p[1]}",file=sys.stderr)
            #p[0] = (str(p[1]),)
            wrapped_scalar_token1 = p[1]
            scalar_token1 = wrapped_scalar_token1.get_value()
            p[0] = (str(scalar_token1),)

        if len(p) == 3:
            if WITHCOMMENTS_PRODUCTIONS_DEBUG:
                # print(f"**** <p_scalar_group> (double-chain entry) Type: ({type(p[1])},{type(p[2])})",file=sys.stderr)
                print(f"**** <p_scalar_group> (double-chain entry) ({p[1]},{p[2]})",file=sys.stderr)
            #p[0] = p[1] + (str(p[2]),)
            wrapped_scalar_token2 = p[2]
            scalar_token2 = wrapped_scalar_token2.get_value()            
            p[0] = p[1] + (str(scalar_token2),)

        if len(p) == 4:
            if WITHCOMMENTS_PRODUCTIONS_DEBUG:
                print(f"**** <p_scalar_group> (????triple-chain entry) ({p[1]},{p[2]},{p[3]})",file=sys.stderr) 
            #p[0] = p[1] + (str(p[3]),)
            wrapped_scalar_token3 = p[3]
            scalar_token3 = wrapped_scalar_token3.get_value()            
            p[0] = p[1] + (str(scalar_token3),)

        if WITHCOMMENTS_PRODUCTIONS_DEBUG:
            print("----",file=sys.stderr)

    def p_ignore_indent_dedent(self, p):
        """
        ignore_indent_dedent    : INDENT DEDENT
        """

    @strict(Sequence, Map)
    def p_flow_collection(self, p):
        """
        flow_collection : F_SEQUENCE_START flow_sequence F_SEQUENCE_END
                        | F_SEQUENCE_START flow_sequence F_SEP F_SEQUENCE_END
                        | F_MAP_START flow_map F_MAP_END
                        | F_MAP_START flow_map F_SEP F_MAP_END
        """
        p[0] = p[2]

    @strict(Sequence)
    def p_flow_sequence__last(self, p):
        """
        flow_sequence   : flow_sequence_item
        """
        p[0] = Sequence(p[1])

    @strict(Sequence)
    def p_flow_sequence__init(self, p):
        """
        flow_sequence   : flow_sequence F_SEP flow_sequence_item
        """
        p[0] = p[1] + Sequence(p[3])

    @strict(Scalar)
    def p_flow_sequence_item(self, p):
        """
        flow_sequence_item  : scalar
        """
        p[0] = p[1]

    @strict(Map)
    def p_flow_map__last(self, p):
        """
        flow_map   : flow_map_item
        """
        p[0] = Map(p[1])

    @strict(Map)
    def p_flow_map__init(self, p):
        """
        flow_map   : flow_map F_SEP flow_map_item
        """
        p[0] = p[1] + Map(p[3])

    @strict(tuple)
    def p_flow_map_item(self, p):
        """
        flow_map_item  : flow_map_item_key flow_map_item_value
        """
        p[0] = p[1], p[2]

    @strict(Scalar)
    def p_flow_map_item_key(self, p):
        """
        flow_map_item_key   : scalar F_MAP_KEY
        """
        p[0] = p[1]

    @strict(Scalar)
    def p_flow_map_item_value(self, p):
        """
        flow_map_item_value    : scalar
        """
        p[0] = p[1]

    # def p_empty(self, p):
    #     """empty    :"""
    #     pass
