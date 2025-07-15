from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from .models import QRPaymentLog, VendorQRCode


class QRPaymentLogSerializer(serializers.ModelSerializer):
    screenshot_file = serializers.FileField(write_only=True)

    class Meta:
        model = QRPaymentLog
        fields = [
            "id",
            "payment_id",
            "payment_status",
            "modified_date",
            "created_date",
            "screenshot_data",
            "screenshot_file_type",
            "screenshot_file",
        ]
        read_only_fields = ["id", "modified_date", "created_date", "screenshot_data", "screenshot_file_type"]

    def validate_screenshot_file(self, value):
        if value is not None and isinstance(value, UploadedFile):
            if value.size is not None and value.size > 4 * 1024 * 1024:  # 4MB
                raise serializers.ValidationError("File size exceeds 4MB")
            if value.content_type is not None and not value.content_type.startswith("image/"):
                raise serializers.ValidationError("Only image files are allowed")
        return value

    def create(self, validated_data):
        file = validated_data.pop("screenshot_file")
        validated_data["screenshot_data"] = file.read()
        validated_data["screenshot_file_type"] = file.content_type
        # return super().create(validated_data)
        return QRPaymentLog.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.payment_status = validated_data.get("payment_status", instance.payment_status)
        if "payment_id" in validated_data:
            instance.payment_id = validated_data["payment_id"]
        return super().update(instance, validated_data)


class VendorQRCodeSerializer(serializers.ModelSerializer):
    qr_code_file = serializers.FileField(write_only=True)

    class Meta:
        model = VendorQRCode
        fields = ("qr_code_data", "content_type", "qr_code_file")
        read_only_fields = ["qr_code_data", "content_type"]

    def validate_screenshot_file(self, value):
        if value is not None and isinstance(value, UploadedFile):
            if value.size is not None and value.size > 4 * 1024 * 1024:  # 4MB
                raise serializers.ValidationError("File size exceeds 4MB")
            if value.content_type is not None and not value.content_type.startswith("image/"):
                raise serializers.ValidationError("Only image files are allowed")
        return value

    def create(self, validated_data):
        file = validated_data.pop("qr_code_file")
        validated_data["qr_code_data"] = file.read()
        validated_data["content_type"] = file.content_type
        return VendorQRCode.objects.create(**validated_data)

    def update(self, instance, validated_data):
        file = validated_data.pop("qr_code_file", None)
        if file:
            instance.qr_code_data = file.read()
            instance.content_type = file.content_type
        instance.save()
        return instance
