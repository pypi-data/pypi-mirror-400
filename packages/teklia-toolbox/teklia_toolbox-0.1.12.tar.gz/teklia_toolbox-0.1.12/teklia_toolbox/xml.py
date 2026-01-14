import logging
from abc import ABC, abstractmethod
from pathlib import Path

from lxml import etree

logger = logging.getLogger(__name__)


class XmlElement(ABC):
    optional = ()

    def __init__(self, element):
        self.path = None
        if isinstance(element, str | Path):
            assert Path(element).exists(), f"Invalid path {element}"
            self.path = element
            element = etree.parse(str(element)).getroot()
        assert isinstance(element, etree._Element), "Not an XML element"
        self.element = element
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.parse()
        return self._data

    def __getattr__(self, name):
        if self._data is None or name not in self._data:
            raise AttributeError
        return self._data[name]

    def _find(self, path, many=False):
        result = self.element.xpath(path, namespaces=self.namespaces)
        if isinstance(result, list) and not many:
            if not result:
                return
            return result[0]
        return result

    def get_text(self, path, dump=False):
        child = self._find(path)
        if child is None:
            return None
        elif isinstance(child, str):
            return child

        # Dump full content with children
        if dump:
            return etree.tostring(child, pretty_print=True).decode("utf-8")

        # Simply get inner text
        return child.text

    def get_float(self, path):
        text = self.get_text(path)
        if not text:
            return None
        return float(text)

    def get_int(self, path):
        text = self.get_text(path)
        if not text:
            return None
        return int(text)

    def get_instance(self, cls, path, many=False):
        child = self._find(path, many)
        if child is None:
            return None

        if many:
            return list(cls(item) for item in child)

        return cls(child)

    @abstractmethod
    def parse(self):
        """
        Returns a dict holding parsed data from XML.
        """

    def as_dict(self):
        # Circular dependencies
        from transkribus.pagexml import Tag

        def _dump(value):
            if isinstance(value, XmlElement | Tag):
                return value.as_dict()
            if isinstance(value, list | tuple):
                return list(map(_dump, value))
            return value

        return {name: _dump(value) for name, value in self.data.items()}
