from django.shortcuts import render , redirect
from django.contrib import messages
from Users.models import UserRegisterModel
from django.conf import settings
from Users.forms import UserRegisterForm
import re
import sys
import time
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn import preprocessing
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
import os
from sklearn.model_selection import train_test_split

def base(request):
    return render(request , 'base.html')

def UserRegister(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST , request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request , 'Registered successfully')
            return redirect('Userlogin')
        else:
            messages.warning(request , 'Invalid credentials')
    else:
        form = UserRegisterForm()
    return render(request , 'Userregister.html' , {'form':form})


def Userlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            if username and password:
                user = UserRegisterModel.objects.get(Username=username , Password=password)
                if user.status == 'Activate':
                    request.session['user_id'] = user.id
                    request.session['username'] =username
                    request.session['Email'] =user.Email
                    request.session['Phone_No'] =user.Phone_No
                    return redirect('UserHome')
                else:
                    messages.warning(request , 'User is deactivated')
                    return redirect('Userlogin')
            else:
                messages.warning(request , 'Invalid credentials')
                return redirect('Userlogin')

        except Exception as e:
            messages.warning(request , f'{e}')

            
    return render(request , 'Userlogin.html')


def UserHome(request):
    user = request.session.get('username')
    email = request.session.get('Email')
    phone = request.session.get('Phone_No')
    return render(request , 'users/UserHome.html' , {'user':user , 'email':email , 'phone':phone})


import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from django.conf import settings
from django.shortcuts import render

def training(request):
    user = request.session.get('username')
    data = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'googleplaystore.csv'))
    
    # Handle missing values (if any)
    data['Reviews'] = pd.to_numeric(data['Reviews'], errors='coerce').fillna(0).astype(int)
    
    # Handle 'Installs' column - remove commas, plus signs, and convert to numeric
    data['Installs'] = data['Installs'].str.replace(',', '').str.replace('+', '')
    data['Installs'] = pd.to_numeric(data['Installs'], errors='coerce').fillna(0).astype(int)  # Replace non-numeric values with 0

    # Drop rows where Rating is missing
    data.dropna(subset=['Rating'], inplace=True)

    # Encoding categorical columns
    le_dict = {}  # Dictionary to store encoders
    for column in ['App', 'Category', 'Genres']:
        le = LabelEncoder()
        data[column] = le.fit_transform(data[column])
        le_dict[column] = le  # Save encoder

    # Select features and target (no 'Price' column now)
    feature = ['App', 'Category', 'Reviews', 'Installs', 'Genres']
    x = data[feature]
    y = data['Rating']  # Rating is the target variable

    # Scale the features (optional, especially useful for other algorithms)
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)

    # Train the Decision Tree Regressor
    model_dt = DecisionTreeRegressor(random_state=42)
    x_train, x_test, y_train, y_test = train_test_split(x_scaled, y, test_size=0.2, random_state=42)
    model_dt.fit(x_train, y_train)
    
    # Train the Support Vector Regressor (SVR)
    model_svr = SVR(kernel='rbf')
    model_svr.fit(x_train, y_train)

    # Predicting on test data
    y_pred_dt = model_dt.predict(x_test)
    y_pred_svr = model_svr.predict(x_test)

    # Evaluate the models
    mae_dt = mean_absolute_error(y_test, y_pred_dt)
    mse_dt = mean_squared_error(y_test, y_pred_dt)
    r2_dt = r2_score(y_test, y_pred_dt)

    mae_svr = mean_absolute_error(y_test, y_pred_svr)
    mse_svr = mean_squared_error(y_test, y_pred_svr)
    r2_svr = r2_score(y_test, y_pred_svr)

    # Save the trained models, encoders, and scaler
    model_dt_path = os.path.join(settings.MEDIA_ROOT, 'trained_model_dt.pkl')
    model_svr_path = os.path.join(settings.MEDIA_ROOT, 'trained_model_svr.pkl')
    encoder_path = os.path.join(settings.MEDIA_ROOT, 'label_encoders.pkl')
    scaler_path = os.path.join(settings.MEDIA_ROOT, 'scaler.pkl')

    joblib.dump(model_dt, model_dt_path)
    joblib.dump(model_svr, model_svr_path)
    joblib.dump(le_dict, encoder_path)
    joblib.dump(scaler, scaler_path)

    # Return results to the template
    return render(request, 'users/training.html', {
        'r2_dt': r2_dt, 'mse_dt': mse_dt, 'mae_dt': mae_dt,
        'r2_svr': r2_svr, 'mse_svr': mse_svr, 'mae_svr': mae_svr,
        "user": user
    })


def DatasetView(request):
    user = request.session.get('username')
    data = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'googleplaystore.csv'))
    data = data.head(100)
    return render(request, 'users/datasetview.html', {
        'data': data.to_html(index=False, classes='w3-table-all', border=0),
        'user': user
    })

#=======================================PREDICATION=======================================
from sklearn.preprocessing import LabelEncoder

# Encode user input for prediction (for each field, handle unseen labels)
def encode_input_column(le, value):
    try:
        # Attempt to transform the input using the LabelEncoder
        return le.transform([value])[0]
    except ValueError:
        # If ValueError occurs, return a default value (0 or any other fallback value)
        return 0

def predication(request):
    predicted_rating = None  # Default value

    if request.method == "POST":
        app = request.POST.get('app')
        category = request.POST.get('category')
        reviews = request.POST.get('reviews')
        installs = request.POST.get('installs')
        genres = request.POST.get('genres')

        # Load and prepare data
        data = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'googleplaystore.csv'))
        data['Reviews'] = pd.to_numeric(data['Reviews'], errors='coerce').fillna(0).astype(int)
        data['Installs'] = data['Installs'].str.replace(',', '').str.replace('+', '')
        data['Installs'] = pd.to_numeric(data['Installs'], errors='coerce').fillna(0).astype(int)
        data.dropna(subset=['Rating'], inplace=True)

        # Encode categorical features
        le_dict = {}
        for column in ['App', 'Category', 'Genres']:
            le = LabelEncoder()
            data[column] = le.fit_transform(data[column])
            le_dict[column] = le

        # Prepare features and target
        feature = ['App', 'Category', 'Reviews', 'Installs', 'Genres']
        x = data[feature]
        y = data['Rating']  # Rating is the target variable

        # Scale the features
        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x)

        # Train models (Decision Tree and SVR)
        model_dt = DecisionTreeRegressor(random_state=42)
        model_svr = SVR(kernel='rbf')

        model_dt.fit(x_scaled, y)
        model_svr.fit(x_scaled, y)

        # Encode user input for prediction with error handling for unseen labels
        encoded_app = encode_input_column(le_dict['App'], app)
        encoded_category = encode_input_column(le_dict['Category'], category)
        encoded_genres = encode_input_column(le_dict['Genres'], genres)

        try:
            encoded_reviews = int(reviews)
            encoded_installs = int(installs)
        except ValueError:
            return render(request, 'users/predication.html', {'error': "Invalid input for Reviews or Installs. Please enter valid numbers."})

        # Prepare input for prediction
        user_input = [[encoded_app, encoded_category, encoded_reviews, encoded_installs, encoded_genres]]

        # Scale the input
        user_input_scaled = scaler.transform(user_input)
        print(user_input_scaled)
        # Predict ratings using both models
        predicted_rating_dt = model_dt.predict(user_input_scaled)[0]
        predicted_rating_svr = model_svr.predict(user_input_scaled)[0]

        # Average the predictions from both models
        predicted_rating = (predicted_rating_dt + predicted_rating_svr) / 2

        # Round the predicted rating to 1 decimal place
        predicted_rating = round(predicted_rating, 1)

        return render(request, 'users/predication.html', {'predicted_rating': predicted_rating})
    
    return render(request, 'users/predication.html')
