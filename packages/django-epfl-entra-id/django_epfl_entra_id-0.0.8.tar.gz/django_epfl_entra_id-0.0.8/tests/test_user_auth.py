import json
from unittest.mock import Mock, patch

import jwt
import pytest
from django.test import RequestFactory, TestCase, override_settings
from user.models import User

from django_epfl_entra_id.auth import EPFLOIDCAB


class EPFLOIDCABUserTestCase(TestCase):
    """Authentication tests with User(AbstractUser)."""

    @override_settings(OIDC_OP_TOKEN_ENDPOINT="https://server.epfl.ch/token")
    @override_settings(OIDC_OP_USER_ENDPOINT="https://server.epfl.ch/user")
    @override_settings(OIDC_RP_CLIENT_ID="example_id")
    @override_settings(OIDC_RP_CLIENT_SECRET="client_secret")
    def setUp(self):
        self.backend = EPFLOIDCAB()

    def test_missing_request_arg(self):
        self.assertIsNone(self.backend.authenticate(request=None))

    @patch("django_epfl_entra_id.auth.EPFLOIDCAB._verify_jws")
    @patch("mozilla_django_oidc.auth.requests")
    @override_settings(OIDC_USE_NONCE=False)
    def test_create_user(self, request_mock, jws_mock):
        auth_request = RequestFactory().get(
            "/foo", {"code": "foo", "state": "bar"}
        )
        auth_request.session = {}

        self.assertEqual(User.objects.filter(sciper="000100").exists(), False)
        jws_mock.return_value = json.dumps({"nonce": "nonce"}).encode("utf-8")
        get_json_mock = Mock()
        get_json_mock.json.return_value = {
            "gaspar": "sakai",
            "email": "jin.sakai@epfl.ch",
            "uniqueid": "000100",
            "given_name": "Jin",
            "family_name": "Sakai",
        }
        request_mock.get.return_value = get_json_mock
        post_json_mock = Mock(status_code=200)
        post_json_mock.json.return_value = {
            "id_token": jwt.encode(
                {"some": "payload"}, "foobar", algorithm="HS256"
            ),
            "access_token": "access_granted",
        }
        request_mock.post.return_value = post_json_mock

        self.assertEqual(
            self.backend.authenticate(request=auth_request),
            User.objects.get(sciper="000100"),
        )
        u = User.objects.get(sciper="000100")
        self.assertEqual(u.username, "sakai")
        self.assertEqual(u.first_name, "Jin")
        self.assertEqual(u.last_name, "Sakai")
        self.assertEqual(u.email, "jin.sakai@epfl.ch")

    @patch("django_epfl_entra_id.auth.EPFLOIDCAB._verify_jws")
    @patch("mozilla_django_oidc.auth.requests")
    @override_settings(OIDC_USE_NONCE=False)
    def test_update_user(self, request_mock, jws_mock):
        auth_request = RequestFactory().get(
            "/foo", {"code": "foo", "state": "bar"}
        )
        auth_request.session = {}

        User.objects.create(
            username="shimura",
            email="jito.shimura@epfl.ch",
            first_name="Jito",
            last_name="Shimura",
            sciper="000101",
        )

        self.assertEqual(User.objects.filter(sciper="000100").exists(), False)
        self.assertEqual(User.objects.filter(sciper="000101").exists(), True)
        jws_mock.return_value = json.dumps({"nonce": "nonce"}).encode("utf-8")
        get_json_mock = Mock()
        get_json_mock.json.return_value = {
            "gaspar": "shimura",
            "email": "lord.shimura@epfl.ch",
            "uniqueid": "000101",
            "given_name": "Lord",
            "family_name": "Shimura",
        }
        request_mock.get.return_value = get_json_mock
        post_json_mock = Mock(status_code=200)
        post_json_mock.json.return_value = {
            "id_token": jwt.encode(
                {"some": "payload"}, "foobar", algorithm="HS256"
            ),
            "access_token": "access_granted",
        }
        request_mock.post.return_value = post_json_mock

        self.assertEqual(
            self.backend.authenticate(request=auth_request),
            User.objects.get(sciper="000101"),
        )
        u = User.objects.get(sciper="000101")
        self.assertEqual(u.first_name, "Lord")
        self.assertEqual(u.email, "lord.shimura@epfl.ch")

    @patch("django_epfl_entra_id.auth.EPFLOIDCAB._verify_jws")
    @patch("mozilla_django_oidc.auth.requests")
    @override_settings(OIDC_USE_NONCE=False)
    def test_update_user_with_same_username(self, request_mock, jws_mock):
        auth_request = RequestFactory().get(
            "/foo", {"code": "foo", "state": "bar"}
        )
        auth_request.session = {}

        User.objects.create(
            username="sakai",
            email="kazumasa.sakai@epfl.ch",
            first_name="Kazumasa",
            last_name="Sakai",
            sciper="000105",
        )

        self.assertEqual(User.objects.filter(sciper="000100").exists(), False)
        self.assertEqual(User.objects.filter(sciper="000105").exists(), True)
        jws_mock.return_value = json.dumps({"nonce": "nonce"}).encode("utf-8")
        get_json_mock = Mock()
        get_json_mock.json.return_value = {
            "gaspar": "sakai",
            "email": "jin.sakai@epfl.ch",
            "uniqueid": "000100",
            "given_name": "Jin",
            "family_name": "Sakai",
        }
        request_mock.get.return_value = get_json_mock
        post_json_mock = Mock(status_code=200)
        post_json_mock.json.return_value = {
            "id_token": jwt.encode(
                {"some": "payload"}, "foobar", algorithm="HS256"
            ),
            "access_token": "access_granted",
        }
        request_mock.post.return_value = post_json_mock

        self.assertEqual(
            self.backend.authenticate(request=auth_request),
            User.objects.get(sciper="000100"),
        )
        u = User.objects.get(sciper="000105")
        self.assertEqual(u.username, "sakai-inactive-1")

        u = User.objects.get(username="sakai")
        self.assertEqual(u.first_name, "Jin")

    @patch("django_epfl_entra_id.auth.EPFLOIDCAB._verify_jws")
    @patch("mozilla_django_oidc.auth.requests")
    @override_settings(OIDC_USE_NONCE=False)
    def test_create_user_without_sciper(self, request_mock, jws_mock):
        auth_request = RequestFactory().get(
            "/foo", {"code": "foo", "state": "bar"}
        )
        auth_request.session = {}

        self.assertEqual(User.objects.filter(sciper="000100").exists(), False)
        jws_mock.return_value = json.dumps({"nonce": "nonce"}).encode("utf-8")
        get_json_mock = Mock()
        get_json_mock.json.return_value = {
            "gaspar": "sakai",
            "email": "jin.sakai@epfl.ch",
            "given_name": "Jin",
            "family_name": "Sakai",
        }
        request_mock.get.return_value = get_json_mock
        post_json_mock = Mock(status_code=200)
        post_json_mock.json.return_value = {
            "id_token": jwt.encode(
                {"some": "payload"}, "foobar", algorithm="HS256"
            ),
            "access_token": "access_granted",
        }
        request_mock.post.return_value = post_json_mock

        with pytest.raises(Exception):
            self.backend.authenticate(request=auth_request)
