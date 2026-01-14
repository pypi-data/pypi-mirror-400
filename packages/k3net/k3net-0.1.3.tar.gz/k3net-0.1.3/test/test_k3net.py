import unittest


import k3net
import k3ut

dd = k3ut.dd


class TestNet(unittest.TestCase):
    def test_const(self):
        self.assertEqual("PUB", k3net.PUB)
        self.assertEqual("INN", k3net.INN)

        self.assertEqual("127.0.0.1", k3net.LOCALHOST)

    def test_exception(self):
        [k3net.NetworkError, k3net.IPUnreachable]

    def test_is_ip4_false(self):
        cases_not_ip4 = (
            None,
            True,
            False,
            1,
            0,
            "",
            "1",
            (),
            [],
            {},
            "1.",
            "1.1",
            "1.1.",
            "1.1.1",
            "1.1.1.",
            ".1.1.1",
            "x.1.1.1",
            "1.x.1.1",
            "1.1.x.1",
            "1.1.1.x",
            "1.1.1.1.",
            ".1.1.1.1",
            "1:1.1.1",
            "1:1:1.1",
            "256.1.1.1",
            "1.256.1.1",
            "1.1.256.1",
            "1.1.1.256",
            "1.1.1.1.",
            "1.1.1.1.1",
            "1.1.1.1.1.",
            "1.1.1.1.1.1",
        )

        for inp in cases_not_ip4:
            self.assertEqual(False, k3net.is_ip4(inp), inp)

    def test_is_ip4_true(self):
        cases_ip4 = (
            "0.0.0.0",
            "0.0.0.1",
            "0.0.1.0",
            "0.1.0.0",
            "1.0.0.0",
            "127.0.0.1",
            "255.255.255.255",
        )

        for inp in cases_ip4:
            self.assertEqual(True, k3net.is_ip4(inp), inp)

    def test_is_ip4_loopback_false(self):
        cases_ip4 = (
            "0.0.0.0",
            "1.1.1.1",
            "126.0.1.0",
            "15.1.0.0",
            "255.0.0.255",
            "126.0.0.1",
            "128.0.0.1",
            "255.255.255.255",
        )

        for ip in cases_ip4:
            self.assertEqual(False, k3net.is_ip4_loopback(ip), ip)

    def test_is_ip4_loopback_true(self):
        cases_ip4 = (
            "127.0.0.0",
            "127.1.1.1",
            "127.0.1.0",
            "127.1.0.0",
            "127.0.0.255",
            "127.0.0.1",
            "127.255.255.255",
        )

        for ip in cases_ip4:
            self.assertEqual(True, k3net.is_ip4_loopback(ip), ip)

    def test_ip_class_and_is_xxx(self):
        self.assertRaises(ValueError, k3net.choose_ips, ["192.168.0.0"], "xx")

        cases_pub = (
            "1.2.3.4",
            "255.255.0.0",
            "171.0.0.0",
            "173.0.0.0",
            "172.15.0.0",
            "172.32.0.0",
            "9.0.0.0",
            "11.0.0.0",
            "192.167.0.0",
            "192.169.0.0",
            "191.168.0.0",
            "193.168.0.0",
        )

        for inp in cases_pub:
            self.assertEqual(k3net.PUB, k3net.ip_class(inp), inp)

            # test is_xxx
            self.assertEqual(True, k3net.is_pub(inp))
            self.assertEqual(False, k3net.is_inn(inp))

            # test choose_xxx
            self.assertEqual([inp], k3net.choose_pub([inp, "192.168.0.0"]))
            self.assertEqual([inp], k3net.choose_pub(["192.168.0.0", inp]))

            self.assertEqual([inp], k3net.choose_ips([inp, "192.168.0.0"], k3net.PUB))
            self.assertEqual([inp], k3net.choose_ips(["192.168.0.0", inp], k3net.PUB))
            self.assertEqual([inp, "192.168.0.0"], k3net.choose_ips([inp, "192.168.0.0"]))
            self.assertEqual(["192.168.0.0", inp], k3net.choose_ips(["192.168.0.0", inp]))

        cases_inn = (
            "127.0.0.1",
            "127.0.0.255",
            "172.16.0.0",
            "172.17.0.0",
            "172.21.0.0",
            "172.30.0.0",
            "172.31.0.0",
            "10.0.0.0",
            "192.168.0.0",
        )

        for inp in cases_inn:
            self.assertEqual(k3net.INN, k3net.ip_class(inp), inp)

            # test is_xxx

            self.assertEqual(True, k3net.is_inn(inp))
            self.assertEqual(False, k3net.is_pub(inp))

            # test choose_xxx
            self.assertEqual([inp], k3net.choose_inn([inp, "1.1.1.1"]))
            self.assertEqual([inp], k3net.choose_inn(["1.1.1.1", inp]))

            self.assertEqual([inp], k3net.choose_ips([inp, "1.1.1.1"], k3net.INN))
            self.assertEqual([inp], k3net.choose_ips(["1.1.1.1", inp], k3net.INN))
            self.assertEqual([inp, "1.1.1.1"], k3net.choose_ips([inp, "1.1.1.1"]))
            self.assertEqual(["1.1.1.1", inp], k3net.choose_ips(["1.1.1.1", inp]))

    def test_ips_prefer(self):
        cases = (
            ([], k3net.PUB, []),
            ([], k3net.INN, []),
            (["1.2.3.4"], k3net.PUB, ["1.2.3.4"]),
            (["1.2.3.4"], k3net.INN, ["1.2.3.4"]),
            (["172.16.0.1"], k3net.PUB, ["172.16.0.1"]),
            (["172.16.0.1"], k3net.INN, ["172.16.0.1"]),
            (["172.16.0.1", "1.2.3.4"], k3net.PUB, ["1.2.3.4", "172.16.0.1"]),
            (["172.16.0.1", "1.2.3.4"], k3net.INN, ["172.16.0.1", "1.2.3.4"]),
            (["1.2.3.4", "172.16.0.1"], k3net.PUB, ["1.2.3.4", "172.16.0.1"]),
            (["1.2.3.4", "172.16.0.1"], k3net.INN, ["172.16.0.1", "1.2.3.4"]),
        )

        for inp_ips, inp_class, outp in cases:
            self.assertEqual(outp, k3net.ips_prefer(inp_ips, inp_class))

    def test_ips_prefer_by_idc(self):
        cases = (
            ("a", "a", [], []),
            ("a", "a", ["1.1.1.1"], ["1.1.1.1"]),
            ("a", "a", ["172.16.0.0"], ["172.16.0.0"]),
            ("a", "a", ["172.16.0.0", "1.1.1.1"], ["172.16.0.0", "1.1.1.1"]),
            ("a", "a", ["1.1.1.1", "172.16.0.0"], ["172.16.0.0", "1.1.1.1"]),
            ("a", "b", [], []),
            ("a", "b", ["1.1.1.1"], ["1.1.1.1"]),
            ("a", "b", ["172.16.0.0"], ["172.16.0.0"]),
            ("a", "b", ["172.16.0.0", "1.1.1.1"], ["1.1.1.1", "172.16.0.0"]),
            ("a", "b", ["1.1.1.1", "172.16.0.0"], ["1.1.1.1", "172.16.0.0"]),
        )

        for idc_a, idc_b, ips, outp in cases:
            self.assertEqual(outp, k3net.choose_by_idc(idc_a, idc_b, ips))

    def test_get_host_ip4(self):
        ips = k3net.get_host_ip4(iface_prefix="")
        self.assertNotEqual([], ips)

        for ip in ips:
            self.assertIsInstance(ip, str)
            self.assertTrue(k3net.is_ip4(ip))

        ips2 = k3net.get_host_ip4(exclude_prefix="")
        self.assertEqual([], ips2, "exclude any")

        self.assertEqual(ips, k3net.get_host_ip4(exclude_prefix=[]), "exclude nothing")

        self.assertEqual(ips, k3net.get_host_ip4(exclude_prefix=None), "exclude nothing")

    def test_get_host_devices(self):
        # TODO can not test
        k3net.get_host_devices(iface_prefix="")

    def test_parse_ip_regex_str(self):
        cases = (
            ("1.2.3.4", ["1.2.3.4"]),
            ("1.2.3.4,127.0.", ["1.2.3.4", "127.0."]),
            ("-1.2.3.4,127.0.", [("1.2.3.4", False), "127.0."]),
            ("-1.2.3.4,-127.0.", [("1.2.3.4", False), ("127.0.", False)]),
        )

        for inp, outp in cases:
            self.assertEqual(outp, k3net.parse_ip_regex_str(inp))

        cases_err = (
            "",
            ",",
            " , ",
            "1,",
            ",1",
            "-1,",
            ",-1",
            "127,-",
            "-,127",
        )
        for inp in cases_err:
            dd("should fail with: ", repr(inp))

            try:
                k3net.parse_ip_regex_str(inp)
                self.fail("should fail with " + repr(inp))
            except ValueError:
                pass

    def test_choose_ips_regex(self):
        cases = (
            (["127.0.0.1", "192.168.0.1"], ["127[.]"], ["127.0.0.1"]),
            (["127.0.0.1", "192.168.0.1"], ["2"], []),
            (["127.0.0.1", "192.168.0.1"], ["[.]"], []),
            (["127.0.0.1", "192.168.0.1"], ["1"], ["127.0.0.1", "192.168.0.1"]),
            # negative match
            (["127.0.0.1", "192.168.0.1"], [("1", False)], []),
            (["127.0.0.1", "192.168.0.1"], [("127", False), ("192", False)], []),
            (["127.0.0.1", "192.168.0.1"], [("12", False)], ["192.168.0.1"]),
            (["127.0.0.1", "192.168.0.1"], ["22", ("12", False)], []),
        )

        for ips, regs, outp in cases:
            dd("case: ", ips, regs, outp)
            self.assertEqual(outp, k3net.choose_by_regex(ips, regs))

    def test_ip_interconvert_num(self):
        cases_ip4_and_ip4_num = (
            ("127.0.0.1", 0x7F000001),
            ("124.51.31.23", 0x7C331F17),
            ("255.255.255.255", 0xFFFFFFFF),
            ("1.2.3.4", 0x01020304),
            ("5.6.7.8", 0x05060708),
        )

        for ips, out in cases_ip4_and_ip4_num:
            self.assertEqual(out, k3net.ip_to_num(ips))

        for out, ipn in cases_ip4_and_ip4_num:
            self.assertEqual(out, k3net.num_to_ip(ipn))

        cases_not_ip4_and_not_ip4_num = (
            None,
            True,
            False,
            "",
            "1",
            (),
            [],
            {},
            "1.",
            "1.1",
            "1.1.",
            "1.1.1",
            "1.1.1.",
            ".1.1.1",
            "x.1.1.1",
            "1.x.1.1",
            "1.1.x.1",
            "1.1.1.x",
            "1.1.1.1.",
            ".1.1.1.1",
            "1:1.1.1",
            "1:1:1.1",
            "256.1.1.1",
            "1.256.1.1",
            "1.1.256.1",
            "1.1.1.256",
            "1.1.1.1.",
            "1.1.1.1.1",
            "1.1.1.1.1.",
            "1.1.1.1.1.1",
            -10,
            -100,
            -110000000000,
            68719476735,
            "dada",
            "mu",
            1099511627775,
            1.3,
            20.5,
            200.0,
        )
        cases_not_ip4 = (
            1,
            0,
        )

        for ip in cases_not_ip4_and_not_ip4_num:
            self.assertRaises(k3net.InvalidIP4, k3net.ip_to_num, ip)
        for ip in cases_not_ip4:
            self.assertRaises(k3net.InvalidIP4, k3net.ip_to_num, ip)

        for ipn in cases_not_ip4_and_not_ip4_num:
            self.assertRaises(k3net.InvalidIP4Number, k3net.num_to_ip, ipn)

    def test_iner_ip_patterns(self):
        old = k3net.net.inner_ip_patterns

        k3net.net.inner_ip_patterns = ["^172[.]18[.]2[.](3[2-9])$", "^172[.]18[.]2[.](4[0-7])$"]

        case_inner_ip_true = (
            "172.18.2.32",
            "172.18.2.37",
            "172.18.2.47",
        )

        case_inner_ip_false = (
            "172.18.2.31",
            "172.18.2.48",
            "172.18.2.49",
        )

        for inp in case_inner_ip_true:
            self.assertEqual(True, k3net.is_inn(inp))

        for inp in case_inner_ip_false:
            self.assertEqual(False, k3net.is_inn(inp))

        k3net.net.inner_ip_patterns = old
