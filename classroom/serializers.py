from rest_framework import serializers
from classroom.models import Routine, Notice, Class, Assignment


class RoutineSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data['added_by'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Routine
        fields = '__all__'
        extra_kwargs = {
            'added_by': {'read_only': True},
            'semester': {'required': True}
        }


class NoticeSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data['added_by'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Notice
        fields = '__all__'
        extra_kwargs = {
            'added_by': {'read_only': True}
        }


class ClassSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Class
        fields = '__all__'
        extra_kwargs = {
            'teacher': {'read_only': True},
        }


class AssignmentSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Assignment
        fields = '__all__'
        extra_kwargs = {
            'teacher': {'read_only': True},
            'semester': {'required': True}
        }
