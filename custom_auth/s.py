from rest_framework import serializers as S 
from .models import *

class Info_s(S.ModelSerializer):
    class Meta:
        model = Info 
        fields = "__all__"



class Event_s(S.ModelSerializer):

    class Meta:
        model = Event
        fields = "__all__"


class Cheque_s(S.ModelSerializer):

    class Meta:
        model = Cheque
        fields = "__all__"