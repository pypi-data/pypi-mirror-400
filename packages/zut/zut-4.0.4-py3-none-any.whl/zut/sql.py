"""
Formatting and parsing for SQL queries.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, Iterable

from zut.tables import Column

if TYPE_CHECKING:
    from typing import Literal

#region Escape

def parse_identifier(value: str|tuple|type|Column, *, quotechar = '"') -> tuple[str|None,str]:
    schema: str|None
    name: str
    if isinstance(value, tuple):
        schema, name = value
    elif isinstance(value, Column):
        schema = None
        name = value.name
    elif isinstance(value, type):
        meta = getattr(value, '_meta', None) # Django model
        if not meta:
            raise TypeError(f'value: {type(value).__name__}')
        if not isinstance(meta.db_table, str):
            raise TypeError(f'value._meta.db_table: {type(meta.db_table).__name__}')
        schema = None
        name = meta.db_table

    elif isinstance(value, str):
        def unescape(value: str) -> str:
            if value.startswith(quotechar) and value.endswith(quotechar):
                if not quotechar in value[1:-1].replace(f'{quotechar}{quotechar}', ''):
                    return value[1:-1].replace(f'{quotechar}{quotechar}', quotechar) # Escaped identifier
                else:
                    raise ValueError("Cannot unescape identifier: %s" % value)
            elif quotechar in value:
                raise ValueError("Cannot unescape identifier: %s" % value)
            else:
                return value

        unsupported = re.escape(f'{quotechar}."`[]')
        m = re.match(f'^(?:({re.escape(quotechar)}?[^{unsupported}]+{re.escape(quotechar)}?)\\.)?({re.escape(quotechar)}?[^{unsupported}]+{re.escape(quotechar)}?)$', value)
        if m:
            schema = unescape(m[1]) if m[1] else None
            name = unescape(m[2])
        else:
            raise ValueError("Cannot parse identifier: %s" % value)
        
    else:
        raise TypeError(f'value: {type(value).__name__}')
    
    return schema, name


def escape_identifier(value: str|tuple|type|Column, *, quotechar = '"') -> str:
    schema, name = parse_identifier(value, quotechar=quotechar)

    def escape(value: str):
        if value.startswith(quotechar) and value.endswith(quotechar) and not quotechar in value[1:-1].replace(f'{quotechar}{quotechar}', ''):
            return value # Already escaped
        else:
            return quotechar + value.replace(quotechar, f'{quotechar}{quotechar}') + quotechar
    
    if schema:
        return escape(schema) + '.' + escape(name)
    else:
        return escape(name)


def escape_literal(value) -> str:
    if value is None:
        return "null"
    elif isinstance(value, datetime):
        raise ValueError("Cannot use datetimes directly with `escape_literal`. Use `get_sql_value` first to remove timezone ambiguity.")
    else:
        return f"'" + str(value).replace("'", "''") + "'"
    #ROADMAP: Should we review conversions?:
    #- Remove restriction on datetimes
    #- if isinstance(value, int): return str(value)
    #- if isinstance(value, bool): return 'true' if value else 'false'

#endregion


#region Columns and tags

def parse_sql_select_column_comments(sql: str) -> dict[str, str]:
    from sqlparse import parse as parse_sql
    from sqlparse import tokens as T
    from sqlparse.sql import Comment, Identifier, IdentifierList, Token

    token: Token

    # Determine last statement
    statement = parse_sql(sql)[-1]
    statement_type = statement.get_type()
    if statement_type != 'SELECT':
        raise ValueError(f"Invalid statement type '{statement_type}': expected 'SELECT'")
        
    # Determine identifiers and associated comments (on the same line)
    idorlists: list[IdentifierList|Identifier] = []
    idorlist_comments: dict[int,Comment] = {}
    last_idorlist_index_for_comment: int|None = None
    dml_found = False
    for token in statement.tokens:
        if not dml_found:
            if token.ttype == T.Keyword.DML:
                dml_found = True
        else: # dml_found
            if token.is_keyword:
                break # Example: SELECT after an UNION            
            elif isinstance(token, (IdentifierList,Identifier)):
                last_idorlist_index_for_comment = len(idorlists)
                idorlists.append(token)
            elif isinstance(token, Comment):
                if last_idorlist_index_for_comment is not None:
                    idorlist_comments[last_idorlist_index_for_comment] = token

    if not idorlists:
        raise ValueError(f"Column identifier tokens not found in SELECT query")
    
    def normalize_comment(token: Comment) -> str:
        m = re.match(r'^/\*(.+)\*/$', token.value)
        if m:
            return m[1].strip()
        
        m = re.match(r'^--(.+)$', token.value)
        if m:
            return m[1].strip()
        
        return token.value.strip()
    
    def get_identifier_comment(identifier: Identifier, outer_comment: Comment|None) -> str:
        comments: list[Comment] = []

        for token in identifier:
            if isinstance(token, Comment):
                comments.append(token)
        
        if outer_comment is not None:
            comments.append(outer_comment)

        result: str|None = None

        for comment in comments:
            text = normalize_comment(comment)
            if text:
                result = (result + '\n' if result else '') + text

        return result or ''

    result = {}

    for idorlist_index, idorlist in enumerate(idorlists):
        idorlist_comment = idorlist_comments.get(idorlist_index)

        identifiers: list[Identifier] = []
        if isinstance(idorlist, IdentifierList):
            for token in idorlist.get_identifiers():
                if not isinstance(token, Identifier):
                    continue # Ignore. Example: a number without a column name
                identifiers.append(token)
        else:
            identifiers.append(idorlist)
        
        for i, identifier in enumerate(identifiers):
            name = identifier.get_name()
            comment = get_identifier_comment(identifier, outer_comment=idorlist_comment if idorlist_comment is not None and i == len(identifiers) - 1 else None)
            result[name] = comment

    return result


def exclude_sql_select_columns(sql: str, excluded_columns: Iterable[Column|str]) -> str:
    """
    Rewrite a SQL SELECT query by excluding some column expressions.

    NOTE: This does not work for UNION SELECTs.
    """
    from sqlparse import parse as parse_sql
    from sqlparse import tokens as T
    from sqlparse.sql import Comment, Identifier, IdentifierList, Token
    
    excluded_column_names: set[str] = {str(column) if not isinstance(column, str) else column for column in excluded_columns}

    token: Token

    # Export non-last statement and keep last
    result_sql = ''
    statements = parse_sql(sql)
    for statement in statements[:-1]:
        result_sql += statement.value

    statement = parse_sql(sql)[-1]
    statement_type = statement.get_type()
    if statement_type != 'SELECT':
        raise ValueError(f"Invalid statement type '{statement_type}': expected 'SELECT'")
            
    # Determine column tokens
    column_tokens: list[Token] = []
    remaining_sql: str|None = None
    dml_found = False
    for token in statement.tokens:
        if not dml_found:
            if token.ttype == T.Keyword.DML:
                dml_found = True
            result_sql += token.value
        elif remaining_sql is None: # dml_found
            if token.is_keyword:
                remaining_sql = token.value # Examples: FROM
            elif isinstance(token, IdentifierList):
                for sub in token.tokens:
                    column_tokens.append(sub)
            else:
                column_tokens.append(token)
        else:
            remaining_sql += token.value

    if not column_tokens:
        raise ValueError(f"Column tokens not found in SELECT query")
    
    # Filter column tokens
    filtered_column_tokens: list[Token] = []
    actually_excluded_column_names: list[str] = []
    actually_included_column_names: list[str] = []

    def remove_from_last_punctuation():
        nonlocal filtered_column_tokens

        last_punctuation_index: int|None = None
        for index, token in enumerate(filtered_column_tokens):
            if token.ttype == T.Punctuation:
                last_punctuation_index = index

        if last_punctuation_index is not None:
            filtered_column_tokens = filtered_column_tokens[:last_punctuation_index]

    for token in column_tokens:
        #print("-", type(token), token.ttype, f">{token.value}<")
        if isinstance(token, Identifier):
            column_name: str = token.get_name() # pyright: ignore[reportAssignmentType]
            if column_name in excluded_column_names:
                remove_from_last_punctuation()
                actually_excluded_column_names.append(column_name)
            else:
                if not actually_included_column_names and actually_excluded_column_names:
                    remove_from_last_punctuation() # Remove previous punctuation: the first column was excluded
                filtered_column_tokens.append(token)
                actually_included_column_names.append(column_name)
        else:         
            filtered_column_tokens.append(token)

    # Finalize result_sql
    for token in filtered_column_tokens:
        result_sql += token.value
    
    if remaining_sql is not None:
        result_sql += remaining_sql
    
    return result_sql
    
    def normalize_comment(token: Comment) -> str:
        m = re.match(r'^/\*(.+)\*/$', token.value)
        if m:
            return m[1].strip()
        
        m = re.match(r'^--(.+)$', token.value)
        if m:
            return m[1].strip()
        
        return token.value.strip()
    
    def get_identifier_comment(identifier: Identifier, outer_comment: Comment|None) -> str:
        comments: list[Comment] = []

        for token in identifier:
            if isinstance(token, Comment):
                comments.append(token)
        
        if outer_comment is not None:
            comments.append(outer_comment)

        result: str|None = None

        for comment in comments:
            text = normalize_comment(comment)
            if text:
                result = (result + '\n' if result else '') + text

        return result or ''

    result = {}

    for idorlist_index, idorlist in enumerate(idorlists):
        idorlist_comment = idorlist_comments.get(idorlist_index)

        identifiers: list[Identifier] = []
        if isinstance(idorlist, IdentifierList):
            for token in idorlist.get_identifiers():
                if not isinstance(token, Identifier):
                    continue # Ignore. Example: a number without a column name
                identifiers.append(token)
        else:
            identifiers.append(idorlist)
        
        for i, identifier in enumerate(identifiers):
            name = identifier.get_name()
            comment = get_identifier_comment(identifier, outer_comment=idorlist_comment if idorlist_comment is not None and i == len(identifiers) - 1 else None)
            result[name] = comment

    return result_sql


def parse_sql_select_column_tags(sql: str) -> dict[str, dict[str,str|Literal[True]]]:
    """
    Does not require module `sqlparse`.
    """
    results: dict[str, dict[str,str|Literal[True]]] = {}

    for name, comments in parse_sql_select_column_comments(sql).items():
        tags = {}

        for comment_line in comments.splitlines(keepends=False):
            comment_line = comment_line.strip()
            for mt in re.finditer(r'#(?P<key>[a-z0-9_]+)(?::(?P<value>[^\s*]+))?', comment_line, re.IGNORECASE):
                tags[mt['key']] = mt['value'] or True

        results[name] = tags

    return results


def parse_sql_select_columns(sql: str) -> dict[str, Column]:
    tags = parse_sql_select_column_tags(sql)
    results = {}

    for column_name, column_tags in tags.items():
        kwargs = {}
        extra = {}

        for tag_name, tag_value in column_tags.items():
            if tag_name in {'name', 'type', 'type_spec', 'default'}:
                kwargs[tag_name] = tag_value
            elif tag_name in {'precision', 'scale'}:
                if isinstance(tag_value, str) and re.match(r'^\d+$', tag_value):
                    kwargs[tag_name] = int(tag_value)
            elif tag_name in {'not_null', 'primary_key', 'identity'}:
                kwargs[tag_name] = tag_value is True or tag_value.lower() in {'1', 'yes', 'true', 'on'}
            else:
                extra[tag_name] = tag_value

        if not 'name' in kwargs:
            kwargs['name'] = column_name

        if extra:
            kwargs['extra'] = extra

        results[column_name] = Column(**kwargs)

    return results

#endregion
