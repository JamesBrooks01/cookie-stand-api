from os import access
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CookieStand


###########################################################################################
# ATTENTION:
# DATABASES should be set to use SQLite
# Easiest way to ensure that is to comment out all the Postgres stuff in project/.env
# That will run using defaults, which is SQLite
###########################################################################################


class CookieStandTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        testuser1 = get_user_model().objects.create_user(
            username="testuser1", password="pass"
        )
        testuser1.save()

        test_cookie_stand = CookieStand.objects.create(
            location="Seattle",
            owner=testuser1,
            description="A nice little stand in Seattle",
            hourly_sales={"7am":"2560"},
            minimum_customers_per_hour = "21",
            maximum_customers_per_hour = "65",
            average_cookies_per_sale = "6.3",
        )
        test_cookie_stand.save()

    def setUp(self):
        self.client.login(username="testuser1", password="pass")

    # def get_token(self):
    #     url = "http://0.0.0.0:8000/api/token/"
    #     user = {"username": "testuser1", "password": "pass"}
    #     token = self.client.post(url, user)
    #     response_token = token.data["access"]
    #     return response_token

    def test_cookie_stands_model(self):
        cookie_stand = CookieStand.objects.get(id=1)
        actual_location = str(cookie_stand.location)
        actual_owner = str(cookie_stand.owner)
        actual_description = str(cookie_stand.description)
        actual_sales = cookie_stand.hourly_sales
        actual_min = str(cookie_stand.minimum_customers_per_hour)
        actual_max = str(cookie_stand.maximum_customers_per_hour)
        actual_avg = str(cookie_stand.average_cookies_per_sale)
        self.assertEqual(actual_owner, "testuser1")
        self.assertEqual(actual_location, "Seattle")
        self.assertEqual(
            actual_description, "A nice little stand in Seattle"
        )
        self.assertEqual(actual_sales, {"7am":"2560"})
        self.assertEqual(actual_min, "21")
        self.assertEqual(actual_max, "65")
        self.assertEqual(actual_avg, "6.3")

    def test_get_cookie_stands_list(self):
        url = reverse("cookie_stands_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cookie_stands = response.data
        self.assertEqual(len(cookie_stands), 1)
        self.assertEqual(cookie_stands[0]["location"], "Seattle")

    def test_get_cookie_stands_by_id(self):
        url = reverse("cookie_stands_detail", args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cookie_stands = response.data
        self.assertEqual(cookie_stands["location"], "Seattle")

    def test_create_cookie_stands(self):
        url = reverse("cookie_stands_list")
        data = {"location":"Berlin","owner":1,"description":"Holen Sie sich hier Cookies","hourly_sales":"8675","minimum_customers_per_hour":"12","maximum_customers_per_hour":"35","average_cookies_per_sale":"5.7"}
        # token = self.get_token()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cookie_stands = CookieStand.objects.all()
        self.assertEqual(len(cookie_stands), 2)
        self.assertEqual(CookieStand.objects.get(id=2).location, "Berlin")

    def test_update_cookie_stands(self):
        url = reverse("cookie_stands_detail", args=(1,))
        data = {
            "location":"Berlin",
            "owner":1,
            "description":"Holen Sie sich hier den Kuchen",
            "hourly_sales":"8675",
            "minimum_customers_per_hour":"12",
            "maximum_customers_per_hour":"35",
            "average_cookies_per_sale":"5.7"
            }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cookie_stand = CookieStand.objects.get(id=1)
        self.assertEqual(cookie_stand.location, data["location"])
        self.assertEqual(cookie_stand.owner.id, data["owner"])
        self.assertEqual(cookie_stand.description, data["description"])

    def test_delete_cookie_stands(self):
        url = reverse("cookie_stands_detail", args=(1,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cookie_stands = CookieStand.objects.all()
        self.assertEqual(len(cookie_stands), 0)

    def test_authentication_required(self):
        self.client.logout()
        url = reverse("cookie_stands_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
