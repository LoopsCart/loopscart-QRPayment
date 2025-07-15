from django.db import models


class VendorQRCode(models.Model):
    qr_code_data = models.BinaryField()
    content_type = models.CharField(max_length=100)

    def __str__(self):
        return "Vendor's QR Code"


class QRPaymentLog(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING"
        ACCEPTED = "ACCEPTED"
        REJECTED = "REJECTED"

    id = models.BigAutoField(primary_key=True)
    payment_id = models.BigIntegerField()
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices)
    screenshot_data = models.BinaryField()
    screenshot_file_type = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment Log for payment ID #{self.payment_id}"
