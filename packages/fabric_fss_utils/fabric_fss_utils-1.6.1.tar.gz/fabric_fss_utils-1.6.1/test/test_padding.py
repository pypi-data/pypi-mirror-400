#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 FABRIC Testbed
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author Komal Thareja (kthare10@renci.org)
import base64
import unittest

from fss_utils.jwt_manager import JWTManager, ValidateCode


class JWTPaddingTest(unittest.TestCase):
    """Tests for JWT base64 padding functionality"""

    def test_add_padding_no_padding_needed(self):
        """Test that strings with length divisible by 4 are not modified"""
        test_string = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"  # len=36, 36 % 4 = 0
        result = JWTManager._add_padding(test_string)
        self.assertEqual(result, test_string)
        self.assertEqual(len(result) % 4, 0)

    def test_add_padding_one_char_needed(self):
        """Test adding one padding character"""
        test_string = "abc"  # len=3, 3 % 4 = 3, needs 1 char
        result = JWTManager._add_padding(test_string)
        self.assertEqual(result, "abc=")
        self.assertEqual(len(result) % 4, 0)
        # Verify it can be decoded
        decoded = base64.urlsafe_b64decode(result)
        self.assertIsNotNone(decoded)

    def test_add_padding_two_chars_needed(self):
        """Test adding two padding characters"""
        test_string = "ab"  # len=2, 2 % 4 = 2, needs 2 chars
        result = JWTManager._add_padding(test_string)
        self.assertEqual(result, "ab==")
        self.assertEqual(len(result) % 4, 0)
        # Verify it can be decoded
        decoded = base64.urlsafe_b64decode(result)
        self.assertIsNotNone(decoded)

    def test_add_padding_jwt_header(self):
        """Test padding a real JWT header"""
        # JWT header: {"alg":"HS256","typ":"JWT"}
        jwt_header = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"  # len=36, already correct
        result = JWTManager._add_padding(jwt_header)
        self.assertEqual(result, jwt_header)
        decoded = base64.urlsafe_b64decode(result)
        self.assertIn(b"HS256", decoded)

    def test_add_padding_jwt_payload(self):
        """Test padding a real JWT payload"""
        # JWT payload: {"sub":"1234567890"}
        jwt_payload = "eyJzdWIiOiIxMjM0NTY3ODkwIn0"  # len=27, needs 1 char
        result = JWTManager._add_padding(jwt_payload)
        self.assertEqual(result, "eyJzdWIiOiIxMjM0NTY3ODkwIn0=")
        self.assertEqual(len(result) % 4, 0)
        decoded = base64.urlsafe_b64decode(result)
        self.assertIn(b"1234567890", decoded)

    def test_encoded_jwt_standard_format(self):
        """Test that JWTs are encoded in standard format (may not have padding)"""
        claims = {"foo": "bar", "user": "test"}
        code, token = JWTManager.encode_and_compress(claims=claims, secret="secret",
                                                     validity=500, compression=False)
        self.assertEqual(code, ValidateCode.VALID)
        self.assertIsNotNone(token)

        # Split JWT into parts
        parts = token.split('.')
        self.assertEqual(len(parts), 3, "JWT should have 3 parts")

        # JWTs use base64url encoding which may omit padding
        # This is standard per RFC 7515
        for i, part in enumerate(parts):
            with self.subTest(part_index=i):
                # Add padding before decoding
                padded_part = JWTManager._add_padding(part)
                try:
                    decoded = base64.urlsafe_b64decode(padded_part)
                    self.assertIsNotNone(decoded)
                except Exception as e:
                    self.fail(f"JWT part {i} should be decodable after padding: {e}")

    def test_decode_jwt_payload_helper(self):
        """Test the decode_jwt_payload helper method"""
        claims = {"foo": "bar", "test": "padding", "user": "john"}
        code, token = JWTManager.encode_and_sign_with_private_key(
            validity=90, claims=claims,
            private_key_file_name="test/data/privkey.pem",
            kid="test-kid", algorithm="RS256"
        )
        self.assertEqual(code, ValidateCode.VALID)
        self.assertIsNotNone(token)

        # Use the decode_jwt_payload helper to decode the payload
        code, payload = JWTManager.decode_jwt_payload(token=token)
        self.assertEqual(code, ValidateCode.VALID)
        self.assertEqual(payload.get("foo"), "bar")
        self.assertEqual(payload.get("test"), "padding")
        self.assertEqual(payload.get("user"), "john")

    def test_decode_handles_unpadded_compressed_token(self):
        """Test that decode can handle unpadded base64 in compressed tokens"""
        claims = {"foo": "bar"}
        code, token = JWTManager.encode_and_compress(claims=claims, secret="secret",
                                                     validity=500, compression=True)
        self.assertEqual(code, ValidateCode.VALID)

        # Remove padding from the compressed token to simulate unpadded input
        unpadded_token = token.rstrip('=')

        # Decode should still work
        code, decoded = JWTManager.decode(cookie=unpadded_token, secret="secret",
                                         verify=True, compression=True)
        self.assertEqual(code, ValidateCode.VALID)
        self.assertEqual(decoded.get("foo"), "bar")

    def test_jwt_can_be_decoded(self):
        """Test that standard JWT can be decoded successfully"""
        claims = {"user": "john", "role": "admin"}
        code, token = JWTManager.encode_and_compress(claims=claims, secret="secret",
                                                     validity=500, compression=False)
        self.assertEqual(code, ValidateCode.VALID)

        # Decode should work with PyJWT
        code, decoded = JWTManager.decode(cookie=token, secret="secret",
                                         verify=True, compression=False)
        self.assertEqual(ValidateCode.VALID, code)
        self.assertEqual(decoded.get("user"), "john")
        self.assertEqual(decoded.get("role"), "admin")

    def test_manual_base64_decode_of_payload(self):
        """Test that JWT payload can be manually decoded with base64 module using padding helper"""
        claims = {"email": "user@example.com", "name": "Test User"}
        code, token = JWTManager.encode_and_compress(claims=claims, secret="secret",
                                                     validity=500, compression=False)
        self.assertEqual(code, ValidateCode.VALID)

        # Extract payload (second part)
        parts = token.split('.')
        payload = parts[1]

        # Add padding before decoding - this is what users need to do
        padded_payload = JWTManager._add_padding(payload)

        # Now should be able to decode with Python's base64 module
        try:
            decoded_bytes = base64.urlsafe_b64decode(padded_payload)
            decoded_str = decoded_bytes.decode('utf-8')
            self.assertIn("user@example.com", decoded_str)
            self.assertIn("Test User", decoded_str)
        except Exception as e:
            self.fail(f"Should be able to manually decode JWT payload after adding padding: {e}")

    def test_decode_jwt_payload_with_unpadded_token(self):
        """Test decode_jwt_payload works with tokens that lack padding"""
        # Create a standard JWT (which typically lacks padding)
        claims = {"sub": "user123", "role": "admin", "email": "test@example.com"}
        code, token = JWTManager.encode_and_compress(claims=claims, secret="secret",
                                                     validity=500, compression=False)
        self.assertEqual(code, ValidateCode.VALID)

        # decode_jwt_payload should handle the padding automatically
        code, payload = JWTManager.decode_jwt_payload(token=token)
        self.assertEqual(code, ValidateCode.VALID)
        self.assertEqual(payload.get("sub"), "user123")
        self.assertEqual(payload.get("role"), "admin")
        self.assertEqual(payload.get("email"), "test@example.com")

    def test_decode_jwt_payload_invalid_token(self):
        """Test decode_jwt_payload with invalid token"""
        # Test with invalid token format
        code, result = JWTManager.decode_jwt_payload(token="invalid.token")
        self.assertEqual(code, ValidateCode.UNPARSABLE_TOKEN)
        self.assertIsInstance(result, Exception)
