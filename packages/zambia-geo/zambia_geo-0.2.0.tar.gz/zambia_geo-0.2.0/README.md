# Zambia Geo

A Python package containing Zambian provinces and cities data.

## Features

* List all Zambian provinces
* Get cities for each province
* Search for cities
* Validate province and city names

## New in v0.2.0: Constituencies
You can now fetch constituencies for each province or district:

```python
    from zambia_geo import get_constituencies
```

# Get constituencies for a specific province
constituencies = get_constituencies("Southern")
for c in constituencies:
    print(c.name)

## Install in Development Mode Locally

1. Create a virtual environment:
   
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install the package in development mode:
   
        git clone https://github.com/sangwani-coder/zambia_geo.git
        cd zambia_geo
        pip install -e .

4. Run Tests

        python3 -m pytest tests/
## Alternative Installation Methods
### Installation in a Project - Force Install

    pip install --force-reinstall git+https://github.com/sangwani-coder/zambia_geo.git

### Download the ZIP and install
    wget https://github.com/sangwani-coder/zambia_geo/archive/main.zip
    pip install main.zip

### Now you can import and use the package in your Python code:

    from zambia_geo import get_all_provinces, get_province_cities
    # Get all provinces
    provinces = get_all_provinces()
    for province in provinces:
        print(province.name, province.capital)

    # Get cities in a province
    cities = get_province_cities("Lusaka")
    for city in cities:
        print(city.name, city.population)

## Usage in Django

To use zambia_geo package in Django model choice fields, you'll need to create choices tuples from the package's data. Here's how you can implement this:

### Example Django Model Usage

    from django.db import models
    from zambia_geo.utils import get_province_choices, get_city_choices

    class UserProfile(models.Model):
        # Province field
        province = models.CharField(
            max_length=50,
            choices=get_province_choices(),
            blank=True,
            null=True
        )
        
        # City field that depends on province
        city = models.CharField(
            max_length=50,
            choices=[],
            blank=True,
            null=True
        )
        
        class Meta:
            verbose_name = "User Profile"
            verbose_name_plural = "User Profiles"
        
        def __str__(self):
            return f"{self.province} - {self.city}"

## Dynamic City Choices Based on Province (Forms)

To make the city choices dynamic based on the selected province, you'll need to use JavaScript or Django's form facilities:

**Step 1: Using Django Forms with JavaScript:**

    # forms.py
    from django import forms
    from .models import UserProfile
    from zambia_geo.utils import get_province_choices, get_city_choices
    
    class UserProfileForm(forms.ModelForm):
        class Meta:
            model = UserProfile
            fields = ['province', 'city']
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['province'].choices = [('', 'Select Province')] + get_province_choices()
            self.fields['city'].choices = [('', 'Select City')]
            
            # Set initial city choices if province is already selected
            if self.instance and self.instance.province:
                self.fields['city'].choices = [('', 'Select City')] + get_city_choices(self.instance.province)

**Step 2: Create a View to handle Ajax Request**

    # views.py
    from django.http import JsonResponse
    from zambia_geo.utils import get_city_choices
    
    def load_cities(request):
        province = request.GET.get('province')
        if province:
            cities = get_city_choices(province)
            return JsonResponse({'cities': cities})
        return JsonResponse({'cities': []})

### Add URL Patten

    # urls.py
    from django.urls import path
    from .views import load_cities
    
    urlpatterns = [
        path('load-cities/', load_cities, name='load_cities'),
        # other paths...
    ]

### In your template

    # admin.py
    <!-- Include jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
    <form method="post" id="profileForm">
        {% csrf_token %}
        
        <div class="form-group">
            {{ form.province.label_tag }}
            {{ form.province }}
        </div>
        
        <div class="form-group">
            {{ form.city.label_tag }}
            {{ form.city }}
        </div>
        
        <button type="submit" class="btn btn-primary">Save</button>
    </form>
    
    <script>
    $(document).ready(function() {
        // When province changes
        $('#id_province').change(function() {
            var provinceId = $(this).val();
            var url = "{% url 'load_cities' %}";
            
            // Clear and disable city dropdown
            $('#id_city').html('<option value="">Select City</option>');
            
            if (provinceId) {
                // Fetch cities for selected province
                $.ajax({
                    url: url,
                    data: {
                        'province': provinceId
                    },
                    success: function(data) {
                        // Populate city dropdown
                        var options = '<option value="">Select City</option>';
                        $.each(data.cities, function(index, city) {
                            options += '<option value="' + city[0] + '">' + city[1] + '</option>';
                        });
                        $('#id_city').html(options);
                    }
                });
            }
        });
    });
    </script>

### Update your view to Handle your Form

    # views.py
    from django.shortcuts import render, redirect
    from .forms import UserProfileForm
    
    def profile_view(request):
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=request.user.profile)
            if form.is_valid():
                form.save()
                return redirect('success_url')
        else:
            form = UserProfileForm(instance=request.user.profile)
        
        return render(request, 'profile_form.html', {'form': form})

## Usage in Flask

      flask_zambia_app/
      ├── app.py
      ├── templates/
      │   └── index.html
      └── requirements.txt


### Flask Application Code:

      # app.py
      from flask import Flask, render_template, request, jsonify
      from zambia_geo.utils import get_province_choices, get_city_choices
      
      app = Flask(__name__)
      
      @app.route('/', methods=['GET', 'POST'])
      def index():
          if request.method == 'POST':
              # Process form submission
              province = request.form.get('province')
              city = request.form.get('city')
              return f"Selected: {province} Province, {city} City"
          
          # GET request - show the form
          provinces = get_province_choices()
          return render_template('index.html', provinces=provinces)
      
      @app.route('/get_cities')
      def get_cities():
          province = request.args.get('province')
          if province:
              cities = get_city_choices(province)
              return jsonify({'cities': cities})
          return jsonify({'cities': []})
      
      if __name__ == '__main__':
          app.run(debug=True)

### Template File:

      <!-- index.html -->
      <!DOCTYPE html>
      <html>
      <head>
          <title>Zambia Provinces and Cities</title>
          <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
          <style>
              .form-group { margin-bottom: 15px; }
              select { padding: 8px; width: 300px; }
          </style>
      </head>
      <body>
          <h1>Select Location in Zambia</h1>
          
          <form method="POST">
              <div class="form-group">
                  <label for="province">Province:</label>
                  <select id="province" name="province" required>
                      <option value="">Select Province</option>
                      {% for code, name in provinces %}
                          <option value="{{ code }}">{{ name }}</option>
                      {% endfor %}
                  </select>
              </div>
              
              <div class="form-group">
                  <label for="city">City:</label>
                  <select id="city" name="city" required disabled>
                      <option value="">Select City (choose province first)</option>
                  </select>
              </div>
              
              <button type="submit">Submit</button>
          </form>
      
          <script>
          $(document).ready(function() {
              $('#province').change(function() {
                  var province = $(this).val();
                  var $citySelect = $('#city');
                  
                  $citySelect.empty().prop('disabled', true);
                  
                  if (province) {
                      $citySelect.append('<option value="">Loading cities...</option>');
                      
                      $.getJSON('/get_cities', {province: province}, function(data) {
                          $citySelect.empty().append('<option value="">Select City</option>');
                          
                          $.each(data.cities, function(index, city) {
                              $citySelect.append(
                                  $('<option>', {
                                      value: city[0],
                                      text: city[1]
                                  })
                              );
                          });
                          
                          $citySelect.prop('disabled', false);
                      });
                  }
              });
          });
          </script>
      </body>
      </html>
