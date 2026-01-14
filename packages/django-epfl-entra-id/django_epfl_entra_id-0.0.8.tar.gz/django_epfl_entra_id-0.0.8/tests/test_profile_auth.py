import json
from unittest.mock import Mock, patch

import jwt
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings

from django_epfl_entra_id.auth import EPFLOIDCAB

User = get_user_model()


class EPFLOIDCABProfileTestCase(TestCase):
    """Authentication tests with UserProfile(models.Model)."""

    @override_settings(OIDC_OP_TOKEN_ENDPOINT="https://server.epfl.ch/token")
    @override_settings(OIDC_OP_USER_ENDPOINT="https://server.epfl.ch/user")
    @override_settings(OIDC_RP_CLIENT_ID="example_id")
    @override_settings(OIDC_RP_CLIENT_SECRET="client_secret")
    def setUp(self):
        self.backend = EPFLOIDCAB()

    @patch("django_epfl_entra_id.auth.EPFLOIDCAB._verify_jws")
    @patch("mozilla_django_oidc.auth.requests")
    @override_settings(OIDC_USE_NONCE=False)
    @override_settings(AUTH_USER_MODEL="auth.User")
    @override_settings(AUTH_PROFILE_MODULE="userprofile.UserProfile")
    def test_create_user_with_profile(self, request_mock, jws_mock):
        auth_request = RequestFactory().get(
            "/foo", {"code": "foo", "state": "bar"}
        )
        auth_request.session = {}

        self.assertEqual(
            User.objects.filter(username="ishikawa").exists(), False
        )
        jws_mock.return_value = json.dumps({"nonce": "nonce"}).encode("utf-8")
        get_json_mock = Mock()
        get_json_mock.json.return_value = {
            "gaspar": "ishikawa",
            "email": "sadanobu.ishikawa@epfl.ch",
            "uniqueid": "000102",
            "given_name": "Sadanobu",
            "family_name": "Ishikawa",
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
            User.objects.get(username="ishikawa"),
        )
        u = User.objects.get(username="ishikawa")
        self.assertEqual(u.first_name, "Sadanobu")
        self.assertEqual(u.last_name, "Ishikawa")
        self.assertEqual(u.email, "sadanobu.ishikawa@epfl.ch")
        self.assertEqual(u.profile.sciper, "000102")

    @patch("django_epfl_entra_id.auth.EPFLOIDCAB._verify_jws")
    @patch("mozilla_django_oidc.auth.requests")
    @override_settings(OIDC_USE_NONCE=False)
    @override_settings(AUTH_USER_MODEL="auth.User")
    @override_settings(AUTH_PROFILE_MODULE="userprofile.UserProfile")
    def test_update_user_with_profile(self, request_mock, jws_mock):
        auth_request = RequestFactory().get(
            "/foo", {"code": "foo", "state": "bar"}
        )
        auth_request.session = {}

        u = User.objects.create(
            username="adachi",
            email="lady.adachi@epfl.ch",
            first_name="Lady",
            last_name="Adachi",
        )
        u.profile.sciper = "000104"
        u.profile.save()

        self.assertEqual(
            User.objects.filter(username="ishikawa").exists(), False
        )
        self.assertEqual(User.objects.filter(username="adachi").exists(), True)
        jws_mock.return_value = json.dumps({"nonce": "nonce"}).encode("utf-8")
        get_json_mock = Mock()
        get_json_mock.json.return_value = {
            "gaspar": "adachi",
            "email": "masako.adachi@epfl.ch",
            "uniqueid": "000104",
            "given_name": "Masako",
            "family_name": "Adachi",
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
            User.objects.get(username="adachi"),
        )
        u = User.objects.get(username="adachi")
        self.assertEqual(u.first_name, "Masako")
        self.assertEqual(u.last_name, "Adachi")
        self.assertEqual(u.email, "masako.adachi@epfl.ch")
        self.assertEqual(u.profile.sciper, "000104")
