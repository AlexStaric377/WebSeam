from django import forms


# --- Фориа Профіль пацієнта
class PacientForm(forms.Form):
    Typegender = [("чол.", "чол."), ("жін.", "жін.")]

    name = forms.CharField(max_length=37, min_length=3, label="Ім'я",
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    surname = forms.CharField(max_length=37, min_length=3, label="Прізвище",
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    gender = forms.ChoiceField(choices=Typegender, label="Стать", widget=forms.Select(attrs={'class': 'form-control'}))
    age = forms.IntegerField(max_value=120, min_value=5, label="Вік",
                             widget=forms.NumberInput(attrs={'class': 'form-control'}))
    profession = forms.CharField(max_length=70, label="Професія", required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    weight = forms.IntegerField(max_value=250, min_value=15, label="Вага", required=False,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
    growth = forms.IntegerField(max_value=230, min_value=115, label="Зріст", required=False,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))
    pind = forms.CharField(max_length=5, min_length=5, label="Поштовий індекс",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "03146"}))
    tel = forms.CharField(label="Телефон", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': " xxx xx xx xxx xx"}))
    email = forms.EmailField(label="Электронна пошта (Email)", required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "ви@example.com"}))


#--- Форма реєестрації входу до кабінету пацієнта
class AccountUserForm(forms.Form):
    login = forms.CharField(max_length=13, label='Телефон:',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': " xxx xx xx xxx xx"}))
    password = forms.CharField(max_length=13, label='Пароль:',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))


#--- Форма реєестрації нового облікового запису для пацієнтів
class ReestrAccountUserForm(forms.Form):
    login = forms.CharField(max_length=13, label='Телефон:',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': " xxx xx xx xxx xx"}))
    password = forms.CharField(max_length=13, label='Пароль:',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    dwpassword = forms.CharField(max_length=13, label='Повторити пароль:',
                                 widget=forms.PasswordInput(attrs={'class': 'form-control'}))


# --- Форма профіль лікаря
class LikarForm(forms.Form):
    kodDoctor = forms.CharField()
    name = forms.CharField(max_length=37, min_length=3, label="Ім'я",
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    surname = forms.CharField(max_length=37, min_length=3, label="Прізвище",
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefon = forms.CharField(max_length=13, min_length=10, label="Телефон", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': " xxx xx xx xxx xx"}))
    email = forms.EmailField(label="Электронна пошта (Email)", required=False,
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control', 'placeholder': "mymail@example.com"}))
    edrpou = forms.CharField(max_length=8, label="ЕДРПОУ", required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    specialnoct = forms.CharField(max_length=70, label="Спеціальність", required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    napryamok = forms.CharField(max_length=70, label="Напрямок", required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    uriwebDoctor = forms.CharField(max_length=70, label="Вебсторінка", required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
