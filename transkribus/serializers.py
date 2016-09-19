# XXX FIXTHIS use rest_framework-like Serializers here

import functools

from eulxml import xmlmap

from prima_page_content import attributes

from rest_framework import serializers


NAMESPACE = 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'


def points_from_string(points_string):
    return attributes.Points.from_string(points_string)

def rect_from_string(points_string):
    points = points_from_string(points_string)
    return points.rect

def tokenize(text, punct=False):

    abbreviations = frozenset([
        'hr', 'prof', 'bsp', 'dh'
    ])

    def split_punct(token):
        if punct is False:
            if token[-1] in (',', '.', '-', ':', ';'):
                return (token[:-1], )
            else:
                return (token, )
        elif len(token) <= 1:
            return (token, )
        elif token.endswith(','):
            return (token[:-1], token[-1])
        elif token.endswith('.'):
            if token[:-1].lower() not in abbreviations:
                return (token[:-1], token[-1])
            else:
                return (token, )
        elif token.endswith('-'):
            return (token[:-1], token[-1])
        else:
            return (token, )

    def concat_token(token_1, token_2):
        return token_1 + token_2

    tokens = [token for token in text.split(' ') if token not in ('', )]
    return functools.reduce(concat_token, map(split_punct, tokens))

def tokenize_line(obj):
    return tokenize(obj.text or '')


class IterableMixin:

    @property
    def children(self):
        raise NotImplementedError

    def __iter__(self):
        return iter(self.children)


# class DeserializeMixin:
#     @classmethod
#     def deserialize(cls, fileobj):
#         return xmlmap.load_xmlobject_from_file(
#             fileobj, xmlclass=cls
#         )


# class PageElement(DeserializeMixin, xmlmap.XmlObject):
class PageElement(xmlmap.XmlObject):
    ROOT_NS = NAMESPACE
    ROOT_NAME = 'PcGts'
    ROOT_NAMESPACES = {'pc': ROOT_NS}

    def __repr__(self):
        return "<{!s}: {!s}>".format(self.__class__.__name__, str(self))


# class MetaData(DeserializeMixin, xmlmap.XmlObject):
class MetaData(xmlmap.XmlObject):

    def __repr__(self):
        return "<{!s}: {!s}>".format(self.__class__.__name__, str(self))


class Collection(MetaData):
    id = xmlmap.IntegerField('colId', required=True)
    name = xmlmap.StringField('colName', required=True)
    role = xmlmap.StringField('role', required=True)
    description = xmlmap.StringField('description', required=True)

    def __str__(self):
        return "{!s}".format(self.id)


class CollectionList(IterableMixin, MetaData):
    collections = xmlmap.NodeListField(
        '/trpCollections/trpCollection', Collection)

    @property
    def children(self):
        return self.collections

    def __str__(self):
        return "{!s}".format(self.collections)


class Document(MetaData):
    id = xmlmap.IntegerField('docId')
    title = xmlmap.StringField('title')
    num_pages = xmlmap.IntegerField('nrOfPages')
    uploader = xmlmap.StringField('uploader')
    # uploaded_at = xmlmap.IntegerField('uploadTimestamp')

    def __str__(self):
        return "{!s}".format(self.id)


class DocumentList(IterableMixin, MetaData):
    documents = xmlmap.NodeListField(
        "/trpDocMetadatas/trpDocMetadata", Document)

    @property
    def children(self):
        return self.documents


class TextArea(PageElement):
    id = xmlmap.StringField('@id')
    text = xmlmap.StringField('pc:TextEquiv/pc:Unicode')
    coords = xmlmap.NodeField('pc:Coords/@points', points_from_string)
    rect = xmlmap.NodeField('pc:Coords/@points', rect_from_string)

    # def __str__(self):
    #     return '{!s}: "{!s}"'.format(self.id, self.text)


class Word(PageElement):
    id = xmlmap.StringField('@id')
    text = xmlmap.StringField('pc:TextEquiv/pc:Unicode')


class Line(PageElement):
    id = xmlmap.StringField('@id')
    rect = xmlmap.NodeField('pc:Coords/@points', rect_from_string)
    text = xmlmap.StringField('pc:TextEquiv/pc:Unicode')
    # tokens = xmlmap.NodeField('pc:TextEquiv/pc:Unicode', tokenize)
    words = xmlmap.NodeListField('pc:Word', Word)
    # coords = xmlmap.NodeField('pc:Coords/@points', points_from_string)
    # baseline = xmlmap.NodeField('pc:Baseline/@points', points_from_string)

    @property
    def children(self):
        return self.words

    # def __str__(self):
    #     return '{!s}: "{!s}"'.format(self.id, self.text)


class Page(IterableMixin, PageElement):
    created = xmlmap.DateTimeField('pc:Metadata/pc:Created')
    lines = xmlmap.NodeListField('.//pc:TextLine', Line)

    @property
    def children(self):
        return self.lines


def CollectionSerializer(fileobj):
    obj = xmlmap.load_xmlobject_from_file(
        fileobj, xmlclass=CollectionList
    )
    assert obj.is_valid()
    return obj


def DocumentSerializer(fileobj):
    obj = xmlmap.load_xmlobject_from_file(
        fileobj, xmlclass=DocumentList
    )
    assert obj.is_valid()
    return obj


def PageSerializer(fileobj):
    page = xmlmap.load_xmlobject_from_file(
        fileobj, xmlclass=Page
    )
    return page


class CollectionSerializer_(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    role = serializers.CharField()
    # description = serializers.CharField()        


class DocumentSerializer_(serializers.Serializer):
    id = serializers.IntegerField()
    # collection_id = serializers.IntegerField()
    title = serializers.CharField()
    num_pages = serializers.IntegerField()
    uploader = serializers.CharField()
    # uploaded_at = serializers.IntegerField()


def get_cropped_image_url(url, rect):
    crop = "{x}x{y}x{width}x{height}".format(**rect.as_dict())
    return "{url}&crop={crop}".format(url=url, crop=crop)


class CoordsField(serializers.Field):
    def to_representation(self, value):
        return list(list(item.as_tuple()) for item in value)


class RectField(serializers.Field):
    def to_representation(self, value):
        return value.as_dict()


class ItemIdentifierSerializer(serializers.Serializer):
    collection_id = serializers.IntegerField()
    document_id = serializers.IntegerField()
    page_id = serializers.IntegerField()
    region_id = serializers.CharField(required=False)
    line_id = serializers.CharField()
    word_id = serializers.CharField()


class LineSerializer(serializers.Serializer):
    # baseline = CoordsField()
    rect = RectField(required=False)
    url = serializers.CharField()
    # url = serializers.SerializerMethodField()

    # def get_url(self, obj):
    #     return get_cropped_image_url(obj.url, obj.rect)


class WordSerializer(serializers.Serializer):
    item_id = ItemIdentifierSerializer(source='id')
    expected = serializers.IntegerField(source='index')
    image = LineSerializer(source='line')
    text = serializers.CharField(source='line.text')
    tokens = serializers.ListSerializer(
        source='line.tokens',
         child=serializers.CharField()
    )
    # tokens = serializers.DictField()
    expected_token = serializers.SerializerMethodField()

    def get_expected_token(self, obj):
        return obj.line.tokens[obj.index]
