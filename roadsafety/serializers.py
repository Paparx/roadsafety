from rest_framework import serializers
from .models import User, RoadAccident


#Serializer for User model
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

        #Password will not be shown in API responses
        extra_kwargs = {
            'password': {'write_only': True}
        }


#Serializer for RoadAccident model
class RoadAccidentSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoadAccident
        fields = '__all__'

        
        read_only_fields = [
            'accident_id',
            'date',
            'time',
            'status',
            'created_date',
            'updated_date',
            'user'
        ]