import unittest
from lbkit.helper import SigInvalidException, validate_glib_signature

class TestSignatureValidateClass(unittest.TestCase):
    def test_validate_glib_signature_b(self):
        validate_glib_signature("b")
        validate_glib_signature("ab")
        validate_glib_signature("bbb")
        validate_glib_signature("{bb}")
        validate_glib_signature("{bb}bbabaab")
        validate_glib_signature("({bb}bbabaab()(b))")
        validate_glib_signature("a{sb}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_y(self):
        validate_glib_signature("y")
        validate_glib_signature("ay")
        validate_glib_signature("yyy")
        validate_glib_signature("{yy}")
        validate_glib_signature("{yy}yyayaay")
        validate_glib_signature("({yy}yyayaay()(y))")
        validate_glib_signature("a{sy}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_n(self):
        validate_glib_signature("n")
        validate_glib_signature("an")
        validate_glib_signature("nnn")
        validate_glib_signature("{nn}")
        validate_glib_signature("{nn}nnanaan")
        validate_glib_signature("({nn}nnanaan()(n))")
        validate_glib_signature("a{sn}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_q(self):
        validate_glib_signature("q")
        validate_glib_signature("aq")
        validate_glib_signature("qqq")
        validate_glib_signature("{qq}")
        validate_glib_signature("{qq}qqaqaaq")
        validate_glib_signature("({qq}qqaqaaq()(q))")
        validate_glib_signature("a{sq}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_i(self):
        validate_glib_signature("i")
        validate_glib_signature("ai")
        validate_glib_signature("iii")
        validate_glib_signature("{ii}")
        validate_glib_signature("{ii}iiaiaai")
        validate_glib_signature("({ii}iiaiaai()(i))")
        validate_glib_signature("a{si}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_u(self):
        validate_glib_signature("u")
        validate_glib_signature("au")
        validate_glib_signature("uuu")
        validate_glib_signature("{uu}")
        validate_glib_signature("{uu}uuauaau")
        validate_glib_signature("({uu}uuauaau()(u))")
        validate_glib_signature("a{su}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_x(self):
        validate_glib_signature("x")
        validate_glib_signature("ax")
        validate_glib_signature("xxx")
        validate_glib_signature("{xx}")
        validate_glib_signature("{xx}xxaxaax")
        validate_glib_signature("({xx}xxaxaax()(x))")
        validate_glib_signature("a{sx}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_t(self):
        validate_glib_signature("t")
        validate_glib_signature("at")
        validate_glib_signature("ttt")
        validate_glib_signature("{tt}")
        validate_glib_signature("{tt}ttataat")
        validate_glib_signature("({tt}ttataat()(t))")
        validate_glib_signature("a{st}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_d(self):
        validate_glib_signature("d")
        validate_glib_signature("ad")
        validate_glib_signature("ddd")
        validate_glib_signature("{dd}")
        validate_glib_signature("{dd}ddadaad")
        validate_glib_signature("({dd}ddadaad()(d))")
        validate_glib_signature("a{sd}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_h(self):
        validate_glib_signature("h")
        validate_glib_signature("ah")
        validate_glib_signature("hhh")
        validate_glib_signature("{hh}")
        validate_glib_signature("{hh}hhahaah")
        validate_glib_signature("({hh}hhahaah()(h))")
        validate_glib_signature("a{sh}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_s(self):
        validate_glib_signature("s")
        validate_glib_signature("as")
        validate_glib_signature("sss")
        validate_glib_signature("{ss}")
        validate_glib_signature("{ss}ssasaas")
        validate_glib_signature("({ss}ssasaas()(s))")
        validate_glib_signature("a{ss}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_g(self):
        validate_glib_signature("g")
        validate_glib_signature("ag")
        validate_glib_signature("ggg")
        validate_glib_signature("{gg}")
        validate_glib_signature("{gg}ggagaag")
        validate_glib_signature("({gg}ggagaag()(g))")
        validate_glib_signature("a{sg}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")
    def test_validate_glib_signature_o(self):
        validate_glib_signature("o")
        validate_glib_signature("ao")
        validate_glib_signature("ooo")
        validate_glib_signature("{oo}")
        validate_glib_signature("{oo}ooaoaao")
        validate_glib_signature("({oo}ooaoaao()(o))")
        validate_glib_signature("a{so}")
        validate_glib_signature("(b)")
        validate_glib_signature("a(b)")
        validate_glib_signature("a(sb)")

    def test_validate_glib_signature(self):
        validate_glib_signature("()")
        validate_glib_signature("(ss)")
        validate_glib_signature("(aaaaaaaaaaaaaaaaaaaaaay)")
        validate_glib_signature("aaaaaaaaaaaaaaaaaaaaaay")
        validate_glib_signature("{saaaaaaaaaaaaaaaaaaaaaay}")

    def test_validate_glib_signature_failed(self):
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("a")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("aaa")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{b}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ayy}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{b}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ab}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{aby}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{y}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ay}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ayy}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{n}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{an}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{any}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{q}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{aq}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{aqy}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{i}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ai}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{aiy}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{u}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{au}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{auy}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{x}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ax}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{axy}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{t}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{at}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{aty}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{d}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ad}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ady}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{h}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ah}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ahy}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{s}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{as}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{asy}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{o}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ao}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{aoy}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{g}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{ag}")
        with self.assertRaises(SigInvalidException):
            validate_glib_signature("{agy}")

if __name__ == "__main__":
    unittest.main()