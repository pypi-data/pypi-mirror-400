import os
import unittest

from aerix_certbot import plugin


class ValidateTokenTests(unittest.TestCase):
    def test_accepts_base64url_token(self):
        token = "aFNw3LyFeBqcBdXabhqgKhfQO4I0dPxututEsXH3umA"
        # Should not raise
        plugin.AerixAuthenticator._validate_token(token)

    def test_accepts_padded_ascii_token(self):
        token = "abcdEFGH1234567890-_="
        plugin.AerixAuthenticator._validate_token(token)

    def test_rejects_path_separators(self):
        with self.assertRaises(plugin.errors.PluginError):
            plugin.AerixAuthenticator._validate_token("valid/../../token")

    def test_rejects_absolute_path(self):
        with self.assertRaises(plugin.errors.PluginError):
            plugin.AerixAuthenticator._validate_token(os.path.join(os.sep, "token"))

    def test_rejects_whitespace(self):
        with self.assertRaises(plugin.errors.PluginError):
            plugin.AerixAuthenticator._validate_token(" token\n")

    def test_rejects_non_ascii(self):
        with self.assertRaises(plugin.errors.PluginError):
            plugin.AerixAuthenticator._validate_token("tøken")


if __name__ == "__main__":
    unittest.main()
