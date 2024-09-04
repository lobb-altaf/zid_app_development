# oauth/views.py
import datetime
import uuid
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views import View
import requests
from .models import ZidUser, ZidUserStore

import oauth.utils as utils


CLIENT_ID = 3348
CLIENT_SECRET = "6CpbZVTgOZjwdp2A7IoUGpYievg2xh4iuYCbcp8k"
BASE_URL = "https://oauth.zid.sa"


from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the zid oauth index.")


class OauthRedirectView(View):
    def get(self, request, *args, **kwargs):
        return redirect(
            f"{BASE_URL}/oauth/authorize?client_id={CLIENT_ID}&response_type=code"
        )


class OauthCallbackView(View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        payload = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
        }
        response = requests.post(f"{BASE_URL}/oauth/token", json=payload)
        # TODO : assicate request with user with TokenData
        if response.status_code == 200:
            data = response.json()
            print("data", data)
            access_token = data["access_token"]
            manager_token = data["authorization"]
            profile_data = utils.get_manager_profile(
                auth_token=manager_token, access_token=access_token
            )["user"]

            # TODO CHECK IS USER ALREADY EXIST
            # TODO associate user_obj with Django User model

            if ZidUser.objects.filter(
                user_id=profile_data["id"], user=request.user
            ).exists():
                # exising account
                zid_user_obj = ZidUser.objects.get(
                    user_id=profile_data["id"], user=request.user
                )
                zid_user_obj.access_token = access_token
                zid_user_obj.refresh_token = data["refresh_token"]
                zid_user_obj.authorization_code = manager_token
                zid_user_obj.token_type = data["token_type"]
                zid_user_obj.expires_in = data["expires_in"]
                zid_user_obj.save()

            else:
                # new account

                zid_user_obj = ZidUser.objects.create(
                    user=request.user,
                    user_id=profile_data["id"],
                    user_uuid=profile_data["uuid"],
                    name=profile_data["name"],
                    email=profile_data["email"],
                    mobile=profile_data["mobile"],
                    access_token=access_token,
                    refresh_token=data["refresh_token"],
                    authorization_code=manager_token,
                    token_type=data["token_type"],
                    expires_in=data["expires_in"],
                )
                zid_user_obj.save()

            if ZidUserStore.objects.filter(
                zid_user=zid_user_obj, store_id=profile_data["store"]["id"]
            ).exists():
                pass
            else:
                # new store
                zid_user_store_obj = ZidUserStore.objects.create(
                    zid_user=zid_user_obj,
                    store_id=profile_data["store"]["id"],
                    store_uuid=profile_data["store"]["uuid"],
                    title=profile_data["store"]["title"],
                    username=profile_data["store"]["username"],
                )
                zid_user_store_obj.save()

        else:
            response.raise_for_status()
        return redirect("/")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# @csrf_exempt
# def create_webhook(request):
#     if request.method == 'POST':
#         api_url = "https://api.zid.sa/v1/managers/webhooks"
#         headers = {
#             "Accept-Language": "en",
#             "Authorization": "Bearer eyJ0eXAiOiJKV1Qi...your_token_here",
#             "X-Manager-Token": "eyJpdiI6Imh3L2dGbmJm...your_token_here",
#             "Content-Type": "application/json"
#         }

#         webhook_data = {
#             "event": "order.status.update",
#             "target_url": "https://webhook.site/7d0aa7ef-c4b5-41f0-8786-335a9c9c1a3e",
#             "original_id": 1,
#             "subscriber": "My Online Store App",
#             "conditions": {
#                 "status": "new",
#                 "delivery_option_id": 55,
#                 "payment_method": "Cash On Delivery"
#             }
#         }

#         response = requests.post(api_url, headers=headers, json=webhook_data)
#         response_data = {
#             "status_code": response.status_code,
#             "content": response.text,
#             "json_response": response.json() if response.headers.get('content-type') == 'application/json' else None,
#             "content_type": response.headers.get('content-type'),
#         }

#         if response.status_code == 200:
#             response_data["message"] = "Webhook subscription created successfully."
#         else:
#             response_data["message"] = f"Error: {response.status_code} - {response.text}"

#         return JsonResponse(response_data)

#     return render(request, 'oauth/create_webhook.html')

# {'access_token': 'eyJpdiI6ImsxdFg0R0FQUUFyeXN2SVdhNmpIc2c9PSIsInZhbHVlIjoiWE1CT1NOZWFSbThZVVlpT2F2MTNDWWlQTjNMaDR0eUgrQzNlUkhYYjhIK3lNOUFOaGV1S2RLVEZTL2IvcmNNVDhIbFpsQkpkdVREUkdsUkRpVXhadmRPSzFIa0VGNU82RCswR2hXVnVJKzlBY2VKQTJkZ1BTZ3UvZWlaR3FoYTNJK01LcHdmNU02TnZDZEEwbmJKSm93S2VMTzBGV3ZPdzk0blNqeWVzVXhUVnZTSTB6RXhLVkpkYitqZEkyNDhRMGFXU1FIRzdVZE1BM0xXdFJYd3M1NnJsdGNvT3NKZkxtYkJNWDFZK3Z6Zz0iLCJtYWMiOiIzMTZlMjczZTE0ZmZjMjBmZGMxNWE1NmMyMjNiMDczNTUxNjg4MDFiM2ZmNTI4OWQ3NmM0MmYwYzRkMDkxNzViIiwidGFnIjoiIn0=',
#  'token_type': 'Bearer', 'expires_in': 31536000,
#    'authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzMzQ4IiwianRpIjoiMWE0NmE0ZWRjMGM2ZDE4MGM4NjdmNjZkZTBlZDIzODkwNWYwMjBmZmYxNDhkNzc0MmE2NGQ0NGM2ZGY2ZmQ3OGE0OWI4ODBlODU3MzM3MTgiLCJpYXQiOjE3MjMxNDMwMTYuNzk0Njg3LCJuYmYiOjE3MjMxNDMwMTYuNzk0Njg5LCJleHAiOjE3NTQ2NzkwMTYuNzUzNTgsInN1YiI6IjQ3MjU4NyIsInNjb3BlcyI6WyJ0aGlyZF9jYXRlZ29yaWVzX3dyaXRlIiwidGhpcmRfY3VzdG9tZXJzX3dyaXRlIiwidGhpcmRfb3JkZXJfd3JpdGUiLCJ0aGlyZF9jb3Vwb25zX3dyaXRlIiwidGhpcmRfZGVsaXZlcnlfb3B0aW9uc193cml0ZSIsInRoaXJkX3dlYmhvb2tfd3JpdGUiLCJ0aGlyZF9wcm9kdWN0X3dyaXRlIiwidGhpcmRfY2F0YWxvZ193cml0ZSIsInRoaXJkX2pzX3dyaXRlIiwidGhpcmRfY3JlYXRlX29yZGVyIiwidGhpcmRfcHJvZHVjdF9zdG9ja193cml0ZSIsInRoaXJkX2ludmVudG9yeV93cml0ZSIsImVtYmVkZGVkX2FwcHNfdG9rZW5zX3dyaXRlIl19.LzdcNSLvmWz9pBXpAqm4yZulXSVVzyooiPDjuwNODrP6-mU99wd0ri1U2bfCEdA7_f1b6tVS6mMAwj9vQjCLUI6qYfcU5E24ZBDdpGNlfpBXRRQmFw27IzYbjGpaO6d2NpCDVdpri5r1-QHHtIIP6et_9jNF4TwIhn550qqh7lg-nySS8LYFtIMK-RQqPwFOA7p9YyqxZ4Tpu2s-diLI3NMOGiQAfAqch5hiD9pqFhxS26J57CF_6UBY4Nyx6Z483dD8d_XVN0uRHm299n1FmUGN4WtYsjjFvCZo5Zubg79Cq6yWx2wELgFrgNwdLDyQ7t4cueGolMly80y2rAEgaJEL4S2zHPG-jOIjqSjwLCrszOmJ6idkBqgETZ6Ad4t4i_xuDiExPcKOehXNr9RvtBKLIZMZhgwb_mfJyGUwoEiR7Q01s_SjmsyUZ-0ZWL3Yh20EzYE3CJ7oue9LPmjAxix4uOUUtq_RaeATQPWr8jAzIDQZA9UtW2xQSV-VfRj4AyzCjw7su-jX8Ejg2wAGcNlSJeB5sMeCBa8Zl35wETqhiGOoTSJqCbTF75PGLPvT0jOFF59C7BlyLOR8-GmbjBaEkLYB3xD1NG-4xMageDxp0ozwnysG90X7d7QISLjkuq4iUBWDYcs-2oXGFC3-XBJMUu3Xu1s3BhzVATjPH_w', 'refresh_token': 'def502000e19b2904546f95b688c9c8f353824f1ca4bd763e5ca4d5e2b348e96e7c9251ca0e5e5ef082b037bbef7ebd89aee63256a6c141d6e196dab0f480eb6a78caff80efdda371f90d992fc0f06d95ba22611cf72dc18381a417b5546b5b7e9fc4fd60d944b9ce778ee54375a3be72f2809bd9953e80ed0abdfeb92aa88bff04b3972581e4bdf3fb11aed087146a7b21a4e10e99ab49e590b04976724886d97956e3aaf7f83b813a600ec2e1312d94680c7412d9711284a1e48d830f2217952f1dba39e4b580e497b2591793a9302046f2bf1fd62e00df5e7ea1afdd37cf162b6ab2d50e7743a469ab2daeb10830ef94eb4d914e6bd865ef9c2b2b234f4ccad5ba9d349c56ea6808de59d88dc9b2ca213e3dec9cf3b1ce462dcc22ca533bdd16c06c8d4c27e9e543135f8d481fd30072c4670d5be825482debfb991dfa545e766dbea542959a500dc45f96127034b08a73ebd027b4200dff5f4bc9059715345aef2dc9e418eda53b107a7241705634dfa6b341fad3845cd3dc3eedca00ce05ed1f028376a146d3d34301da5c2b20a887cce206807d9f16b7752c4b0dc33d320b7adcea1bbf3835923da0f945d9067e43a042c46da600a4c1634d82c4b0f189d9068b15f762b09bb2bbbbf41d8af19b074aa6ec37ef14257db3708848916308a0ba13e49033e76a67014ac7d8f75b1056a0558e58d1fcd6222d4550469cc460aa9da88be1574d4204d03b487d86e0f45ad06b14491bcd1cf1939df5987a96dcd48c06f45db28bdd63b0026de31e5fed47772212e6a55a2c32b7991be957ac38679c0e4f6c9c4e68bba442370333774a7b265abd222cd7b47cb06701586406234f0dd73ae1fd7710cf793e834e115a9d15ead6e972ceda990e4a0e96b3d4a2c45e71ea8c8eba3eabd5b49795e40e86659c2ad0f0371baa9183fd2'}


@csrf_exempt
def create_webhook(request):
    token_data = ZidUser.objects.latest("created_at")
    if request.method == "POST":
        api_url = "https://api.zid.sa/v1/managers/webhooks"

        headers = {
            "Accept-Language": "en",
            "Authorization": f"Bearer {token_data.authorization_code}",
            "X-Manager-Token": token_data.access_token,
            "Content-Type": "application/json",
        }

        webhook_data = {
            # "event": "order.status.update",
            "event": "order.create",
            "target_url": "https://lm1h3n2p-8000.inc1.devtunnels.ms/webhook/ ",
            "original_id": 3500,
            "subscriber": "My Online Store App",
            "conditions": {
                "status": "new",
                # "delivery_option_id": 55,
                "payment_method": "Cash On Delivery",
            },
        }

        #     webhook_data = {
        #     "event": "order.create",
        #     "target_url": "https://webhook.site/c5f8dcff-1170-42da-a465-462c8d8147b2",
        #     "original_id": 1,
        #     "subscriber": "e2065cb56f5533494522c46a72f1dfb0",
        # }

        response = requests.post(api_url, headers=headers, json=webhook_data)
        print(response.text)
        print("------------------")
        print(response.status_code)

        print("------------------")
        print(response)
        print("------------------")

        # print(response.json())
        response_data = {
            "status_code": response.status_code,
            "content": response.text,
            "json_response": (
                response.json()
                if response.headers.get("content-type") == "application/json"
                else None
            ),
            "content_type": response.headers.get("content-type"),
        }

        if response.status_code == 200:
            response_data["message"] = "Webhook subscription created successfully."
        else:
            response_data["message"] = (
                f"Error: {response.status_code} - {response.text}"
            )

        return JsonResponse(response_data)

    return render(request, "oauth/create_webhook.html")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json


import hashlib
import base64
import ecdsa
import lxml.etree as ET
import cryptography.x509
from bs4 import BeautifulSoup  # , Comment
import sys
import os
import io


def create_an_invoice(
    invoice_data,
    seller_data,
    customer_data,
    delivery_data,
    payment_data,
    products,
    discount_on_totals,
    charge_on_totals,
):

    # try:
    def number_with_n_digits_after_the_point(the_number, n=2):
        if type(the_number) == int:
            zeros = "0" * n
            the_number = float("{}.{}".format(the_number, zeros))
            return the_number

        elif type(the_number) == float:
            the_number_as_str = str(the_number)
            before_the_point = the_number_as_str.split(".")[0]
            after_the_point = the_number_as_str.split(".")[-1][:n]
            the_number = float("{}.{}".format(before_the_point, after_the_point))
            return the_number

    # Sperate each kind

    each_kind = {}
    each_kind_total = {}
    after_discount_each_kind_total = {}
    after_charge_each_kind_total = {}

    each_tax = {}
    each_tax_total = {}
    after_discount_each_tax_total = {}
    after_charge_each_tax_total = {}

    for i in products:
        if each_kind.get(i.get("tax_id_letter")):
            each_kind.get(i.get("tax_id_letter")).append(i)
        else:
            each_kind.update({i.get("tax_id_letter"): [i]})

    if each_kind.get("S"):
        for i in each_kind.get("S"):
            if each_tax.get(i.get("tax_percentage")):
                each_tax.get(i.get("tax_percentage")).append(i)
            else:
                each_tax.update({i.get("tax_percentage"): [i]})

        each_kind.pop("S")

    # Calculate the total of each kind

    for i in each_kind:
        the_products = each_kind.get(i)
        the_total_of_products = 0.0
        the_kind_of_products = i

        for product in the_products:
            the_quantity = product.get("quantity")
            the_price = number_with_n_digits_after_the_point(product.get("final_price"))

            product_total_without_tax = number_with_n_digits_after_the_point(
                round(the_price * the_quantity, 10)
            )

            if product.get("charge_on_total"):
                if product.get("charge_on_total").get("charge_value") > 0:
                    if (
                        product.get("charge_on_total").get("charge_type")
                        == "percentage"
                    ):
                        charge_on_total = number_with_n_digits_after_the_point(
                            round(
                                product_total_without_tax
                                * (
                                    product.get("charge_on_total").get("charge_value")
                                    / 100
                                ),
                                10,
                            )
                        )
                    else:
                        charge_on_total = number_with_n_digits_after_the_point(
                            round(
                                product.get("charge_on_total").get("charge_value"), 10
                            )
                        )
                else:
                    charge_on_total = 0.0
            else:
                charge_on_total = 0.0

            if product.get("discount_on_total"):
                if product.get("discount_on_total").get("discount_value") > 0:
                    if (
                        product.get("discount_on_total").get("discount_type")
                        == "percentage"
                    ):
                        discount_on_total = number_with_n_digits_after_the_point(
                            round(
                                product_total_without_tax
                                * (
                                    product.get("discount_on_total").get(
                                        "discount_value"
                                    )
                                    / 100
                                ),
                                10,
                            )
                        )
                    else:
                        discount_on_total = number_with_n_digits_after_the_point(
                            round(
                                product.get("discount_on_total").get("discount_value"),
                                10,
                            )
                        )
                else:
                    discount_on_total = 0.0
            else:
                discount_on_total = 0.0

            product_total_without_tax_with_discount_and_charge = (
                number_with_n_digits_after_the_point(
                    round(
                        (product_total_without_tax + charge_on_total)
                        - discount_on_total,
                        10,
                    )
                )
            )

            the_total_of_products += product_total_without_tax_with_discount_and_charge

        each_kind_total.update(
            {
                the_kind_of_products: number_with_n_digits_after_the_point(
                    round(the_total_of_products, 10)
                )
            }
        )

    for i in each_tax:
        the_products = each_tax.get(i)
        the_total_of_products = 0.0
        the_tax_of_products = i

        for product in the_products:
            the_quantity = product.get("quantity")
            the_price = number_with_n_digits_after_the_point(product.get("final_price"))

            product_total_without_tax = number_with_n_digits_after_the_point(
                round(the_price * the_quantity, 10)
            )

            if product.get("charge_on_total"):
                if product.get("charge_on_total").get("charge_value") > 0:
                    if (
                        product.get("charge_on_total").get("charge_type")
                        == "percentage"
                    ):
                        charge_on_total = number_with_n_digits_after_the_point(
                            round(
                                product_total_without_tax
                                * (
                                    product.get("charge_on_total").get("charge_value")
                                    / 100
                                ),
                                10,
                            )
                        )
                    else:
                        charge_on_total = number_with_n_digits_after_the_point(
                            round(
                                product.get("charge_on_total").get("charge_value"), 10
                            )
                        )
                else:
                    charge_on_total = 0.0
            else:
                charge_on_total = 0.0

            if product.get("discount_on_total"):
                if product.get("discount_on_total").get("discount_value") > 0:
                    if (
                        product.get("discount_on_total").get("discount_type")
                        == "percentage"
                    ):
                        discount_on_total = number_with_n_digits_after_the_point(
                            round(
                                product_total_without_tax
                                * (
                                    product.get("discount_on_total").get(
                                        "discount_value"
                                    )
                                    / 100
                                ),
                                10,
                            )
                        )
                    else:
                        discount_on_total = number_with_n_digits_after_the_point(
                            round(
                                product.get("discount_on_total").get("discount_value"),
                                10,
                            )
                        )
                else:
                    discount_on_total = 0.0
            else:
                discount_on_total = 0.0

            product_total_without_tax_with_discount_and_charge = (
                number_with_n_digits_after_the_point(
                    round(
                        (product_total_without_tax + charge_on_total)
                        - discount_on_total,
                        10,
                    )
                )
            )

            the_total_of_products += product_total_without_tax_with_discount_and_charge

        each_tax_total.update(
            {
                the_tax_of_products: number_with_n_digits_after_the_point(
                    round(the_total_of_products, 10)
                )
            }
        )

    # functions to calculate the total and the tax

    def calculate_the_total_without_tax():
        total_of_the_invoice = 0.0

        for i in each_kind_total:
            total_of_the_invoice += each_kind_total.get(i)

        for i in each_tax_total:
            total_of_the_invoice += each_tax_total.get(i)

        return number_with_n_digits_after_the_point(round(total_of_the_invoice, 10))

    def calculate_the_total_after_discount():
        total_of_the_invoice_after_discount = 0.0

        for i in after_discount_each_kind_total:
            total_of_the_invoice_after_discount += after_discount_each_kind_total.get(i)

        for i in after_discount_each_tax_total:
            total_of_the_invoice_after_discount += after_discount_each_tax_total.get(i)

        return number_with_n_digits_after_the_point(
            round(total_of_the_invoice_after_discount, 10)
        )

    def calculate_the_total_after_charge():
        total_of_the_invoice_after_charge = 0.0

        for i in after_charge_each_kind_total:
            total_of_the_invoice_after_charge += after_charge_each_kind_total.get(i)

        for i in after_charge_each_tax_total:
            total_of_the_invoice_after_charge += after_charge_each_tax_total.get(i)

        return number_with_n_digits_after_the_point(
            round(total_of_the_invoice_after_charge, 10)
        )

    def calculate_the_tax():
        the_total_of_the_tax = 0.0

        for i in after_discount_each_tax_total:

            the_total_without_discount_and_without_charge_and_without_tax = (
                each_tax_total.get(i)
            )
            the_discounted_amount = number_with_n_digits_after_the_point(
                round(each_tax_total.get(i) - after_discount_each_tax_total.get(i), 10)
            )
            the_charged_amount = number_with_n_digits_after_the_point(
                round(after_charge_each_tax_total.get(i) - each_tax_total.get(i), 10)
            )

            the_total_with_discount_and_with_charge_and_without_tax = (
                the_total_without_discount_and_without_charge_and_without_tax
                + the_charged_amount
                - the_discounted_amount
            )
            the_total_tax = number_with_n_digits_after_the_point(
                round(
                    the_total_with_discount_and_with_charge_and_without_tax * (i / 100),
                    10,
                )
            )

            the_total_of_the_tax += the_total_tax

        the_total_of_the_tax = number_with_n_digits_after_the_point(
            round(the_total_of_the_tax, 10)
        )

        return the_total_of_the_tax

    # claculate the the discount amount

    if discount_on_totals.get("discount_type") == "percentage":
        the_percentage_of_the_discount_on_totals = discount_on_totals.get(
            "discount_value"
        )
    else:
        the_percentage_of_the_discount_on_totals = number_with_n_digits_after_the_point(
            round(
                (
                    (
                        discount_on_totals.get("discount_value")
                        / calculate_the_total_without_tax()
                    )
                    * 100
                ),
                10,
            )
        )

    # claculate the the charge amount

    if charge_on_totals.get("charge_type") == "percentage":
        the_percentage_of_the_charge_on_totals = charge_on_totals.get("charge_value")
    else:
        the_percentage_of_the_charge_on_totals = number_with_n_digits_after_the_point(
            round(
                (
                    (
                        charge_on_totals.get("charge_value")
                        / calculate_the_total_without_tax()
                    )
                    * 100
                ),
                10,
            )
        )

    # claculate the the discount

    for i in each_kind_total:
        the_amount = each_kind_total.get(i)
        the_percentage_of_the_discount_on_totals_under_1 = (
            the_percentage_of_the_discount_on_totals / 100
        )
        the_final_amount = the_amount - (
            the_amount * the_percentage_of_the_discount_on_totals_under_1
        )  # here is the problem
        after_discount_each_kind_total.update(
            {i: number_with_n_digits_after_the_point(round(the_final_amount, 10))}
        )

    for i in each_tax_total:
        the_amount = each_tax_total.get(i)
        the_percentage_of_the_discount_on_totals_under_1 = (
            the_percentage_of_the_discount_on_totals / 100
        )
        the_final_amount = the_amount - (
            the_amount * the_percentage_of_the_discount_on_totals_under_1
        )
        after_discount_each_tax_total.update(
            {i: number_with_n_digits_after_the_point(round(the_final_amount, 10))}
        )

    # balance the rest of the discount

    if discount_on_totals.get("discount_type") == "amount":
        the_discount_amount = discount_on_totals.get("discount_value")
        the_discounted_amount = round(
            calculate_the_total_without_tax() - calculate_the_total_after_discount(), 10
        )

        while the_discount_amount > the_discounted_amount:

            the_discount_amount = discount_on_totals.get("discount_value")
            the_discounted_amount = round(
                calculate_the_total_without_tax()
                - calculate_the_total_after_discount(),
                10,
            )

            discounting_status = False

            if the_discount_amount > the_discounted_amount:

                the_rest = round(the_discount_amount - the_discounted_amount, 10)

                for i in after_discount_each_tax_total:
                    if after_discount_each_tax_total.get(i) > the_rest:
                        the_new_amount = after_discount_each_tax_total.get(i) - the_rest
                        after_discount_each_tax_total.update(
                            {
                                i: number_with_n_digits_after_the_point(
                                    round(the_new_amount, 10)
                                )
                            }
                        )
                        discounting_status = True
                        break

                if not discounting_status:
                    for i in after_discount_each_kind_total:
                        if after_discount_each_kind_total.get(i) > the_rest:
                            the_new_amount = (
                                after_discount_each_kind_total.get(i) - the_rest
                            )
                            after_discount_each_kind_total.update(
                                {
                                    i: number_with_n_digits_after_the_point(
                                        round(the_new_amount, 10)
                                    )
                                }
                            )
                            discounting_status = True
                            break

        while the_discount_amount < the_discounted_amount:

            the_discount_amount = discount_on_totals.get("discount_value")
            the_discounted_amount = round(
                calculate_the_total_without_tax()
                - calculate_the_total_after_discount(),
                10,
            )

            adding_status = False

            if the_discount_amount < the_discounted_amount:

                the_rest = round(the_discounted_amount - the_discount_amount, 10)

                for i in after_discount_each_tax_total:
                    if after_discount_each_tax_total.get(i) > the_rest:
                        the_new_amount = after_discount_each_tax_total.get(i) + the_rest
                        after_discount_each_tax_total.update(
                            {
                                i: number_with_n_digits_after_the_point(
                                    round(the_new_amount, 10)
                                )
                            }
                        )
                        adding_status = True
                        break

                if not adding_status:
                    for i in after_discount_each_kind_total:
                        if after_discount_each_kind_total.get(i) > the_rest:
                            the_new_amount = (
                                after_discount_each_kind_total.get(i) + the_rest
                            )
                            after_discount_each_kind_total.update(
                                {
                                    i: number_with_n_digits_after_the_point(
                                        round(the_new_amount, 10)
                                    )
                                }
                            )
                            adding_status = True
                            break

    # claculate the the charge

    for i in each_kind_total:
        the_amount = each_kind_total.get(i)
        the_percentage_of_the_charge_on_totals_under_1 = (
            the_percentage_of_the_charge_on_totals / 100
        )
        the_final_amount = the_amount + (
            the_amount * the_percentage_of_the_charge_on_totals_under_1
        )  # here is the problem
        after_charge_each_kind_total.update(
            {i: number_with_n_digits_after_the_point(round(the_final_amount, 10))}
        )

    for i in each_tax_total:
        the_amount = each_tax_total.get(i)
        the_percentage_of_the_charge_on_totals_under_1 = (
            the_percentage_of_the_charge_on_totals / 100
        )
        the_final_amount = the_amount + (
            the_amount * the_percentage_of_the_charge_on_totals_under_1
        )
        after_charge_each_tax_total.update(
            {i: number_with_n_digits_after_the_point(round(the_final_amount, 10))}
        )

    # balance the rest of the charge

    if charge_on_totals.get("charge_type") == "amount":
        the_charge_amount = charge_on_totals.get("charge_value")
        the_charged_amount = round(
            calculate_the_total_after_charge() - calculate_the_total_without_tax(), 10
        )

        while the_charge_amount > the_charged_amount:

            the_charge_amount = charge_on_totals.get("charge_value")
            the_charged_amount = round(
                calculate_the_total_after_charge() - calculate_the_total_without_tax(),
                10,
            )

            charging_status = False

            if the_charge_amount > the_charged_amount:

                the_rest = round(the_charge_amount - the_charged_amount, 10)

                for i in after_charge_each_tax_total:
                    # if after_charge_each_tax_total.get(i) > the_rest:
                    the_new_amount = after_charge_each_tax_total.get(i) + the_rest
                    after_charge_each_tax_total.update(
                        {
                            i: number_with_n_digits_after_the_point(
                                round(the_new_amount, 10)
                            )
                        }
                    )
                    charging_status = True
                    break

                if not charging_status:
                    for i in after_charge_each_kind_total:
                        # if after_charge_each_kind_total.get(i) > the_rest:
                        the_new_amount = after_charge_each_kind_total.get(i) + the_rest
                        after_charge_each_kind_total.update(
                            {
                                i: number_with_n_digits_after_the_point(
                                    round(the_new_amount, 10)
                                )
                            }
                        )
                        charging_status = True
                        break

        while the_charge_amount < the_charged_amount:

            the_charge_amount = charge_on_totals.get("charge_value")
            the_charged_amount = round(
                calculate_the_total_after_charge() - calculate_the_total_without_tax(),
                10,
            )

            adding_status = False

            if the_charge_amount < the_charged_amount:

                the_rest = round(the_charged_amount - the_charge_amount, 10)

                for i in after_charge_each_tax_total:
                    if after_charge_each_tax_total.get(i) > the_rest:
                        the_new_amount = after_charge_each_tax_total.get(i) - the_rest
                        after_charge_each_tax_total.update(
                            {
                                i: number_with_n_digits_after_the_point(
                                    round(the_new_amount, 10)
                                )
                            }
                        )
                        adding_status = True
                        break

                if not adding_status:
                    for i in after_charge_each_kind_total:
                        if after_charge_each_kind_total.get(i) > the_rest:
                            the_new_amount = (
                                after_charge_each_kind_total.get(i) - the_rest
                            )
                            after_charge_each_kind_total.update(
                                {
                                    i: number_with_n_digits_after_the_point(
                                        round(the_new_amount, 10)
                                    )
                                }
                            )
                            adding_status = True
                            break

    def create_the_encryption_tags():
        final_encryption_tags = []

        final_encryption_tags.append("<ext:UBLExtensions>")
        final_encryption_tags.append("<ext:UBLExtension>")
        final_encryption_tags.append(
            "<ext:ExtensionURI>urn:oasis:names:specification:ubl:dsig:enveloped:xades</ext:ExtensionURI>"
        )
        final_encryption_tags.append("<ext:ExtensionContent>")
        final_encryption_tags.append(
            '<sig:UBLDocumentSignatures xmlns:sig="urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2" xmlns:sac="urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2" xmlns:sbc="urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2">'
        )
        final_encryption_tags.append("<sac:SignatureInformation>")
        final_encryption_tags.append(
            "<cbc:ID>urn:oasis:names:specification:ubl:signature:1</cbc:ID>"
        )
        final_encryption_tags.append(
            "<sbc:ReferencedSignatureID>urn:oasis:names:specification:ubl:signature:Invoice</sbc:ReferencedSignatureID>"
        )
        final_encryption_tags.append(
            '<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Id="signature">'
        )
        final_encryption_tags.append("<ds:SignedInfo>")
        final_encryption_tags.append(
            '<ds:CanonicalizationMethod Algorithm="http://www.w3.org/2006/12/xml-c14n11"/>'
        )
        final_encryption_tags.append(
            '<ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256"/>'
        )
        final_encryption_tags.append('<ds:Reference Id="invoiceSignedData" URI="">')
        final_encryption_tags.append("<ds:Transforms>")
        final_encryption_tags.append(
            '<ds:Transform Algorithm="http://www.w3.org/TR/1999/REC-xpath-19991116">'
        )
        final_encryption_tags.append(
            "<ds:XPath>not(//ancestor-or-self::ext:UBLExtensions)</ds:XPath>"
        )
        final_encryption_tags.append("</ds:Transform>")
        final_encryption_tags.append(
            '<ds:Transform Algorithm="http://www.w3.org/TR/1999/REC-xpath-19991116">'
        )
        final_encryption_tags.append(
            "<ds:XPath>not(//ancestor-or-self::cac:Signature)</ds:XPath>"
        )
        final_encryption_tags.append("</ds:Transform>")
        final_encryption_tags.append(
            '<ds:Transform Algorithm="http://www.w3.org/TR/1999/REC-xpath-19991116">'
        )
        final_encryption_tags.append(
            "<ds:XPath>not(//ancestor-or-self::cac:AdditionalDocumentReference[cbc:ID='QR'])</ds:XPath>"
        )
        final_encryption_tags.append("</ds:Transform>")
        final_encryption_tags.append(
            '<ds:Transform Algorithm="http://www.w3.org/2006/12/xml-c14n11"/>'
        )
        final_encryption_tags.append("</ds:Transforms>")
        final_encryption_tags.append(
            '<ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>'
        )
        final_encryption_tags.append("<ds:DigestValue></ds:DigestValue>")
        final_encryption_tags.append("</ds:Reference>")
        final_encryption_tags.append(
            '<ds:Reference Type="http://www.w3.org/2000/09/xmldsig#SignatureProperties" URI="#xadesSignedProperties">'
        )
        final_encryption_tags.append(
            '<ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>'
        )
        final_encryption_tags.append("<ds:DigestValue></ds:DigestValue>")
        final_encryption_tags.append("</ds:Reference>")
        final_encryption_tags.append("</ds:SignedInfo>")
        final_encryption_tags.append("<ds:SignatureValue></ds:SignatureValue>")
        final_encryption_tags.append("<ds:KeyInfo>")
        final_encryption_tags.append("<ds:X509Data>")
        final_encryption_tags.append("<ds:X509Certificate></ds:X509Certificate>")
        final_encryption_tags.append("</ds:X509Data>")
        final_encryption_tags.append("</ds:KeyInfo>")
        final_encryption_tags.append("<ds:Object>")
        final_encryption_tags.append(
            '<xades:QualifyingProperties xmlns:xades="http://uri.etsi.org/01903/v1.3.2#" Target="signature">'
        )
        final_encryption_tags.append(
            '<xades:SignedProperties Id="xadesSignedProperties">'
        )
        final_encryption_tags.append("<xades:SignedSignatureProperties>")
        final_encryption_tags.append("<xades:SigningTime></xades:SigningTime>")
        final_encryption_tags.append("<xades:SigningCertificate>")
        final_encryption_tags.append("<xades:Cert>")
        final_encryption_tags.append("<xades:CertDigest>")
        final_encryption_tags.append(
            '<ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>'
        )
        final_encryption_tags.append("<ds:DigestValue></ds:DigestValue>")
        final_encryption_tags.append("</xades:CertDigest>")
        final_encryption_tags.append("<xades:IssuerSerial>")
        final_encryption_tags.append("<ds:X509IssuerName></ds:X509IssuerName>")
        final_encryption_tags.append("<ds:X509SerialNumber></ds:X509SerialNumber>")
        final_encryption_tags.append("</xades:IssuerSerial>")
        final_encryption_tags.append("</xades:Cert>")
        final_encryption_tags.append("</xades:SigningCertificate>")
        final_encryption_tags.append("</xades:SignedSignatureProperties>")
        final_encryption_tags.append("</xades:SignedProperties>")
        final_encryption_tags.append("</xades:QualifyingProperties>")
        final_encryption_tags.append("</ds:Object>")
        final_encryption_tags.append("</ds:Signature>")
        final_encryption_tags.append("</sac:SignatureInformation>")
        final_encryption_tags.append("</sig:UBLDocumentSignatures>")
        final_encryption_tags.append("</ext:ExtensionContent>")
        final_encryption_tags.append("</ext:UBLExtension>")
        final_encryption_tags.append("</ext:UBLExtensions>")

        return "\n".join(final_encryption_tags)

    ################################
    #
    ################################

    def create_the_tags_of_the_information():
        final_information_tags = []

        final_information_tags.append("<cbc:ProfileID>reporting:1.0</cbc:ProfileID>")
        final_information_tags.append(
            "<cbc:ID>{}</cbc:ID>".format(invoice_data.get("invoice_number"))
        )
        final_information_tags.append(
            "<cbc:UUID>{}</cbc:UUID>".format(invoice_data.get("invoice_uuid"))
        )
        final_information_tags.append(
            "<cbc:IssueDate>{}</cbc:IssueDate>".format(
                invoice_data.get("invoice_issue_date")
            )
        )
        final_information_tags.append(
            "<cbc:IssueTime>{}</cbc:IssueTime>".format(
                invoice_data.get("invoice_issue_time")
            )
        )
        final_information_tags.append(
            '<cbc:InvoiceTypeCode name="{}">{}</cbc:InvoiceTypeCode>'.format(
                invoice_data.get("invoice_type_code"),
                invoice_data.get("invoice_type_number"),
            )
        )
        final_information_tags.append('<cbc:Note languageID="ar">ABC</cbc:Note>')
        final_information_tags.append(
            "<cbc:DocumentCurrencyCode>SAR</cbc:DocumentCurrencyCode>"
        )
        final_information_tags.append("<cbc:TaxCurrencyCode>SAR</cbc:TaxCurrencyCode>")

        return "\n".join(final_information_tags)

    def create_the_tag_of_the_source_invoice():
        if invoice_data.get("billingreference_number"):
            final_source_tags = []
            final_source_tags.append("<cac:BillingReference>")
            final_source_tags.append("<cac:InvoiceDocumentReference>")
            final_source_tags.append(
                "<cbc:ID>{}</cbc:ID>".format(
                    invoice_data.get("billingreference_number")
                )
            )
            final_source_tags.append("</cac:InvoiceDocumentReference>")
            final_source_tags.append("</cac:BillingReference>")

            return "\n".join(final_source_tags)
        else:
            return ""

    ################################
    #
    ################################

    def create_counter_tag():
        final_counter_tags = []

        final_counter_tags.append("<cac:AdditionalDocumentReference>")
        final_counter_tags.append("<cbc:ID>ICV</cbc:ID>")
        final_counter_tags.append(
            "<cbc:UUID>{}</cbc:UUID>".format(invoice_data.get("the_counter"))
        )
        final_counter_tags.append("</cac:AdditionalDocumentReference>")

        return "\n".join(final_counter_tags)

    ################################
    #
    ################################

    def create_PIH_tag():
        final_PIH_tag = []

        final_PIH_tag.append("<cac:AdditionalDocumentReference>")
        final_PIH_tag.append("<cbc:ID>PIH</cbc:ID>")
        final_PIH_tag.append("<cac:Attachment>")
        final_PIH_tag.append(
            '<cbc:EmbeddedDocumentBinaryObject mimeCode="text/plain">{}</cbc:EmbeddedDocumentBinaryObject>'.format(
                invoice_data.get("the_PIH")
            )
        )
        final_PIH_tag.append("</cac:Attachment>")
        final_PIH_tag.append("</cac:AdditionalDocumentReference>")

        return "\n".join(final_PIH_tag)

    ################################
    #
    ################################

    def create_QR_tag():
        final_QR_tag = []

        final_QR_tag.append("<cac:AdditionalDocumentReference>")
        final_QR_tag.append("<cbc:ID>QR</cbc:ID>")
        final_QR_tag.append("<cac:Attachment>")
        final_QR_tag.append(
            '<cbc:EmbeddedDocumentBinaryObject mimeCode="text/plain"></cbc:EmbeddedDocumentBinaryObject>'
        )
        final_QR_tag.append("</cac:Attachment>")
        final_QR_tag.append("</cac:AdditionalDocumentReference>")

        return "\n".join(final_QR_tag)

    ################################
    #
    ################################

    def create_signature_tag():
        final_signature_tag = []

        final_signature_tag.append("<cac:Signature>")
        final_signature_tag.append(
            "<cbc:ID>urn:oasis:names:specification:ubl:signature:Invoice</cbc:ID>"
        )
        final_signature_tag.append(
            "<cbc:SignatureMethod>urn:oasis:names:specification:ubl:dsig:enveloped:xades</cbc:SignatureMethod>"
        )
        final_signature_tag.append("</cac:Signature>")

        return "\n".join(final_signature_tag)

    ################################
    #
    ################################

    def create_supplier_party_tag():
        final_supplier_party_tag = []

        final_supplier_party_tag.append("<cac:AccountingSupplierParty>")

        if (
            (
                (seller_data.get("type_of_PartyIdentification"))
                and (seller_data.get("PartyIdentification"))
            )
            or seller_data.get("StreetName")
            or seller_data.get("AdditionalStreetName")
            or seller_data.get("BuildingNumber")
            or seller_data.get("PlotIdentification")
            or seller_data.get("CitySubdivisionName")
            or seller_data.get("CityName")
            or seller_data.get("PostalZone")
            or seller_data.get("CountrySubentity")
            or seller_data.get("country_IdentificationCode")
            or seller_data.get("vat_registration_number_CompanyID")
            or seller_data.get("RegistrationName")
        ):
            final_supplier_party_tag.append("<cac:Party>")

            if (seller_data.get("type_of_PartyIdentification")) and (
                seller_data.get("PartyIdentification")
            ):
                final_supplier_party_tag.append("<cac:PartyIdentification>")
                final_supplier_party_tag.append(
                    '<cbc:ID schemeID="{}">{}</cbc:ID>'.format(
                        seller_data.get("type_of_PartyIdentification"),
                        seller_data.get("PartyIdentification"),
                    )
                )
                final_supplier_party_tag.append("</cac:PartyIdentification>")

            if (
                seller_data.get("StreetName")
                or seller_data.get("AdditionalStreetName")
                or seller_data.get("BuildingNumber")
                or seller_data.get("PlotIdentification")
                or seller_data.get("CitySubdivisionName")
                or seller_data.get("CityName")
                or seller_data.get("PostalZone")
                or seller_data.get("CountrySubentity")
                or seller_data.get("country_IdentificationCode")
            ):
                final_supplier_party_tag.append("<cac:PostalAddress>")

                if seller_data.get("StreetName"):
                    final_supplier_party_tag.append(
                        "<cbc:StreetName>{}</cbc:StreetName>".format(
                            seller_data.get("StreetName")
                        )
                    )

                if seller_data.get("AdditionalStreetName"):
                    final_supplier_party_tag.append(
                        "<cbc:AdditionalStreetName>{}</cbc:AdditionalStreetName>".format(
                            seller_data.get("AdditionalStreetName")
                        )
                    )

                if seller_data.get("BuildingNumber"):
                    final_supplier_party_tag.append(
                        "<cbc:BuildingNumber>{}</cbc:BuildingNumber>".format(
                            seller_data.get("BuildingNumber")
                        )
                    )

                if seller_data.get("PlotIdentification"):
                    final_supplier_party_tag.append(
                        "<cbc:PlotIdentification>{}</cbc:PlotIdentification>".format(
                            seller_data.get("PlotIdentification")
                        )
                    )

                if seller_data.get("CitySubdivisionName"):
                    final_supplier_party_tag.append(
                        "<cbc:CitySubdivisionName>{}</cbc:CitySubdivisionName>".format(
                            seller_data.get("CitySubdivisionName")
                        )
                    )

                if seller_data.get("CityName"):
                    final_supplier_party_tag.append(
                        "<cbc:CityName>{}</cbc:CityName>".format(
                            seller_data.get("CityName")
                        )
                    )

                if seller_data.get("PostalZone"):
                    final_supplier_party_tag.append(
                        "<cbc:PostalZone>{}</cbc:PostalZone>".format(
                            seller_data.get("PostalZone")
                        )
                    )

                if seller_data.get("CountrySubentity"):
                    final_supplier_party_tag.append(
                        "<cbc:CountrySubentity>{}</cbc:CountrySubentity>".format(
                            seller_data.get("CountrySubentity")
                        )
                    )

                if seller_data.get("country_IdentificationCode"):
                    final_supplier_party_tag.append("<cac:Country>")
                    final_supplier_party_tag.append(
                        "<cbc:IdentificationCode>{}</cbc:IdentificationCode>".format(
                            seller_data.get("country_IdentificationCode")
                        )
                    )
                    final_supplier_party_tag.append("</cac:Country>")

                final_supplier_party_tag.append("</cac:PostalAddress>")

            if seller_data.get("vat_registration_number_CompanyID"):
                final_supplier_party_tag.append("<cac:PartyTaxScheme>")
                final_supplier_party_tag.append(
                    "<cbc:CompanyID>{}</cbc:CompanyID>".format(
                        seller_data.get("vat_registration_number_CompanyID")
                    )
                )
                final_supplier_party_tag.append("<cac:TaxScheme>")
                final_supplier_party_tag.append("<cbc:ID>VAT</cbc:ID>")
                final_supplier_party_tag.append("</cac:TaxScheme>")
                final_supplier_party_tag.append("</cac:PartyTaxScheme>")

            if seller_data.get("RegistrationName"):
                final_supplier_party_tag.append("<cac:PartyLegalEntity>")
                final_supplier_party_tag.append(
                    "<cbc:RegistrationName>{}</cbc:RegistrationName>".format(
                        seller_data.get("RegistrationName")
                    )
                )
                final_supplier_party_tag.append("</cac:PartyLegalEntity>")

            final_supplier_party_tag.append("</cac:Party>")

        final_supplier_party_tag.append("</cac:AccountingSupplierParty>")

        return "\n".join(final_supplier_party_tag)

    ################################
    #
    ################################

    def create_customer_party_tag():
        final_customer_party_tag = []

        final_customer_party_tag.append("<cac:AccountingCustomerParty>")

        if (
            (
                (customer_data.get("type_of_PartyIdentification"))
                and (customer_data.get("PartyIdentification"))
            )
            or customer_data.get("StreetName")
            or customer_data.get("AdditionalStreetName")
            or customer_data.get("BuildingNumber")
            or customer_data.get("PlotIdentification")
            or customer_data.get("CitySubdivisionName")
            or customer_data.get("CityName")
            or customer_data.get("PostalZone")
            or customer_data.get("CountrySubentity")
            or customer_data.get("country_IdentificationCode")
            or customer_data.get("vat_registration_number_CompanyID")
            or customer_data.get("RegistrationName")
        ):
            final_customer_party_tag.append("<cac:Party>")

            if (customer_data.get("type_of_PartyIdentification")) and (
                customer_data.get("PartyIdentification")
            ):
                final_customer_party_tag.append("<cac:PartyIdentification>")
                final_customer_party_tag.append(
                    '<cbc:ID schemeID="{}">{}</cbc:ID>'.format(
                        customer_data.get("type_of_PartyIdentification"),
                        customer_data.get("PartyIdentification"),
                    )
                )
                final_customer_party_tag.append("</cac:PartyIdentification>")

            if (
                customer_data.get("StreetName")
                or customer_data.get("AdditionalStreetName")
                or customer_data.get("BuildingNumber")
                or customer_data.get("PlotIdentification")
                or customer_data.get("CitySubdivisionName")
                or customer_data.get("CityName")
                or customer_data.get("PostalZone")
                or customer_data.get("CountrySubentity")
                or customer_data.get("country_IdentificationCode")
            ):
                final_customer_party_tag.append("<cac:PostalAddress>")

                if customer_data.get("StreetName"):
                    final_customer_party_tag.append(
                        "<cbc:StreetName>{}</cbc:StreetName>".format(
                            customer_data.get("StreetName")
                        )
                    )

                if customer_data.get("AdditionalStreetName"):
                    final_customer_party_tag.append(
                        "<cbc:AdditionalStreetName>{}</cbc:AdditionalStreetName>".format(
                            customer_data.get("AdditionalStreetName")
                        )
                    )

                if customer_data.get("BuildingNumber"):
                    final_customer_party_tag.append(
                        "<cbc:BuildingNumber>{}</cbc:BuildingNumber>".format(
                            customer_data.get("BuildingNumber")
                        )
                    )

                if customer_data.get("PlotIdentification"):
                    final_customer_party_tag.append(
                        "<cbc:PlotIdentification>{}</cbc:PlotIdentification>".format(
                            customer_data.get("PlotIdentification")
                        )
                    )

                if customer_data.get("CitySubdivisionName"):
                    final_customer_party_tag.append(
                        "<cbc:CitySubdivisionName>{}</cbc:CitySubdivisionName>".format(
                            customer_data.get("CitySubdivisionName")
                        )
                    )

                if customer_data.get("CityName"):
                    final_customer_party_tag.append(
                        "<cbc:CityName>{}</cbc:CityName>".format(
                            customer_data.get("CityName")
                        )
                    )

                if customer_data.get("PostalZone"):
                    final_customer_party_tag.append(
                        "<cbc:PostalZone>{}</cbc:PostalZone>".format(
                            customer_data.get("PostalZone")
                        )
                    )

                if customer_data.get("CountrySubentity"):
                    final_customer_party_tag.append(
                        "<cbc:CountrySubentity>{}</cbc:CountrySubentity>".format(
                            customer_data.get("CountrySubentity")
                        )
                    )

                if customer_data.get("country_IdentificationCode"):
                    final_customer_party_tag.append("<cac:Country>")
                    final_customer_party_tag.append(
                        "<cbc:IdentificationCode>{}</cbc:IdentificationCode>".format(
                            customer_data.get("country_IdentificationCode")
                        )
                    )
                    final_customer_party_tag.append("</cac:Country>")

                final_customer_party_tag.append("</cac:PostalAddress>")

            if customer_data.get("vat_registration_number_CompanyID"):
                final_customer_party_tag.append("<cac:PartyTaxScheme>")
                final_customer_party_tag.append(
                    "<cbc:CompanyID>{}</cbc:CompanyID>".format(
                        customer_data.get("vat_registration_number_CompanyID")
                    )
                )
                final_customer_party_tag.append("<cac:TaxScheme>")
                final_customer_party_tag.append("<cbc:ID>VAT</cbc:ID>")
                final_customer_party_tag.append("</cac:TaxScheme>")
                final_customer_party_tag.append("</cac:PartyTaxScheme>")

            if customer_data.get("RegistrationName"):
                final_customer_party_tag.append("<cac:PartyLegalEntity>")
                final_customer_party_tag.append(
                    "<cbc:RegistrationName>{}</cbc:RegistrationName>".format(
                        customer_data.get("RegistrationName")
                    )
                )
                final_customer_party_tag.append("</cac:PartyLegalEntity>")

            final_customer_party_tag.append("</cac:Party>")

        final_customer_party_tag.append("</cac:AccountingCustomerParty>")

        return "\n".join(final_customer_party_tag)

    ################################
    #
    ################################

    # "Delivery": {
    #         "ActualDeliveryDate": credit_supply_date,
    #         # "LatestDeliveryDate": ""
    #     },
    def create_delivery_tag():
        final_delivery_means_tag = []

        final_delivery_means_tag.append("<cac:Delivery>")
        final_delivery_means_tag.append(
            "<cbc:ActualDeliveryDate>{}</cbc:ActualDeliveryDate>".format(
                delivery_data.get("actual_delivery_date")
            )
        )

        final_delivery_means_tag.append("</cac:Delivery>")

        return "\n".join(final_delivery_means_tag)

    def create_payment_means_tag():
        final_payment_means_tag = []

        final_payment_means_tag.append("<cac:PaymentMeans>")
        final_payment_means_tag.append(
            "<cbc:PaymentMeansCode>{}</cbc:PaymentMeansCode>".format(
                payment_data.get("payment_method")
            )
        )

        if payment_data.get("payment_reason"):
            final_payment_means_tag.append(
                "<cbc:InstructionNote>{}</cbc:InstructionNote>".format(
                    payment_data.get("payment_reason")
                )
            )

        final_payment_means_tag.append("</cac:PaymentMeans>")

        return "\n".join(final_payment_means_tag)

    def create_allowance_charge_tag():
        final_allowance_charge_tag = []

        # AllowanceCharge for charge

        for i in each_kind_total:
            the_charge_amount = charge_on_totals.get("charge_value")
            the_charged_amount = number_with_n_digits_after_the_point(
                round(after_charge_each_kind_total.get(i) - each_kind_total.get(i), 10)
            )
            the_amount_before_charge = each_kind_total.get(i)

            final_allowance_charge_tag.append("<cac:AllowanceCharge>")
            final_allowance_charge_tag.append(
                "<cbc:ChargeIndicator>true</cbc:ChargeIndicator>"
            )
            final_allowance_charge_tag.append(
                "<cbc:AllowanceChargeReasonCode>CG</cbc:AllowanceChargeReasonCode>"
            )
            final_allowance_charge_tag.append(
                "<cbc:AllowanceChargeReason>Cleaning</cbc:AllowanceChargeReason>"
            )

            if charge_on_totals.get("charge_type") == "percentage":
                final_allowance_charge_tag.append(
                    "<cbc:MultiplierFactorNumeric>{}</cbc:MultiplierFactorNumeric>".format(
                        the_charge_amount
                    )
                )
                final_allowance_charge_tag.append(
                    '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                        the_charged_amount
                    )
                )
                final_allowance_charge_tag.append(
                    '<cbc:BaseAmount currencyID="SAR">{}</cbc:BaseAmount>'.format(
                        the_amount_before_charge
                    )
                )
            else:
                final_allowance_charge_tag.append(
                    '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                        the_charged_amount
                    )
                )

            final_allowance_charge_tag.append("<cac:TaxCategory>")
            final_allowance_charge_tag.append(
                '<cbc:ID schemeID="UN/ECE 5305" schemeAgencyID="6">{}</cbc:ID>'.format(
                    i
                )
            )
            final_allowance_charge_tag.append("<cbc:Percent>0.0</cbc:Percent>")
            final_allowance_charge_tag.append("<cac:TaxScheme>")
            final_allowance_charge_tag.append(
                '<cbc:ID schemeID="UN/ECE 5153" schemeAgencyID="6">VAT</cbc:ID>'
            )
            final_allowance_charge_tag.append("</cac:TaxScheme>")
            final_allowance_charge_tag.append("</cac:TaxCategory>")
            final_allowance_charge_tag.append("</cac:AllowanceCharge>")
            final_allowance_charge_tag.append("\n")

        for i in each_tax_total:
            the_charge_amount = charge_on_totals.get("charge_value")
            the_charged_amount = number_with_n_digits_after_the_point(
                round(after_charge_each_tax_total.get(i) - each_tax_total.get(i), 10)
            )
            the_amount_before_charge = each_tax_total.get(i)

            final_allowance_charge_tag.append("<cac:AllowanceCharge>")
            final_allowance_charge_tag.append(
                "<cbc:ChargeIndicator>true</cbc:ChargeIndicator>"
            )
            final_allowance_charge_tag.append(
                "<cbc:AllowanceChargeReasonCode>CG</cbc:AllowanceChargeReasonCode>"
            )
            final_allowance_charge_tag.append(
                "<cbc:AllowanceChargeReason>Cleaning</cbc:AllowanceChargeReason>"
            )

            if charge_on_totals.get("charge_type") == "percentage":
                final_allowance_charge_tag.append(
                    "<cbc:MultiplierFactorNumeric>{}</cbc:MultiplierFactorNumeric>".format(
                        the_charge_amount
                    )
                )
                final_allowance_charge_tag.append(
                    '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                        the_charged_amount
                    )
                )
                final_allowance_charge_tag.append(
                    '<cbc:BaseAmount currencyID="SAR">{}</cbc:BaseAmount>'.format(
                        the_amount_before_charge
                    )
                )
            else:
                final_allowance_charge_tag.append(
                    '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                        the_charged_amount
                    )
                )

            final_allowance_charge_tag.append("<cac:TaxCategory>")
            final_allowance_charge_tag.append(
                '<cbc:ID schemeID="UN/ECE 5305" schemeAgencyID="6">S</cbc:ID>'
            )
            final_allowance_charge_tag.append("<cbc:Percent>{}</cbc:Percent>".format(i))
            final_allowance_charge_tag.append("<cac:TaxScheme>")
            final_allowance_charge_tag.append(
                '<cbc:ID schemeID="UN/ECE 5153" schemeAgencyID="6">VAT</cbc:ID>'
            )
            final_allowance_charge_tag.append("</cac:TaxScheme>")
            final_allowance_charge_tag.append("</cac:TaxCategory>")
            final_allowance_charge_tag.append("</cac:AllowanceCharge>")
            final_allowance_charge_tag.append("\n")

        # AllowanceCharge for discount

        for i in each_kind_total:
            the_discount_amount = discount_on_totals.get("discount_value")
            the_discounted_amount = number_with_n_digits_after_the_point(
                round(
                    each_kind_total.get(i) - after_discount_each_kind_total.get(i), 10
                )
            )
            the_amount_before_discount = each_kind_total.get(i)

            final_allowance_charge_tag.append("<cac:AllowanceCharge>")
            final_allowance_charge_tag.append(
                "<cbc:ChargeIndicator>false</cbc:ChargeIndicator>"
            )
            final_allowance_charge_tag.append(
                "<cbc:AllowanceChargeReasonCode>95</cbc:AllowanceChargeReasonCode>"
            )
            final_allowance_charge_tag.append(
                "<cbc:AllowanceChargeReason>Discount</cbc:AllowanceChargeReason>"
            )

            if discount_on_totals.get("discount_type") == "percentage":
                final_allowance_charge_tag.append(
                    "<cbc:MultiplierFactorNumeric>{}</cbc:MultiplierFactorNumeric>".format(
                        the_discount_amount
                    )
                )
                final_allowance_charge_tag.append(
                    '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                        the_discounted_amount
                    )
                )
                final_allowance_charge_tag.append(
                    '<cbc:BaseAmount currencyID="SAR">{}</cbc:BaseAmount>'.format(
                        the_amount_before_discount
                    )
                )
            else:
                final_allowance_charge_tag.append(
                    '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                        the_discounted_amount
                    )
                )

            final_allowance_charge_tag.append("<cac:TaxCategory>")
            final_allowance_charge_tag.append(
                '<cbc:ID schemeID="UN/ECE 5305" schemeAgencyID="6">{}</cbc:ID>'.format(
                    i
                )
            )
            final_allowance_charge_tag.append("<cbc:Percent>0.0</cbc:Percent>")
            final_allowance_charge_tag.append("<cac:TaxScheme>")
            final_allowance_charge_tag.append(
                '<cbc:ID schemeID="UN/ECE 5153" schemeAgencyID="6">VAT</cbc:ID>'
            )
            final_allowance_charge_tag.append("</cac:TaxScheme>")
            final_allowance_charge_tag.append("</cac:TaxCategory>")
            final_allowance_charge_tag.append("</cac:AllowanceCharge>")
            final_allowance_charge_tag.append("\n")

        for i in each_tax_total:
            the_discount_amount = discount_on_totals.get("discount_value")
            the_discounted_amount = number_with_n_digits_after_the_point(
                round(each_tax_total.get(i) - after_discount_each_tax_total.get(i), 10)
            )
            the_amount_before_discount = each_tax_total.get(i)

            final_allowance_charge_tag.append("<cac:AllowanceCharge>")
            final_allowance_charge_tag.append(
                "<cbc:ChargeIndicator>false</cbc:ChargeIndicator>"
            )
            final_allowance_charge_tag.append(
                "<cbc:AllowanceChargeReasonCode>95</cbc:AllowanceChargeReasonCode>"
            )
            final_allowance_charge_tag.append(
                "<cbc:AllowanceChargeReason>Discount</cbc:AllowanceChargeReason>"
            )

            if discount_on_totals.get("discount_type") == "percentage":
                final_allowance_charge_tag.append(
                    "<cbc:MultiplierFactorNumeric>{}</cbc:MultiplierFactorNumeric>".format(
                        the_discount_amount
                    )
                )
                final_allowance_charge_tag.append(
                    '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                        the_discounted_amount
                    )
                )
                final_allowance_charge_tag.append(
                    '<cbc:BaseAmount currencyID="SAR">{}</cbc:BaseAmount>'.format(
                        the_amount_before_discount
                    )
                )
            else:
                final_allowance_charge_tag.append(
                    '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                        the_discounted_amount
                    )
                )

            final_allowance_charge_tag.append("<cac:TaxCategory>")
            final_allowance_charge_tag.append(
                '<cbc:ID schemeID="UN/ECE 5305" schemeAgencyID="6">S</cbc:ID>'
            )
            final_allowance_charge_tag.append("<cbc:Percent>{}</cbc:Percent>".format(i))
            final_allowance_charge_tag.append("<cac:TaxScheme>")
            final_allowance_charge_tag.append(
                '<cbc:ID schemeID="UN/ECE 5153" schemeAgencyID="6">VAT</cbc:ID>'
            )
            final_allowance_charge_tag.append("</cac:TaxScheme>")
            final_allowance_charge_tag.append("</cac:TaxCategory>")
            final_allowance_charge_tag.append("</cac:AllowanceCharge>")
            final_allowance_charge_tag.append("\n")

        return "\n".join(final_allowance_charge_tag)

    def create_tax_total_tags():
        TaxExemptionReasonCode_and_TaxExemptionReason = {}

        final_tax_total_tags = []
        TaxSubtotal_tags_list = []

        # for i in after_discount_each_tax_total:
        #     the_total_without_tax = after_discount_each_tax_total.get(i)

        #     the_total_tax = number_with_n_digits_after_the_point(round(after_discount_each_tax_total.get(i) * (i / 100) , 10))

        #     TaxSubtotal_tags_list.append("<cac:TaxSubtotal>")
        #     TaxSubtotal_tags_list.append("<cbc:TaxableAmount currencyID=\"SAR\">{}</cbc:TaxableAmount>".format(the_total_without_tax))
        #     TaxSubtotal_tags_list.append("<cbc:TaxAmount currencyID=\"SAR\">{}</cbc:TaxAmount>".format(the_total_tax))
        #     TaxSubtotal_tags_list.append("<cac:TaxCategory>")
        #     TaxSubtotal_tags_list.append("<cbc:ID schemeID=\"UN/ECE 5305\" schemeAgencyID=\"6\">S</cbc:ID>")
        #     TaxSubtotal_tags_list.append("<cbc:Percent>{}</cbc:Percent>".format(i))
        #     TaxSubtotal_tags_list.append("<cac:TaxScheme>")
        #     TaxSubtotal_tags_list.append("<cbc:ID schemeID=\"UN/ECE 5153\" schemeAgencyID=\"6\">VAT</cbc:ID>")
        #     TaxSubtotal_tags_list.append("</cac:TaxScheme>")
        #     TaxSubtotal_tags_list.append("</cac:TaxCategory>")
        #     TaxSubtotal_tags_list.append("</cac:TaxSubtotal>")
        #     TaxSubtotal_tags_list.append("\n")

        # for i in after_discount_each_kind_total:
        #     for product in products:
        #         TaxExemptionReasonCode_and_TaxExemptionReason.update({product.get("tax_id_letter") : {"TaxExemptionReasonCode":product.get("exemption_code"),
        #                                                                                             "TaxExemptionReason":product.get("exemption_reason")}})

        #     the_total_without_tax = after_discount_each_kind_total.get(i)
        #     TaxExemptionReasonCode = TaxExemptionReasonCode_and_TaxExemptionReason.get(i).get("TaxExemptionReasonCode")
        #     TaxExemptionReason = TaxExemptionReasonCode_and_TaxExemptionReason.get(i).get("TaxExemptionReason")

        #     TaxSubtotal_tags_list.append("<cac:TaxSubtotal>")
        #     TaxSubtotal_tags_list.append("<cbc:TaxableAmount currencyID=\"SAR\">{}</cbc:TaxableAmount>".format(the_total_without_tax))
        #     TaxSubtotal_tags_list.append("<cbc:TaxAmount currencyID=\"SAR\">0.0</cbc:TaxAmount>")
        #     TaxSubtotal_tags_list.append("<cac:TaxCategory>")
        #     TaxSubtotal_tags_list.append("<cbc:ID schemeID=\"UN/ECE 5305\" schemeAgencyID=\"6\">{}</cbc:ID>".format(i))
        #     TaxSubtotal_tags_list.append("<cbc:Percent>0.00</cbc:Percent>")
        #     TaxSubtotal_tags_list.append("<cbc:TaxExemptionReasonCode>{}</cbc:TaxExemptionReasonCode>".format(TaxExemptionReasonCode))
        #     TaxSubtotal_tags_list.append("<cbc:TaxExemptionReason>{}</cbc:TaxExemptionReason>".format(TaxExemptionReason))
        #     TaxSubtotal_tags_list.append("<cac:TaxScheme>")
        #     TaxSubtotal_tags_list.append("<cbc:ID schemeID=\"UN/ECE 5153\" schemeAgencyID=\"6\">VAT</cbc:ID>")
        #     TaxSubtotal_tags_list.append("</cac:TaxScheme>")
        #     TaxSubtotal_tags_list.append("</cac:TaxCategory>")
        #     TaxSubtotal_tags_list.append("</cac:TaxSubtotal>")
        #     TaxSubtotal_tags_list.append("\n")

        for i in each_tax_total:
            the_total_without_discount_and_without_charge_and_without_tax = (
                each_tax_total.get(i)
            )
            the_discounted_amount = number_with_n_digits_after_the_point(
                round(each_tax_total.get(i) - after_discount_each_tax_total.get(i), 10)
            )
            the_charged_amount = number_with_n_digits_after_the_point(
                round(after_charge_each_tax_total.get(i) - each_tax_total.get(i), 10)
            )
            the_total_with_discount_and_with_charge_and_without_tax = (
                number_with_n_digits_after_the_point(
                    round(
                        the_total_without_discount_and_without_charge_and_without_tax
                        + the_charged_amount
                        - the_discounted_amount,
                        10,
                    )
                )
            )
            the_total_tax = number_with_n_digits_after_the_point(
                round(
                    the_total_with_discount_and_with_charge_and_without_tax * (i / 100),
                    10,
                )
            )

            TaxSubtotal_tags_list.append("<cac:TaxSubtotal>")
            TaxSubtotal_tags_list.append(
                '<cbc:TaxableAmount currencyID="SAR">{}</cbc:TaxableAmount>'.format(
                    the_total_with_discount_and_with_charge_and_without_tax
                )
            )
            TaxSubtotal_tags_list.append(
                '<cbc:TaxAmount currencyID="SAR">{}</cbc:TaxAmount>'.format(
                    the_total_tax
                )
            )
            TaxSubtotal_tags_list.append("<cac:TaxCategory>")
            TaxSubtotal_tags_list.append(
                '<cbc:ID schemeID="UN/ECE 5305" schemeAgencyID="6">S</cbc:ID>'
            )
            TaxSubtotal_tags_list.append("<cbc:Percent>{}</cbc:Percent>".format(i))
            TaxSubtotal_tags_list.append("<cac:TaxScheme>")
            TaxSubtotal_tags_list.append(
                '<cbc:ID schemeID="UN/ECE 5153" schemeAgencyID="6">VAT</cbc:ID>'
            )
            TaxSubtotal_tags_list.append("</cac:TaxScheme>")
            TaxSubtotal_tags_list.append("</cac:TaxCategory>")
            TaxSubtotal_tags_list.append("</cac:TaxSubtotal>")
            TaxSubtotal_tags_list.append("\n")

        # this code below does not put more than one TaxExemptionReasonCode for each letter :

        for i in each_kind_total:
            for product in products:
                TaxExemptionReasonCode_and_TaxExemptionReason.update(
                    {
                        product.get("tax_id_letter"): {
                            "TaxExemptionReasonCode": product.get("exemption_code"),
                            "TaxExemptionReason": product.get("exemption_reason"),
                        }
                    }
                )

            the_total_without_discount_and_without_charge_and_without_tax = (
                each_kind_total.get(i)
            )
            the_discounted_amount = number_with_n_digits_after_the_point(
                round(
                    each_kind_total.get(i) - after_discount_each_kind_total.get(i), 10
                )
            )
            the_charged_amount = number_with_n_digits_after_the_point(
                round(after_charge_each_kind_total.get(i) - each_kind_total.get(i), 10)
            )
            the_total_with_discount_and_with_charge_and_without_tax = (
                number_with_n_digits_after_the_point(
                    round(
                        the_total_without_discount_and_without_charge_and_without_tax
                        + the_charged_amount
                        - the_discounted_amount,
                        10,
                    )
                )
            )

            TaxExemptionReasonCode = TaxExemptionReasonCode_and_TaxExemptionReason.get(
                i
            ).get("TaxExemptionReasonCode")
            TaxExemptionReason = TaxExemptionReasonCode_and_TaxExemptionReason.get(
                i
            ).get("TaxExemptionReason")

            TaxSubtotal_tags_list.append("<cac:TaxSubtotal>")
            TaxSubtotal_tags_list.append(
                '<cbc:TaxableAmount currencyID="SAR">{}</cbc:TaxableAmount>'.format(
                    the_total_with_discount_and_with_charge_and_without_tax
                )
            )
            TaxSubtotal_tags_list.append(
                '<cbc:TaxAmount currencyID="SAR">0.0</cbc:TaxAmount>'
            )
            TaxSubtotal_tags_list.append("<cac:TaxCategory>")
            TaxSubtotal_tags_list.append(
                '<cbc:ID schemeID="UN/ECE 5305" schemeAgencyID="6">{}</cbc:ID>'.format(
                    i
                )
            )
            TaxSubtotal_tags_list.append("<cbc:Percent>0.00</cbc:Percent>")
            TaxSubtotal_tags_list.append(
                "<cbc:TaxExemptionReasonCode>{}</cbc:TaxExemptionReasonCode>".format(
                    TaxExemptionReasonCode
                )
            )
            TaxSubtotal_tags_list.append(
                "<cbc:TaxExemptionReason>{}</cbc:TaxExemptionReason>".format(
                    TaxExemptionReason
                )
            )
            TaxSubtotal_tags_list.append("<cac:TaxScheme>")
            TaxSubtotal_tags_list.append(
                '<cbc:ID schemeID="UN/ECE 5153" schemeAgencyID="6">VAT</cbc:ID>'
            )
            TaxSubtotal_tags_list.append("</cac:TaxScheme>")
            TaxSubtotal_tags_list.append("</cac:TaxCategory>")
            TaxSubtotal_tags_list.append("</cac:TaxSubtotal>")
            TaxSubtotal_tags_list.append("\n")

        # if you want to put more than one TaxExemptionReasonCode for one letter you have to comment in the code below :

        # for i in each_kind_total:
        #     TaxExemptionReasons_dictionary = {}
        #     for product in products:
        #         if product.get("tax_id_letter") == i:
        #             TaxExemptionReasons_dictionary.update({product.get("exemption_code"):product.get("exemption_reason")})

        #     for TaxExemptionReason in TaxExemptionReasons_dictionary:

        #         the_total_without_discount_and_without_charge_and_without_tax = each_kind_total.get(i)
        #         the_discounted_amount = number_with_n_digits_after_the_point(round(each_kind_total.get(i) - after_discount_each_kind_total.get(i) , 10))
        #         the_charged_amount = number_with_n_digits_after_the_point(round(after_charge_each_kind_total.get(i) - each_kind_total.get(i) , 10))
        #         the_total_with_discount_and_with_charge_and_without_tax = number_with_n_digits_after_the_point(round(the_total_without_discount_and_without_charge_and_without_tax + the_charged_amount - the_discounted_amount , 10))

        #         TaxExemptionReasonCode = TaxExemptionReason
        #         TaxExemptionReason = TaxExemptionReasons_dictionary.get(TaxExemptionReason)

        #         TaxSubtotal_tags_list.append("<cac:TaxSubtotal>")
        #         TaxSubtotal_tags_list.append("<cbc:TaxableAmount currencyID=\"SAR\">{}</cbc:TaxableAmount>".format(the_total_with_discount_and_with_charge_and_without_tax))
        #         TaxSubtotal_tags_list.append("<cbc:TaxAmount currencyID=\"SAR\">0.0</cbc:TaxAmount>")
        #         TaxSubtotal_tags_list.append("<cac:TaxCategory>")
        #         TaxSubtotal_tags_list.append("<cbc:ID schemeID=\"UN/ECE 5305\" schemeAgencyID=\"6\">{}</cbc:ID>".format(i))
        #         TaxSubtotal_tags_list.append("<cbc:Percent>0.00</cbc:Percent>")
        #         TaxSubtotal_tags_list.append("<cbc:TaxExemptionReasonCode>{}</cbc:TaxExemptionReasonCode>".format(TaxExemptionReasonCode))
        #         TaxSubtotal_tags_list.append("<cbc:TaxExemptionReason>{}</cbc:TaxExemptionReason>".format(TaxExemptionReason))
        #         TaxSubtotal_tags_list.append("<cac:TaxScheme>")
        #         TaxSubtotal_tags_list.append("<cbc:ID schemeID=\"UN/ECE 5153\" schemeAgencyID=\"6\">VAT</cbc:ID>")
        #         TaxSubtotal_tags_list.append("</cac:TaxScheme>")
        #         TaxSubtotal_tags_list.append("</cac:TaxCategory>")
        #         TaxSubtotal_tags_list.append("</cac:TaxSubtotal>")
        #         TaxSubtotal_tags_list.append("\n")

        final_tax_total_tags.append("<cac:TaxTotal>")
        final_tax_total_tags.append(
            '<cbc:TaxAmount currencyID="SAR">{}</cbc:TaxAmount>'.format(
                calculate_the_tax()
            )
        )
        final_tax_total_tags.append("</cac:TaxTotal>")

        final_tax_total_tags.append("<cac:TaxTotal>")
        final_tax_total_tags.append(
            '<cbc:TaxAmount currencyID="SAR">{}</cbc:TaxAmount>'.format(
                calculate_the_tax()
            )
        )
        final_tax_total_tags.append("\n".join(TaxSubtotal_tags_list))
        final_tax_total_tags.append("</cac:TaxTotal>")
        return "\n".join(final_tax_total_tags)

    def create_legal_monetary_total_tag():
        final_legal_monetary_total_tag = []
        the_discounted_value = number_with_n_digits_after_the_point(
            round(
                calculate_the_total_without_tax()
                - calculate_the_total_after_discount(),
                10,
            )
        )
        the_charged_value = number_with_n_digits_after_the_point(
            round(
                calculate_the_total_after_charge() - calculate_the_total_without_tax(),
                10,
            )
        )
        the_total_without_tax = number_with_n_digits_after_the_point(
            round(
                calculate_the_total_without_tax()
                + the_charged_value
                - the_discounted_value,
                10,
            )
        )
        the_total_with_tax = number_with_n_digits_after_the_point(
            round(
                calculate_the_tax()
                + calculate_the_total_without_tax()
                + the_charged_value
                - the_discounted_value,
                10,
            )
        )

        final_legal_monetary_total_tag.append("<cac:LegalMonetaryTotal>")
        final_legal_monetary_total_tag.append(
            '<cbc:LineExtensionAmount currencyID="SAR">{}</cbc:LineExtensionAmount>'.format(
                calculate_the_total_without_tax()
            )
        )
        final_legal_monetary_total_tag.append(
            '<cbc:TaxExclusiveAmount currencyID="SAR">{}</cbc:TaxExclusiveAmount>'.format(
                the_total_without_tax
            )
        )
        final_legal_monetary_total_tag.append(
            '<cbc:TaxInclusiveAmount currencyID="SAR">{}</cbc:TaxInclusiveAmount>'.format(
                the_total_with_tax
            )
        )
        final_legal_monetary_total_tag.append(
            '<cbc:AllowanceTotalAmount currencyID="SAR">{}</cbc:AllowanceTotalAmount>'.format(
                the_discounted_value
            )
        )
        final_legal_monetary_total_tag.append(
            '<cbc:ChargeTotalAmount currencyID="SAR">{}</cbc:ChargeTotalAmount>'.format(
                the_charged_value
            )
        )
        final_legal_monetary_total_tag.append(
            '<cbc:PrepaidAmount currencyID="SAR">0.0</cbc:PrepaidAmount>'
        )
        final_legal_monetary_total_tag.append(
            '<cbc:PayableAmount currencyID="SAR">{}</cbc:PayableAmount>'.format(
                the_total_with_tax
            )
        )
        final_legal_monetary_total_tag.append("</cac:LegalMonetaryTotal>")

        return "\n".join(final_legal_monetary_total_tag)

    def create_a_product_tag():
        the_final_tags_of_the_products_as_list = []

        id_number = 0

        for product in products:
            id_number += 1

            product_number = product.get("number")
            product_name = product.get("name")
            product_quantity = product.get("quantity")
            product_price = number_with_n_digits_after_the_point(
                round(product.get("final_price"), 10)
            )
            product_tax = product.get("tax_percentage")
            product_tax_id_letter = product.get("tax_id_letter")
            product_exemption_code = product.get("exemption_code")
            product_exemption_reason = product.get("exemption_reason")
            product_total_without_tax = number_with_n_digits_after_the_point(
                round(product_price * product_quantity, 10)
            )

            if product.get("charge_on_total"):
                if product.get("charge_on_total").get("charge_value") > 0:
                    if (
                        product.get("charge_on_total").get("charge_type")
                        == "percentage"
                    ):
                        charge_on_total = number_with_n_digits_after_the_point(
                            round(
                                product_total_without_tax
                                * (
                                    product.get("charge_on_total").get("charge_value")
                                    / 100
                                ),
                                10,
                            )
                        )
                    else:
                        charge_on_total = number_with_n_digits_after_the_point(
                            round(
                                product.get("charge_on_total").get("charge_value"), 10
                            )
                        )
                else:
                    charge_on_total = 0.0
            else:
                charge_on_total = 0.0

            if product.get("discount_on_total"):
                if product.get("discount_on_total").get("discount_value") > 0:
                    if (
                        product.get("discount_on_total").get("discount_type")
                        == "percentage"
                    ):
                        discount_on_total = number_with_n_digits_after_the_point(
                            round(
                                product_total_without_tax
                                * (
                                    product.get("discount_on_total").get(
                                        "discount_value"
                                    )
                                    / 100
                                ),
                                10,
                            )
                        )
                    else:
                        discount_on_total = number_with_n_digits_after_the_point(
                            round(
                                product.get("discount_on_total").get("discount_value"),
                                10,
                            )
                        )
                else:
                    discount_on_total = 0.0
            else:
                discount_on_total = 0.0

            product_total_without_tax_with_discount_and_charge = (
                number_with_n_digits_after_the_point(
                    round(
                        (product_total_without_tax + charge_on_total)
                        - discount_on_total,
                        10,
                    )
                )
            )
            product_total_tax = number_with_n_digits_after_the_point(
                round(
                    product_total_without_tax_with_discount_and_charge
                    * (product_tax / 100),
                    10,
                )
            )
            product_total_with_tax = number_with_n_digits_after_the_point(
                round(
                    product_total_without_tax_with_discount_and_charge
                    + product_total_tax,
                    10,
                )
            )

            the_final_tag_of_the_product_as_list = []
            the_final_tag_of_the_product_as_list.append("<cac:InvoiceLine>")
            the_final_tag_of_the_product_as_list.append(
                "<cbc:ID>{}</cbc:ID>".format(id_number)
            )
            the_final_tag_of_the_product_as_list.append(
                '<cbc:InvoicedQuantity unitCode="PCE">{}</cbc:InvoicedQuantity>'.format(
                    product_quantity
                )
            )
            the_final_tag_of_the_product_as_list.append(
                '<cbc:LineExtensionAmount currencyID="SAR">{}</cbc:LineExtensionAmount>'.format(
                    product_total_without_tax_with_discount_and_charge
                )
            )

            if product.get("charge_on_total"):
                if product.get("charge_on_total").get("charge_value") > 0:
                    the_final_tag_of_the_product_as_list.append("<cac:AllowanceCharge>")
                    the_final_tag_of_the_product_as_list.append(
                        "<cbc:ChargeIndicator>true</cbc:ChargeIndicator>"
                    )
                    the_final_tag_of_the_product_as_list.append(
                        "<cbc:AllowanceChargeReasonCode>CG</cbc:AllowanceChargeReasonCode>"
                    )
                    the_final_tag_of_the_product_as_list.append(
                        "<cbc:AllowanceChargeReason>Cleaning</cbc:AllowanceChargeReason>"
                    )

                    if (
                        product.get("charge_on_total").get("charge_type")
                        == "percentage"
                    ):
                        the_final_tag_of_the_product_as_list.append(
                            '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                                charge_on_total
                            )
                        )

                        # if (True) == (True):
                        #     the_final_tag_of_the_product_as_list.append("<cbc:MultiplierFactorNumeric>{}</cbc:MultiplierFactorNumeric>".format(product.get("charge_on_total").get("charge_value")))
                        #     the_final_tag_of_the_product_as_list.append("<cbc:Amount currencyID=\"SAR\">{}</cbc:Amount>".format(charge_on_total))
                        #     the_final_tag_of_the_product_as_list.append("<cbc:BaseAmount currencyID=\"SAR\">{}</cbc:BaseAmount>".format())
                        # else:
                        #     the_final_tag_of_the_product_as_list.append("<cbc:Amount currencyID=\"SAR\">{}</cbc:Amount>".format())
                    else:
                        the_final_tag_of_the_product_as_list.append(
                            '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                                charge_on_total
                            )
                        )

                    the_final_tag_of_the_product_as_list.append(
                        "</cac:AllowanceCharge>"
                    )

            if product.get("discount_on_total"):
                if product.get("discount_on_total").get("discount_value") > 0:
                    the_final_tag_of_the_product_as_list.append("<cac:AllowanceCharge>")
                    the_final_tag_of_the_product_as_list.append(
                        "<cbc:ChargeIndicator>false</cbc:ChargeIndicator>"
                    )
                    the_final_tag_of_the_product_as_list.append(
                        "<cbc:AllowanceChargeReasonCode>95</cbc:AllowanceChargeReasonCode>"
                    )
                    the_final_tag_of_the_product_as_list.append(
                        "<cbc:AllowanceChargeReason>Discount</cbc:AllowanceChargeReason>"
                    )

                    if (
                        product.get("discount_on_total").get("discount_type")
                        == "percentage"
                    ):
                        the_final_tag_of_the_product_as_list.append(
                            '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                                discount_on_total
                            )
                        )

                        # if (True) == (True):
                        #     the_final_tag_of_the_product_as_list.append("<cbc:MultiplierFactorNumeric>{}</cbc:MultiplierFactorNumeric>".format())
                        #     the_final_tag_of_the_product_as_list.append("<cbc:Amount currencyID=\"SAR\">{}</cbc:Amount>".format())
                        #     the_final_tag_of_the_product_as_list.append("<cbc:BaseAmount currencyID=\"SAR\">{}</cbc:BaseAmount>".format())
                        # else:
                        #     the_final_tag_of_the_product_as_list.append("<cbc:Amount currencyID=\"SAR\">{}</cbc:Amount>".format())
                    else:
                        the_final_tag_of_the_product_as_list.append(
                            '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                                discount_on_total
                            )
                        )

                    the_final_tag_of_the_product_as_list.append(
                        "</cac:AllowanceCharge>"
                    )

            the_final_tag_of_the_product_as_list.append("<cac:TaxTotal>")
            the_final_tag_of_the_product_as_list.append(
                '<cbc:TaxAmount currencyID="SAR">{}</cbc:TaxAmount>'.format(
                    product_total_tax
                )
            )
            the_final_tag_of_the_product_as_list.append(
                '<cbc:RoundingAmount currencyID="SAR">{}</cbc:RoundingAmount>'.format(
                    product_total_with_tax
                )
            )
            the_final_tag_of_the_product_as_list.append("</cac:TaxTotal>")

            the_final_tag_of_the_product_as_list.append("<cac:Item>")
            the_final_tag_of_the_product_as_list.append(
                "<cbc:Name>{}</cbc:Name>".format(product_name)
            )

            if product.get("number"):
                the_final_tag_of_the_product_as_list.append(
                    "<cac:SellersItemIdentification>"
                )
                the_final_tag_of_the_product_as_list.append(
                    "<cbc:ID>{}</cbc:ID>".format(product_number)
                )
                the_final_tag_of_the_product_as_list.append(
                    "</cac:SellersItemIdentification>"
                )

            the_final_tag_of_the_product_as_list.append("<cac:ClassifiedTaxCategory>")
            the_final_tag_of_the_product_as_list.append(
                "<cbc:ID>{}</cbc:ID>".format(product_tax_id_letter)
            )
            the_final_tag_of_the_product_as_list.append(
                "<cbc:Percent>{}</cbc:Percent>".format(product_tax)
            )
            the_final_tag_of_the_product_as_list.append("<cac:TaxScheme>")
            the_final_tag_of_the_product_as_list.append("<cbc:ID>VAT</cbc:ID>")
            the_final_tag_of_the_product_as_list.append("</cac:TaxScheme>")
            the_final_tag_of_the_product_as_list.append("</cac:ClassifiedTaxCategory>")

            the_final_tag_of_the_product_as_list.append("</cac:Item>")
            the_final_tag_of_the_product_as_list.append("<cac:Price>")
            the_final_tag_of_the_product_as_list.append(
                '<cbc:PriceAmount currencyID="SAR">{}</cbc:PriceAmount>'.format(
                    product_price
                )
            )
            the_final_tag_of_the_product_as_list.append(
                '<cbc:BaseQuantity unitCode="PCE">1</cbc:BaseQuantity>'
            )

            if product.get("discount_on_unit"):
                if product.get("discount_on_unit").get("discount_value") > 0:
                    the_final_tag_of_the_product_as_list.append("<cac:AllowanceCharge>")
                    the_final_tag_of_the_product_as_list.append(
                        "<cbc:ChargeIndicator>false</cbc:ChargeIndicator>"
                    )
                    the_final_tag_of_the_product_as_list.append(
                        "<cbc:AllowanceChargeReasonCode>95</cbc:AllowanceChargeReasonCode>"
                    )
                    the_final_tag_of_the_product_as_list.append(
                        "<cbc:AllowanceChargeReason>Discount</cbc:AllowanceChargeReason>"
                    )

                    if (
                        product.get("discount_on_unit").get("discount_type")
                        == "percentage"
                    ):

                        if (
                            number_with_n_digits_after_the_point(
                                round(
                                    (
                                        product.get("final_price")
                                        / (
                                            1
                                            - (
                                                product.get("discount_on_unit").get(
                                                    "discount_value"
                                                )
                                                / 100
                                            )
                                        )
                                    ),
                                    10,
                                )
                            )
                            - number_with_n_digits_after_the_point(
                                round(
                                    (
                                        (
                                            product.get("final_price")
                                            / (
                                                1
                                                - (
                                                    product.get("discount_on_unit").get(
                                                        "discount_value"
                                                    )
                                                    / 100
                                                )
                                            )
                                        )
                                        * (
                                            product.get("discount_on_unit").get(
                                                "discount_value"
                                            )
                                            / 100
                                        )
                                    ),
                                    10,
                                )
                            )
                        ) == (product.get("final_price")):
                            the_final_tag_of_the_product_as_list.append(
                                "<cbc:MultiplierFactorNumeric>{}</cbc:MultiplierFactorNumeric>".format(
                                    product.get("discount_on_unit").get(
                                        "discount_value"
                                    )
                                )
                            )
                            the_final_tag_of_the_product_as_list.append(
                                '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                                    number_with_n_digits_after_the_point(
                                        round(
                                            (
                                                (
                                                    product.get("final_price")
                                                    / (
                                                        1
                                                        - (
                                                            product.get(
                                                                "discount_on_unit"
                                                            ).get("discount_value")
                                                            / 100
                                                        )
                                                    )
                                                )
                                                * (
                                                    product.get("discount_on_unit").get(
                                                        "discount_value"
                                                    )
                                                    / 100
                                                )
                                            ),
                                            10,
                                        )
                                    )
                                )
                            )
                            the_final_tag_of_the_product_as_list.append(
                                '<cbc:BaseAmount currencyID="SAR">{}</cbc:BaseAmount>'.format(
                                    number_with_n_digits_after_the_point(
                                        round(
                                            (
                                                product.get("final_price")
                                                / (
                                                    1
                                                    - (
                                                        product.get(
                                                            "discount_on_unit"
                                                        ).get("discount_value")
                                                        / 100
                                                    )
                                                )
                                            ),
                                            10,
                                        )
                                    )
                                )
                            )
                        else:
                            the_final_tag_of_the_product_as_list.append(
                                '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                                    number_with_n_digits_after_the_point(
                                        round(
                                            (
                                                number_with_n_digits_after_the_point(
                                                    round(
                                                        (
                                                            product.get("final_price")
                                                            / (
                                                                1
                                                                - (
                                                                    product.get(
                                                                        "discount_on_unit"
                                                                    ).get(
                                                                        "discount_value"
                                                                    )
                                                                    / 100
                                                                )
                                                            )
                                                        ),
                                                        10,
                                                    )
                                                )
                                                - product.get("final_price")
                                            ),
                                            10,
                                        )
                                    )
                                )
                            )
                            the_final_tag_of_the_product_as_list.append(
                                '<cbc:BaseAmount currencyID="SAR">{}</cbc:BaseAmount>'.format(
                                    number_with_n_digits_after_the_point(
                                        round(
                                            (
                                                product.get("final_price")
                                                / (
                                                    1
                                                    - (
                                                        product.get(
                                                            "discount_on_unit"
                                                        ).get("discount_value")
                                                        / 100
                                                    )
                                                )
                                            ),
                                            10,
                                        )
                                    )
                                )
                            )
                    else:
                        the_final_tag_of_the_product_as_list.append(
                            '<cbc:Amount currencyID="SAR">{}</cbc:Amount>'.format(
                                product.get("discount_on_unit").get("discount_value")
                            )
                        )
                        the_final_tag_of_the_product_as_list.append(
                            '<cbc:BaseAmount currencyID="SAR">{}</cbc:BaseAmount>'.format(
                                number_with_n_digits_after_the_point(
                                    round(
                                        product.get("final_price")
                                        + product.get("discount_on_unit").get(
                                            "discount_value"
                                        ),
                                        10,
                                    )
                                )
                            )
                        )

                    the_final_tag_of_the_product_as_list.append(
                        "</cac:AllowanceCharge>"
                    )

            the_final_tag_of_the_product_as_list.append("</cac:Price>")
            the_final_tag_of_the_product_as_list.append("</cac:InvoiceLine>")
            the_final_tag_of_the_product_as_list.append("\n")
            the_final_tag_of_the_product_as_string = "\n".join(
                the_final_tag_of_the_product_as_list
            )
            the_final_tags_of_the_products_as_list.append(
                the_final_tag_of_the_product_as_string
            )

        return "\n".join(the_final_tags_of_the_products_as_list)

    the_final_invoice_as_list = []

    the_final_invoice_as_list.append('<?xml version="1.0" encoding="UTF-8"?>')
    the_final_invoice_as_list.append(
        '<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">'
    )
    the_final_invoice_as_list.append(create_the_encryption_tags())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_the_tags_of_the_information())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_the_tag_of_the_source_invoice())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_counter_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_PIH_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_QR_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_signature_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_supplier_party_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_customer_party_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_delivery_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_payment_means_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_allowance_charge_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_tax_total_tags())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_legal_monetary_total_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append(create_a_product_tag())
    the_final_invoice_as_list.append("\n")
    the_final_invoice_as_list.append("</Invoice>")

    the_final_invoice = "\n".join(the_final_invoice_as_list)

    return the_final_invoice


# except:
#     return False


import json
from django.http import HttpResponse


def zid_json_to_invoice(request):
    data = """
    {
        "id":39060802,
        "code":"zvlI7EW61M",
        "store_id":440532,
        "order_url":"https://iqyj65.zid.store/o/zvlI7EW61M/inv",
        "store_name":"info@zedna.sa",
        "shipping_method_code":"custom",
        "store_url":"https://iqyj65.zid.store/",
        "order_status":{"name":"جديد","code":"new"},
        "currency_code":"SAR",
        "customer":{"id":6726929,
        "name":"جلوى زاهى المطيري",
        "verified":1,
        "email":"jelwi2021@gmail.com",
        "mobile":"966504850155","note":"",
        "type":"individual"},
        "has_different_consignee":false,
        "is_guest_customer":false,
        "is_gift_order":false,
        "gift_card_details":null,
        "is_quick_checkout_order":false,
        "order_total":1500,
        "order_total_string":"1,500.00 SAR",
        "has_different_transaction_currency":false,
        "transaction_reference":null,
        "transaction_amount":1500,
        "transaction_amount_string":"1,500.00 SAR",
        "issue_date":"15-07-2024 | 09:01 م",
        "payment_status":"pending",
        "is_potential_fraud":false,
        "source":"Merchant Admin",
        "source_code":"md",
        "is_reseller_transaction":false,
        "created_at":"2024-07-15 18:01:25",
        "updated_at":"2024-07-15 18:01:26",
        "tags":[],
        "requires_shipping":true,
        "shipping":{
            "method":{
                "id":514675,
                "name":"zedna_delivery",
                "code":"custom",
                "estimated_delivery_time":"zedna_delivery",
                "icon":"https://media.zid.store/7df0f7ba-33c1-4377-8b41-4850f99a249a/8c6debf2-be9d-49f2-ba75-ef365f6fdef1.png",
                "is_system_option":false,
                "waybill":null,
                "had_errors_while_fetching_waybill":false,
                "waybill_tracking_id":null,
                "has_waybill_and_packing_list":false,
                "tracking":{"number":null,"status":null,"url":null},
                "order_shipping_status":null,
                "inventory_address":[],
                "courier":null,
                "return_shipment":null
            },
            "address":{
                "formatted_address":"N/A",
                "street":"الملك سلمان",
                "district":"الملك سلمان",
                "lat":null,
                "lng":null,
                "short_address":"alta1234",
                "meta":{"city_name":null,"postcode":"1223","building_number":"12345","additional_number":"12345"},
                "city":{"id":1,"name":"الرياض"},
                "country":{"id":184,"name":"السعودية"}
            }
        },
        "payment":{
            "method":{
                "name":"Cash on Delivery",
                "code":"zid_cod",
                "type":"zid_cod"
            },
            "invoice":[
                {"code":"sub_totals","value":"1500.00000000000000","value_string":"1,500.00 SAR","title":"Sub Totals"},
                {"code":"total","value":"1500.00000000000000","value_string":"1,500.00 SAR","title":"Total"}
            ]
        },
        "cod_confirmed":false,
        "reverse_order_label_request":null,
        "customer_note":"",
        "gift_message":null,
        "payment_link":null,
        "weight":2000,
        "weight_cost_details":[],
        "currency":{
            "order_currency":{"id":4,"code":"SAR","exchange_rate":1},
            "order_store_currency":{"id":4,"code":"SAR","exchange_rate":null}
        },
        "coupon":null,
        "products":[
            {
                "id":"9fa8145c-2910-40e0-a259-543f58569551",
                "parent_id":null,
                "parent_name":null,
                "product_class":null,
                "name":"printer",
                "short_description":{"ar":"","en":""},
                "sku":"Z.440532.16985738088897874",
                "barcode":null,
                "custom_fields":[],
                "quantity":1,
                "weight":{"value":2,"unit":"kg"},
                "is_taxable":true,
                "is_discounted":false,
                "vouchers":null,
                "meta":null,
                "net_price_with_additions":1500,
                "net_price_with_additions_string":"1,500.00 SAR",
                "price_with_additions":1500,
                "price_with_additions_string":"1,500.00 SAR",
                "net_price":1500,
                "net_price_string":"1,500.00 SAR",
                "net_sale_price":null,
                "net_sale_price_string":null,
                "net_additions_price":0,
                "net_additions_price_string":null,
                "gross_price":1500,
                "gross_price_string":"1,500.00 SAR",
                "gross_sale_price":null,
                "gross_sale_price_string":null,
                "price_before":null,
                "price_before_string":null,
                "total_before":null,
                "total_before_string":null,
                "gross_additions_price":0,
                "gross_additions_price_string":null,
                "tax_percentage":0,
                "tax_amount":"0.00000000000000",
                "tax_amount_string":"0.00 SAR",
                "tax_amount_string_per_item":"0.00 SAR",
                "price":1500,
                "price_string":"1,500.00 SAR",
                "additions_price":0,
                "additions_price_string":"0.00 SAR",
                "total":1500,
                "total_string":"1,500.00 SAR",
                "images":[
                    {
                        "id":"1f4f5c51-daa3-4e27-9e16-024e70c5f176",
                        "origin":"https://media.zid.store/thumbs/7df0f7ba-33c1-4377-8b41-4850f99a249a/1f4f5c51-daa3-4e27-9e16-024e70c5f176-thumbnail-500x500.png",
                        "thumbs":{
                            "fullSize":"https://media.zid.store/7df0f7ba-33c1-4377-8b41-4850f99a249a/1f4f5c51-daa3-4e27-9e16-024e70c5f176.png",
                            "thumbnail":"https://media.zid.store/thumbs/7df0f7ba-33c1-4377-8b41-4850f99a249a/1f4f5c51-daa3-4e27-9e16-024e70c5f176-thumbnail-370x370.png",
                            "small":"https://media.zid.store/thumbs/7df0f7ba-33c1-4377-8b41-4850f99a249a/1f4f5c51-daa3-4e27-9e16-024e70c5f176-thumbnail-500x500.png",
                            "medium":"https://media.zid.store/thumbs/7df0f7ba-33c1-4377-8b41-4850f99a249a/1f4f5c51-daa3-4e27-9e16-024e70c5f176-thumbnail-770x770.png",
                            "large":"https://media.zid.store/thumbs/7df0f7ba-33c1-4377-8b41-4850f99a249a/1f4f5c51-daa3-4e27-9e16-024e70c5f176-thumbnail-1000x1000.png"
                        }
                    }
                ],
                "options":[]
            }
        ],
        "products_count":1,
        "products_sum_total_string":"1,500.00 SAR",
        "language":"en",
        "histories":[],
        "is_reactivated":false,
        "return_policy":null,
        "packages_count":1,
        "inventory_address":null,
        "reseller_meta":null,
        "zidship_ticket_number":null,
        "edits_count":0
    }
    """

    json_data = json.loads(data)

    # Extract customer data
    customer_name = json_data["customer"]["name"]
    customer_email = json_data["customer"]["email"]
    customer_mobile = json_data["customer"]["mobile"]
    customer_postcode = json_data["shipping"]["address"]["meta"]["postcode"]
    customer_building_number = json_data["shipping"]["address"]["meta"][
        "building_number"
    ]
    customer_additional_number = json_data["shipping"]["address"]["meta"][
        "additional_number"
    ]
    customer_city_name = json_data["shipping"]["address"]["city"]["name"]

    # Extract product data for all products
    products = json_data["products"]
    products_details = []

    for product in products:
        product_details = {
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": product["quantity"],
            "tax_percentage": product["tax_percentage"],
        }
        products_details.append(product_details)

    # Extract invoice data
    issue_date = json_data["issue_date"]
    new_irn = json_data["id"]
    unique_id = json_data["id"]
    payment_method = json_data["payment"]["method"]["name"]

    total_discount_amount = json_data["coupon"]
    product_discounts = json_data["coupon"]

    # Print the extracted values
    print(f"Order ID: {unique_id}")
    print(f"Customer Name: {customer_name}")
    print(f"Customer Email: {customer_email}")
    print(f"Customer Mobile: {customer_mobile}")
    print(f"Customer Postcode: {customer_postcode}")
    print(f"Customer Building Number: {customer_building_number}")
    print(f"Customer Additional Number: {customer_additional_number}")
    print(f"Customer City Name: {customer_city_name}")
    print(f"Payment Method: {payment_method}")
    print(f"Issue Date: {issue_date}")

    for product in products_details:
        print(f"Product ID: {product['id']}")
        print(f"Product Name: {product['name']}")
        print(f"Product Price: {product['price']}")
        print(f"Product Quantity: {product['quantity']}")
        print(f"Product Tax Percentage: {product['tax_percentage']}")
        print("")

    print("Received webhook data:", json_data)
    return HttpResponse("Received webhook data:")


import datetime


# Function to identify the type of webhook
def identify_webhook_type(webhook_data):
    if (
        "app_id" in webhook_data
        and "status" in webhook_data
        and "event_name" in webhook_data
    ):
        return "app_installation"
    elif (
        "id" in webhook_data
        and "order_url" in webhook_data
        and "customer" in webhook_data
    ):
        return "order"
    else:
        return "unknown"


from django.http import JsonResponse
import requests


@csrf_exempt
def handle_webhook(request):

    #######We must need to get current user in here THIS IS THE MAIN REQUIREMENT BASED ON IT WE WILL MAKE OPERATION#######
    # request_user = request.user
    # if request_user.is_company_user:
    #     supplier = request_user.manager_id
    # else:
    #     supplier = request_user

    # if request.user.is_company_admin:
    #     user_id = request.user.id
    # elif request.user.is_company_user:
    #     user_id = request.user.manager_id

    # print(request_user)

    if request.method == "POST":
        try:
            json_data = json.loads(request.body)
            print("Received webhook data:", json_data)

            # Identify the type of webhook
            webhook_type = identify_webhook_type(json_data)

            # Process the webhook based on its type
            if webhook_type == "app_installation":
                # Handle app installation logic
                print("Processing app installation webhook")
                print(json_data)
                print("Processing app installation webhook")

                # Add your app installation handling logic here
            elif webhook_type == "order":
                # Handle order logic
                print("Processing order webhook")
                print(json_data)
                store = ZidUserStore.objects.get(store_id=json_data["store_id"])
                # get user from store
                get_store_user = store.zid_user.user.id

                # request_user = request.user
                # if request_user.is_company_user:
                #     supplier = request_user.manager_id
                # else:
                #     supplier = request_user

                # if request.user.is_company_admin:
                #     user_id = request.user.id
                # elif request.user.is_company_user:
                #     user_id = request.user.manager_id

                # print(request_user)
                # Add your order handling logic here
                # Extract customer data
                customer_name = json_data["customer"]["name"]
                customer_email = json_data["customer"]["email"]
                customer_mobile = json_data["customer"]["mobile"]
                customer_postcode = json_data["shipping"]["address"]["meta"]["postcode"]
                customer_building_number = json_data["shipping"]["address"]["meta"][
                    "building_number"
                ]
                customer_additional_number = json_data["shipping"]["address"]["meta"][
                    "additional_number"
                ]
                customer_city_name = json_data["shipping"]["address"]["city"]["name"]
                # Extract product data for all products
                # Extract invoice data
                issue_date = json_data["created_at"]
                new_irn = json_data["id"]
                unique_id = json_data["id"]
                payment_method = json_data["payment"]["method"]["name"]

                total_discount_amount = json_data["coupon"]
                product_discounts = json_data["coupon"]

                products = json_data["products"]

                product_list = []

                for product in products:

                    # Assuming `product` is an instance of `InvoiceProducts` model
                    product_data = {
                        "number": product["id"],
                        "name": product["name"],
                        # "final_price": float(product['price']),
                        "final_price": float(product["net_price"]),
                        "quantity": int(product["quantity"]),
                        "with_tax": "yes",
                        # "tax_percentage":float(product['tax_percentage']),
                        "tax_percentage": float(product["tax_percentage"] * 100),
                        "tax_id_letter": "S",
                        "exemption_code": "S",
                        "exemption_reason": "test rate",
                    }

                    # Check for discount_on_total, discount_on_unit, and charge_on_total
                    if product["tax_percentage"]:
                        product_data["discount_on_total"] = {
                            "discount_type": "percentage",
                            "discount_value": float(product["tax_percentage"]),
                        }

                    product_list.append(product_data)

                unique_id = str(uuid.uuid4())

                # Convert the string to a datetime object
                datetime_obj = datetime.datetime.strptime(
                    issue_date, "%Y-%m-%d %H:%M:%S"
                )

                # Extract date and time components
                date = datetime_obj.date()
                time = datetime_obj.time()

                # Find the invoice item with code 'vat'
                vat_item = next(
                    item
                    for item in json_data["payment"]["invoice"]
                    if item["code"] == "vat"
                )

                # Now you can access the value
                total_tax_amount = vat_item["value"]
                if total_tax_amount:
                    total_tax_amount = float(total_tax_amount)
                else:
                    total_tax_amount = 0

                print(total_tax_amount)

                print("Total discount amount:", total_discount_amount)
                print(type(total_discount_amount))
                if total_discount_amount:
                    total_discount_amount = float(total_discount_amount)
                else:
                    total_discount_amount = 0

                print("Total discount amount:", total_discount_amount)
                print(type(total_discount_amount))

                invoice_data = {
                    "invoice_number": new_irn,
                    "billingreference_number": "",
                    "invoice_uuid": unique_id,
                    "invoice_issue_date": date,
                    "invoice_issue_time": time,
                    # "invoice_type_code": "0200000",
                    "invoice_type_code": "0100000",
                    "invoice_type_number": "388",
                    "the_counter": "1",
                    "the_PIH": "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ==",
                }

                seller_data = {
                    "type_of_PartyIdentification": "CRN",
                    "PartyIdentification": "",
                    "StreetName": "",
                    "AdditionalStreetName": "",
                    "BuildingNumber": "",
                    "PlotIdentification": "",
                    "CitySubdivisionName": "",
                    "CityName": "",
                    "PostalZone": "",
                    "CountrySubentity": "",
                    "country_IdentificationCode": "SA",
                    "vat_registration_number_CompanyID": "",
                    "RegistrationName": "",
                }

                customer_data = {
                    "type_of_PartyIdentification": "",
                    "PartyIdentification": "",
                    "StreetName": "",
                    "AdditionalStreetName": "",
                    "BuildingNumber": customer_building_number,
                    "PlotIdentification": customer_additional_number,
                    "CitySubdivisionName": "",
                    "CityName": customer_city_name,
                    "PostalZone": customer_postcode,
                    "CountrySubentity": "",
                    "country_IdentificationCode": "SA",
                    "vat_registration_number_CompanyID": "",
                    "RegistrationName": customer_name,
                }

                invoice_products = product_list

                # payment_data = {"payment_method": payment_method,
                #                 "payment_reason": ""}
                payment_data = {
                    "payment_method": "10",
                    "payment_reason": payment_method,
                }

                # this discount is on the total of the invoice
                discount_data = {
                    "discount_type": "amount",  # you can put either (amount) or (percentage)
                    "discount_value": total_discount_amount,
                }

                # this charge is on the total of the invoice
                charge_data = {
                    "charge_type": "amount",  # you can put either (amount) or (percentage)
                    # "charge_value": product_discounts
                    "charge_value": total_tax_amount,
                }
                delivery_data = {"actual_delivery_date": date}

                result = create_an_invoice(
                    invoice_data=invoice_data,
                    seller_data=seller_data,
                    customer_data=customer_data,
                    products=invoice_products,
                    payment_data=payment_data,
                    discount_on_totals=discount_data,
                    charge_on_totals=charge_data,
                    delivery_data=delivery_data,
                )
                print(result)

            else:
                print("Unknown webhook type received")
                return JsonResponse({"error": "Unknown webhook type"}, status=400)

            return JsonResponse(
                {"message": "Webhook received successfully"}, status=200
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def create_invoice_view(request):

    data = """
    {
   "id":39862770,
   "code":"brk8xsj7Nk",
   "store_id":440532,
   "order_url":"https:\/\/iqyj65.zid.store\/o\/brk8xsj7Nk\/inv",
   "store_name":"info@zedna.sa",
   "shipping_method_code":"custom",
   "store_url":"https:\/\/iqyj65.zid.store\/",
   "order_status":{
      "name":"\u062c\u062f\u064a\u062f",
      "code":"new"
   },
   "currency_code":"SAR",
   "customer":{
      "id":6726929,
      "name":"\u062c\u0644\u0648\u0649 \u0632\u0627\u0647\u0649 \u0627\u0644\u0645\u0637\u064a\u0631\u064a",
      "verified":1,
      "email":"jelwi2021@gmail.com",
      "mobile":"966504850155",
      "note":"",
      "type":"individual"
   },
   "has_different_consignee":false,
   "is_guest_customer":false,
   "is_gift_order":false,
   "gift_card_details":null,
   "is_quick_checkout_order":false,
   "order_total":1725,
   "order_total_string":"1,725.00 SAR",
   "has_different_transaction_currency":false,
   "transaction_reference":null,
   "transaction_amount":1725,
   "transaction_amount_string":"1,725.00 SAR",
   "issue_date":"09-08-2024 | 04:10 \u0635",
   "payment_status":"pending",
   "is_potential_fraud":false,
   "source":"Merchant Admin",
   "source_code":"md",
   "is_reseller_transaction":false,
   "created_at":"2024-08-09 01:10:22",
   "updated_at":"2024-08-09 01:10:22",
   "tags":[
      
   ],
   "requires_shipping":true,
   "shipping":{
      "method":{
         "id":514675,
         "name":"zedna_delivery",
         "code":"custom",
         "estimated_delivery_time":"zedna_delivery",
         "icon":"https:\/\/media.zid.store\/7df0f7ba-33c1-4377-8b41-4850f99a249a\/8c6debf2-be9d-49f2-ba75-ef365f6fdef1.png",
         "is_system_option":false,
         "waybill":null,
         "had_errors_while_fetching_waybill":false,
         "waybill_tracking_id":null,
         "has_waybill_and_packing_list":false,
         "tracking":{
            "number":null,
            "status":null,
            "url":null
         },
         "order_shipping_status":null,
         "inventory_address":[
            
         ],
         "courier":null,
         "return_shipment":null
      },
      "address":{
         "formatted_address":"N\/A",
         "street":"\u0627\u0644\u0645\u0644\u0643 \u0633\u0644\u0645\u0627\u0646",
         "district":"\u0627\u0644\u0645\u0644\u0643 \u0633\u0644\u0645\u0627\u0646",
         "lat":null,
         "lng":null,
         "short_address":"alta1234",
         "meta":{
            "city_name":null,
            "postcode":"1223",
            "building_number":"12345",
            "additional_number":"12345"
         },
         "city":{
            "id":1,
            "name":"\u0627\u0644\u0631\u064a\u0627\u0636"
         },
         "country":{
            "id":184,
            "name":"\u0627\u0644\u0633\u0639\u0648\u062f\u064a\u0629"
         }
      }
   },
   "payment":{
      "method":{
         "name":"Cash on Delivery",
         "code":"zid_cod",
         "type":"zid_cod"
      },
      "invoice":[
         {
            "code":"sub_totals_before_vat",
            "value":"1500.00000000000000",
            "value_string":"1,500.00 SAR",
            "title":"Total without VAT"
         },
         {
            "code":"taxable_amount",
            "value":"1500.00000000000000",
            "value_string":"1,500.00 SAR",
            "title":"Taxable amount"
         },
         {
            "code":"vat",
            "value":"225.00000000000000",
            "value_string":"225.00 SAR",
            "title":"VAT (%15)"
         },
         {
            "code":"sub_totals_after_vat",
            "value":"1725.00000000000000",
            "value_string":"1,725.00 SAR",
            "title":"Total Inc. VAT"
         },
         {
            "code":"total",
            "value":"1725.00000000000000",
            "value_string":"1,725.00 SAR",
            "title":"Total"
         }
      ]
   },
   "cod_confirmed":false,
   "reverse_order_label_request":null,
   "customer_note":"",
   "gift_message":null,
   "payment_link":null,
   "weight":2000,
   "weight_cost_details":[
      
   ],
   "currency":{
      "order_currency":{
         "id":4,
         "code":"SAR",
         "exchange_rate":1
      },
      "order_store_currency":{
         "id":4,
         "code":"SAR",
         "exchange_rate":null
      }
   },
   "coupon":null,
   "products":[
      {
         "id":"9fa8145c-2910-40e0-a259-543f58569551",
         "parent_id":null,
         "parent_name":null,
         "product_class":null,
         "name":"printer",
         "short_description":{
            "ar":"",
            "en":""
         },
         "sku":"Z.440532.16985738088897874",
         "barcode":null,
         "custom_fields":[
            
         ],
         "quantity":1,
         "weight":{
            "value":2,
            "unit":"kg"
         },
         "is_taxable":true,
         "is_discounted":false,
         "vouchers":null,
         "meta":null,
         "net_price_with_additions":1500,
         "net_price_with_additions_string":"1,500.00 SAR",
         "price_with_additions":1725,
         "price_with_additions_string":"1,725.00 SAR",
         "net_price":1500,
         "net_price_string":"1,500.00 SAR",
         "net_sale_price":null,
         "net_sale_price_string":null,
         "net_additions_price":0,
         "net_additions_price_string":null,
         "gross_price":1725,
         "gross_price_string":"1,725.00 SAR",
         "gross_sale_price":null,
         "gross_sale_price_string":null,
         "price_before":null,
         "price_before_string":null,
         "total_before":null,
         "total_before_string":null,
         "gross_additions_price":0,
         "gross_additions_price_string":null,
         "tax_percentage":0.15,
         "tax_amount":"225.00000000000000",
         "tax_amount_string":"225.00 SAR",
         "tax_amount_string_per_item":"225.00 SAR",
         "price":1725,
         "price_string":"1,725.00 SAR",
         "additions_price":0,
         "additions_price_string":"0.00 SAR",
         "total":1725,
         "total_string":"1,725.00 SAR",
         "images":[
            {
               "id":"1f4f5c51-daa3-4e27-9e16-024e70c5f176",
               "origin":"https:\/\/media.zid.store\/thumbs\/7df0f7ba-33c1-4377-8b41-4850f99a249a\/1f4f5c51-daa3-4e27-9e16-024e70c5f176-thumbnail-500x500.png",
               "thumbs":{
                  "fullSize":"https:\/\/media.zid.store\/7df0f7ba-33c1-4377-8b41-4850f99a249a\/1f4f5c51-daa3-4e27-9e16-024e70c5f176.png",
                  "thumbnail":"https:\/\/media.zid.store\/thumbs\/7df0f7ba-33c1-4377-8b41-4850f99a249a\/1f4f5c51-daa3-4e27-9e16-024e70c5f176-thumbnail-370x370.png",
                  "small":"https:\/\/media.zid.store\/thumbs\/7df0f7ba-33c1-4377-8b41-4850f99a249a\/1f4f5c51-daa3-4e27-9e16-024e70c5f176-thumbnail-500x500.png",
                  "medium":"https:\/\/media.zid.store\/thumbs\/7df0f7ba-33c1-4377-8b41-4850f99a249a\/1f4f5c51-daa3-4e27-9e16-024e70c5f176-thumbnail-770x770.png",
                  "large":"https:\/\/media.zid.store\/thumbs\/7df0f7ba-33c1-4377-8b41-4850f99a249a\/1f4f5c51-daa3-4e27-9e16-024e70c5f176-thumbnail-1000x1000.png"
               }
            }
         ],
         "options":[
            
         ]
      }
   ],
   "products_count":1,
   "products_sum_total_string":"1,725.00 SAR",
   "language":"en",
   "histories":[
      
   ],
   "is_reactivated":false,
   "return_policy":null,
   "packages_count":1,
   "inventory_address":null,
   "reseller_meta":null,
   "zidship_ticket_number":null,
   "edits_count":0
}
    """

    # if request.method == 'POST':
    invoice_type = "0101000"
    json_data = json.loads(data)

    print(json_data)

    # Extract customer data
    customer_name = json_data["customer"]["name"]
    customer_email = json_data["customer"]["email"]
    customer_mobile = json_data["customer"]["mobile"]
    customer_postcode = json_data["shipping"]["address"]["meta"]["postcode"]
    customer_building_number = json_data["shipping"]["address"]["meta"][
        "building_number"
    ]
    customer_additional_number = json_data["shipping"]["address"]["meta"][
        "additional_number"
    ]
    customer_city_name = json_data["shipping"]["address"]["city"]["name"]

    # Extract product data for all products

    # Extract invoice data
    # issue_date = json_data['issue_date']
    issue_date = json_data["created_at"]
    new_irn = json_data["id"]
    unique_id = json_data["id"]
    payment_method = json_data["payment"]["method"]["name"]

    total_discount_amount = json_data["coupon"]
    product_discounts = json_data["coupon"]

    products = json_data["products"]

    product_list = []

    for product in products:

        # Assuming `product` is an instance of `InvoiceProducts` model
        product_data = {
            "number": product["id"],
            "name": product["name"],
            # "final_price": float(product['price']),
            "final_price": float(product["net_price"]),
            "quantity": int(product["quantity"]),
            "with_tax": "yes",
            # "tax_percentage":float(product['tax_percentage']),
            "tax_percentage": float(product["tax_percentage"] * 100),
            "tax_id_letter": "S",
            "exemption_code": "S",
            "exemption_reason": "test rate",
        }

        # Check for discount_on_total, discount_on_unit, and charge_on_total
        if product["tax_percentage"]:
            product_data["discount_on_total"] = {
                "discount_type": "percentage",
                "discount_value": float(product["tax_percentage"]),
            }

        product_list.append(product_data)

    unique_id = str(uuid.uuid4())

    # Convert the string to a datetime object
    datetime_obj = datetime.datetime.strptime(issue_date, "%Y-%m-%d %H:%M:%S")

    # Extract date and time components
    date = datetime_obj.date()
    time = datetime_obj.time()

    # Find the invoice item with code 'vat'
    vat_item = next(
        item for item in json_data["payment"]["invoice"] if item["code"] == "vat"
    )

    # Now you can access the value
    total_tax_amount = vat_item["value"]
    if total_tax_amount:
        total_tax_amount = float(total_tax_amount)
    else:
        total_tax_amount = 0

    print(total_tax_amount)

    print("Total discount amount:", total_discount_amount)
    print(type(total_discount_amount))
    if total_discount_amount:
        total_discount_amount = float(total_discount_amount)
    else:
        total_discount_amount = 0

    print("Total discount amount:", total_discount_amount)
    print(type(total_discount_amount))

    invoice_data = {
        "invoice_number": new_irn,
        "billingreference_number": "",
        "invoice_uuid": unique_id,
        "invoice_issue_date": date,
        "invoice_issue_time": time,
        # "invoice_type_code": "0200000",
        "invoice_type_code": "0100000",
        "invoice_type_number": "388",
        "the_counter": "1",
        "the_PIH": "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ==",
    }

    seller_data = {
        "type_of_PartyIdentification": "CRN",
        "PartyIdentification": "",
        "StreetName": "",
        "AdditionalStreetName": "",
        "BuildingNumber": "",
        "PlotIdentification": "",
        "CitySubdivisionName": "",
        "CityName": "",
        "PostalZone": "",
        "CountrySubentity": "",
        "country_IdentificationCode": "SA",
        "vat_registration_number_CompanyID": "",
        "RegistrationName": "",
    }

    customer_data = {
        "type_of_PartyIdentification": "",
        "PartyIdentification": "",
        "StreetName": "",
        "AdditionalStreetName": "",
        "BuildingNumber": customer_building_number,
        "PlotIdentification": customer_additional_number,
        "CitySubdivisionName": "",
        "CityName": customer_city_name,
        "PostalZone": customer_postcode,
        "CountrySubentity": "",
        "country_IdentificationCode": "SA",
        "vat_registration_number_CompanyID": "",
        "RegistrationName": customer_name,
    }

    invoice_products = product_list

    # payment_data = {"payment_method": payment_method,
    #                 "payment_reason": ""}
    payment_data = {"payment_method": "10", "payment_reason": payment_method}

    # this discount is on the total of the invoice
    discount_data = {
        "discount_type": "amount",  # you can put either (amount) or (percentage)
        "discount_value": total_discount_amount,
    }

    # this charge is on the total of the invoice
    charge_data = {
        "charge_type": "amount",  # you can put either (amount) or (percentage)
        # "charge_value": product_discounts
        "charge_value": total_tax_amount,
    }
    delivery_data = {"actual_delivery_date": date}

    result = create_an_invoice(
        invoice_data=invoice_data,
        seller_data=seller_data,
        customer_data=customer_data,
        products=invoice_products,
        payment_data=payment_data,
        discount_on_totals=discount_data,
        charge_on_totals=charge_data,
        delivery_data=delivery_data,
    )
    print(result)

    return HttpResponse("You have successfully created an invoice.")
