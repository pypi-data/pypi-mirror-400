from __future__ import annotations

from abc import abstractmethod

from typing import TYPE_CHECKING

from .generic import ContentHandler

if TYPE_CHECKING:
    from lxml import etree


class XMLHandler(ContentHandler):
    content_types = []
    file_extensions = [".xml"]
    
    uri_attributes = []
    uri_elements = []

    def __init__(self, url, content: bytes | None = None, **kwargs):
        super().__init__(url, content, **kwargs)

    def read(self):
        return "Handling XML file."

    @property
    def document(self) -> etree._Element:
        if not self._document:
            from lxml import etree
            self._document = etree.fromstring(self.content)
        return self._document

    @property
    def xml_document(self) -> etree._Element:
        return self.document

    @staticmethod
    def is_supported_content(content) -> bool:
        try:
            from lxml import etree
            etree.fromstring(content)
            return True
        except Exception:
            return False
