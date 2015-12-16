#!/usr/bin/python
from builder import Builder, Field
from unittest import TestCase

PACKET_DEF_PATH = "dhcp/request.pkt"
TMPL_TWO_FIELDS = "foo[1], foe[2]"
TMPL_TOKEN = "foo[1]"


class BuilderTests(TestCase):
    def test_set_template(self):
        b = Builder()

        b.set_template(TMPL_TWO_FIELDS)

        self.assertEqual(TMPL_TWO_FIELDS, b.template)

    def test_correct_number_of_fields(self):
        b = Builder()

        b.set_template(TMPL_TWO_FIELDS)
        b.prepare()

        self.assertEqual(2, b.count())

    def test_correct_names_of_fields(self):
        b = Builder()

        b.set_template(TMPL_TWO_FIELDS)
        b.prepare()

        fields = b.get_fields()

        self.assertEqual(2, len(fields))
        self.assertTrue("foo" in fields)
        self.assertTrue("foe" in fields)

    def test_correct_sizes_of_fields(self):
        b = Builder()

        b.set_template(TMPL_TWO_FIELDS)
        b.prepare()

        fields = b.get_fields()

        self.assertEqual(1, fields["foo"].size)
        self.assertEqual(2, fields["foe"].size)

    def test_is_correct(self):
        b = Builder()
        b.set_template(TMPL_TWO_FIELDS)
        b.prepare()
        self.assertFalse(b.is_correct())

        b = Builder()
        b.set_template("foo[1] = 128")
        b.prepare()
        self.assertTrue(b.is_correct())

        b = Builder()
        b.set_template("foo[1] = 0, foe[2], bar[1] = 2")
        b.prepare()
        self.assertFalse(b.is_correct())

        b.fields["foe"].value = 3
        self.assertTrue(b.is_correct())

    def test_get_raw(self):
        b = Builder()
        b.set_template("foo[1] = 1, foe[2] = 2")
        b.prepare()

        self.assertTrue(b.is_correct())

        target = "\x01\x00\x02"
        self.assertEqual(target, b.get_raw())


class FieldTests(TestCase):
    def test_create_from_token(self):
        f = Field(TMPL_TOKEN)

        self.assertEqual("foo", f.name)
        self.assertEqual(1, f.size)

    def test_default_value(self):
        f = Field("foo[1] = 0x01")
        self.assertEqual(0x01, f.value)

        f = Field("foo[1] = 0b101")
        self.assertEqual(5, f.value)

        f = Field("foo[1] = 18")
        self.assertEqual(18, f.value)

    def test_to_string(self):
        f = Field("foo[1]=      128")
        s = "foo[1] = 0x80"
        self.assertEqual(s, str(f))

        f = Field("foo[1]")
        s = "foo[1] = None"
        self.assertEqual(s, str(f))

    def test_get_raw(self):
        f = Field("foo[4] = 0xABCDEF")
        raw = f.get_raw()
        target = "\x00\xAB\xCD\xEF"
        self.assertEqual(target, raw)

        f = Field("foo[1] = 0xABCDEF")
        raw = f.get_raw()
        target = "\xEF"
        self.assertEqual(target, raw)

    def test_long_fields(self):
        f = Field("foo[16] = 0x11111111 22222222 33333333 44444444")
        raw = f.get_raw()
        target = "\x11"*4 + "\x22"*4 + "\x33"*4 + "\x44"*4
        self.assertEqual(target, raw)
