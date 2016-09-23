# from django import forms
# from Hmt import models
#
# class TaskModelForm(forms.ModelForm):
#     class Meta:
#         model = models.Task
#         exclude = ()
#     def __init__(self,*args,**kwargs):
#         super(TaskModelForm,self).__init__(*args,**kwargs)
#         for field_name in self.base_fields:
#             field = self.base_fields[field_name]
#             field.widget.attrs.update({'class':'form-control'})