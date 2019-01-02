from django.shortcuts import render
from django.http import HttpResponse


class Dashboard():
    def index(self):
        return render(self, 'admin/login.html')
