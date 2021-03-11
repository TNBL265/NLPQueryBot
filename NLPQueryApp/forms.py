from django import forms

Subtopic_Choices = (
    ("finance","finance"),
    ("option2","option2"),
    ("option3","option3"),

)

Privacy_Choices = (
    ('yes','yes'),
    ('no','no'),

)

class NLPQueryForm(forms.Form):
    question = forms.CharField()
    document =  forms.FileField()
    subtopic =  forms.ChoiceField(choices = Subtopic_Choices)
    privacy =  forms.ChoiceField(choices = Privacy_Choices, widget=forms.RadioSelect)

    