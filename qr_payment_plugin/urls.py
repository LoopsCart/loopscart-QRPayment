from django.urls import path

from .views import (
    QRPaymentLogAdminView,
    QRPaymentLogCustomerView,
    QRPaymentLogsDetailView,
    QRPaymentSSView,
    QRPaymentStatusView,
    VendorQRDetailView,
    VendorQRUploadView,
)

urlpatterns = [
    path("vendor/upload/", VendorQRUploadView.as_view(), name="vendor qr upload"),
    path("vendor/", VendorQRDetailView.as_view(), name="show qr"),
    path("payment-records/<int:pk>/", QRPaymentSSView.as_view(), name="qr payment record detail"),  # to see the individual payment record
    path("payment-record-list/", QRPaymentLogsDetailView.as_view(), name="qr payment record list"),  # to see the entire payment records
    path("receipt-upload/", QRPaymentLogCustomerView.as_view(), name="qr payment customer upload"),  # payment summary for customer
    path("transaction-update/", QRPaymentLogAdminView.as_view(), name="qr payment status admin management"),  # payment management for admin
    path("payment-status/<int:pk>/", QRPaymentStatusView.as_view(), name="qr payment status"),  # to see the payment final status
]
