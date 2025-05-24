from django import forms


class PacientForm(forms.Form):
    Typegender = [("чол.", "чол."), ("жін.", "жін.")]

    firstName = forms.CharField(max_length=37, min_length=3, label="Ім'я",
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    lastName = forms.CharField(max_length=37, min_length=3, label="Прізвище",
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    gender = forms.ChoiceField(choices=Typegender, label="Стать", widget=forms.Select(attrs={'class': 'form-control'}))
    age = forms.IntegerField(max_value=120, min_value=5, label="Вік",
                             widget=forms.NumberInput(attrs={'class': 'form-control'}))
    profession = forms.CharField(max_length=70, label="Професія", required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    weight = forms.IntegerField(max_value=250, min_value=15, label="Вага", required=False,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
    body_height = forms.IntegerField(max_value=230, min_value=115, label="Зріст", required=False,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))
    post_index = forms.CharField(max_length=5, min_length=5, label="Поштовий індекс",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "03146"}))
    mob_telefon = forms.IntegerField(max_value=999999999999, label="Телефон", widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': " xxx xx xx xxx xx"}))
    email = forms.EmailField(label="Электронна пошта (Email)", required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "ви@example.com"}))
