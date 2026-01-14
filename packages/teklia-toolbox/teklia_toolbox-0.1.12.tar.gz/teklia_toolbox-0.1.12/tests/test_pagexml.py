from pathlib import Path

import pytest

from teklia_toolbox.pagexml import PageXmlPage

SAMPLES = Path(__file__).parent / "samples"


def test_simple():
    page_xml = PageXmlPage(SAMPLES / "simple.xml")

    assert page_xml.metadata.creator == "TRP"
    assert page_xml.metadata.created == "2017-07-19T13:58:10.738+02:00"
    assert page_xml.metadata.last_change == "2017-07-19T14:04:22.502+02:00"

    assert page_xml.page.image_name == "FRAN_0021_0023_L.jpg"
    assert page_xml.page.image_width == "3195"
    assert page_xml.page.image_height == "3731"
    assert page_xml.page.ordering == ["TextRegion_1500465748446_12"]
    assert len(page_xml.page.text_regions) == 1

    region = page_xml.page.text_regions[0]
    assert region.id == "TextRegion_1500465748446_12"
    assert region.points == [(2974, 1270), (16, 1270), (18, 105), (2976, 105)]
    assert len(region.tags) == 1
    assert region.tags[0].name == "readingOrder"
    assert region.tags[0].index == "0"


def test_2_regions():
    page_xml = PageXmlPage(SAMPLES / "2_regions.xml")

    assert len(page_xml.page.text_regions) == 2
    assert page_xml.page.ordering == [
        "TextRegion_1522155769847_482",
        "TextRegion_1522155769847_481",
    ]
    region_1, region_2 = page_xml.page.text_regions

    assert region_1.id == "TextRegion_1522155769847_482"
    assert region_2.id == "TextRegion_1522155769847_481"
    assert len(region_1.tags) == 1
    assert region_1.tags[0].name == "readingOrder"
    assert region_1.tags[0].index == "0"
    assert len(region_2.tags) == 1
    assert region_2.tags[0].name == "readingOrder"
    assert region_2.tags[0].index == "1"
    assert region_1.points == [(3509, 1675), (0, 1675), (0, 0), (3509, 0)]
    assert region_2.points == [(3509, 4569), (0, 4569), (0, 1675), (3509, 1675)]

    assert page_xml.page.sort_regions(page_xml.page.text_regions) == [
        region_1,
        region_2,
    ]


def test_no_reading_order():
    page_xml = PageXmlPage(SAMPLES / "no_reading_order.xml")

    assert len(page_xml.page.text_regions) == 3
    assert page_xml.page.ordering == []
    region_1, region_2, region_3 = page_xml.page.text_regions

    assert region_1.id == "TextRegion_1522155769847_482"
    assert region_2.id == "TextRegion_1522155769847_481"
    assert region_3.id == "TextRegion_1522155769847_484"

    assert (
        page_xml.page.sort_regions(page_xml.page.text_regions)
        == page_xml.page.text_regions
    )


def test_unordered():
    page_xml = PageXmlPage(SAMPLES / "unordered.xml")

    assert len(page_xml.page.text_regions) == 3
    assert page_xml.page.ordering == [
        "TextRegion_1522155769847_482",
        "TextRegion_1522155769847_481",
        "TextRegion_1522155769847_484",
    ]

    region_1, region_2, region_3 = page_xml.page.text_regions
    assert region_1.id == "TextRegion_1522155769847_482"
    assert region_2.id == "TextRegion_1522155769847_481"
    assert region_3.id == "TextRegion_1522155769847_484"

    assert page_xml.page.sort_regions(page_xml.page.text_regions) == [
        region_1,
        region_2,
        region_3,
    ]


def test_transcript():
    page_xml = PageXmlPage(SAMPLES / "transcript.xml")

    assert len(page_xml.page.relations) == 1
    assert page_xml.page.relations[0] == [
        "TextRegion_1540299380975_9",
        "TextRegion_1540299473514_23",
    ]
    assert len(page_xml.page.text_regions) == 2
    region_1, region_2 = page_xml.page.text_regions

    assert region_1.id == "TextRegion_1540299380975_9"
    assert region_1.points == [(12, 34), (56, 78), (910, 1112)]
    assert region_1.text == "B .1\nLouis Joseph\nPierre Siméon\nLemieux"
    assert len(region_1.tags) == 2
    assert region_1.tags[0].as_dict() == {
        "name": "readingOrder",
        "index": "0",
    }
    assert region_1.tags[1].as_dict() == {
        "name": "structure",
        "type": "marginalia",
    }

    assert len(region_1.lines) == 4
    line_1, line_2, line_3, line_4 = region_1.lines

    assert line_1.id == "r1l6"
    assert len(line_1.tags) == 2
    assert line_1.tags[0].as_dict() == {
        "name": "readingOrder",
        "index": "0",
    }
    assert line_1.tags[1].as_dict() == {
        "name": "structure",
        "type": "ref",
    }
    assert line_1.points == [(12, 34), (56, 78), (910, 1112)]
    assert line_1.baseline == [(13, 37), (42, 42), (37, 13)]
    assert line_1.text == "B .1"

    assert line_2.id == "r1l7"
    assert len(line_2.tags) == 2
    assert line_2.tags[0].as_dict() == {
        "name": "readingOrder",
        "index": "1",
    }
    assert line_2.tags[1].as_dict() == {
        "name": "_prenom",
        "offset": "0",
        "length": "12",
        "continued": "true",
        "_role": "sujet",
    }
    assert line_2.points == [(12, 34), (56, 78), (910, 1112)]
    assert line_2.baseline == [(13, 37), (42, 42), (37, 13)]
    assert line_2.text == "Louis Joseph"

    assert line_3.id == "r1l8"
    assert len(line_3.tags) == 2
    assert line_3.tags[0].as_dict() == {
        "name": "readingOrder",
        "index": "2",
    }
    assert line_3.tags[1].as_dict() == {
        "name": "_prenom",
        "offset": "0",
        "length": "13",
        "continued": "true",
        "_role": "sujet",
    }
    assert line_3.points == [(12, 34), (56, 78), (910, 1112)]
    assert line_3.baseline == [(13, 37), (42, 42), (37, 13)]
    assert line_3.text == "Pierre Siméon"

    assert line_4.id == "r1l9"
    assert len(line_4.tags) == 2
    assert line_4.tags[0].as_dict() == {
        "name": "readingOrder",
        "index": "3",
    }
    assert line_4.tags[1].as_dict() == {
        "name": "_nom",
        "offset": "0",
        "length": "7",
    }
    assert line_4.points == [(12, 34), (56, 78), (910, 1112)]
    assert line_4.baseline == [(13, 37), (42, 42), (37, 13)]
    assert line_4.text == "Lemieux"

    assert region_2.id == "TextRegion_1540299473514_23"
    assert len(region_2.tags) == 1
    assert region_2.tags[0].as_dict() == {
        "name": "readingOrder",
        "index": "1",
    }
    assert region_2.points == [(12, 34), (56, 78), (910, 1112)]
    assert (
        region_2.text
        == "Le onze janvier mil neuf centsept\nnous prêtre soussigné avons baptisé Louis"
    )
    assert len(region_2.lines) == 2
    line_1, line_2 = region_2.lines

    assert line_1.id == "r2l12"
    assert len(line_1.tags) == 2
    assert line_1.tags[0].as_dict() == {
        "name": "readingOrder",
        "index": "0",
    }
    assert line_1.tags[1].as_dict() == {
        "name": "_date",
        "offset": "3",
        "length": "30",
        "_enregistrement": "1",
    }
    assert line_1.points == [(12, 34), (56, 78), (910, 1112)]
    assert line_1.baseline == [(13, 37), (42, 42), (37, 13)]
    assert line_1.confidence is None
    assert line_1.text == "Le onze janvier mil neuf centsept"

    assert line_2.id == "r2l13"
    assert len(line_2.tags) == 2
    assert line_2.tags[0].as_dict() == {
        "name": "readingOrder",
        "index": "1",
    }
    assert line_2.tags[1].as_dict() == {
        "name": "_prenom",
        "offset": "36",
        "length": "5",
        "continued": "true",
        "_role": "sujet",
    }
    assert line_2.points == [(12, 34), (56, 78), (910, 1112)]
    assert line_2.baseline == [(13, 37), (42, 42), (37, 13)]
    assert line_2.confidence == 0.42
    assert line_2.text == "nous prêtre soussigné avons baptisé Louis"


def test_no_namespace():
    with pytest.raises(
        Exception, match="There are no URLs, the PAGE namespace is missing"
    ):
        PageXmlPage(SAMPLES / "no_namespace.xml")


def test_multiple_versions():
    with pytest.raises(
        Exception, match="can't manage different versions at the same time"
    ):
        PageXmlPage(SAMPLES / "multiple_versions.xml")


def test_different_version():
    page_xml = PageXmlPage(SAMPLES / "different_version.xml")
    assert page_xml.page.image_name == "0_f546b_default.jpg"
    assert page_xml.page.image_width == "3509"
    assert page_xml.page.image_height == "4905"
    assert len(page_xml.page.text_regions) == 1

    region = page_xml.page.text_regions[0]
    assert len(region.lines) == 2
    line_1, line_2 = region.lines
    assert line_1.points == [
        (830, 1479),
        (834, 1389),
        (907, 1373),
        (948, 1389),
        (1006, 1357),
    ]
    assert line_1.baseline == [(830, 1479), (2592, 1467)]
    assert line_1.text == "LA BIBLIOTHÈQUE NATIONALE EN 1984"

    assert line_2.points == [
        (862, 2333),
        (879, 2178),
        (985, 2207),
        (1042, 2190),
        (1100, 2219),
    ]
    assert line_2.baseline == [(862, 2333), (2539, 2333)]
    assert line_2.text == "RAPPORT D'ACTIVITÉ"
