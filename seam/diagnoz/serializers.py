from rest_framework import serializers

from diagnoz.models import Complaint


# class ComplaintSerializer(serializers.Serializer):

#    KeyComplaint = serializers.CharField()
#    Name = serializers.CharField()
#    IdUser = serializers.CharField()

# def create(self, validated_data):
#    return Complaint.objects.create(**validated_data)

# def update(instance, validated_data):
#    instance.KeyComplaint = validated_data.get('KeyComplaint', instance.KeyComplaint)
#    instance.Name = validated_data.get('Name', instance.Name)
#    instance.IdUser = validated_data.get('IdUser', instance.IdUser)
#    instance.save()
#    return instance


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['KeyComplaint', 'Name', 'IdUser']


def create(validated_data):
    return Complaint.objects.create(**validated_data)


def update(instance, validated_data):
    instance.KeyComplaint = validated_data.get('KeyComplaint', instance.KeyComplaint)
    instance.Name = validated_data.get('Name', instance.Name)
    instance.IdUser = validated_data.get('IdUser', instance.IdUser)
    instance.save()
    return instance
