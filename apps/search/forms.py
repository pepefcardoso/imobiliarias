from django import forms


class SearchForm(forms.Form):
    city = forms.CharField(required=False, initial="Tubarão")
    neighborhood = forms.CharField(required=False)
    min_price = forms.FloatField(required=False, min_value=0)
    max_price = forms.FloatField(required=False, min_value=0, initial=320000)
    min_bedrooms = forms.IntegerField(required=False, min_value=0, initial=1)
    min_bathrooms = forms.IntegerField(required=False, min_value=0, initial=1)
    min_parking = forms.IntegerField(required=False, min_value=0, initial=1)
    min_area = forms.FloatField(required=False, min_value=0, initial=50)
    max_area = forms.FloatField(required=False, min_value=0)
    business_type = forms.CharField(required=False, initial="venda")