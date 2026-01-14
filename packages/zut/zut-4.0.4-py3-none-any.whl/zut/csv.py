"""
Write and read CSV tables.
"""
from __future__ import annotations

import csv
import json
import logging
import os
import sys
from contextlib import AbstractContextManager, contextmanager
from datetime import datetime, time, timezone, tzinfo
from decimal import Decimal
from enum import Enum, Flag
from io import SEEK_END, StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, TYPE_CHECKING, Any, Callable, Mapping, Sequence, Set

from zut.tables import Column, dump_tabulate
from zut.time import is_iso_datetime, make_aware, make_naive, parse_tz

if TYPE_CHECKING:
    from typing import Literal

    Converter = Callable[[Any],Any]|Any


#region High-level wrapper functions

def dump_csv(data: Any, file: CsvFile|str|os.PathLike|IO[str], columns: Sequence[str|Column]|dict[str,Converter]|None = None, *, append: bool = False, delay = False, delimiter: Literal[',',';','\t','locale']|str|None = None, encoding: str|None = None, tz: tzinfo|Literal['local','utc','']|str|None = None, archivate: bool|str|os.PathLike|None = None):
    """
    :param tz: If set, aware datetimes are written to the CSV file as naive datetimes in the given timezone.
    """
    with CsvWriter(file, columns, append=append, delay=delay, delimiter=delimiter, encoding=encoding, tz=tz, archivate=archivate) as writer:
        for row in data:
            writer.writerow(row)
        return writer


def dump_csv_or_tabulate(data: Any, file: str|os.PathLike|IO[str]|None, columns: Sequence[str|Column]|dict[str,Converter]|None = None, *, tabulate_headers: Sequence[str]|None = None, append: bool = False, delay = False, delimiter: Literal[',',';','\t','locale']|str|None = None, encoding: str|None = None, tz: tzinfo|Literal['local','utc','']|str|None = None):
    """
    Dump to CSV if `file` is a path or tabulate to stdout or stderr if `file` is stdout or stderr.

    Usefull for flexible `--out` arguments of command-line applications.
    """
    if file is None:
        pass # Do nothing
    elif file in {sys.stdout, sys.stderr}:
        dump_tabulate(data, file=file, headers=tabulate_headers if tabulate_headers is not None else columns)
    else:
        return dump_csv(data, file, columns, append=append, delay=delay, delimiter=delimiter, encoding=encoding, tz=tz)


@contextmanager
def dump_csv_temp(data: Any, columns: Sequence[str|Column]|dict[str,Converter]|None = None, *, append: bool = False, delay = False, delimiter: Literal[',',';','\t','locale']|str|None = None, encoding: str|None = None, tz: tzinfo|Literal['local','utc','']|str|None = None):
    """
    :param tz: If set, aware datetimes are written to the CSV file as naive datetimes in the given timezone.
    """    
    writer = None
    try:
        with CsvWriter(columns=columns, append=append, delay=delay, delimiter=delimiter, encoding=encoding, tz=tz) as writer:
            for row in data:
                writer.writerow(row)
 
        yield writer
    finally:
        if writer is not None:
            writer.path.unlink()


def load_csv(file: CsvFile|str|os.PathLike|IO[str], columns: Sequence[str|Column]|dict[str,Converter]|None = None, *, tz: tzinfo|Literal['local','utc','']|None = None, delimiter: Literal[',',';','\t','locale']|None = None, encoding = 'utf-8-sig') -> list[dict[str,Any]]:
    """
    :param tz: If set, naive datetimes read from the CSV file are considered as aware datetimes in the given timezone.
    """
    with CsvReader(file, columns, tz=tz, delimiter=delimiter, encoding=encoding) as reader:
        return [data for data in reader.iter_dicts()]

#endregion


#region Write CSV

class CsvWriter:
    def __init__(self, file: CsvFile|str|os.PathLike|IO[str]|None = None, columns: Sequence[str|Column]|dict[str,Converter]|None = None, *, append: bool = False, delay = False, delimiter: Literal[',',';','\t','locale']|str|None = None, encoding: str|None = None, tz: tzinfo|Literal['local','utc','']|str|None = None, archivate: bool|str|os.PathLike|None = None, accept_additional_existing_columns: bool|Literal['warn'] = 'warn', accept_missing_existing_columns: bool|Literal['warn'] = 'warn'):
        # Determine final CSV configuration settings
        self._file: CsvFile
        if isinstance(file, CsvFile):
            if columns is not None:
                file.columns = columns
            if delimiter is not None:
                file.delimiter = delimiter
            if encoding is not None:
                file.encoding = encoding
            if tz is not None:
                file.tz = tz
            self._file = file
        elif file is not None:
            self._file = CsvFile(file, columns, delimiter=delimiter, encoding=encoding, tz=tz)
        else:
            self._file = CsvFile(os.devnull, columns, delimiter=delimiter, encoding=encoding, tz=tz)
        
        # Management of actual file object
        self._fp_manager: AbstractContextManager[IO[str]]|None = None
        self._fp: IO[str]|None = None
        
        # Prepare other variables
        self.append = append
        self.delay = delay
        self.accept_additional_existing_columns = accept_additional_existing_columns
        self.accept_missing_existing_columns = accept_missing_existing_columns
        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__qualname__}")
        self._archivate = archivate
        self._rowcount = 0
        self._actually_written_rowcount = 0
        self._missing_keys: list[str] = []
        self._additional_keys: list[str] = []
        self._delayed_rows: list[Mapping[str,Any]|Sequence[Any]] = []
        self._columns_prepared = False
        self._existing_columns_to_append: list[str]|None = None
        self._existing_indexes: list[int|None]|None = None

    def __enter__(self):
        if self._fp is not None:
            raise ValueError(f"Context manager {type(self).__name__} already entered")

        needs_newline = False
        if self._file.is_devnull:
            self._fp_manager = NamedTemporaryFile('w', encoding=self._file.encoding, newline='', suffix='.csv', delete=False).__enter__()
            self._fp = self._fp_manager.file
            self._file.path = Path(self._fp_manager.name)
        elif isinstance(self._file.file, Path):
            if self._file.file.exists():
                if self.append:
                    if not self._file.no_headers:
                        self._existing_columns_to_append = self._file.existing_columns
                    needs_newline = not self._file.ends_with_newline
                else:
                    if self._archivate:
                        from zut.paths import archivate_file
                        archivate_file(self._file.file, self._archivate)
            self._file.file.parent.mkdir(parents=True, exist_ok=True)
            self._fp_manager = open(self._file.file, 'a' if self.append else 'w', encoding=self._file.encoding, newline='')
            self._fp = self._fp_manager.__enter__()
        else:
            if self.append:
                if not self._file.no_headers:
                    self._existing_columns_to_append = self._file.existing_columns
                needs_newline = not self._file.ends_with_newline
            self._fp_manager = None # managed externally
            self._fp = self._file.file
            self._fp.seek(0, SEEK_END)

        if needs_newline:
            self._fp.write('\n')

        if self._file._columns:
            self._prepare_columns()

        return self
    
    def __exit__(self, exc_type = None, exc_value = None, traceback = None):
        self.flush()
        if self._fp_manager is not None:
            self._fp_manager.__exit__(None, None, None)

    @property
    def fp(self) -> IO[str]:
        if self._fp is None:
            raise ValueError(f"Context manager {type(self).__name__} not entered")   
        return self._fp

    @property
    def file(self) -> CsvFile:
        return self._file

    @property
    def path(self) -> Path:
        return self._file.path

    @property
    def name(self) -> str:
        return self._file.name
        
    @property
    def columns(self) -> list[Column]:
        if self._file is None or self._file.columns is None:
            raise ValueError("No columns")
        return self._file.columns
    
    @columns.setter
    def columns(self, columns: Sequence[str|Column]|dict[str,Converter]):
        if self._columns_prepared:
            raise ValueError("Columns already prepared")
        self._file.columns = columns
        self._prepare_columns()

    @property
    def rowcount(self):
        return self._rowcount

    def _prepare_columns(self):
        columns = self._file.columns

        if columns is not None and self._existing_columns_to_append is not None and self._existing_columns_to_append != columns:          
            # Determine existing columns that are missing or must be reindexed within given columns
            column_indexes = {column.name: index for index, column in enumerate(columns)}
            self._existing_indexes = []
            additional_existing_columns = []
            for name in self._existing_columns_to_append:
                index = column_indexes.get(name)
                if index is None:
                    additional_existing_columns.append(name)
                self._existing_indexes.append(index)

            if additional_existing_columns:
                main_message = f"Additional column(s) in existing CSV file: {', '.join(additional_existing_columns)} (file: {self._file.name})"
                if not self.accept_additional_existing_columns:
                    raise ValueError(main_message)
                self._logger.log(logging.WARNING if self.accept_additional_existing_columns == 'warn' else logging.DEBUG, f"{main_message}. Rows will be appended with a null value for these columns.")
            
            # Determine given columns that are missing in exising columns
            missing_existing_columns = []
            for index, column in enumerate(columns):
                if not column.name in self._existing_columns_to_append:
                    self._existing_indexes.append(index)
                    missing_existing_columns.append(column.name)

            if missing_existing_columns:
                main_message = f"Missing column(s) in existing CSV file: {', '.join(missing_existing_columns)} (file: {self._file.name})"
                if not self.accept_missing_existing_columns:
                    raise ValueError(main_message)
                self._logger.log(logging.WARNING if self.accept_missing_existing_columns == 'warn' else logging.DEBUG, f"{main_message}. Rows will be appended with additional values but without column names.")

        self._columns_prepared = True        
        if not self._file.no_headers and not self._existing_columns_to_append:
            if columns is None:
                raise ValueError("Missing column names")
            self._actual_write(columns)
        self.flush()

    def _prepare_row(self, row: Sequence[Any]) -> Sequence[Any]:
        if self._existing_indexes is not None:
            row = [row[index] if index is not None and index < len(row) else None for index in self._existing_indexes]

        for i in range(len(row)):
            value = row[i]
            must_assign = False

            if value is not None and self._file.columns is not None and len(self._file.columns) > i:
                column = self._file.columns[i]
                if column.converter is not None:
                    if callable(column.converter):
                        newvalue = column.converter(value)
                    else:
                        newvalue = column.converter
                    
                    if newvalue != value:
                        value = newvalue
                        must_assign = True

            if self._file.tz and isinstance(value, datetime) and value.tzinfo:
                value = make_naive(value, self._file.tz)
                must_assign = True

            if must_assign:
                if not isinstance(row, list):
                    row = list(row)
                row[i] = value

        return row

    def flush(self):
        if not self._delayed_rows:
            return
        
        if not self._file.columns:
            self.columns = get_headers_from_rows(self._delayed_rows)
            return # NOTE: _prepare_columns (including _actual_write and then another flush) will be called from headers.setter
        
        for row in self._delayed_rows:
            self._actually_written_rowcount += 1
            self._actual_write(row)
        self._delayed_rows.clear()
        self.delay = False

    def writerow(self, row: Mapping[str,Any]|Sequence[Any]):
        self._rowcount += 1
        if self.delay:
            self._delayed_rows.append(row)
        else:
            self._actually_written_rowcount += 1
            self._actual_write(row)
    
    def _actual_write(self, row: Mapping[str,Any]|Sequence[Any]):
        if isinstance(row, Mapping):
            row = self._dict_to_row(row)
        else:
            row_dict = getattr(row, '__dict__', None)
            if row_dict is not None:
                row = self._dict_to_row(row_dict)
            else:
                self._check_sequence_length(row)

        row = self._prepare_row(row)
        
        row_str = ''
        first = True
        for value in row:
            if first:
                first = False
            else:
                row_str += self._file.delimiter
            row_str += self._file.escape_csv_value(self._file.to_csv_value(value))
        row_str += self._file.newline

        self.fp.write(row_str)
        self.fp.flush()

    def _check_sequence_length(self, row: Sequence[Any]):
        columns = self._file.columns
        if not columns:
            return
        
        if len(row) != len(columns):
            self._logger.warning(f"Invalid length for row {self._actually_written_rowcount}: {len(row)} (headers length: {len(columns)})")
    
    def _dict_to_row(self, row: Mapping[str,Any]):
        if not self._file.columns:
            self.columns = [str(key) for key in row] # NOTE: _prepare_columns (including _actual_write) will be called from headers.setter
        
        actual_row = []
        missing_keys = []
        column_names = set()
        for column in self.columns:
            column_names.add(column.name)
            if column.name in row:
                value = row[column.name]
            else:
                value = None
                if not self.delay and not column.name in self._missing_keys: # (if we have been delaying, no reason to warn: we actually expect to have missing keys, that's why we waited for more dicts to come)
                    missing_keys.append(column.name)
            actual_row.append(value)

        if missing_keys:
            self._logger.warning(f"Missing key(s) from row {self._actually_written_rowcount}: {', '.join(missing_keys)} (file: {self.name}). Rows will be appended with null values for these columns.")
            for key in missing_keys:
                self._missing_keys.append(key)

        for key in self._additional_keys:
            actual_row.append(row.get(key))

        additional_keys = []
        for key in row:
            if not key in column_names and not key in self._additional_keys:
                actual_row.append(row[key])
                additional_keys.append(key)

        if additional_keys:
            self._logger.warning(f"Additional key(s) from row {self._actually_written_rowcount}: {', '.join(additional_keys)} (file: {self.name}). Rows will be appended with additional values but without column names.")
            for key in additional_keys:
                self._additional_keys.append(key)

        return actual_row


def get_headers_from_rows(rows: Mapping[str,Any]|Sequence[Any]) -> list[str]:
    headers: list[str] = []

    def insert_header(header: str, following_keys: list[str]):
        # Try to keep the global order of headers: insert just before the first existing that we know is after the given header
        pos = len(headers)
        for key in following_keys:
            try:
                pos = headers.index(key)
                break
            except ValueError:
                continue
        headers.insert(pos, header)
        
    for row in rows:
        if not isinstance(row, Mapping):
            continue

        keys = list(row.keys())
        for i, key in enumerate(keys):
            if key in headers:
                continue                
            insert_header(key, keys[i+1:])

    return headers

#endregion


#region Read CSV

class CsvReader:
    def __init__(self, file: CsvFile|str|os.PathLike|IO[str], columns: Sequence[str|Column]|dict[str,Converter]|None = None, *, delimiter: Literal[',',';','\t','locale']|None = None, encoding = 'utf-8-sig', tz: tzinfo|Literal['local','utc','']|None = None, accept_additional_actual_columns: bool|Literal['warn'] = 'warn', accept_missing_actual_columns: bool|Literal['warn'] = 'warn'):
        # Determine final CSV configuration settings
        self._file: CsvFile
        if isinstance(file, CsvFile):
            if columns is not None:
                file.columns = columns
            if delimiter is not None:
                file.delimiter = delimiter
            if encoding is not None:
                file.encoding = encoding
            if tz is not None:
                file.tz = tz
            self._file = file
        else:
            self._file = CsvFile(file, columns, delimiter=delimiter, encoding=encoding, tz=tz)

        # Management of actual file object
        self._fp_manager: AbstractContextManager[IO[str]]|None = None
        self._fp: IO[str]|None = None
        
        # Prepare other variables
        self.accept_additional_actual_columns = accept_additional_actual_columns
        self.accept_missing_actual_columns = accept_missing_actual_columns
        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__qualname__}")
        self._actual_reader = None
        self._actual_columns: list[str]|None = None
        self._actual_indexes: list[int|None]|None = None
        self._columns_prepared = False
        self._rowcount = 0

    def __enter__(self):
        if self._fp is not None:
            raise ValueError(f"Context manager {type(self).__name__} already entered")

        if isinstance(self._file.file, Path):
            self._fp_manager = open(self._file.file, 'r', encoding=self._file.encoding, newline='')
            self._fp = self._fp_manager.__enter__()
        else:
            self._fp_manager = None # managed externally
            self._fp = self._file.file
    
        if sys.version_info >= (3, 13) and self._file.nullval == '!quoted': # NOTE: QUOTE_NOTNULL does not seem to work correctly on Python 3.12
            self._actual_reader = csv.reader(self._fp, delimiter=self._file.delimiter, quoting=csv.QUOTE_NOTNULL)
        else:
            self._actual_reader = csv.reader(self._fp, delimiter=self._file.delimiter)

        if not self._file.no_headers:
            self._actual_columns = next(self._actual_reader)

        if self._file._columns:
            self._prepare_columns()
            
        return self
    
    def __exit__(self, exc_type = None, exc_value = None, traceback = None):
        if self._fp_manager is not None:
            self._fp_manager.__exit__(None, None, None)

    @property
    def fp(self) -> IO[str]:
        if self._fp is None:
            raise ValueError(f"Context manager {type(self).__name__} not entered")   
        return self._fp

    @property
    def file(self) -> CsvFile:
        return self._file

    @property
    def path(self) -> Path:
        return self._file.path

    @property
    def name(self) -> str:
        return self._file.name
    
    @property
    def columns(self) -> list[Column]:
        columns = self._file.columns
        if columns is None:
            raise ValueError("No columns")
        return columns
    
    @columns.setter
    def columns(self, columns: Sequence[str|Column]|dict[str,Converter]):
        if self._columns_prepared:
            raise ValueError("Columns already prepared")
        self._file.columns = columns
        self._prepare_columns()
    
    @property
    def rowcount(self) -> int:
        """ Number of rows read for now. """
        return self._rowcount
    
    @property
    def actual_reader(self):
        if self._actual_reader is None:
            raise ValueError(f"Context manager {type(self).__name__} not entered")  
        return self._actual_reader
    
    def _prepare_columns(self):        
        columns = self.columns
        
        if columns is not None and self._actual_columns is not None and self._actual_columns != columns:
            # Determine given columns that are missing or must be reindexed within actual columns
            actual_indexes = {name: index for index, name in enumerate(self._actual_columns)}
            self._actual_indexes = []
            missing_actual_columns = []
            for column in columns:
                index = actual_indexes.get(column.name)
                if index is None:
                    missing_actual_columns.append(column.name)
                self._actual_indexes.append(index)

            if missing_actual_columns:
                main_message = f"Missing column(s) in actual CSV file: {', '.join(missing_actual_columns)} (file: {self._file.name})"
                if not self.accept_missing_actual_columns:
                    raise ValueError(main_message)
                self._logger.log(logging.WARNING if self.accept_missing_actual_columns == 'warn' else logging.DEBUG, f"{main_message}. Rows will always contain null values for these columns.")

            # Determine actual columns that are missing in given columns
            additional_actual_columns: dict[str,int] = {}
            column_names = {column.name for column in columns}
            for name, actual_index in actual_indexes.items():
                if not name in column_names:
                    additional_actual_columns[name] = actual_index

            if additional_actual_columns:
                main_message = f"Additional column(s) in actual CSV file: {', '.join(additional_actual_columns)} (file: {self._file.name})"
                if not self.accept_additional_actual_columns:
                    raise ValueError(main_message)
                self._logger.log(logging.WARNING if self.accept_additional_actual_columns == 'warn' else logging.DEBUG, f"{main_message}. Rows will additional values for these columns.")

        self._columns_prepared = True

    def _prepare_rows(self, row: list[str|None]) -> list[Any]:
        if self._actual_indexes is not None:
            row = [row[index] if index is not None and index < len(row) else None for index in self._actual_indexes]

        nullval = None if self._file.nullval == '!quoted' else self._file.nullval

        for i in range(len(row)):
            value = row[i]

            if nullval is not None and value is not None and value == nullval:
                value = None

            if value is not None and self._file.columns is not None and len(self._file.columns) > i:
                column = self._file.columns[i]
                if column.converter is not None:
                    if callable(column.converter):
                        newvalue = column.converter(value)
                    else:
                        newvalue = column.converter
                    
                    if newvalue != value:
                        value = newvalue

            if isinstance(value, str):
                if is_iso_datetime(value):
                    value = datetime.fromisoformat(value)

            if self._file.tz and isinstance(value, datetime) and not value.tzinfo:
                value = make_aware(value, self._file.tz)

            row[i] = value

        return row
        
    def __iter__(self):
        return self

    def __next__(self):
        if not self._columns_prepared:
            self._prepare_columns()
        row = next(self.actual_reader)
        self._rowcount += 1
        return self._prepare_rows(row) # pyright: ignore[reportArgumentType]
    
    def iter_rows(self):
        for row in self:
            yield row
    
    def iter_dicts(self):
        for row in self:
            yield self._row_to_dict(row)

    def _row_to_dict(self, row: Sequence[Any]) -> dict[str,Any]:
        if len(row) < len(self.columns):
            missing_columns = [column.name for column in self.columns[len(row):]]
            self._logger.warning(f"Missing column{'s' if len(missing_columns) > 1 else ''} in row {self._rowcount}: {', '.join(missing_columns)} (file: {self.name}). Row will contain null values for {'these columns' if len(missing_columns) > 1 else 'this column'}.")

        elif len(row) > len(self.columns):
            if len(row) > len(self.columns)+1:
                message = f"Additional columns in row {self._rowcount}: columns n°{len(self.columns)+1} to {len(row)} (file: {self.name}). Row will not contain a value for these columns."
            else:
                message = f"Additional column in row {self._rowcount}: column n°{len(self.columns)+1} (file: {self.name}). Row will not contain a value for this column."
            self._logger.warning(message)
        
        return {column.name: row[i] if i < len(row) else None for i, column in enumerate(self.columns)}
    

def get_csv_columns(file: str|os.PathLike|IO[str], *, encoding = 'utf-8-sig', quotechar = '"') -> list[str]:
    columns = CsvFile(file, encoding=encoding, quotechar=quotechar).existing_columns
    if columns is None:
        raise ValueError(f"Cannot read CSV columns from {file}")
    return columns

#endregion


#region Format

class CsvFile:
    default_delimiter: Literal[',',';','\t','locale']|str = ','
    default_decimal_separator: Literal['.',',','locale','!delimiter']|str = '!delimiter'
    default_encoding: str = 'utf-8-sig'
    default_tz: tzinfo|Literal['local','utc','']|str = ''
    default_nullval: Literal['','!quoted']|str = '!quoted'
    default_quotechar: str = '"'
    default_newline: str = '\n'    
    default_lists: Literal['visual','json','pg'] = 'pg'
    default_dicts: Literal['visual','json'] = 'json'
    default_enums: Literal['name','value'] = 'value'
    default_no_microsecond: bool = False
    default_no_scientific_notation: bool = False

    def __init__(self, file: str|os.PathLike|IO[str], columns: Sequence[str|Column]|dict[str,Converter]|None = None, *, no_headers = False, existing_columns: list[str]|None = None, delimiter: Literal[',',';','\t','locale']|str|None = None, decimal_separator: Literal['.',',','locale','!delimiter']|str|None = None, encoding: str|None = None, tz: tzinfo|Literal['local','utc','']|str|None = None, nullval: Literal['','!quoted']|str|None = None, quotechar: str|None = None, newline: str|None = None, ends_with_newline: bool|None = None, lists: Literal['visual','json','pg']|None = None, dicts: Literal['visual','json']|None = None, enums: Literal['name','value']|None = None, no_microsecond: bool|None = None, no_scientific_notation: bool|None = None):
        self._logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__qualname__}')
        self._set_defaults()

        self._file: Path|IO[str]
        self._name: str
        self._is_devnull = False
        if isinstance(file, (str, os.PathLike)):
            if file == os.devnull:
                self._is_devnull = True
            self._file  = Path(file) if not isinstance(file, Path) else file
            self._name = '<null>' if self._is_devnull else self._file.name
        else:
            self._file = file
            self._name = getattr(file, 'name', f'<{type(file).__name__}>')

        # Associated to property setters
        self._columns_read = False
        self._columns: list[Column|Literal['*']]|None = None
        if columns is not None:
            self.columns = columns

        self._delimiter: Literal[',',';','\t','locale']|str|None = None
        if delimiter is not None:
            self.delimiter = delimiter

        self._decimal_separator: Literal['.',',','locale','!delimiter']|str|None = None
        if decimal_separator is not None:
            self.decimal_separator = decimal_separator

        self._encoding: str|None = None
        if encoding is not None:
            self.encoding = encoding

        self._tz: tzinfo|Literal['local','']|None = None
        if tz is not None:
            self.tz = tz

        # Other parameters that can be examined from the file
        self._newline: str|None = newline
        self._ends_with_newline: bool|None = ends_with_newline
        self._existing_columns: list[str]|None = existing_columns

        # Set once and for all (no property setters or examination)
        self.no_headers: bool = no_headers
        self.nullval: Literal['','!quoted']|str = nullval if nullval is not None else self.default_nullval
        self.quotechar: str = quotechar if quotechar is not None else self.default_quotechar            
        self.lists: Literal['visual','json','pg'] = lists if lists is not None else self.default_lists
        self.dicts: Literal['visual','json'] = dicts if dicts is not None else self.default_dicts
        self.enums: Literal['name','value'] = enums if enums is not None else self.default_enums
        self.no_microsecond: bool = no_microsecond if no_microsecond is not None else self.default_no_microsecond
        self.no_scientific_notation: bool = no_scientific_notation if no_scientific_notation is not None else self.default_no_scientific_notation

        # Internal
        self._real_path: Path|None = None
        self._examined: bool|Literal['full'] = False

    def _set_defaults(self):
        self.default_delimiter = self.__class__.default_delimiter
        self.default_decimal_separator = self.__class__.default_decimal_separator
        self.default_encoding = self.__class__.default_encoding
        self.default_tz = self.__class__.default_tz
        self.default_nullval = self.__class__.default_nullval
        self.default_quotechar = self.__class__.default_quotechar
        self.default_newline = self.__class__.default_newline
        self.default_lists = self.__class__.default_lists
        self.default_dicts = self.__class__.default_dicts
        self.default_enums = self.__class__.default_enums
        self.default_no_microsecond = self.__class__.default_no_microsecond
        self.default_no_scientific_notation = self.__class__.default_no_scientific_notation

        fmt = os.environ.get('CSV_FORMAT')
        if fmt:
            fmt_lower = fmt.lower()                    
            if fmt_lower == 'pg' or fmt_lower == 'postgres' or fmt_lower == 'postgresql':
                # Export lists as PostgreSQL array literals and dicts as JSON
                # (same as defaults except encoding: UTF-8 instead of UTF-8 with BOM)
                self.default_delimiter = ','
                self.default_decimal_separator = '!delimiter'
                self.default_encoding = 'utf-8'
                self.default_tz = ''
                self.default_nullval = '!quoted'
                self.default_quotechar = '"'
                self.default_newline = '\n'    
                self.default_lists = 'pg'
                self.default_dicts = 'json'
                self.default_enums = 'value'
                self.default_no_microsecond = False
                self.default_no_scientific_notation = False
            
            elif fmt_lower == 'excel' or fmt_lower == 'xlsx' or fmt_lower == 'xls':
                # Datetimes in local timezone, no microseconds, no scientific notation, visual lists and dicts. CSV delimiter and decimal separator depend on the locale
                self.default_delimiter = 'locale'
                self.default_decimal_separator = '!delimiter'
                self.default_encoding = 'utf-8-sig'
                self.default_tz = 'local'
                self.default_nullval = '!quoted'
                self.default_quotechar = '"'
                self.default_newline = '\n'    
                self.default_lists = 'visual'
                self.default_dicts = 'visual'
                self.default_enums = 'name'
                self.default_no_microsecond = True
                self.default_no_scientific_notation = True
            
            elif fmt_lower == 'visual':
                # Export lists and dicts as easily visuable strings when possible, otherwise as JSON
                self.default_lists = 'visual'
                self.default_dicts = 'visual'
                self.default_enums = 'name'
            
            elif fmt_lower == 'json':
                # Export lists and dicts as JSON
                self.default_lists = 'json'
                self.default_dicts = 'json'
                
            else:
                self._logger.warning(f"Unknown value for CSV_FORMAT environment variable: {fmt}")

    @property
    def is_devnull(self) -> bool:
        return self._is_devnull

    @property
    def file(self) -> Path|IO[str]:
        return self._file

    @property
    def path(self) -> Path:
        if self._real_path is not None:
            return self._real_path
        if not isinstance(self._file, Path):
            raise ValueError("This CSV file is not associated to a path")
        return self._file

    @path.setter
    def path(self, value: Path):
        if not self.is_devnull:
            raise ValueError("Alternative path can be set only for devnull")
        self._real_path = value

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def columns(self) -> list[Column]|None:
        """ List of CSV columns. """
        if not self._columns_read:

            if self._columns is None or '*' in self._columns:
                if not self._examined:
                    self.examine()

                if self._columns is None:
                    if self.existing_columns is not None:
                        self._columns = [Column(name) for name in self.existing_columns]
                else:
                    orig_columns = self._columns.copy()
                    orig_names = {column.name for column in orig_columns if column != '*'}
                    self._columns = []
                    asterix = False
                    for column in orig_columns:
                        if column == '*':
                            if asterix:
                                raise ValueError("Several '*' placeholders")
                            
                            if self.existing_columns is not None:
                                for name in self.existing_columns:
                                    if not name in orig_names:
                                        self._columns.append(Column(name))

                            asterix = True
                        else:
                            self._columns.append(column)

            self._columns_read = True

        return self._columns # pyright: ignore[reportReturnType]
    
    @columns.setter
    def columns(self, values: Sequence[str|Column]|dict[str,Converter]):
        if not values:
            self._columns = None
        elif isinstance(values, dict):
            self._columns = [Column(name, converter=converter) for name, converter in values.items()]
        else:
            self._columns = [Column(column) if not isinstance(column, Column) else column for column in values]
    
    @property
    def delimiter(self) -> Literal[',',';','\t']|str:
        """ Separator between CSV values. """
        if self._delimiter is None:
            if not self._examined:
                self.examine()
            if self._delimiter is None:
                self._delimiter = self.default_delimiter
        
        if self._delimiter == 'locale':
            from zut.locale import get_locale_decimal_separator
            self._delimiter = ';' if get_locale_decimal_separator() == ',' else ','
        
        return self._delimiter

    @delimiter.setter
    def delimiter(self, value: Literal[',',';','\t','locale']|str):
        self._delimiter = value

    @property
    def decimal_separator(self) -> Literal['.',',']|str:
        """ Decimal separator within CSV values. """
        if self._decimal_separator is None:
            self._decimal_separator = self.default_decimal_separator
        
        if self._decimal_separator == '!delimiter':
            if self.delimiter == ';':
                self._decimal_separator = ','
            else:
                self._decimal_separator = '.'
        
        elif self._decimal_separator == 'locale':
            from zut.locale import get_locale_decimal_separator
            value: Literal['.',','] = get_locale_decimal_separator() # pyright: ignore[reportAssignmentType]
            self._decimal_separator = value
        
        return self._decimal_separator

    @decimal_separator.setter
    def decimal_separator(self, value: Literal['.',',','locale','!delimiter']|str):
        self._decimal_separator = value

    @property
    def encoding(self) -> str:
        """ Encoding of the CSV file. """
        if self._encoding is None:
            self._encoding = self.default_encoding
            return self._encoding
        return self._encoding

    @encoding.setter
    def encoding(self, value: str):
        self._encoding = value

    @property
    def tz(self) -> tzinfo|Literal['local','']:
        """ If not empty:
            - on writing: aware datetimes are written as naive datetimes in the given timezone
            - on reading: naive datetimes are made aware in the given timezone """
        if self._tz is None:
            self._tz = self._parse_tz(self.default_tz)
            return self._tz
        return self._tz

    @tz.setter
    def tz(self, value: tzinfo|Literal['local','utc','']|str):
        self._tz = self._parse_tz(value)

    @classmethod
    def _parse_tz(cls, value: tzinfo|Literal['local','utc','']|str) -> tzinfo|Literal['local','']:
        if not value:
            return ''
        elif value == 'local' or value == 'localtime':
            return 'local'
        elif value == 'utc':
            return timezone.utc
        elif isinstance(value, tzinfo):
            return value
        else:
            return parse_tz(value)

    @property
    def newline(self) -> str:
        if self._newline is None:
            if not self._examined:
                self.examine()
            if self._newline is None:
                self._newline = self.default_newline
        
        return self._newline

    @property
    def ends_with_newline(self) -> bool:
        if self._ends_with_newline is None:
            if self._examined != 'full':
                self.examine(full=True)
            if self._ends_with_newline is None:
                self._ends_with_newline = False
        
        return self._ends_with_newline

    @property
    def existing_columns(self) -> list[str]|None:
        if self._existing_columns is None:
            if not self._examined:
                self.examine()
        
        return self._existing_columns

    def examine(self, *, full = False) -> None:
        """
        Determines `existing_columns`, `delimiter` and `newline` properties if they are not already set.
        If `full`, also determines `ends_with_newline`.
        """
        file: IO[str]        
        if isinstance(self._file, Path):
            if not os.path.exists(self._file):
                self._examined = 'full'
                return
            initial_pos = None
            file = open(self._file, 'r', encoding=self.encoding, newline='')
        else:
            initial_pos = self._file.tell()
            self._file.seek(0)
            file = self._file

        try:
            first_line_io = StringIO()
            first_line_ended = False
            buf_size = 65536
            while True:
                chunk = file.read(buf_size)
                if not chunk:
                    break

                if not first_line_ended:
                    pos = chunk.find('\n')
                    if pos >= 0:
                        if self._newline is None:
                            if pos > 0 and chunk[pos-1] == '\r':
                                self._newline = '\r\n'
                            else:
                                self._newline = '\n'
                    else:
                        pos = chunk.find('\r')
                        if self._newline is None:
                            if pos >= 0:
                                self._newline = '\r'

                    if pos >= 0:
                        first_line_io.write(chunk[:pos])
                        first_line_ended = True
                        if not full or self._ends_with_newline is not None:
                            break # Avoid reading the entire file
                    else:
                        first_line_io.write(chunk)

                if full and self._ends_with_newline is None:
                    self._ends_with_newline = chunk[-1] == '\n'

            if first_line_io.tell() == 0:
                # No content
                if self._newline is None:
                    self._newline = self.default_newline
                if self._ends_with_newline is None:
                    self._ends_with_newline = False
                if self._delimiter is None:
                    self._delimiter = self.default_delimiter
                self._examined = 'full'
                return

            # Guess the delimiter
            if self._delimiter is None:
                first_line_str = first_line_io.getvalue()

                comma_count = first_line_str.count(',')
                semicolon_count = first_line_str.count(';')
                if semicolon_count > comma_count:
                    self._delimiter = ';'
                elif comma_count > 0:
                    self._delimiter = ','
                else:
                    self._delimiter = self.default_delimiter

            # Read column names
            if not self.no_headers and self._existing_columns is None:
                first_line_io.seek(0)
                reader = csv.reader(first_line_io, delimiter=self._delimiter, quotechar=self.quotechar, doublequote=True)
                self._existing_columns = next(reader)

            self._examined = 'full' if full else True
        finally:
            # Ensure we move back the fp were it was
            if initial_pos is not None:
                file.seek(initial_pos)
            else:
                file.close()

    def to_csv_value(self, value: Any) -> Any:
        """
        Format a CSV value.

        :param value:               Value to format.
        :param decimal_separator:   Decimal separator to use.
        :param tz:                  If set, aware datetimes are written to the CSV file as naive datetimes in the given timezone.
        :param no_microseconds:     If true, output datetimes have no microseconds. They have hours, minutes and seconds.
        :param visual:              If true, the following changes are made in the output format:
            - Enums: use name instead of value
            - List: use 'A|B|C' format instead of postgresql array literal or json format
            - Enum names are used instead of enum values, and lists and dicts will be e
        """
        def format_value(value: Any, *, root: bool):    
            if value is None:
                return None

            if self.tz:
                if isinstance(value, str):
                    if is_iso_datetime(value):
                        value = datetime.fromisoformat(value)

            if isinstance(value, str):
                return value

            elif isinstance(value, (Enum,Flag)):
                return value.name if self.enums == 'name' else value.value
                
            elif isinstance(value, bool):
                return 'true' if value else 'false'
            
            elif isinstance(value, int):
                return value
            
            elif isinstance(value, (float,Decimal)):
                from zut.convert import get_number_str
                str_value = get_number_str(value, no_scientific_notation=True if self.no_scientific_notation else False)

                if self.decimal_separator != '.':
                    return str_value.replace('.', self.decimal_separator)

                return str_value
            
            elif isinstance(value, (datetime,time)):
                if self.tz:
                    if value.tzinfo and isinstance(value, datetime): # make the datetime naive if it is not already
                        value = make_naive(value, 'local' if self.tz is True else self.tz)
                if self.no_microsecond:
                    return value.replace(microsecond=0)
                return value
            
            elif isinstance(value, Mapping):
                if root and self.dicts == 'visual':
                    from zut.convert import get_visual_dict_str
                    return get_visual_dict_str(value)
                
                else:
                    from zut.json import ExtendedJSONEncoder
                    return json.dumps(value, ensure_ascii=False, cls=ExtendedJSONEncoder)

            elif isinstance(value, (Sequence,Set)):
                if root and self.lists == 'visual':
                    if len(value) == 1:
                        return format(next(iter(value)))
                    
                    from zut.convert import get_visual_list_str
                    return get_visual_list_str(value)
            
                elif self.lists == 'pg':
                    from zut.convert import get_pg_array_str
                    return get_pg_array_str(value)
                
                else:
                    from zut.json import ExtendedJSONEncoder
                    return json.dumps(value, ensure_ascii=False, cls=ExtendedJSONEncoder)
                    
            else:
                return value

        return format_value(value, root=True)

    def escape_csv_value(self, value: Any) -> str:
        if value is None:    
            return '' if self.nullval == '!quoted' else self.nullval
        if not isinstance(value, str):
            value = str(value)
        if value == '':
            return f'{self.quotechar}{self.quotechar}'

        need_escape = False
        result = ''
        for c in value:
            if c == self.delimiter:
                result += c
                need_escape = True
            elif c == self.quotechar:
                result += f'{c}{c}'
                need_escape = True
            elif c == '\n' or c == '\r':
                result += c
                need_escape = True
            else:
                result += c

        if need_escape:
            result = f'{self.quotechar}{result}{self.quotechar}'
        else:
            result = result

        return result
    
#endregion
