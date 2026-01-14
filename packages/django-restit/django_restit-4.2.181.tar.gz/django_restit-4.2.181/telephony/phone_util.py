from django.conf import settings
from objict import objict
import phonenumbers

try:
    import twilio
    import twilio.rest
except ImportError:
    pass

client = twilio.rest.Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)


def lookup(number, country="US", name_lookup=True):
    extra_info = ['carrier']
    if name_lookup:
        extra_info.append("caller-name")
    number = normalize(number, country)
    output = objict(success=False)
    try:
        resp = client.lookups.v1.phone_numbers(number).fetch(type=extra_info)
    except Exception as err:
        output.reason = str(err)
        return output
    output.success = True
    output.number = number
    output.carrier = objict.fromdict(resp.carrier)
    if resp.caller_name:
        output.owner_name = resp.caller_name.get("caller_name", None)
        output.owner_kind = resp.caller_name.get("caller_type", None)
    return output


def lookup2(number, country="US", name_lookup=True):
    extra_info = ['line_type_intelligence']
    if name_lookup:
        extra_info = ["caller_name"]
        # extra_info.append("sim_swap")
        # extra_info.append("call_forwarding")
        # extra_info.append("live_activity")
    number = normalize(number, country)
    output = objict(success=False)
    try:
        resp = client.lookups.v2.phone_numbers(number).fetch(fields=extra_info)
    except Exception as err:
        output.reason = str(err)
        return output
    return resp
    # output.success = True
    # output.number = number
    # output.carrier = objict.fromdict(resp.lineTypeIntelligence)
    # if resp.callerName:
    #     output.owner_name = resp.callerName.get("caller_name", None)
    #     output.owner_kind = resp.callerName.get("caller_type", None)
    # return output


    # ? access_key = 66b9eeb5c801549b999e91dab5a9e2d6
    # & number = 6172853630
    # & country_code = US
    # & format = 1

import requests
numverify_key = settings.NUMVERIFY_KEY
numverify_url = "http://apilayer.net/api/validate"


def verify(number, country_code="US", format=1):
    r = requests.get(numverify_url, dict(
        number=number, country_code=country_code,
        format=format, access_key=numverify_key))
    try:
        return objict.fromdict(r.json())
    except Exception:
        pass
    return None


def validate(number, country_code="US"):
    """
    {
        'NumberValidateResponse': {
            'Carrier': 'string',
            'City': 'string',
            'CleansedPhoneNumberE164': 'string',
            'CleansedPhoneNumberNational': 'string',
            'Country': 'string',
            'CountryCodeIso2': 'string',
            'CountryCodeNumeric': 'string',
            'County': 'string',
            'OriginalCountryCodeIso2': 'string',
            'OriginalPhoneNumber': 'string',
            'PhoneType': 'string',
            'PhoneTypeCode': 123,
            'Timezone': 'string',
            'ZipCode': 'string'
        }
    }
    """
    from metrics.providers import aws
    client = aws.getClient(service="pinpoint")
    pr = client.phone_number_validate(
        NumberValidateRequest=dict(
            IsoCountryCode="US",
            PhoneNumber="+12024132409"))
    if pr:
        pr = objict.fromdict(pr)
        if pr.NumberValidateResponse:
            info = pr.NumberValidateResponse
            out = objict()
            for k, v in info:
                kl = ''.join(['_' + i.lower() if i.isupper() else i for i in k]).lstrip('_')
                out[kl] = v
            return out
    return None


def sendSMS(to_num, from_num, msg, country="US"):
    to_num = normalize(to_num, country)
    from_num = normalize(from_num, country)
    tmsg = client.messages.create(body=msg, to=to_num, from_=from_num)
    return tmsg


def sendWhatsApp(to_num, from_num, msg, country="US"):
    to_num = normalize(to_num, country)
    to_num = f"whatsapp:{to_num}"
    from_num = normalize(from_num, country)
    from_num = f"whatsapp:{from_num}"
    tmsg = client.messages.create(body=msg, to=to_num, from_=from_num)
    return tmsg


def find(text, country="US"):
    # finds any phone numbers in the text blob
    numbers = []
    for match in phonenumbers.PhoneNumberMatcher(text, country):
        numbers.append(normalize(match.number, country))
    return numbers


def isValid(number, country="US"):
    return phonenumbers.is_valid_number(phonenumbers.parse(number, country))


def normalize(raw_phone, country="US"):
    # turns a number like 202-413-2409 into +12024132409
    return convert_to_e164(raw_phone, country)


def convert_to_e164(raw_phone, country="US"):
    if not raw_phone:
        return

    if raw_phone[0] == '+':
        # Phone number may already be in E.164 format.
        parse_type = None
    else:
        # If no country code information present, assume it's a US number
        parse_type = country

    phone_representation = phonenumbers.parse(raw_phone, parse_type)
    return phonenumbers.format_number(
        phone_representation,
        phonenumbers.PhoneNumberFormat.E164)
