from rest_framework import serializers

from .models import Benefactor
from .models import Charity, Task


class BenefactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefactor
        fields = ('experience','free_time_per_week')
    #def create(self, validated_data):
    #   return Benefactor.objects.create_user(**validated_data)


class CharitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Charity
        fields = ('name','reg_number')
    #def create(self, validated_data):
    #    return Charity.objects.create_user(**validated_data)

class TaskSerializer(serializers.ModelSerializer):
    pass
