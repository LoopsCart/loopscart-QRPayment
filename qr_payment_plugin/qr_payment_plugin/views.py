from django.http import Http404, HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import QRPaymentLog, VendorQRCode
from .serializers import QRPaymentLogSerializer, VendorQRCodeSerializer


class VendorQRUploadView(APIView):
    def post(self, request):
        try:
            # vendor_id = request.data.get("vendor_id")
            serializer = VendorQRCodeSerializer(data=request.data)
            if serializer.is_valid():
                # instance = serializer.save(vendor_id=vendor_id)
                serializer.save()
                # return Response({"success": True, "id": instance.vendor_id}, status=status.HTTP_201_CREATED)
                return Response({"success": True}, status=status.HTTP_201_CREATED)

            print("error", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendorQRDetailView(APIView):
    def post(self, request, format=None):
        # vendor_id = request.data.get("vendor_id")
        try:
            # qr = VendorQRCode.objects.get(pk=vendor_id)
            qr = VendorQRCode.objects.first()
            if qr:
                return HttpResponse(qr.qr_code_data, content_type=qr.content_type)
            raise VendorQRCode.DoesNotExist
        except VendorQRCode.DoesNotExist:
            raise Http404("Not found")


class QRPaymentLogAdminView(APIView):
    def post(self, request):
        id = request.data.get("log_id")
        payment_id = request.data.get("payment_id")
        payment_status = QRPaymentLog.PaymentStatus(request.data.get("payment_status"))

        if isPaymentComplete(payment_id):
            return Response({"error": "Payment is already complete"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = QRPaymentLog.objects.filter(id=id).latest("modified_date")
            if instance:
                instance.payment_status = payment_status
                instance.save()
                return Response(
                    {"success": True, "payment_id": instance.payment_id, "payment_stats": instance.payment_status},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response({"error": "Payment not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QRPaymentLogCustomerView(APIView):
    def post(self, request):
        try:
            payment_id = request.data.get("payment_id")
            if isPaymentComplete(payment_id):
                return Response({"success": False, "error": "Payment ID already complete"}, status=status.HTTP_400_BAD_REQUEST)

            request.data["payment_status"] = QRPaymentLog.PaymentStatus.PENDING
            serializer = QRPaymentLogSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                return Response({"success": True, "id": instance.payment_id}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def isPaymentComplete(payment_id):
    try:
        payment_log = QRPaymentLog.objects.filter(payment_id=payment_id).latest("modified_date")
        if payment_log and (
            payment_log.payment_status == QRPaymentLog.PaymentStatus.ACCEPTED
            or payment_log.payment_status == QRPaymentLog.PaymentStatus.REJECTED
        ):
            return True
        return False
    except QRPaymentLog.DoesNotExist:
        return False


class QRPaymentStatusView(APIView):
    def get(self, request, pk):
        try:
            payment_id = int(pk)
            instance = QRPaymentLog.objects.filter(payment_id=payment_id).order_by("-modified_date").first()
            if instance:
                data = QRPaymentLogSerializer(instance).data
                data.pop("screenshot_data", None)
                return Response(data)
            else:
                return Response({"error": "Not found"})
        except ValueError:
            return Response({"error": "Invalid payment_id"}, status=status.HTTP_400_BAD_REQUEST)


class QRPaymentLogsDetailView(APIView):
    def post(self, request, format=None):
        payment_id = request.data.get("payment_id")
        try:
            logs = QRPaymentLog.objects.filter(payment_id=payment_id).order_by("-modified_date")
            response = [
                {
                    "id": log.id,
                    "payment_id": log.payment_id,
                    "payment_status": log.payment_status,
                    "created_date": log.created_date,
                    "modified_date": log.modified_date,
                }
                for log in logs
            ]
            return Response(response)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QRPaymentSSView(APIView):
    def get(self, request, pk):
        id = int(pk)
        try:
            instance = QRPaymentLog.objects.get(id=id)
            if instance:
                return HttpResponse(instance.screenshot_data, content_type=instance.screenshot_file_type)
        except Exception:
            raise Http404("Not found")
