from django.http import Http404, HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import QRPaymentLog, VendorQRCode
from .serializers import QRPaymentLogSerializer, VendorQRCodeSerializer

# payment_id == order_id


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
        try:
            qr = VendorQRCode.objects.first()
            if qr:
                serializer = VendorQRCodeSerializer(qr)
                return Response(serializer.data)
                # return HttpResponse(qr.qr_code, content_type="image/jpeg")
            raise VendorQRCode.DoesNotExist
        except VendorQRCode.DoesNotExist:
            raise Http404("Not found")


class QRPaymentLogAdminView(APIView):
    def post(self, request):
        payment_id = request.data.get("order_id")
        payment_status = QRPaymentLog.PaymentStatus(request.data.get("payment_status"))

        if isPaymentComplete(payment_id):
            return Response({"error": "Payment is already complete"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = QRPaymentLog.objects.filter(payment_id=payment_id).latest("modified_date")
            if instance:
                instance.payment_status = payment_status
                instance.save()
                return Response(
                    {"success": True, "order_id": instance.payment_id, "payment_stats": instance.payment_status},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response({"error": "Payment not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QRPaymentLogCustomerView(APIView):
    def post(self, request):
        try:
            payment_id = request.data.get("order_id")
            if isPaymentComplete(payment_id):
                return Response({"success": False, "error": "Payment ID already complete"}, status=status.HTTP_400_BAD_REQUEST)

            mutable_request_data = request.data.copy()
            mutable_request_data["payment_status"] = QRPaymentLog.PaymentStatus.PENDING
            mutable_request_data["payment_id"] = payment_id

            serializer = QRPaymentLogSerializer(data=mutable_request_data)
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
            or payment_log.payment_status == QRPaymentLog.PaymentStatus.ABANDONED
        ):
            return True
        return False
    except QRPaymentLog.DoesNotExist:
        return False


class QRPaymentStatusView(APIView):
    def get(self, request, pk):
        try:
            payment_id = int(pk)
            instance = QRPaymentLog.objects.filter(payment_id=payment_id).latest("modified_date")
            if instance:
                data = QRPaymentLogSerializer(instance).data
                data.pop("screenshot_data", None)
                return Response(data)
            else:
                return Response({"error": "Not found"})
        except ValueError:
            return Response({"error": "Invalid Order id"}, status=status.HTTP_400_BAD_REQUEST)


class QRPaymentLogsDetailView(APIView):
    def post(self, request, format=None):
        payment_id = request.data.get("order_id")
        try:
            logs = QRPaymentLog.objects.filter(payment_id=payment_id).order_by("-modified_date")
            serializer = QRPaymentLogSerializer(logs, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QRPaymentSSView(APIView):
    def get(self, request, pk):
        id = int(pk)
        try:
            instance = QRPaymentLog.objects.get(id=id)
            if instance:
                return HttpResponse(instance.screenshot_file, content_type="image/jpeg")
        except Exception:
            raise Http404("Not found")
