from django.shortcuts import render, redirect
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncMonth
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from geopy.geocoders import Nominatim
import uuid
from django.contrib.auth.hashers import make_password, check_password

from .models import RoadAccident, User
from .serializers import UserSerializer, RoadAccidentSerializer


#API VIEWSETS

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RoadAccidentViewSet(viewsets.ModelViewSet):
    queryset = RoadAccident.objects.all()
    serializer_class = RoadAccidentSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['login_id'],
            properties={
                'login_id': openapi.Schema(type=openapi.TYPE_STRING),
                'area_name': openapi.Schema(type=openapi.TYPE_STRING),
                'severity': openapi.Schema(type=openapi.TYPE_STRING),
                'cause': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def update(self, request, *args, **kwargs):
        login_id = request.data.get("login_id")

        if not login_id:
            return Response({"error": "login_id is required"}, status=400)

        try:
            user = User.objects.get(login_id=login_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid user"}, status=400)

        if user.user_type != "admin":
            return Response({"error": "Only admin can update"}, status=403)

        request.data.pop("login_id")
        return super().update(request, *args, **kwargs)


    @action(detail=False, methods=['post'])
    def report(self, request):
        login_id = request.data.get("login_id")

        if not login_id:
            return Response({"error": "login_id is required"}, status=400)

        try:
            user = User.objects.get(login_id=login_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid user"}, status=400)

        if user.user_type not in ['admin', 'reporter']:
            return Response({"error": "Permission denied"}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        accident_id = str(uuid.uuid4())[:10]

        serializer.save(
            accident_id=accident_id,
            user=user,
            status="pending"
        )

        return Response(serializer.data, status=201)


# FRONTEND VIEWS

def home_view(request):
    return render(request, 'homepage.html', {
        'logged_in': request.session.get('logged_in')
    })

def accident_hotspot_view(request):
    return render(request, 'mappage.html')


def legal_view(request):
    return render(request, 'privacyandterms.html')


def profile_view(request):

    if not request.session.get('logged_in'):
        return redirect('login')

    user = User.objects.filter(email=request.session.get('username')).first()
    accidents = RoadAccident.objects.filter(user=user).order_by('-date')

    #COUNTS
    total_reports = accidents.count()
    pending_reports = accidents.filter(status="pending").count()
    resolved_reports = accidents.filter(status="resolved").count()

    #FILTER
    status_filter = request.GET.get('status')

    if status_filter:
        accidents = accidents.filter(status=status_filter)

    return render(request, 'profile.html', {
        'accidents': accidents,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'resolved_reports': resolved_reports,
        'user': user,
        'role': request.session.get('role')
    })

def delete_report(request, accident_id):

    if not request.session.get('logged_in'):
        return redirect('login')

    accident = RoadAccident.objects.filter(accident_id=accident_id).first()

    if accident:
        accident.delete()

    return redirect('profile')


def update_status(request, accident_id):

    if not request.session.get('logged_in'):
        return redirect('login')

    accident = RoadAccident.objects.filter(accident_id=accident_id).first()

    if accident:
        if accident.status == "pending":
            accident.status = "resolved"
        elif accident.status == "resolved":
            accident.status = "danger"
        else:
            accident.status = "pending"

        accident.save()

    return redirect('profile')

def report_view(request):

    if not request.session.get('logged_in'):
        return redirect('login')

    if request.session.get('role', '').lower() != 'reporter':
        return redirect('home')

    if request.method == 'POST':
        location = (request.POST.get('location') or "").strip()
        severity = request.POST.get('severity')
        description = request.POST.get('description')

        user = User.objects.filter(email=request.session.get('username')).first()

        geolocator = Nominatim(user_agent="accitrack")

        try:
            location_obj = geolocator.geocode(location + ", India", timeout=10)

            if location_obj:
                latitude = location_obj.latitude
                longitude = location_obj.longitude
            else:
                latitude = 21.2514
                longitude = 81.6296

        except Exception:
            latitude = 21.2514
            longitude = 81.6296

        print("LAT:", latitude, "LNG:", longitude)

        RoadAccident.objects.create(
            accident_id=str(uuid.uuid4())[:10],
            user=user,
            area_name=location,
            severity=severity.lower(),
            cause=description,
            status='pending',
            latitude=latitude,
            longitude=longitude
        )

        return redirect('profile')

    return render(request, 'report.html')

def signup_view(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'User already exists'})

        user = User.objects.create(
            user_id=str(uuid.uuid4())[:10],
            login_id=email,
            name=email,
            email=email,
            password=make_password(password),
            user_type=role.lower()
        )

        request.session['logged_in'] = True
        request.session['username'] = user.email
        request.session['role'] = user.user_type

        return redirect('home')

    return render(request, 'signup.html')

def login_view(request):

    error = None

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(email=email).first()
        print("USER QUERYSET:", user)  # Debugging line
        try:
            if user:
                print("USER FOUND:", user.email)
            else:
                print("USER NOT FOUND")
        except Exception as e:
            print("ERROR:", e)
            
        if user and check_password(password, user.password):
            request.session['logged_in'] = True
            request.session['username'] = user.email
            request.session['role'] = user.user_type

            return redirect('home')
        else:
            error = "Invalid email or password"

    return render(request, 'login.html', {'error': error})

def logout_view(request):
    request.session.flush()
    return redirect('home')

def accident_data(request):
    accidents = RoadAccident.objects.all()

    data = []
    for acc in accidents:
        data.append({
            "lat": float(acc.latitude) if acc.latitude else None,
            "lng": float(acc.longitude) if acc.longitude else None,
            "status": acc.status,
            "location": acc.area_name
        })

    return JsonResponse(data, safe=False)

   