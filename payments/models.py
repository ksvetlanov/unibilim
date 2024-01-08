from django.db import models
from students.models import Student
from professors.models import Professors

 

class Payments(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_payments")
    professor = models.ForeignKey(Professors, on_delete=models.CASCADE, related_name="professor_payments")
    description = models.TextField()
    service = models.CharField(max_length=255)
    time_slots = models.JSONField(blank=True, null=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
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

    STATUS_CHOICES_MEETING = [
        ('SENT', 'Sent'),
        ('DID NOT SENT', 'Did not send'),
    ]
    status_new_meeting = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES_MEETING,
        default='DID NOT SENT'
    )

    def __str__(self):
        return f'{self.service} {self.student.surname} {self.amount}'
