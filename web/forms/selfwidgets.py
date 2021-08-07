from django.forms import RadioSelect
class ColorRadioSelect(RadioSelect):
    template_name = 'color_templates/radio.html'
    option_template_name = 'color_templates/select_option.html'