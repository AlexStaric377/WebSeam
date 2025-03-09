from rest_framework import serializers

from diagnoz.models import Complaint


class ComplaintSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    KeyComplaint = serializers.CharField(style={'base_template': 'textarea.html'})
    Name = serializers.CharField(style={'base_template': 'textarea.html'})
    IdUser = serializers.CharField(style={'base_template': 'textarea.html'})

    def create(self, validated_data):
        return Complaint.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.KeyComplaint = validated_data.get('KeyComplaint', instance.KeyComplaint)
        instance.Name = validated_data.get('Name', instance.Name)
        instance.IdUser = validated_data.get('IdUser', instance.IdUser)
        instance.save()
        return instance
