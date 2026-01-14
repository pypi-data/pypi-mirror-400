import json
from base64 import urlsafe_b64encode

try:
    from fido2 import webauthn
    import fido2
    from fido2.server import Fido2Server
    from fido2.utils import websafe_decode, websafe_encode
    from fido2 import cbor
    fido2.features.webauthn_json_mapping.enabled = True
except Exception:
    pass

from rest import settings
from rest import helpers as rh
from account.models import UserPassKey


from objict import objict
# platform == fires apple keychain
# cross-platform = tries for bluetooh
FIDO_KEY_ATTACHMENT = settings.get("FIDO_KEY_ATTACHMENT", "cross-platform")

FIDO_SERVER_ID = settings.get("FIDO_SERVER_ID", settings.SERVER_NAME)
FIDO_SERVER_NAME = settings.get("FIDO_SERVER_NAME", settings.SITE_LABEL)


def verify_origin(id):
    return True


def getServer(request=None, rp_id=FIDO_SERVER_ID, rp_name=FIDO_SERVER_NAME):
    if request is not None:
        rp_id = request.DATA.get(["rp_id", "fido_server_id"], rp_id)
        rp_name = request.DATA.get(["rp_name", "fido_server_name"], rp_name)
    rp = webauthn.PublicKeyCredentialRpEntity(id=rp_id, name=rp_name)
    return Fido2Server(rp, verify_origin=verify_origin)


def registerBegin(member, request, attachment=FIDO_KEY_ATTACHMENT):
    """
    data = CredentialCreationOptions
    state = {'challenge': '4yZmyZmnWP11t7g1S151oVgL0Vw0AU9GegTYJM2_928', 'user_verification': None}
    """

    server = getServer(request)
    reg_data = dict(
        id=rh.toBase64(member.getUUID()),
        name=member.username,
        displayName=member.display_name)
    data, state = server.register_begin(
        reg_data,
        authenticator_attachment=attachment,
        resident_key_requirement=webauthn.ResidentKeyRequirement.PREFERRED)
    rp = objict(server.rp)
    data = objict.fromdict(dict(data))
    data.excludeCredentials = getUserCredentials(member, websafe=True)
    rh.debug("data", data)
    # rh.debug("registerBegin", rp, server.rp.id_hash)
    return data, state, rp


def registerComplete(request, fido2_state, rp_id):
    credentials = request.DATA.get("credentials")
    # rh.debug("registerComplete", fido2_state, rp_id)
    server = getServer(request, rp_id)
    rp = objict(server.rp)
    # rh.debug("registerBegin", rp, server.rp.id_hash)

    auth_data = server.register_complete(
        fido2_state,
        response=credentials
    )

    user_key = UserPassKey(
        uuid=credentials.id,
        name=request.DATA.get("key_name", ""),
        rp_id=rp_id,
        member=request.member,
        platform=request.DATA.getUserAgentPlatform(),
        token=websafe_encode(auth_data.credential_data))
    # Store `auth_data.credential_data` in your database associated with the user
    user_key.save()
    return user_key


def getUserCredentials(member, websafe=False):
    if member is None:
        return []
    creds = [webauthn.AttestedCredentialData(websafe_decode(uk.token)) for uk in member.passkeys.all()]
    if websafe:
        return [dict(
            type="public-key",
            id=rh.toBase64(acd.credential_id)) for acd in creds]
    return creds


def authBegin(request):
    server = getServer(request)
    stored_credentials = getUserCredentials(request.member)
    auth_data, state = server.authenticate_begin(stored_credentials)
    return auth_data, state, objict(server.rp)


def authComplete(request, fido2_state, rp_id):
    credential = request.DATA.get("credential")
    upk = UserPassKey.objects.filter(uuid=credential.id, is_enabled=1).last()
    if upk is None:
        raise Exception("PassKey not found on host.")
    stored_credentials = [webauthn.AttestedCredentialData(websafe_decode(upk.token))]
    server = getServer(request, rp_id)
    cred = server.authenticate_complete(
        fido2_state,
        credentials=stored_credentials,
        response=credential)
    request.member = upk.member
    request.member.canLogin(request, using_password=False)  # throws exception if cannot login
    request.member.loginNoPassword(request=request)
    request.member.log(
        "passkey_login", "passkey login succesful", 
        request, method="login", level=7)
    upk.touch()
    return upk
