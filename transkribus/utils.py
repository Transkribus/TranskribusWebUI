from collections import Hashable

from prima_page_content import attributes


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

def get_cropped_image_url(url, rect):
    crop = "{x}x{y}x{width}x{height}".format(**rect.as_dict())
    return "{url}&crop={crop}".format(url=url, crop=crop)


class Root: pass
class Child: pass


class mURL(Hashable):

    def __init__(self, string, parent=Root):
        self.string = string.rstrip('/')
        self.parent = parent
        self.separator = '/'

    @property
    def url(self):
        return str(self)

    def is_root(self):
        return self.parent is Root

    def convert(self, maybe_string):
        if type(maybe_string) is not str:
            return str(maybe_string)
        else:
            return maybe_string        

    def create(self, maybe_string, parent=Child):
        if parent is Child:
            parent = self
        return self.__class__(self.convert(maybe_string),
                              parent=parent)

    def concatenate(self, maybe_string):
        suffix = self.convert(maybe_string)
        return self.create(self.string + suffix,
                           parent=self.parent)

    def __getitem__(self, index):
        return self.concatenate(index)

    def __getattr__(self, name):
        # NOTE: if name in members(str) return else create
        # return getattr(self.string, name, self.create(name))
        return self.create(name)

    def __call__(self, *maybe_strings):
        parent = self.parent
        obj = self
        for maybe_string in maybe_strings:
            obj = obj.create(maybe_string, parent=obj)
            parent = obj
        return obj

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        if type(other) is str:
            return other == str(self)
        elif type(other) is self.__class__:
            return self.string == other.string
        else:
            return hash(self) == hash(other)

    def __str__(self):
        strings = [self.string]
        if not self.is_root():
            strings.insert(0, str(self.parent))
        return self.separator.join(strings)

    def __repr__(self):
        return "{}({})".format(self.__class__.name, str(self))

