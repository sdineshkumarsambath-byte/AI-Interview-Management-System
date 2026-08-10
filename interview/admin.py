from django.contrib import admin
from .models import Candidate

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email',)
    search_fields = ('name', 'email',)

admin.site.register(Candidate, CandidateAdmin)

    
from .models import Question

admin.site.register(Question)