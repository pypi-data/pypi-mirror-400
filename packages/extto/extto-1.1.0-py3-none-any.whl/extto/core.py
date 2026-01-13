from abc import ABC, abstractmethod
from typing import Any
import mmap
import re
import pathlib
import sys
from functools import reduce


class DataNotFoundError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class DataFormattingError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class LineExtractor(ABC):
    '''
    Abstract class on which all LineExtractors are based.\n

    LineExtractors extract all text on a given line.

    An Extractor can be instantiated and called on a file, or alternatively\n
    can be used through the .extract() convenience staticmethod.\n

    Attributes
    ----------
    PATTERN: bytes
        Regex pattern for line to extract as bytes object
    MODIFIERS: list[re.RegexFlag]
        RegexFlag modifiers used in matching
    blocks: list[str]
        Extracted string blocks (lines)
    data: list[Any]
        Processed data, one entry per line.\n
        Typing of data is left to implementations
    '''

    def __init__(self):
        # Set all to empty
        self._data = []
        self._blocks = []
        return

    @property
    @abstractmethod
    def PATTERN() -> bytes:
        '''
        Regex pattern for line
        '''
        raise NotImplementedError

    #: Modifiers for line/block matching
    MODIFIERS: list[re.RegexFlag] = []

    @property
    def data(self) -> Any:
        '''
        Processed data
        '''
        return self._data

    @data.setter
    def data(self, value) -> Any:
        self._data = value
        return

    @property
    def blocks(self) -> list[str]:
        '''
        List of processed blocks, each is a string match to self.pattern
        '''
        return self._blocks

    @blocks.setter
    def blocks(self, value) -> list[str]:
        if not isinstance(value, list):
            raise ValueError('Blocks should be list of strings')
        else:
            if not all(isinstance(entry, str) for entry in value):
                raise ValueError('Blocks should be list of strings')
            else:
                self._blocks = value
        return

    @classmethod
    @abstractmethod
    def extract(file_name: str) -> list[Any]:
        '''
        Convenience method which instantiates class, extracts blocks, and
        returns processed datasets

        Parameters
        ----------
        file_name: str
            Name of file to parse

        Returns
        -------
        list[Any]
            Each entry contains processed data, as defined in cls.data
        '''
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _process_block(block: str) -> Any:
        '''
        Processes single string block and returns processed output

        Parameters
        ----------
        block: str
            Block extracted from file using cls.extract_blocks

        Returns
        -------
        Any
            Data, as defined in cls.data
        '''
        raise NotImplementedError

    def __call__(self, file_name: str, process: bool = False,
                 before: str = None, after: str = None,
                 **kwargs) -> None:
        '''
        Extracts blocks from file using PATTERN.\n\n

        Optionally, extraction can be limited to before or
        after certain strings.\n\n

        Data can also be processed after extraction.

        Parameters
        ----------
        file_name: str
            File to parse
        process: bool, optional
            If True, process data after extraction using\n
            self._process_block. Default is False.
        before: str, default None
            Only consider data before this string (first occurrence, exclusive)
        after: str, default None
            Only consider data after this string (first occurrence, inclusive)
        kwargs: dict
            Additional keyword arguments passed to self._process_block
        '''

        # Get blocks
        self.blocks = self._extract_blocks(file_name, before, after)

        # and optionally process data
        if process:
            self._data = [
                self._process_block(block, **kwargs)
                for block in self.blocks
            ]
        else:
            self._data = []

        return

    def _extract_blocks(self, file_name: str, before: str = None,
                        after: str = None) -> list[str]:
        '''
        Extracts blocks (lines) from file according to pattern

        Parameters
        ----------
        file_name: str
            File to be read
        before: str, default None
            Only consider data before this string (first occurrence, exclusive)
        after: str, default None
            Only consider data after this string (first occurrence, inclusive)

        Returns
        -------
        list[str]
            Blocks (lines) extracted from file with utf-8 encoding
        '''

        if len(self.MODIFIERS) == 0:
            modifiers = re.NOFLAG
        else:
            modifiers = reduce(lambda x, y: x | y, self.MODIFIERS)

        _re = re.compile(
            self.PATTERN,
            modifiers
        )

        if before is not None:
            pattern = re.compile(bytes(before, 'utf-8'))
            with open(file_name, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    match = pattern.search(mm)
            if match is None:
                end = sys.maxsize
            else:
                end = match.end()
        else:
            end = sys.maxsize

        if after is not None:
            pattern = re.compile(bytes(after, 'utf-8'))
            with open(file_name, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    match = pattern.search(mm)
            if match is None:
                start = sys.maxsize
            else:
                start = match.start()
        else:
            start = 0

        # Open file as bytes, find matching blocks
        with open(file_name, mode='rb') as file_obj:
            with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj: # noqa
                lines = _re.findall(mmap_obj, start, end)

        lines = [
            block.decode('utf-8')
            for block in lines
        ]

        if not len(lines):
            raise DataNotFoundError(f'No relevant data found in {file_name}')

        return lines


class BetweenExtractor(ABC):
    '''
    Abstract class on which all BetweenExtractors are based.\n

    BetweenExtractors extract all text between the designated START_ and\n
    END_PATTERN lines.\n\n

    An Extractor can be instantiated and called on a file, or alternatively\n
    can be used through the .extract() convenience staticmethod.\n

    Attributes
    ----------
    START_PATTERN: bytes
        Regex pattern for start of section
    END_PATTERN: bytes
        Regex pattern for end of section
    MODIFIERS: list[re.RegexFlag]
        RegexFlag modifiers used in matching
    blocks: list[str]
        Extracted string blocks
    data: list[Any]
        Processed data, one entry per block.\n
        Typing of data is left to implementations
    '''

    def __init__(self):
        # Set all to empty
        self._data = []
        self._blocks = []
        return

    @property
    @abstractmethod
    def START_PATTERN() -> bytes:
        '''
        Regex pattern for start of section
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def END_PATTERN() -> bytes:
        '''
        Regex pattern for start of section
        '''
        raise NotImplementedError

    @property
    def PATTERN(self) -> bytes:
        '''
        Regex pattern used in matching
        '''
        return self.START_PATTERN + rb'([\S\s]*?)' + self.END_PATTERN

    #: Modifiers for line/block matching
    MODIFIERS: list[re.RegexFlag] = []

    @property
    def data(self) -> Any:
        '''
        Processed data
        '''
        return self._data

    @data.setter
    def data(self, value) -> Any:
        self._data = value
        return

    @property
    def blocks(self) -> list[str]:
        '''
        List of processed blocks, each is a string match to self.PATTERN
        '''
        return self._blocks

    @blocks.setter
    def blocks(self, value) -> list[str]:
        if not isinstance(value, list):
            raise ValueError('Blocks should be list of strings')
        else:
            if not all(isinstance(entry, str) for entry in value):
                raise ValueError('Blocks should be list of strings')
            else:
                self._blocks = value
        return

    @staticmethod
    def extract(file_name: str) -> list[Any]:
        '''
        Convenience method which instantiates class, extracts blocks, and
        returns processed datasets

        Parameters
        ----------
        file_name: str
            Name of file to parse

        Returns
        -------
        list[Any]
            Each entry contains processed data, as defined in cls.data
        '''
        _ext = BetweenExtractor()
        _ext(file_name, process=True)
        return _ext.data

    @staticmethod
    @abstractmethod
    def _process_block(block: str) -> Any:
        '''
        Processes single string block and returns processed output

        Parameters
        ----------
        block: str
            Block extracted from file using cls.extract_blocks

        Returns
        -------
        Any
            Data, as defined in cls.data
        '''
        raise NotImplementedError

    def __call__(self, file_name: str, process: bool = False,
                 before: str = None, after: str = None,
                 **kwargs) -> None:
        '''
        Extracts blocks from file using PATTERN.\n\n

        Optionally, extraction can be limited to before
        or after certain strings.\n\n

        Data can also be processed after extraction.

        Parameters
        ----------
        file_name: str
            File to parse
        process: bool, optional
            If True, process data after extraction using\n
            self._process_block. Default is False.
        before: str, default None
            Only consider data before this string (first occurrence, exclusive)
        after: str, default None
            Only consider data after this string (first occurrence, inclusive)
        kwargs: dict
            Additional keyword arguments passed to self._process_block
        '''

        # Get blocks
        self.blocks = self._extract_blocks(file_name, before, after)

        # and optionally process data
        if process:
            self._data = [
                self._process_block(block, **kwargs)
                for block in self.blocks
            ]
        else:
            self._data = []

        return

    def _extract_blocks(self, file_name: str, before: str = None,
                        after: str = None) -> list[str]:
        '''
        Extracts blocks from file according to pattern

        Parameters
        ----------
        file_name: str
            File to be read
        before: str, default None
            Only consider data before this string (first occurrence, exclusive)
        after: str, default None
            Only consider data after this string (first occurrence, inclusive)

        Returns
        -------
        list[str]
            Blocks extracted from file with utf-8 encoding
        '''

        if len(self.MODIFIERS) == 0:
            modifiers = re.NOFLAG
        else:
            modifiers = reduce(lambda x, y: x | y, self.MODIFIERS)

        block_match = re.compile(
            self.PATTERN,
            modifiers
        )

        if before is not None:
            pattern = re.compile(bytes(before, 'utf-8'))
            with open(file_name, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    match = pattern.search(mm)
            if match is None:
                end = sys.maxsize
            else:
                end = match.start()
        else:
            end = sys.maxsize

        if after is not None:
            pattern = re.compile(bytes(after, 'utf-8'))
            with open(file_name, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    match = pattern.search(mm)
            if match is None:
                start = sys.maxsize
            else:
                start = match.start()
        else:
            start = 0

        # Open file as bytes, find matching blocks
        with open(file_name, mode='rb') as file_obj:
            with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj: # noqa
                blocks = block_match.findall(mmap_obj, start, end)

        blocks = [
            block.decode('utf-8')
            for block in blocks
        ]

        if not len(blocks):
            raise DataNotFoundError(f'No relevant data found in {file_name}')

        return blocks


def find_lines(file_name: str | pathlib.Path, pattern: bytes,
               modifiers: re.RegexFlag = []) -> list[str]:
    '''
    Utility function which retrieves all lines in file which match to pattern\n
    Internally uses re.findall

    Parameters
    ----------
    file_name: str | pathlib.Path
        File to parse
    pattern: bytes
        Regular expression pattern to match as bytes object\n
        e.g. b'^[0-9]{4}-[0-9]{2}-[0-9]{2}'
    modifiers: list[re.RegexFlag], optional
        RegexFlag objects used for matching

    Returns
    -------
    list[str]
        All matches from the specifiied file

    Raises
    ------
    DataNotFoundError
        If no matches found in file
    '''

    if len(modifiers) == 0:
        modifiers = re.NOFLAG
    else:
        modifiers = reduce(lambda x, y: x | y, modifiers)

    _re = re.compile(
        pattern.encode(),
        modifiers
    )

    # Open file as bytes, find matching blocks
    with open(file_name, mode='rb') as file_obj:
        with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj: # noqa
            blocks = _re.findall(mmap_obj)

    blocks = [
        block.decode('utf-8')
        for block in blocks
    ]

    if not len(blocks):
        raise DataNotFoundError(f'No relevant data found in {file_name}')

    return blocks
