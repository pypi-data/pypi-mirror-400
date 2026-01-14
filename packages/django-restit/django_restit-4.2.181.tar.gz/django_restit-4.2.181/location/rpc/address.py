from rest import decorators as rd
from location import models as location


@rd.url('address')
@rd.url('address/<int:pk>')
def rest_on_address(request, pk=None):
    return location.Address.on_rest_request(request, pk)
