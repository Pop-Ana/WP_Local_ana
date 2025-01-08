from django.shortcuts import render, redirect, get_object_or_404
from .models import Workshop, Schüler, Klasse
from django.http import HttpResponse, JsonResponse
from django.template import loader
import requests, json
from django.conf import settings 
from django.views.decorators.csrf import csrf_exempt

def login_page(request):
    return render(request, 'login.html')

def list_workshops(request):
    workshops = Workshop.objects.all()
    workshop_participants = {
        workshop.id: workshop.teilnahme_set.all() for workshop in workshops
    }
    return render(request, 'workshop_list.html', {
        'workshops': workshops,
        'workshop_participants': workshop_participants,
    })

def add_workshops(request):
  template = loader.get_template('add_workshop.html')
  return HttpResponse(template.render())

# Schüler zur Workshop Teilnahme freischalten oder wieder beschränken 
def students_permission(request):
    classes = Klasse.objects.prefetch_related('students').all()  # Prefetch related students for each class
    return render(request, 'students_permission.html', {
        'classes': classes,
    })

@csrf_exempt
def update_student_permission(request, student_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            permission = data.get('permission', False)  # Get the new permission state
            student = Schüler.objects.get(id=student_id)
            student.permission_granted = permission  # Update the permission_granted field
            student.save()
            return JsonResponse({'success': True, 'message': f"Permission for {student.name} has been updated."})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Schüler.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def update_class_permission(request, class_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON body
            action = data.get("action")
            if not action:
                return JsonResponse({"error": "Missing action parameter"}, status=400)

            class_group = get_object_or_404(Klasse, pk=class_id)

            if action == "allow":
                class_group.students.update(permission_granted=True)
                return JsonResponse({"success": True, "message": "All students have been granted permission."})

            elif action == "deny":
                class_group.students.update(permission_granted=False)
                return JsonResponse({"success": True, "message": "All students have been denied permission."})

            else:
                return JsonResponse({"error": "Invalid action"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)