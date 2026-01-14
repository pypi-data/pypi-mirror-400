from rest import decorators as rd
from rest import views as rv
from rest import helpers as rh
from rest import settings
from rest import crypto
from urllib.parse import urlencode
from django.shortcuts import redirect
from account.oauth import google
from account.models import Member
from objict import objict
from datetime import datetime, timedelta
REST_PREFIX = settings.get("REST_PREFIX", "api/")


@rd.url('oauth/google/login')
@rd.never_cache
def oauth_google_login(request):
    code = request.DATA.get("code")
    error = request.DATA.get("error", "unknown error")
    state = request.DATA.get("state")
    app_url = settings.DEFAULT_LOGIN_URL

    # rh.log_print("google/login", request.DATA.toDict(), request.session.get("state"))

    if state:
        # this is where we should pull out the passed in state and get the proper URL
        state = objict.fromJSON(rh.hexToString(state))
        rh.log_print("state", state)
        app_url = state.url

    if not code:
        params = urlencode({'error': error})
        separator = '&' if '?' in app_url and app_url[-1] != '?' else '?'
        return redirect(f"{app_url}{separator}{params}")

    redirect_uri = f"{request.scheme}://{request.get_host()}/{REST_PREFIX}account/oauth/google/login"
    auth_data = google.getAccessToken(code, redirect_uri)
    if auth_data is None or auth_data.access_token is None:
        params = urlencode({'error': "failed to get access token from google"})
        separator = '&' if '?' in app_url and app_url[-1] != '?' else '?'
        return redirect(f"{app_url}{separator}{params}")

    user_data = google.getUserInfo(auth_data.access_token)
    if user_data is None:
        params = urlencode({'error': "failed to get user data from google"})
        separator = '&' if '?' in app_url and app_url[-1] != '?' else '?'
        return redirect(f"{app_url}{separator}{params}")

    if not user_data.email:
        params = urlencode({'error': "no email with account"})
        separator = '&' if '?' in app_url and app_url[-1] != '?' else '?'
        return redirect(f"{app_url}{separator}{params}")

    # TODO allow new accounts?
    member = Member.objects.filter(email=user_data.email).last()
    if member is None:
        params = urlencode({'error': "user not found"})
        separator = '&' if '?' in app_url and app_url[-1] != '?' else '?'
        return redirect(f"{app_url}{separator}{params}")

    member.setProperties(auth_data, category="google_auth")
    member.setProperties(user_data, category="google")

    if not member.first_name and user_data.given_name:
        member.first_name = user_data.given_name

    if not member.last_name and user_data.family_name:
        member.last_name = user_data.family_name

    if not member.display_name and user_data.name:
        member.display_name = user_data.name

    member.auth_code = crypto.randomString(16)
    member.auth_code_expires = datetime.now() + timedelta(minutes=5)
    member.save()
    member.auditLog("user succesfully authenticated with google", "google_oauth", level=17)

    params = urlencode({'oauth_code': member.auth_code, "username":member.username, "auth_method":"google_oauth"})
    rurl = None
    separator = '&' if '?' in app_url and app_url[-1] != '?' else '?'
    rurl = f"{app_url}{separator}{params}"
    return redirect(rurl)
