#!/usr/bin/python
import struct


class BadFormatException(Exception):
    pass


class Field:
    """
    This is single field in the packet
    It has name, length and default value
    """
    name = None
    size = None
    value = None

    def __init__(self, token):
        size_start = token.find('[')
        size_end = token.find(']')
        default_start = token.find('=')

        if size_start == -1 or size_end == -1:
            raise BadFormatException

        self.name = token[:size_start]

        try:
            self.size = int(token[size_start+1:size_end])
        except:
            raise BadFormatException

        if default_start != -1:
            base = 10

            default = token[default_start+1:]

            if default[:2] == '0x':
                base = 16
            elif default[:2] == '0b':
                base = 2

            self.value = int(default, base)

    def __str__(self):
        s = "{name}[{size}] = "

        if self.value:
            s += "0x{value:x}"
        else:
            s += "{value}"

        d = {
            'name': self.name,
            'size': self.size,
            'value': self.value,
            }

        return s.format(**d)

    def get_raw(self):
        hs = "{:0" + str(self.size*2) + "x}"
        hs = hs.format(self.value)
        b = [hs[i:i+2] for i in range(0, len(hs), 2)]
        i = [int(bi, 16) for bi in b]
        fmt = '!' + 'B'*len(i)

        return struct.pack(fmt, *i)[-self.size:]


class Builder:
    """
    Pass this class a template,
    and it will create a builder for that packet type
    """
    def __init__(self, template=None):
        self.__common_init()
        self.set_template(template)

    def __common_init(self):
        self.fields = {}
        self.tokens = None
        self.order = []

    def set_template(self, template):
        template = template.replace(' ', '')
        self.template = template
        self.prepare()

    def prepare(self):
        if self.tokens == '' or self.template is None:
            return

        self.__common_init()
        self.tokens = self.template.split(',')

        line = 1

        try:
            for token in self.tokens:
                if '\n' in token:
                    line += 1
                    token = token.replace('\n', '')

                f = Field(token)
                self.fields[f.name] = f
                self.order.append(f.name)
        except BadFormatException:
            self.__common_init()
            print("Failed to read {} at line {}".format(token, line))

    def count(self):
        return len(self.tokens)

    def get_fields(self):
        return self.fields

    def is_correct(self):
        values = [field.value for field in self.fields.itervalues()]
        return None not in values

    def get_raw(self):
        r = "".join([self.fields[i].get_raw() for i in self.order])
        return r
