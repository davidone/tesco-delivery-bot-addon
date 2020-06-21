import argparse
import os
import wrap
from unittest import TestCase, mock


class MainTescoAddon(TestCase):
    @mock.patch("subprocess.run")
    def test_check_tesco(self, mock_subprocess_run):
        process_mock = mock.MagicMock(stdout="foo", stderr="bar")
        mock_subprocess_run.return_value = process_mock
        ret_val = wrap.check_tesco("/")
        self.assertEqual(ret_val, [])

        process_mock = mock.MagicMock(stdout="foo\nbar", stderr="")
        mock_subprocess_run.return_value = process_mock
        ret_val = wrap.check_tesco("/")
        self.assertEqual(ret_val, ["foo", "bar"])

    def test_process_tesco(self):
        ret_assert = "2020-07-02T19:00:00.000Z - " "2020-07-02T20:00:00.000Z"
        tesco_list = [
            "  { start: 2020-06-30T18:00:00.000Z, end: 2020-06-30T19:00:00.000Z },",
            "  { start: 2020-07-01T19:00:00.000Z, end: 2020-07-01T20:00:00.000Z },",
            "  { start: 2020-07-02T19:00:00.000Z, end: 2020-07-02T20:00:00.000Z }",
        ]
        days_list = ["2020-07-02"]
        ret_val = wrap.process_tesco(tesco_list, days_list)
        self.assertEqual(ret_val, ret_assert)

    @mock.patch("http.client.HTTPSConnection")
    def test_send_po(self, mock_http_client):
        mock_http_client.return_value.getresponse.return_value = mock.MagicMock(
            status=200
        )
        ret_val = wrap.send_po("foobar")
        self.assertEqual(ret_val, True)

        mock_http_client.return_value.getresponse.return_value = mock.MagicMock(
            status=403
        )
        ret_val = wrap.send_po("foobar")
        self.assertEqual(ret_val, False)

    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(days="2020-07-02", dtb_path="/"),
    )
    def test_argparse(self, mock_argparse):
        ret_val = wrap.main_argparse()
        self.assertEqual(ret_val, ("2020-07-02", "/"))

    @mock.patch.dict(os.environ, {"PO_API_TOKEN": "foo", "PO_USER_KEY": "bar"})
    def test_define_po_keys(self):
        ret_val = wrap.define_po_keys()
        self.assertEqual(ret_val, None)

    @mock.patch.dict(os.environ, {"PO_API_TOKEN": "foo"})
    def test_define_po_keys(self):
        with self.assertRaises(SystemExit) as cm:
            wrap.define_po_keys()
        self.assertEqual(cm.exception.code, 1)

    @mock.patch("time.sleep", side_effect=Exception("whoops"))
    @mock.patch("wrap.send_po")
    @mock.patch("wrap.process_tesco")
    @mock.patch("wrap.check_tesco")
    @mock.patch("wrap.define_po_keys")
    @mock.patch("wrap.main_argparse", return_value=("2020-07-02", "/"))
    def test_main(
        self,
        mock_argparse,
        mock_define_po_keys,
        mock_check_tesco,
        mock_process_tesco,
        mock_send_po,
        mock_time_sleep,
    ):
        with self.assertRaises(Exception) as cm:
            wrap.main()
        self.assertEqual(str(cm.exception), "whoops")
