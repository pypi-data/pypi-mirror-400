import re

from teklia_toolbox.xml import XmlElement

CSS_RULES_REGEX = re.compile(r"(\S+)\s*{([^}]+)}")
CSS_PROPERTIES_REGEX = re.compile(r"(\S+?):\s*(\S+?);")
CSS_ESCAPE_REGEX = re.compile(r"\\u([0-9a-f]{4})", re.IGNORECASE)


def unescape_css_string(value):
    """
    Remove Transkribus' "CSS escapes": \\u followed by 4 characters to denote Unicode characters.
    https://gitlab.com/readcoop/transkribus/TranskribusCore/-/blob/f2deecaa1233126070e64ccc4e1eaa48d905fd11/src/main/java/eu/transkribus/core/model/beans/customtags/CssSyntaxTag.java#L29-49
    """
    return CSS_ESCAPE_REGEX.sub(lambda match: chr(int(match.group(1), 16)), value)


class Tag:
    def __init__(self, name, value):
        self.name = name
        if isinstance(value, dict):
            self.__dict__.update(value)
        for match in CSS_PROPERTIES_REGEX.finditer(value):
            prop_name, prop_value = match.groups()
            # Some special characters are escaped using \uXXXX; this unescapes them
            prop_value = unescape_css_string(prop_value)
            setattr(self, prop_name, prop_value)

    def as_dict(self):
        return self.__dict__

    @classmethod
    def build(cls, text):
        if not text:
            return []
        tags = []
        for match in CSS_RULES_REGEX.finditer(text):
            tags.append(cls(*match.groups()))
        return tags


class PageXmlElement(XmlElement):
    def __init__(self, path):
        super().__init__(path)
        nsmap = set(
            [
                self.element.nsmap.get(idx)
                for idx in self.element.nsmap
                if self.element.nsmap.get(idx).startswith(
                    "http://schema.primaresearch.org/PAGE/gts/pagecontent/"
                )
            ]
        )
        if len(nsmap) == 1:
            self.namespaces = {"page": list(nsmap)[0]}
        elif len(nsmap) > 1:
            raise Exception("can't manage different versions at the same time")
        else:
            raise Exception("There are no URLs, the PAGE namespace is missing")
        self._data = self.parse()


class Region(PageXmlElement):
    optional = ("custom",)

    def get_points(self, path):
        text = self._find(path)
        if text is None:
            # if Coords doesn't have a points attribute we check if it
            # has Point elements as children, to support versions of PAGE
            # prior to 2013-07-15

            points = []
            list_x = self._find("page:Coords/page:Point/@x", many=True)
            list_y = self._find("page:Coords/page:Point/@y", many=True)
            if list_x is None or list_y is None:
                return
            assert len(list_x) == len(
                list_y
            ), "the list of x and y coordinates do not have the same lengths"
            for x, y in zip(list_x, list_y, strict=True):
                points.append((int(x), int(y)))
            return points
        else:
            points = []
            for coords in filter(None, map(str.strip, text.split(" "))):
                x, y = coords.split(",", 1)
                points.append((int(x), int(y)))
            return points

    def parse(self):
        return {
            "id": self.get_text("@id"),
            "points": self.get_points("page:Coords/@points"),
            "tags": Tag.build(self.get_text("@custom")),
        }


class TextLine(Region):
    optional = Region.optional + ("confidence",)

    def parse(self):
        data = super().parse()
        data.update(
            text=self.get_text("page:TextEquiv/page:Unicode"),
            baseline=self.get_points("page:Baseline/@points"),
            confidence=self.get_float("page:TextEquiv/@conf"),
        )
        return data


class TextRegion(Region):
    optional = Region.optional + ("type", "confidence")

    def parse(self):
        data = super().parse()
        data.update(
            type=self.get_text("@type"),
            text=self.get_text("page:TextEquiv/page:Unicode"),
            confidence=self.get_float("page:TextEquiv/@conf"),
            lines=self.get_instance(TextLine, "page:TextLine", many=True),
        )
        return data


class GraphicRegion(Region):
    optional = Region.optional + ("type",)

    def parse(self):
        data = super().parse()
        data.update(type=self.get_text("@type"))
        return data


class PageElement(PageXmlElement):
    optional = ("type",)

    def get_ordering(self):
        return [
            ref.get("regionRef")
            for ref in sorted(
                self._find(
                    "page:ReadingOrder/page:OrderedGroup/page:RegionRefIndexed",
                    many=True,
                ),
                key=lambda elt: int(elt.get("index")),
            )
        ]

    def get_relations(self):
        relations = []
        for relation in self._find(
            'page:Relations/page:Relation[@type="link"]', many=True
        ):
            refs = relation.findall("page:RegionRef", namespaces=self.namespaces)
            assert (
                len(refs) >= 2
            ), f"Expected at least two regions in relation, got {len(refs)}"
            relations.append([ref.get("regionRef") for ref in refs])
        return relations

    def parse(self):
        return {
            "image_name": self.get_text("@imageFilename"),
            "image_width": self.get_text("@imageWidth"),
            "image_height": self.get_text("@imageHeight"),
            "type": self.get_text("@type"),
            "text_regions": self.get_instance(TextRegion, "page:TextRegion", many=True),
            "separator_regions": self.get_instance(
                Region, "page:SeparatorRegion", many=True
            ),
            "table_regions": self.get_instance(Region, "page:TableRegion", many=True),
            "graphic_regions": self.get_instance(
                GraphicRegion, "page:GraphicRegion", many=True
            ),
            "music_regions": self.get_instance(Region, "page:MusicRegion", many=True),
            "noise_regions": self.get_instance(Region, "page:NoiseRegion", many=True),
            "unknown_regions": self.get_instance(
                Region, "page:UnknownRegion", many=True
            ),
            "ordering": self.get_ordering(),
            "relations": self.get_relations(),
        }

    def sort_regions(self, regions):
        if len(regions) <= 1 or not self.ordering:
            return regions
        return sorted(
            regions,
            key=lambda region: self.ordering.index(region.id)
            if region.id in self.ordering
            else 0,
        )


class TranskribusMetadata(PageXmlElement):
    def parse(self):
        return {
            "doc_id": self.get_int("@docId"),
            "page_id": self.get_int("@pageId"),
            "page_number": self.get_int("@pageNr"),
            "status": self.get_text("@status"),
        }


class PageXmlMetadata(PageXmlElement):
    optional = ("comments",)

    def parse(self):
        return {
            "creator": self.get_text("page:Creator"),
            "created": self.get_text("page:Created"),
            "last_change": self.get_text("page:LastChange"),
            "comments": self.get_text("page:Comments"),
            "transkribus_metadata": self.get_instance(
                TranskribusMetadata, "page:TranskribusMetadata"
            ),
        }


class PageXmlPage(PageXmlElement):
    def parse(self):
        return {
            "metadata": self.get_instance(PageXmlMetadata, "page:Metadata"),
            "page": self.get_instance(PageElement, "page:Page"),
        }
