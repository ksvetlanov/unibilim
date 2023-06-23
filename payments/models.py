from django.db import models
#from students.models import Students
from professors.models import Professors
#from ???.models import StudentRequest  

class Payments(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
#    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name="student_payments")
    professor = models.ForeignKey(Professors, on_delete=models.CASCADE, related_name="professor_payments")
    description = models.TextField()
    service = models.CharField(max_length=255)
    #student_request = models.ForeignKey(StudentRequest, on_delete=models.CASCADE, related_name="payments")
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('DECLINED', 'Declined'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
    )
