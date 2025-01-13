from django.shortcuts import render, redirect, get_object_or_404
from .models import Workshop, Schüler, Klasse, Lehrer
from django.http import HttpResponse, JsonResponse
from django.template import loader
import requests, json
from django.conf import settings 
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

def login_page(request):
    return render(request, 'login.html')

def display_and_edit(request):
    workshops = Workshop.objects.all()
    return render(request, 'display_and_edit.html', {'workshops': workshops})

def list_workshops(request):
    workshops = Workshop.objects.all()
    workshop_participants = {
        workshop.id: workshop.teilnahme_set.all() for workshop in workshops
    }
    return render(request, 'workshop_list.html', {
        'workshops': workshops,
        'workshop_participants': workshop_participants,
    })

# Workshop hinzufügen
def add_workshop(request):
    template = loader.get_template('add_workshop.html')

    if request.method == 'POST':
        title = request.POST.get('name')
        description = request.POST.get('description')
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        location = request.POST.get('location')
        participants = request.POST.get('participants')
        cost_str = request.POST.get('cost')
        teacher_kuerzel = request.POST.get('teacher_kuerzel')

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            participants = int(participants)
            cost = float(cost_str)
        except ValueError:
            return HttpResponse("Ungültige Eingabedaten.", status=400)

        try:
            teacher = Lehrer.objects.get(kuerzel=teacher_kuerzel)
        except Lehrer.DoesNotExist:
            return HttpResponse("Lehrer nicht gefunden.", status=404)

        new_workshop = Workshop(
            title=title,
            description=description,
            date=date,
            starttime=start_time,
            endtime=end_time,
            location=location,
            participant_limit=participants,
            cost=cost,
            teacher=teacher
        )
        new_workshop.save()

        return redirect('workshops')

    teachers = Lehrer.objects.all()
    return render(request, 'add_workshop.html', {'teachers': teachers})

# Workshop bearbeiten
def edit_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)

    if request.method == 'POST':
        title = request.POST.get('name')
        description = request.POST.get('description')
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        location = request.POST.get('location')
        participants = request.POST.get('participants')
        cost_str = request.POST.get('cost')
        teacher_kuerzel = request.POST.get('teacher_kuerzel')

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            participants = int(participants)
            cost = float(cost_str)
        except ValueError:
            return HttpResponse("Ungültige Eingabedaten.", status=400)

        try:
            teacher = Lehrer.objects.get(kuerzel=teacher_kuerzel)
        except Lehrer.DoesNotExist:
            return HttpResponse("Lehrer nicht gefunden.", status=404)

        workshop.title = title
        workshop.description = description
        workshop.date = date
        workshop.starttime = start_time
        workshop.endtime = end_time
        workshop.location = location
        workshop.participant_limit = participants
        workshop.cost = cost
        workshop.teacher = teacher
        workshop.save()

        return redirect('workshops')

    teachers = Lehrer.objects.all()
    context = {
        'workshop': workshop,
        'teachers': teachers
    }
    return render(request, 'edit_workshop.html', context)

# Workshop löschen
def delete_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)
    if request.method == 'POST':
        workshop.delete()
        return redirect('workshops')
    return render(request, 'confirm_delete.html', {'workshop': workshop})

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