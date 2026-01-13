""" XML Tree File Writing Abstract Class.
"""
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Iterable, Generator
from xml.etree.ElementTree import ElementTree, tostring

from changelist_data.changelist import Changelist


class BaseXMLTree(metaclass=ABCMeta):
    """ A Base Abstract Class providing writing capabilities for an XML Tree class.
    """

    @abstractmethod
    def get_root(self) -> ElementTree:
        raise NotImplementedError

    @abstractmethod
    def get_changelists(self) -> list[Changelist]:
        raise NotImplementedError

    @abstractmethod
    def generate_changelists(self) -> Generator[Changelist, None, None]:
        raise NotImplementedError

    @abstractmethod
    def update_changelists(
        self,
        changelists: list[Changelist] | Iterable[Changelist],
    ): raise NotImplementedError

    def write_tree(
        self, path: Path,
    ) -> bool:
        """ Write the Tree as XML to the given Path.
    - Ensures that all parent directories exist, and creates the file if necessary.

    **Parameters:**
     - path (Path): The Path to the File.

    **Returns:**
     bool - True if data was written to the file.
        """
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        xml_bytes = tostring(
            element=self.get_root().getroot(),
            encoding='UTF-8',
            method='xml',
            xml_declaration=True,
            short_empty_elements=True,
        )
        if (updated_xml := _replace_xml_declaration_quotes(xml_bytes)) is not None:
            xml_bytes = updated_xml
        return path.write_bytes(xml_bytes) > 0


def _find_single_quotes_in_xml_declaration(
    xml_bytes: bytes,
) -> list[int] | None:
    if (decl_index := xml_bytes.index(b'<?xml')) < 0:
        return None
    if (decl2_index := xml_bytes.index(b'?>', decl_index)) <= decl_index:
        return None
    index_list = list(filter(
        lambda i: xml_bytes[i] == ord(b"'"),
        range(decl_index, decl2_index + 1)
    ))
    if (quote_count := len(index_list)) < 2 or quote_count % 2 != 0:
        return None
    return index_list


def _replace_xml_declaration_quotes(
    xml_bytes: bytes,
) -> bytearray | None:
    if (single_quote_indices := _find_single_quotes_in_xml_declaration(xml_bytes)) is None:
        return None
    xml_array = bytearray(xml_bytes)
    for idx in single_quote_indices:
        xml_array[idx] = ord(b'"')
    return xml_array
