from django.core.exceptions import ValidationError
from django.db import models


def validate_file_size(value):
    filesize = value.size

    if filesize > 4 * 1024 * 1024:  # 4MB
        raise ValidationError("The maximum file size that can be uploaded is 4MB")
    else:
        return value


class VendorQRCode(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    qr_code_file = models.ImageField(upload_to="qr_code/", validators=[validate_file_size])

    def __str__(self):
        return f"{self.name} QR Code"


class QRPaymentLog(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING"
        ACCEPTED = "ACCEPTED"
        REJECTED = "REJECTED"
        ABANDONED = "ABANDONED"  # meaning the transaction itself is cancled

    id = models.BigAutoField(primary_key=True)
    order_id = models.BigIntegerField()
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices)
    screenshot_file = models.ImageField(upload_to="screenshot/", validators=[validate_file_size])
    remarks = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment Log for payment ID #{self.order_id}"
