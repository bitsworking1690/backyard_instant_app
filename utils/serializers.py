from rest_framework import serializers


class CustomBaseModelSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        # Check for unexpected keys
        allowed_keys = set(self.fields.keys())
        extra_keys = set(data.keys()) - allowed_keys
        if extra_keys:
            raise serializers.ValidationError(
                {"detail": f"Unexpected fields: {', '.join(extra_keys)}"}
            )
        return super().to_internal_value(data)


class CustomBaseSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        # Check for unexpected keys
        allowed_keys = set(self.fields.keys())
        extra_keys = set(data.keys()) - allowed_keys
        if extra_keys:
            raise serializers.ValidationError(
                {"detail": f"Unexpected fields: {', '.join(extra_keys)}"}
            )
        return super().to_internal_value(data)
