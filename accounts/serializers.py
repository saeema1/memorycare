"""
Serializers for accounts app
"""
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    assigned_doctor = serializers.SerializerMethodField()
    assigned_caregiver = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'date_of_birth', 'address',
            'emergency_contact_name', 'emergency_contact_phone', 'alzheimers_duration_years',
            'specialization', 'license_number', 'assigned_doctor', 'assigned_caregiver',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    
    def get_assigned_doctor(self, obj):
        if obj.assigned_doctor:
            d = obj.assigned_doctor
            return {'id': d.id, 'username': d.username, 'first_name': d.first_name, 'last_name': d.last_name, 'email': d.email}
        return None

    def get_assigned_caregiver(self, obj):
        if obj.assigned_caregiver:
            c = obj.assigned_caregiver
            return {'id': c.id, 'username': c.username, 'first_name': c.first_name, 'last_name': c.last_name, 'email': c.email}
        return None

    def create(self, validated_data):
        """Create a new user"""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update user instance"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
