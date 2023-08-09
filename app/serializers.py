from rest_framework import serializers
from app.models import student, Final_HS,prompts_ai, prompts_list

class LoginSerializer(serializers.Serializer):
    uname = serializers.CharField()
    pswd = serializers.CharField()

class studentSerializer(serializers.ModelSerializer):
    class Meta:
        model = student
        fields = '__all__'  # To include all fields of the Student model

class FinalHSSerializer(serializers.ModelSerializer):
    class Meta:
        model = Final_HS
        fields = '__all__'  # To include all fields of the FinalHS model


class promptSerializer(serializers.ModelSerializer):
    class Meta:
        model = prompts_ai
        fields = '__all__'  


class promptlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = prompts_list
        fields = '__all__' 
