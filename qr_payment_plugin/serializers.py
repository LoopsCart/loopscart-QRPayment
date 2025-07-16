from rest_framework import serializers

from .models import QRPaymentLog, VendorQRCode


class QRPaymentLogSerializer(serializers.ModelSerializer):
    screenshot_file = serializers.ImageField(write_only=True)

    class Meta:
        model = QRPaymentLog
        fields = [
            "id",
            "payment_id",
            "payment_status",
            "modified_date",
            "created_date",
            "screenshot_file",
        ]
        read_only_fields = ["id", "modified_date", "created_date"]

    def create(self, validated_data):
        return QRPaymentLog.objects.create(**validated_data)


class VendorQRCodeSerializer(serializers.ModelSerializer):
    qr_code = serializers.ImageField(use_url=True)

    class Meta:
        model = VendorQRCode
        fields = ("qr_code", "name", "description")

    def create(self, validated_data):
        # If a QR code already exists, update it. Otherwise, create a new one.
        existing_qr = VendorQRCode.objects.first()
        if existing_qr:
            for attr, value in validated_data.items():
                setattr(existing_qr, attr, value)
            existing_qr.save()
            return existing_qr
        else:
            return VendorQRCode.objects.create(**validated_data)
