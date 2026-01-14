from rest import decorators as rd
from rest import crypto
from rest.mail import render_to_mail
from rest import views as rv
# from rest.views import restStatus, restGet, restPermissionDenied
from rest.jwtoken import JWToken, JWT_KEY, JWT_EXPIRES, JWT_REFRESH_EXPIRES
from rest import helpers
from rest import settings
from account import models as am
from medialib.qrcode import generateQRCode
from django.http import HttpResponse
from datetime import datetime, timedelta

ALLOW_BASIC_LOGIN = settings.get("ALLOW_BASIC_LOGIN", False)
FORGET_ALWAYS_TRUE = settings.get("FORGET_ALWAYS_TRUE", True)
JWT_UPDATE_REFRESH_TOKEN = settings.get("JWT_UPDATE_REFRESH_TOKEN", False)


@rd.urlPOST(r'^login$')
@rd.urlPOST(r'^login/$')
@rd.never_cache
def member_login(request):
    if not ALLOW_BASIC_LOGIN:
        return jwt_login(request)
    username = request.DATA.get('username', None)
    auth_code = request.DATA.get(["auth_code", "code", "invite_token"], None)
    if username and auth_code:
        return member_login_uname_code(request, username, auth_code)
    password = request.DATA.get('password', None)
    if username and password:
        return member_login_uname_pword(request, username, password)
    return rv.restPermissionDenied(request, f"Invalid credentials {username}/{auth_code}", 401)


@rd.urlPOST(r'^jwt/login$')
@rd.urlPOST(r'^jwt/login/$')
@rd.never_cache
def jwt_login(request):
    # poor mans JWT, carried over
    auth_method = "basic"
    username = request.DATA.get('username', None)
    if not username:
        return rv.restPermissionDenied(request, "Password and/or Username is incorrect", error_code=422)
    member = getMemberByUsername(username)
    if not member:
        return rv.restPermissionDenied(request, error=f"Password and/or Username is incorrect for {username}", error_code=422)
    auth_code = request.DATA.get(["auth_code", "code", "invite_token"], None)
    if username and auth_code:
        # this is typically used for OAUTH (final)
        return member_login_uname_code(request, username, auth_code)
    password = request.DATA.get('password', None)
    member.canLogin(request)  # throws exception if cannot login
    if member.requires_totp or member.has_totp:
        auth_method = "basic+totp"
        resp = checkForTOTP(request, member)
        if resp is not None:
            return resp
    if not member.login(request=request, password=password):
        # we do not want permission denied catcher invoked as it is already handled in login method
        return rv.restStatus(request, False, error=f"Invalid Credentials {username}", error_code=401)
    return on_complete_jwt(request, member, auth_method)


def on_complete_jwt(request, member, method="basic"):
    if member.security_token is None or member.security_token == JWT_KEY or member.force_single_session:
        member.refreshSecurityToken()

    member.log(
        "jwt_login", "jwt login succesful",
        request, method="login", level=7)

    device_id = request.DATA.get(["device_id", "deviceID"])

    token = JWToken(
        user_id=member.pk,
        key=member.security_token,
        device_id=device_id,
        access_expires_in=member.getProperty("jwt.expires_in", JWT_EXPIRES, field_type=int),
        refresh_expires_in=member.getProperty("jwt.refresh_expires_in", JWT_REFRESH_EXPIRES, field_type=int))

    request.user = member.getUser()
    request.member = member
    request.signature = token.session_id
    request.device_id = device_id
    request.buid = request.DATA.get("__buid__", None)
    request.auth_session = am.AuthSession.NewSession(request, method)
    if not bool(device_id) and bool(request.buid):
        device_id = request.buid
    if bool(device_id):
        am.MemberDevice.register(request, member, device_id)
    request.jwt_token = token.access_token  # this tells the middleware to store in cookie
    return rv.restGet(
        request,
        dict(
            access=token.access_token,
            refresh=token.refresh_token,
            id=member.pk))


@rd.urlPOST(r'^jwt/logout$')
@rd.urlPOST(r'^jwt/logout/$')
@rd.never_cache
def jwt_logout(request):
    # this will force our token to change
    if request.member:
        request.member.log("jwt_logout", "jwt logout", request, method="logout", level=25)
        request.member.sendEvent("logout", "user requested logout")
        request.member.refreshSecurityToken()
        request.clear_jwt_cookie = True  # tells middleware to remove from cookie
    return rv.restStatus(request, True)


@rd.urlPOST(r'^jwt/refresh$')
@rd.urlPOST(r'^jwt/refresh/$')
@rd.never_cache
def jwt_refresh(request):
    # poor mans JWT, carried over
    rtoken = request.DATA.get(['refresh_token', 'refresh'], None)
    if not bool(rtoken):
        return rv.restPermissionDenied(request, error="requires token", error_code=703)
    token = JWToken(token=rtoken)
    if not token.payload.user_id:
        return rv.restPermissionDenied(request, error="invalid token", error_code=-701)
    member = am.Member.objects.filter(pk=token.payload.user_id).last()
    if not member:
        return rv.restPermissionDenied(request, error=f"Password or Username is incorrect for uid:{token.payload.user_id}", error_code=422)
    token.key = member.security_token
    if not token.is_valid:
        request.member = member
        return rv.restPermissionDenied(request, error="invalid token", error_code=-702)
    if member.security_token is None:
        member.refreshSecurityToken()
    member.canLogin(request)
    token.refresh(member.getProperty("jwt.expires_in", JWT_EXPIRES, field_type=int))
    request.jwt_token = token.access_token  # this tells the middleware to store in cookie
    if JWT_UPDATE_REFRESH_TOKEN:
        token.refresh_expires_in = member.getProperty("jwt.refresh_expires_in", JWT_REFRESH_EXPIRES, field_type=int)
        rtoken = token.refresh_token
    return rv.restGet(request, dict(access=token.access_token, refresh=rtoken))


def getMemberByUsername(username):
    member = None
    username = username.lower()
    if username.count('@') == 1:
        member = am.Member.objects.filter(email=username).last()
    if not member:
        member = am.Member.objects.filter(username=username).last()
    return member


def checkForTOTP(request, member):
    if not member.has_totp and not member.phone_number:
        member.reportIncident(
            "account", f"{member.username} TOTP not set", level=8,
            error_code=455,
            request=request)
        return None
    if not member.has_totp:
        # we have a phone number so tell them to login with code
        # they will need to request a code
        request.member = member
        return rv.restPermissionDenied(
            request, error=member.phone_number[-4:],
            error_code=454)
    totp_code = request.DATA.get("totp_code", None)
    if totp_code is None:
        # member.log("login_blocked", "requires MFA (TOTP)", request, method="login", level=31)
        request.member = member
        return rv.restPermissionDenied(request, error="Requires MFA (TOTP)", error_code=455)
    if not member.totp_verify(totp_code):
        request.member = member
        member.log("login_blocked", "Invalid MFA code", request, method="login", level=31)
        return rv.restPermissionDenied(request, error="Invalid Credentials", error_code=456)
    return None


def member_login_uname_pword(request, username, password):
    member = getMemberByUsername(username)
    if not member:
        return rv.restPermissionDenied(request, error=f"Password or Username is not correct for {username}", error_code=422)
    member.canLogin(request)  # throws exception if cannot login
    if member.requires_totp or member.has_totp:
        resp = checkForTOTP(request, member)
        if resp is not None:
            return resp
    if not member.login(request=request, password=password, use_jwt=False):
        request.member = member
        member.log("login_failed", "incorrect password", request, method="login", level=31)
        return rv.restPermissionDenied(request, error="Password or Username is incorrect", error_code=401)

    member.log("password_login", "password login", request, method="login", level=7)
    if request.session is not None:
        request.session["member_id"] = member.pk
        request.session["_auth_user_id"] = member.pk
    return rv.restGet(request, dict(id=member.pk, session_key=request.session.session_key))


def member_login_uname_code(request, username, auth_code):
    member = getMemberByUsername(username)
    if not member:
        return rv.restPermissionDenied(request, error=f"Username or code is incorrect {username}/{auth_code}", error_code=422)
    if not member.is_active:
        request.member = member
        member.log("login_blocked", "account is not active", request, method="login", level=31)
        return rv.restPermissionDenied(request, error=f"{username} Account disabled", error_code=410)
    if member.is_blocked:
        request.member = member
        member.log("login_blocked", "account is locked out", request, method="login", level=31)
        return rv.restPermissionDenied(request, error=f"{username} Account locked out", error_code=411)
    auth_code = auth_code.replace('-', '').replace(' ', '')
    if member.auth_code is None or member.auth_code != auth_code:
        request.member = member
        member.log("login_blocked", "accessing used or expired token link", request, method="login", level=31)
        return rv.restPermissionDenied(request, f"token already used or expired for {username}", error_code=492)
    if member.auth_code_expires < datetime.now():
        request.member = member
        member.log("login_blocked", "accessing expired token link", request, method="login", level=31)
        return rv.restPermissionDenied(request, "token expired", error_code=493)
    password = request.DATA.get('new_password', None)
    if password:
        member.setPassword(password)
    member.auth_code = None
    member.auth_code_expires = None
    member.canLogin(request, using_password=False)  # throws exception if cannot login
    member.loginNoPassword(request)
    member.save()
    member.log("code_login", "code login", request, method="login", level=8)
    if request.DATA.get("auth_method") == "basic" and ALLOW_BASIC_LOGIN:
        return rv.restGet(request, dict(id=member.pk, session_key=request.session.session_key))
    return on_complete_jwt(request, member, "auth_code")


@rd.url(r'^logout$')
@rd.url(r'^logout/$')
@rd.never_cache
def member_logout(request):
    """
    | Parameters: none

    | Return: status + error

    | Logout
    """
    if request.user.is_authenticated:
        request.user.log("logout", "user logged out", request, method="logout", level=8)
    request.member.logout(request)
    return rv.restStatus(request, True)


@rd.url(r'^loggedin/$')
@rd.never_cache
def is_member_logged_in(request):
    """
    | param: none

    | Return: status + error

    | Check if the current user is logged in
    """
    if request.user:
        return rv.restStatus(request, request.user.is_authenticated)
    return rv.restStatus(request, False)


@rd.urlPOST('invite/validate')
@rd.requires_params(["username"])
def member_invite_confirm(request):
    username = request.DATA.get('username', None)
    auth_code = request.DATA.get(["auth_token", "invite_token"], None)
    member = getMemberByUsername(username)
    if not member or not auth_code:
        return rv.restPermissionDenied(request, error=f"Username or code is incorrect {username}/{auth_code}", error_code=422)
    auth_code = auth_code.replace('-', '').replace(' ', '')
    if member.auth_code is None or member.auth_code != auth_code:
        return rv.restStatus(request, False)
    return rv.restStatus(request, True)


@rd.urlPOST('mfa/request_code')
@rd.requires_params(["username"])
def member_request_code(request):
    member, resp = get_member_from_request(request)
    if resp is not None:
        return resp
    return member_forgot_password_code(request, member)


def get_member_from_request(request):
    username = request.DATA.get('username', None)
    if not username:
        return None, rv.restPermissionDenied("Username is required")
    member = getMemberByUsername(username)
    if not member:
        return member, rv.restPermissionDenied(request, error=f"Password or Username is incorrect for {username}", error_code=422)
    if not member.is_active:
        request.member = member
        member.log("login_blocked", "account is not active", request, method="login", level=31)
        return member, rv.restPermissionDenied(request, error=f"{member.username} Account disabled", error_code=410)
    if member.is_blocked:
        request.member = member
        member.log("login_blocked", "account is locked out", request, method="login", level=31)
        return member, rv.restPermissionDenied(request, error=f"{member.username} Account locked out", error_code=411)
    return member, None


@rd.urlPOST('forgot')
@rd.never_cache
def member_forgot_password(request):
    """
    | param: username = use the username as the lookup
    | param: email = use the email as the lookup

    | Return: status + error

    | Send fgroupet password reset instructions
    """
    member, resp = get_member_from_request(request)
    if member is None:
        if FORGET_ALWAYS_TRUE:
            return rv.restStatus(request, True, msg="Password reset instructions have been sent to your email. (If valid account)")
        return resp
    if resp is not None and not member.is_active:
        if FORGET_ALWAYS_TRUE:
            return rv.restStatus(request, True, msg="Password reset instructions have been sent to your email. (If valid account)")
        return resp

    if request.DATA.get("use_code", False):
        return member_forgot_password_code(request, member)

    if member.auth_code is not None and member.auth_code_expires > datetime.now():
        if FORGET_ALWAYS_TRUE:
            return rv.restStatus(request, True, msg="Password reset instructions have been sent to your email. (If valid account)")
        return rv.restPermissionDenied(request, "already sent valid auth code")

    member.auth_code = crypto.randomString(16)
    member.auth_code_expires = datetime.now() + timedelta(minutes=10)
    member.save()
    member.log("forgot", "user requested password reset", request, method="password_reset", level=17)

    token = "{}-{}".format(crypto.obfuscateID("Member", member.id), member.auth_code)
    render_to_mail("registration/password_reset_email", {
        'user': member,
        'uuid': member.uuid,
        'token': token,
        'subject': 'password reset',
        'to': [member.email],
    })

    return rv.restStatus(request, True, msg="Password reset instructions have been sent to your email. (If valid account)")


def member_forgot_password_code(request, member):
    member.generateAuthCode(6)
    code = "{} {}".format(member.auth_code[:3], member.auth_code[3:])

    context = helpers.getContext(
        request,
        user=member,
        code=code)

    if member.notify(
            context=context,
            email_only=False,
            force=True,
            subject="Login Code",
            template=settings.get("EMAIL_TEMPLATE_RESET", "email/reset_code.html"),
            sms_msg="Your login code is:\n{}".format(code)):
        member.log("requested", "user requested password reset code", request, method="login_token", level=8)
        return rv.restStatus(request, True)
    request.member = member
    member.log("error", "No valid email/phone, check users profile!", request, method="login_token", level=6)
    return rv.restPermissionDenied(request, error="No valid email/phone, check users profile!")


# time based one time passwords
@rd.urlGET('totp/qrcode')
@rd.login_required
def totp_qrcode(request):
    token = request.member.getProperty("totp_token", category="secrets", default=None)
    reset = request.DATA.get("force_reset", False)
    if token is not None and not reset:
        return rv.restPermissionDenied(request, "token exists")
    params = dict(data=request.member.totp_getURI())
    error = request.DATA.get("error", None)
    if error is not None:
        params["error"] = error
    version = request.DATA.get("version", None)
    if version is not None:
        params["version"] = int(version)
    img_format = request.DATA.get("format", "png")
    if img_format is not None:
        params["img_format"] = img_format
    scale = request.DATA.get("scale", 4)
    if scale is not None:
        params["scale"] = int(scale)
    code = generateQRCode(**params)
    if img_format == "base64":
        return HttpResponse(code, content_type="text/plain")
    elif img_format == "svg":
        return HttpResponse(code, content_type="image/svg+xml")
    return HttpResponse(code, content_type="image/png")


# time based one time passwords
@rd.urlPOST(r'^totp/verify$')
@rd.login_required
def totp_verify(request):
    code = request.DATA.get("code", None)
    if code is None or len(code) != 6:
        return rv.restPermissionDenied(request, "invalid code format")
    if not request.member.totp_verify(code):
        return rv.restPermissionDenied(request, "invalid code")
    request.member.setProperty("totp_verified", 1)
    return rv.restStatus(request, True)


# time based one time passwords
@rd.urlPOST('security/ip/failed_logins')
@rd.login_required
def failed_logins_by_ip(request):
    ips = am.Member.GetIPsWithFailedLoginAttempts(request.DATA.get("threshold", 10))
    lst = [dict(ip=k, count=v) for k, v in ips.items()]
    return rv.restList(request, lst)
