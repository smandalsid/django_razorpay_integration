from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
# Create your views here.

razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def home(request):
    currency="INR"
    amount=10000
    razorpay_order=razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='0'))
    razorpay_order_id=razorpay_order['id']
    callback_url='payment_handler/'

    context={}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request, "home.html", locals())

@csrf_exempt
def payment_handler(request):
    if request.method=="POST":
        try:
            payment_id=request.POST.get('razorpay_payment_id', '')
            razorpay_order_id=request.POST.get('razorpay_order_id', '')
            signature=request.POST.get('razorpay_signature', '')
            params_dict={
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id' : payment_id,
                'razorpay_signature': signature,
            }

            result=razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                amount=10000
                try:
                    razorpay_client.payment.capture(payment_id, amount)
                    return render(request, "payment_success.html")
                except:
                    return render(request, "payment_fail.html")
            else:
                return render(request, "payment_fail.html")
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()
    