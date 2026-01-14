from rest import decorators as rd
from rest import views as rv
from account.models import UserPassKey
from account import passkeys
from account.rpc.auth import on_complete_jwt


@rd.url('passkey')
@rd.url('passkey/<int:pk>')
def rest_on_processor(request, pk=None):
    return UserPassKey.on_rest_request(request, pk)


@rd.url('passkeys/register/begin')
@rd.login_required
def rest_on_passkeys_reg_begin(request):
    data, state, rp = passkeys.registerBegin(
        request.member, request,
        request.DATA.get("authenticator", "platform"))
    # state needs to be stored in a session key of some kind
    # or in redis with expires in 5m?
    request.session["fido2_state"] = state
    request.session["fido2_rp_id"] = rp.id
    return rv.restResult(request, data)


@rd.url('passkeys/register/end')
@rd.login_required
def rest_on_passkeys_reg_complete(request):
    uk = passkeys.registerComplete(
        request,
        request.session.pop("fido2_state"),
        request.session.pop("fido2_rp_id"))
    return rv.restStatus(request, True)


@rd.url('passkeys/auth/begin')
def rest_on_passkeys_auth_begin(request):
    data, state, rp = passkeys.authBegin(request)
    # state needs to be stored in a session key of some kind
    # or in redis with expires in 5m?
    request.session["fido2_state"] = state
    request.session["fido2_rp_id"] = rp.id
    return rv.restResult(request, dict(data))


@rd.url('passkeys/auth/confirm')
def rest_on_passkeys_auth_complete(request):
    uk = passkeys.authComplete(
        request,
        request.session.pop("fido2_state"),
        request.session.pop("fido2_rp_id"))
    # we now want to handle the JWT or basic login flow
    return on_complete_jwt(request, uk.member, "passkey")
