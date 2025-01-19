from django.shortcuts import render, redirect, get_object_or_404
from .models import Workshop, Schüler, Klasse, Lehrer, TwoDayWorkshop, Teilnahme
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
    two_day_workshops = TwoDayWorkshop.objects.all()
    return render(request, 'display_and_edit.html', {
        'workshops': workshops,
        'two_day_workshops': two_day_workshops,
    })

def list_workshops(request):
    workshops = Workshop.objects.all()
    workshop_participants = {
        workshop.id: workshop.teilnahme_set.all() for workshop in workshops
    }
    two_day_workshops = TwoDayWorkshop.objects.all()
    return render(request, 'workshop_list.html', {
        'workshops': workshops,
        'two_day_workshops': two_day_workshops,
        'workshop_participants': workshop_participants,
    })

def get_students_by_class(request, class_id):
    students = Schüler.objects.filter(klasse_id=class_id)
    students_data = [{'id': student.id, 'name': student.name} for student in students]
    return JsonResponse({'students': students_data})

# Workshop hinzufügen
def add_workshop(request):
    if request.method == 'POST':
        workshop_type = request.POST.get('workshop_type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        participants = request.POST.get('participants')
        cost = request.POST.get('cost')
        teacher_kuerzel = request.POST.get('teacher_kuerzel')

        try:
            teacher = Lehrer.objects.get(kuerzel=teacher_kuerzel)
        except Lehrer.DoesNotExist:
            return HttpResponse("Lehrer nicht gefunden.", status=404)

        if workshop_type == 'single':
            date_str = request.POST.get('date')
            start_time_str = request.POST.get('start_time')
            end_time_str = request.POST.get('end_time')

            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()
            except ValueError:
                return HttpResponse("Ungültige Eingabedaten.", status=400)

            new_workshop = Workshop(
                title=title,
                description=description,
                location=location,
                date=date,
                starttime=start_time,
                endtime=end_time,
                participant_limit=participants,
                cost=cost,
                teacher=teacher
            )
            new_workshop.save()

        elif workshop_type == 'two_day':
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            day1_start_time_str = request.POST.get('day1_start_time')
            day1_end_time_str = request.POST.get('day1_end_time')
            day2_start_time_str = request.POST.get('day2_start_time')
            day2_end_time_str = request.POST.get('day2_end_time')
            overnight = request.POST.get('overnight') == 'on'

            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                day1_start_time = datetime.strptime(day1_start_time_str, "%H:%M").time()
                day1_end_time = datetime.strptime(day1_end_time_str, "%H:%M").time()
                day2_start_time = datetime.strptime(day2_start_time_str, "%H:%M").time() if day2_start_time_str else None
                day2_end_time = datetime.strptime(day2_end_time_str, "%H:%M").time() if day2_end_time_str else None
            except ValueError:
                return HttpResponse("Ungültige Eingabedaten.", status=400)

            new_two_day_workshop = TwoDayWorkshop(
                title=title,
                description=description,
                location=location,
                start_date=start_date,
                end_date=end_date,
                day1_start_time=day1_start_time,
                day1_end_time=day1_end_time,
                day2_start_time=day2_start_time,
                day2_end_time=day2_end_time,
                overnight=overnight,
                participant_limit=participants,
                cost=cost,
                teacher=teacher
            )
            new_two_day_workshop.save()

        # Schüler zuweisen
        student_ids = request.POST.get('selected_students').split(',')
        for student_id in student_ids:
            student = Schüler.objects.get(id=student_id)
            if workshop_type == 'single':
                Teilnahme.objects.create(student=student, workshop=new_workshop)
            elif workshop_type == 'two_day':
                Teilnahme.objects.create(student=student, workshop=new_two_day_workshop)

        return redirect('display_and_edit')

    teachers = Lehrer.objects.all()
    classes = Klasse.objects.all()
    students = Schüler.objects.all()
    return render(request, 'add_workshop.html', {'teachers': teachers, 'classes': classes, 'students': students})

# Workshop bearbeiten
def edit_single_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        participants = request.POST.get('participants')
        cost = request.POST.get('cost')
        teacher_kuerzel = request.POST.get('teacher_kuerzel')

        try:
            teacher = Lehrer.objects.get(kuerzel=teacher_kuerzel)
        except Lehrer.DoesNotExist:
            return HttpResponse("Lehrer nicht gefunden.", status=404)

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError:
            return HttpResponse("Ungültige Eingabedaten.", status=400)

        workshop.title = title
        workshop.description = description
        workshop.location = location
        workshop.date = date
        workshop.starttime = start_time
        workshop.endtime = end_time
        workshop.participant_limit = participants
        workshop.cost = cost
        workshop.teacher = teacher
        workshop.save()

        return redirect('display_and_edit')

    teachers = Lehrer.objects.all()
    return render(request, 'edit_workshop.html', {
        'workshop': workshop,
        'workshop_type': 'single',
        'teachers': teachers
    })

def edit_two_day_workshop(request, workshop_id):
    workshop = get_object_or_404(TwoDayWorkshop, id=workshop_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        day1_start_time_str = request.POST.get('day1_start_time')
        day1_end_time_str = request.POST.get('day1_end_time')
        day2_start_time_str = request.POST.get('day2_start_time')
        day2_end_time_str = request.POST.get('day2_end_time')
        overnight = request.POST.get('overnight') == 'on'
        participants = request.POST.get('participants')
        cost = request.POST.get('cost')
        teacher_kuerzel = request.POST.get('teacher_kuerzel')

        try:
            teacher = Lehrer.objects.get(kuerzel=teacher_kuerzel)
        except Lehrer.DoesNotExist:
            return HttpResponse("Lehrer nicht gefunden.", status=404)

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            day1_start_time = datetime.strptime(day1_start_time_str, "%H:%M").time()
            day1_end_time = datetime.strptime(day1_end_time_str, "%H:%M").time()
            day2_start_time = datetime.strptime(day2_start_time_str, "%H:%M").time() if day2_start_time_str else None
            day2_end_time = datetime.strptime(day2_end_time_str, "%H:%M").time() if day2_end_time_str else None
        except ValueError:
            return HttpResponse("Ungültige Eingabedaten.", status=400)

        workshop.title = title
        workshop.description = description
        workshop.location = location
        workshop.start_date = start_date
        workshop.end_date = end_date
        workshop.day1_start_time = day1_start_time
        workshop.day1_end_time = day1_end_time
        workshop.day2_start_time = day2_start_time
        workshop.day2_end_time = day2_end_time
        workshop.overnight = overnight
        workshop.participant_limit = participants
        workshop.cost = cost
        workshop.teacher = teacher
        workshop.save()

        return redirect('display_and_edit')

    teachers = Lehrer.objects.all()
    return render(request, 'edit_workshop.html', {
        'workshop': workshop,
        'workshop_type': 'two_day',
        'teachers': teachers
    })

# Workshop löschen
def delete_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)
    if request.method == 'POST':
        workshop.delete()
        return redirect('display_and_edit')
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