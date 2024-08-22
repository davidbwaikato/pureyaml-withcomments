# coding=utf-8
"""Yaml tokens."""
from __future__ import absolute_import

import sys

from textwrap import dedent

from .utils import find_column, rollback_lexpos
from ..exceptions import YAMLUnknownSyntaxError


from ..nodes import *  # noqa

#WITHCOMMENTS_TOKENS_DEBUG=False
WITHCOMMENTS_TOKENS_DEBUG=True

class TokenList(object):
    tokens = [  # :off
        'DOC_START',
        'DOC_END',
        'B_SEQUENCE_COMPACT_START',
        'B_SEQUENCE_START',
        'B_MAP_COMPACT_KEY',
        'B_MAP_COMPACT_VALUE',
        'B_MAP_KEY',
        'B_MAP_VALUE',
        'B_LITERAL_START',
        'B_LITERAL_END',
        'B_FOLD_START',
        'B_FOLD_END',
        'DOUBLEQUOTE_START',
        'DOUBLEQUOTE_END',
        'SINGLEQUOTE_START',
        'SINGLEQUOTE_END',
        'CAST_TYPE',
        'SCALAR',
        'INDENT',
        'DEDENT',
        'F_SEQUENCE_START',
        'F_SEQUENCE_END',
        'F_MAP_START',
        'F_MAP_END',
        'F_MAP_KEY',
        'F_SEP',

    ]  # :on

#class YAMLCommentedScalarToken(LexToken):
class YAMLCommentedScalarToken():
    def __init__(self,value,lineno):
        ## Ensure deep copying of all attributes from the passed LexToken 't'
        #for attr, value in t.__dict__.items():
        #    setattr(self, attr, copy.deepcopy(value))            
        self.value = value
        self.lineno = lineno

        self.comments = [ ]
        
    def get_value(self):
        return self.value
    
    def has_comments(self):
        return len(self.comments)>0

    def append_comment(self, comment_lineno, comment):
        if (len(self.comments) == 0):
            # special case to handle if first comment
            # => need to check if it is on the same lineno
            #    if not, then add in a blank 'None' comment
            if (comment_lineno != self.lineno):
                print("********* Comment on different line to MRS Token!!!",file=sys.stderr)  
                self.comments.append(None)
                
        self.comments.append(comment)

    def get_comments(self):
        return self.comments

    def __str__(self):
        if self.has_comments():
            return f"YAMLCommentedScalarToken(value={self.value.strip()} ,comments={self.comments})"
        else:
            return f"YAMLCommentedScalarToken(value={self.value})"

    @staticmethod
    def WrapAsString(str,lineno):

        if WITHCOMMENTS_TOKENS_DEBUG:
            print(f"**** WrapAsString, str={str}, lineno={lineno}",file=sys.stderr)
            
        return YAMLCommentedScalarToken(str,lineno)
        
    
# noinspection PyMethodMayBeStatic,PyIncorrectDocstring,PySingleQuotedDocstring,PyPep8Naming
class YAMLTokens(TokenList):
    def __init__(self):
        self.indent_stack = [1]
        YAMLTokens.StartOfDocComments = None
        YAMLTokens.MostRecentScalarNode = None        
        YAMLTokens.MostRecentScalarToken = None
        
    def get_indent_status(self, t):        
        column = find_column(t)
        curr_depth, next_depth = self.indent_stack[-1], column

        # If a comment is next, then we are in a NODENT situation
        next_pos = t.lexer.lexpos
        if next_pos < len(t.lexer.lexdata) and t.lexer.lexdata[next_pos] == '#':
            status = 'NODENT'
        else:
            if next_depth > curr_depth:
                status = 'INDENT'
            elif next_depth < curr_depth:
                status = 'DEDENT'
            else:
                status = 'NODENT'

        return status, curr_depth, next_depth
    
    # LEXER
    # ===================================================================
    states = (  # :off
        ('tag', 'inclusive'),
        ('doublequote', 'exclusive'),
        ('comment', 'exclusive'),
        ('singlequote', 'exclusive'),
        ('literal', 'exclusive'),
        ('fold', 'exclusive'),
        ('flowsequence', 'exclusive'),
        ('flowmap', 'exclusive'),
    )  # :on

    literals = '"'
    
    # state: multiple
    # -------------------------------------------------------------------

    def t_ignore_INDENT(self, t):
        r'\n\s*'
        t.lexer.lineno += 1
        
        indent_status, curr_depth, next_depth = self.get_indent_status(t)

        if indent_status == 'NODENT':
            return

        if indent_status == 'INDENT':
            # note: also set by
            #   * t_B_SEQUENCE_COMPACT_START
            #   * t_B_MAP_COMPACT_KEY
            #   * t_B_MAP_COMPACT_VALUE
            self.indent_stack.append(next_depth)

        if indent_status == 'DEDENT':
            indent_delta = curr_depth - next_depth
            step = self.indent_stack.pop() - self.indent_stack[-1]

            # If dedent is larger then last indent
            if indent_delta > step:
                # Go back and reevaluate this token.
                rollback_lexpos(t)
                t.lexer.lineno -= 1
                
        t.type = indent_status
        return t

    # state: tag
    # -------------------------------------------------------------------
    def t_begin_tag(self, t):
        r'(?<!\\)!'
        t.lexer.push_state('tag')

    def t_tag_end(self, t):
        r'\ '
        t.lexer.pop_state()

    def t_tag_CAST_TYPE(self, t):
        r'(?<=\!)[a-z]+'
        return t

    # state: doublequote
    # -------------------------------------------------------------------
    def t_doublequote_SCALAR(self, t):
        r'(?:\\"|[^"])+'
        if WITHCOMMENTS_TOKENS_DEBUG:
            print(f"**** <t_doublequote_SCALAR>: {t}", file=sys.stderr)
        t.value = YAMLCommentedScalarToken(t.value,t.lineno)
        YAMLTokens.MostRecentScalarNode = None
        YAMLTokens.MostRecentScalarToken = t
        return t

    def t_begin_doublequote(self, t):
        r'(?<!\\)"'

        t.lexer.push_state('doublequote')
        t.type = 'DOUBLEQUOTE_START'
        return t

    def t_doublequote_end(self, t):
        r'(?<!\\)"'
        t.lexer.pop_state()
        t.type = 'DOUBLEQUOTE_END'
        return t
    
    # state: comment
    # -------------------------------------------------------------------
    # ****
    def t_comment_ignore_COMMENT(self, t):
        r'[^\n]+'
        if WITHCOMMENTS_TOKENS_DEBUG:
            print(f"**** comment = {t.value}", file=sys.stderr)
        if YAMLTokens.MostRecentScalarNode:
            if WITHCOMMENTS_TOKENS_DEBUG:
                print(f"**** <t_comment_ignore_COMMENT> MRS.node = {YAMLTokens.MostRecentScalarNode}", file=sys.stderr)
            YAMLTokens.MostRecentScalarNode.append_comment(t.value)
        else:
            if YAMLTokens.MostRecentScalarToken:
                if WITHCOMMENTS_TOKENS_DEBUG:
                    print(f"**** <t_comment_ignore_COMMENT> MRS.token_value = {YAMLTokens.MostRecentScalarToken.value.get_value()}", file=sys.stderr)                    
                YAMLTokens.MostRecentScalarToken.value.append_comment(t.lexer.lineno,t.value)
            else:
                # Start of Doc comment
                if YAMLTokens.StartOfDocComments:
                    if WITHCOMMENTS_TOKENS_DEBUG:
                        print(f"**** DocStart appending comment",file=sys.stderr)
                    YAMLTokens.StartOfDocComments.append(t.value)
                else:
                    if WITHCOMMENTS_TOKENS_DEBUG:
                        print(f"**** DocStart adding comment",file=sys.stderr)
                    YAMLTokens.StartOfDocComments = [ t.value ]

    
    def t_INITIAL_flowsequence_flowmap_begin_comment(self, t):
        r'\s*[\#\%]\ ?'
        t.lexer.push_state('comment')

    def t_comment_end(self, t):
        r'(?=\n)'
        t.lexer.pop_state()
        
        
    # state: singlequote
    # -------------------------------------------------------------------
    # ****
    def t_singlequote_SCALAR(self, t):
        r"(?:\\'|[^']|'')+"
        if WITHCOMMENTS_TOKENS_DEBUG:
            print(f"**** <t_singlequote_SCALAR>: {t}", file=sys.stderr)
        t.value = YAMLCommentedScalarToken(t.value,t.lineno)
        YAMLTokens.MostRecentScalarNode = None        
        YAMLTokens.MostRecentScalarToken = t        
        return t

    def t_begin_singlequote(self, t):
        r"(?<!\\)'"
        t.lexer.push_state('singlequote')
        t.type = 'CAST_TYPE'
        t.type = 'SINGLEQUOTE_START'
        return t

    def t_singlequote_end(self, t):
        r"(?<!\\)'"
        t.lexer.pop_state()
        t.type = 'SINGLEQUOTE_END'
        return t

    # state: literal
    # -------------------------------------------------------------------
    # ****
    def t_literal_SCALAR(self, t):
        r'.+'
        if WITHCOMMENTS_TOKENS_DEBUG:
            print(f"**** <t_literal_SCALAR>: {t}", file=sys.stderr)
        t.value = YAMLCommentedScalarToken(t.value,t.lineno)
        YAMLTokens.MostRecentScalarNode = None        
        YAMLTokens.MostRecentScalarToken = t        
        return t

    def t_begin_literal(self, t):
        r'\ *(?<!\\)\|\ ?\n'
        t.lexer.lineno += 1
        
        t.lexer.push_state('literal')
        t.type = 'B_LITERAL_START'
        return t

    def t_literal_end(self, t):
        r'\n+\ *'
        t.lexer.lineno += t.value.count('\n')
        
        column = find_column(t)
        indent = self.indent_stack[-1]
        if column < indent:
            rollback_lexpos(t)
            t.lexer.lineno -= t.value.count('\n')
        if column <= indent:
            t.lexer.pop_state()
            t.type = 'B_LITERAL_END'
        if column > indent:            
            t.type = 'SCALAR'
            # print("**** !!!!! LITERAL END",file=sys.stderr)
            t.value = YAMLCommentedScalarToken(t.value,t.lineno)
            YAMLTokens.MostRecentScalarNode = None        
            YAMLTokens.MostRecentScalarToken = t        
            
        return t

    # state: fold
    # -------------------------------------------------------------------
    # ****
    def t_fold_SCALAR(self, t):
        r'.+'
        if WITHCOMMENTS_TOKENS_DEBUG:
            print(f"**** <t_fold_SCALAR>: {t}", file=sys.stderr)
        t.value = YAMLCommentedScalarToken(t.value,t.lineno)
        YAMLTokens.MostRecentScalarNode = None
        YAMLTokens.MostRecentScalarToken = t        
        return t

    def t_begin_fold(self, t):
        r'\ *(?<!\\)\>\ ?\n'
        t.lexer.lineno += 1
        
        t.lexer.push_state('fold')
        t.type = 'B_FOLD_START'
        return t

    def t_fold_end(self, t):
        r'\n+\ *'
        t.lexer.lineno += t.value.count('\n')
        
        column = find_column(t)
        indent = self.indent_stack[-1]
        if column < indent:
            rollback_lexpos(t)
            t.lexer.lineno += t.value.count('\n')            
        if column <= indent:
            t.lexer.pop_state()
            t.type = 'B_FOLD_END'
        if column > indent:
            t.type = 'SCALAR'
            # print("**** !!!!! FOLD END",file=sys.stderr)
            t.value = YAMLCommentedScalarToken(t.value,t.lineno)
            YAMLTokens.MostRecentScalarNode = None        
            YAMLTokens.MostRecentScalarToken = t        
            
        return t

    # state: flowsequence and flowmap
    # -------------------------------------------------------------------
    def t_flowsequence_flowmap_F_SEP(self, t):
        r','
        return t

    def t_flowsequence_flowmap_ignore_space(self, t):
        r'\s+'

    # state: flowsequence
    # -------------------------------------------------------------------
    # ****
    def t_flowsequence_SCALAR(self, t):
        r'[^\[\],\#]+'
        if WITHCOMMENTS_TOKENS_DEBUG:
            print(f"**** <t_flowsequence_SCALAR>: {t}", file=sys.stderr)
        t.value = YAMLCommentedScalarToken(t.value,t.lineno)
        YAMLTokens.MostRecentScalarNode = None        
        YAMLTokens.MostRecentScalarToken = t        
        return t
    
    def t_begin_flowsequence(self, t):
        r'\['
        t.lexer.push_state('flowsequence')
        t.type = 'F_SEQUENCE_START'
        return t

    def t_flowsequence_end(self, t):
        r'\]'
        t.lexer.pop_state()
        t.type = 'F_SEQUENCE_END'
        return t

    # state: flowmap
    # -------------------------------------------------------------------
    # ****
    def t_flowmap_SCALAR(self, t):
        r'[^\{\}\:,\#]+'
        if WITHCOMMENTS_TOKENS_DEBUG:
            print(f"**** <t_flowmap_SCALAR>: {t}", file=sys.stderr)
        t.value = YAMLCommentedScalarToken(t.value,t.lineno)
        YAMLTokens.MostRecentScalarNode = None        
        YAMLTokens.MostRecentScalarToken = t        
        return t
    
    def t_flowmap_F_MAP_KEY(self, t):
        r'\:\ ?'
        return t

    def t_begin_flowmap(self, t):
        r'\{'
        t.lexer.push_state('flowmap')
        t.type = 'F_MAP_START'
        return t

    def t_flowmap_end(self, t):
        r'\}'
        t.lexer.pop_state()
        t.type = 'F_MAP_END'

        return t

    # state: INITIAL
    # -------------------------------------------------------------------
    # t_ignore_EOL = r'\s*\n'
    # ****
    def t_ignore_EOL(self, t):
        r'\s*\n'
        t.lexer.lineno += 1
        return t

    def t_DOC_START(self, t):
        r'\-\-\-'
        return t

    def t_DOC_END(self, t):
        r'\.\.\.'
        return t

    def t_B_SEQUENCE_COMPACT_START(self, t):
        r"""
          \-\ + (?=  -\   )
          #          ^ ^ sequence indicator
        | \-\ + (?=  [\{\[]\   |  [^:\n]*:\s   )
          #            ^ ^          ^^^ map indicator
          #            ^ ^ flow indicator
        """

        indent_status, curr_depth, next_depth = self.get_indent_status(t)

        if indent_status == 'INDENT':
            self.indent_stack.append(next_depth)
            return t

        msg = dedent("""
            expected 'INDENT', got  {indent_status!r}
            current_depth:          {curr_depth}
            next_depth:             {next_depth}
            token:                  {t}
        """).format(**vars())

        raise YAMLUnknownSyntaxError(msg)

    def t_B_SEQUENCE_START(self, t):
        r'-\ +|-(?=\n)'
        return t

    def t_B_MAP_COMPACT_KEY(self, t):
        r"""
          \?\ + (?=  -\   )
          #          ^ ^ sequence indicator
        | \?\ + (?=  [\{\[]\   |  [^:\n]*:\s   )
          #            ^ ^          ^^^ map indicator
          #            ^ ^ flow indicator
        """

        indent_status, curr_depth, next_depth = self.get_indent_status(t)

        if indent_status == 'INDENT':
            self.indent_stack.append(next_depth)
            return t

        msg = dedent("""
            expected 'INDENT', got  {indent_status!r}
            current_depth:          {curr_depth}
            next_depth:             {next_depth}
            token:                  {t}
        """).format(**vars())

        raise YAMLUnknownSyntaxError(msg)

    def t_B_MAP_COMPACT_VALUE(self, t):
        r"""
          \:\ + (?=  -\   )
          #          ^ ^ sequence indicator
        | \:\ + (?=  [\{\[]\   |  [^:\n]*:\s   )
          #            ^ ^          ^^^ map indicator
          #            ^ ^ flow indicator
        """

        indent_status, curr_depth, next_depth = self.get_indent_status(t)

        if indent_status == 'INDENT':
            self.indent_stack.append(next_depth)
            return t

        msg = dedent("""
            expected 'INDENT', got  {indent_status!r}
            current_depth:          {curr_depth}
            next_depth:             {next_depth}
            token:                  {t}
        """).format(**vars())

        raise YAMLUnknownSyntaxError(msg)

    def t_B_MAP_KEY(self, t):
        r'\?\ +|\?(?=\n)'
        return t

    def t_B_MAP_VALUE(self, t):
        r':\ +|:(?=\n)'
        return t

    def t_ignore_unused_indicators(self, t):
        r'\ *[\@\`].*(?=\n)'

    def t_SCALAR(self, t):
        r'(?:\\.|[^\n\#\:\-\|\>]|[\:\-\|\>]\S)+'
        if WITHCOMMENTS_TOKENS_DEBUG:
            print(f"**** <t_SCALAR>: {t}", file=sys.stderr)
        t.value = YAMLCommentedScalarToken(t.value,t.lineno)
        YAMLTokens.MostRecentScalarNode = None        
        YAMLTokens.MostRecentScalarToken = t        
        return t


    # ****
    def t_comment_error(self, t):
        print(f"<comment> Illegal character '{t.value[0]}'",file=sys.stderr)
        t.lexer.skip(1)
    def t_doublequote_error(self, t):
        print(f"<doublequote> Illegal character '{t.value[0]}'",file=sys.stderr)
        t.lexer.skip(1)
    def t_literal_error(self, t):
        print(f"<literal> Illegal character '{t.value[0]}'",file=sys.stderr)
        t.lexer.skip(1)
    def t_fold_error(self, t):
        print(f"<fold> Illegal character '{t.value[0]}'",file=sys.stderr)
        t.lexer.skip(1)
    def t_flowsequence_error(self, t):
        print(f"<flowsequence> Illegal character '{t.value[0]}'",file=sys.stderr)
        t.lexer.skip(1)
    def t_flowmap_error(self, t):
        print(f"<flowmap> Illegal character '{t.value[0]}'",file=sys.stderr)
        t.lexer.skip(1)
    def t_singlequote_error(self, t):
        print(f"<singlequote> Illegal character '{t.value[0]}'",file=sys.stderr)
        t.lexer.skip(1)

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}'",file=sys.stderr)
        t.lexer.skip(1)
    
