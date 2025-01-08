from django.db import models

# Base User
class Benutzer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

# Admin
class Admin(Benutzer):
    pass # Admin-specific fields can be added here if needed

# Teacher
class Lehrer(Benutzer):
    kuerzel = models.CharField(max_length=10)  

    def __str__(self):
        return f"{self.kuerzel} - {self.name}"

# Class (Klasse) for Students
class Klasse(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

# Student 
class Schüler(Benutzer):
    klasse = models.ForeignKey(Klasse, on_delete=models.SET_NULL, null=True, related_name="students")
    permission_granted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.klasse.name if self.klasse else 'No Class'})"
    
# Workshop
class Workshop(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    participant_limit = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    teacher = models.ForeignKey(Lehrer, on_delete=models.CASCADE, related_name="workshops")

    def __str__(self):
        return self.title

# Participation Model for Students Joining Workshops
class Teilnahme(models.Model):
    student = models.ForeignKey(Schüler, on_delete=models.CASCADE)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'workshop')

    def __str__(self):
        return f"{self.student.name} participating in {self.workshop.title}"