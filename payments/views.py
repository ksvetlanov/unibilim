from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payments
from .serializers import PaymentsSerializer, InitiatePaymentSerializer, ResponseSerializer
from django.shortcuts import get_object_or_404
from django.http import Http404,  JsonResponse
from random import shuffle
import requests
import hashlib
from drf_yasg.utils import swagger_auto_schema
from students.models import Student
from professors.models import Professors
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import logging
from meetings.models import Meetings
import datetime
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv


load_dotenv()

pg_merchant_id = os.getenv('MERCHANT_ID')
secret_key = os.getenv('SECRET_KEY')


logger = logging.getLogger(__name__)
@method_decorator(csrf_exempt, name='dispatch')
class PaymentResultView(View):
    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('pg_order_id')
        print("order_id", order_id)
        payment_id = request.POST.get('pg_payment_id')
        print("payment_id", payment_id)
        status = create_request(payment_id)
        print(status)
        try:
            payment = Payments.objects.get(id=order_id)
            print(f"Current payment status: {payment.status}")

            if status == 'success':
                payment.status = 'COMPLETED'
                for slot in payment.time_slots:
                    meeting_time = datetime.datetime.strptime(slot, "%Y-%m-%dT%H:%M:%SZ")
                    Meetings.objects.create(
                        subject=payment.service,
                        student=payment.student,
                        professor=payment.professor,
                        datetime=meeting_time,
                        status='PENDING'
                    )
            elif status == 'waiting':
                pass
            else:
                payment.status = 'DECLINED'

            payment.save()
            print('Payment status updated successfully')
            return JsonResponse({'status': 'success', 'message': 'Payment status updated successfully'})

        except Payments.DoesNotExist:
            print(f"Payment with order_id {order_id} does not exist.")
            return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)
        except Exception as e:
            print(f"Error processing payment: {e}")
            return JsonResponse({'status': 'error', 'message': 'Error processing payment'}, status=500)



class InitiatePaymentView(APIView):
    @swagger_auto_schema(
    request_body=InitiatePaymentSerializer,
    responses={200: ResponseSerializer()},
    operation_description="""
    Endpoint инициирует процесс оплаты и возвращает ответ в формате XML. 
    Поле 'time_slots' ожидает список объектов.
    Каждый объект должен быть строкой, содержащей дату и время в формате 'YYYY-MM-DDTHH:MM:SS'. 
    Например: '2023-07-20T14:30:00'.
    """
)

    def post(self, request, format=None):
        student_id = request.user.student.id
        token = request.auth.key
        student = Student.objects.get(id=student_id)
        professor_id = request.data.get('professor_id') 
        professor = Professors.objects.get(id=professor_id)
        time_slots = request.data.get('time_slots') 
        amount_per_slot = request.data.get('amount') 
        service = request.data.get('service') 

        total_amount = len(time_slots) * int(amount_per_slot)


        # формирование описания платежа
        description_lines = []
        for slot in time_slots:  
            description_lines.append(f'Payment for {service}({slot})')

        description = '\n'.join(description_lines)
        
        print("Total Amount:", total_amount)
        print("Description:", description)

        # создаем запись платежа в базе данных
        payment = Payments.objects.create(
            amount=total_amount,
            student=student,
            description=description,
            service=service,
            status='PENDING',
            professor=professor,
            time_slots=time_slots,
        )

        payment_data, pg_payment_id = self.initiate_payment(total_amount, description, student_id, payment.id)
        payment.payment_id = pg_payment_id
        payment.save()
        # возвращаем ответ с информацией о платеже
        serializer = PaymentsSerializer(payment)
        
        return Response({         
            'payment_data': payment_data
        })

    def initiate_payment(self, amount, description, user_id, payment_id ):
        def make_flat_params_array(arr_params, parent_name=''):
            arr_flat_params = []
            i = 0
            for key in sorted(arr_params.keys()):
                i += 1
                val = arr_params[key]
                name = f'{parent_name}{key}{str(i).zfill(3)}'
                if isinstance(val, dict):
                    arr_flat_params.extend(make_flat_params_array(val, name))
                    continue
                arr_flat_params.append((name, str(val)))
            return arr_flat_params

        pg_salt = list('qwertyuiolkjhgfdsazxcvbnm')
        shuffle(pg_salt)
        pg_salt = ''.join(pg_salt)



        request = {
            'pg_order_id': str(payment_id),  # преобразовываем user_id в строку, так как все значения должны быть строками
            'pg_merchant_id': pg_merchant_id,
            'pg_amount': str(amount),
            'pg_description': description,  # используем описание, которое мы сформировали ранее
            'pg_salt': pg_salt,
            'pg_success_url': 'https://class.unibilim.kg/success/',
            'pg_failure_url': 'https://class.unibilim.kg/error_payment/',
            'pg_success_url_method': 'GET',
            'pg_failure_url_method': 'GET',
            'pg_currency': 'KGS',
            'pg_request_method': 'POST',            
            'pg_language': 'ru',
            'pg_result_url': 'https://backend-prod.unibilim.kg/check_payment/',
            'pg_testing_mode': '1',
            'pg_user_id': str(user_id),     
        }

        request_for_signature = make_flat_params_array(request)
        request_for_signature.insert(0, ("method_name", "init_payment.php"))
        request_for_signature.append(("secret_key", secret_key))

        pg_sig = hashlib.md5(';'.join(x[1] for x in request_for_signature).encode()).hexdigest()   
        request['pg_sig'] = pg_sig    

        # Вы можете реализовать проверку ответа здесь, если это необходимо
        response = requests.post('https://api.freedompay.money/init_payment.php', data=request)
        xml_str = response.text    
        root = ET.fromstring(xml_str)
        pg_payment_id = root.find('pg_payment_id').text
        pg_redirect_url = root.find('pg_redirect_url').text
        return pg_redirect_url, pg_payment_id
        #return response  # Вы можете вернуть более полезные данные здесь, например response.json(), если это необходимо


class PaymentsViewSet(viewsets.ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer


def make_flat_params_array(arr_params, parent_name=''):
        arr_flat_params = []
        i = 0
        for key in sorted(arr_params.keys()):
            i += 1
            val = arr_params[key]
            name = f'{parent_name}{key}{str(i).zfill(3)}'
            if isinstance(val, dict):
                arr_flat_params.extend(make_flat_params_array(val, name))
                continue
            arr_flat_params.append((name, str(val)))
        return arr_flat_params
    
def create_request(pg_payment_id):
    pg_salt = list('qwertyuiolkjhgfdsazxcvbnm')
    shuffle(pg_salt)
    pg_salt = ''.join(pg_salt)
   

  

    request = {       
        'pg_payment_id': pg_payment_id,
        'pg_merchant_id': pg_merchant_id,
        'pg_salt': pg_salt,
   
    }

    

    request_for_signature = make_flat_params_array(request)
    request_for_signature.insert(0, ("method_name", "get_status3.php"))
    request_for_signature.append(("secret_key", secret_key))

    pg_sig = hashlib.md5(';'.join(x[1] for x in request_for_signature).encode()).hexdigest()   
    request['pg_sig'] = pg_sig  
    response = requests.post('https://api.freedompay.money/get_status3.php', data=request)  
    response_content = response.content    
    root = ET.fromstring(response_content)

    # Извлечение данных из XML
    pg_status = root.find('pg_payment_status').text
    
    return pg_status




