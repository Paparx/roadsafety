from django.db import models

#user model
#Stores system users like admin, reporter, viewer

class User(models.Model):

    #Different roles allowed in the system
    USER_TYPES = [
        ('admin', 'Admin'),
        ('reporter', 'Reporter'),
        ('viewer', 'Viewer'),
    ]

    user_id = models.CharField(max_length=20, primary_key=True)
    login_id = models.CharField(max_length=30, unique=True)

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)

    #Password stored as text (basic level project)
    password = models.CharField(max_length=128)

    user_type = models.CharField(max_length=20, choices=USER_TYPES)

    #Automatically stores when record is created/updated
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user_type})"


#road accident model
#Stores accident details for hotspot analysis

class RoadAccident(models.Model):

    #Severity level options
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    #Status options
    STATUS_CHOICES = [
    ('danger', 'Danger'),
    ('pending', 'Pending'),
    ('resolved', 'Resolved'),
]
    accident_id = models.CharField(max_length=20, primary_key=True)

    #Each accident is linked to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accidents")

    #Automatically stores date and time of reporting
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    #Basic accident details
    area_name = models.CharField(max_length=150)

    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    cause = models.CharField(max_length=150)

    #Default status is Pending
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Accident {self.accident_id} - {self.area_name}"