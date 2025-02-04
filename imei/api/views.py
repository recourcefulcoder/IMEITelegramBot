import json
from http import HTTPStatus

from django.http import HttpResponse
from django.utils.decorators import classonlymethod
from rest_framework.response import Response
from rest_framework.authentication import BaseAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView

import requests

from .utils import imei_valid

IMEICHECK_URL = "https://api.imeicheck.net/v1/checks"
IMEICHECK_TOKEN = "e4oEaZY1Kom5OXzybETkMlwjOCy3i8GSCGTHzWrhd4dc563b"


def do_nothing(request):
    return HttpResponse("OK")


class QueryParamTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token_key = request.query_params.get("token")
        if not token_key:
            return None

        try:
            token = Token.objects.get(key=token_key)
            return (token.user, token)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid token")


class CheckImei(APIView):

    # authentication_classes = [QueryParamTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        imei = request.GET.get("imei")
        if imei is None:
            return Response(
                data={"error": "invalid request - no imei provided"},
                status=HTTPStatus.BAD_REQUEST,
            )
        if not imei_valid(imei):
            return Response(
                data={"error": "invalid imei"}, status=HTTPStatus.BAD_REQUEST
            )

        headers = {
            "Authorization": "Bearer " + IMEICHECK_TOKEN,
            "Content-Type": "application/json",
        }

        payload = json.dumps({"deviceId": imei, "serviceId": 15})
        response = requests.post(IMEICHECK_URL, headers=headers, data=payload)

        return Response(data=response.json(), status=response.status_code, content_type="application/json")
