from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__)

# Load the saved model and scaler
beta = joblib.load('beta_coefficients.pkl')
main_scaler = joblib.load('main_scaler.pkl')

# Define the columns used during training
training_columns = ['bathrooms', 'square_feet', 'latitude', 'longitude', 'time',
       'has_photo_Thumbnail', 'has_photo_Yes', 'state_AR', 'state_AZ',
       'state_CA', 'state_CO', 'state_CT', 'state_DC', 'state_DE', 'state_FL',
       'state_GA', 'state_IA', 'state_ID', 'state_IL', 'state_IN', 'state_KS',
       'state_KY', 'state_LA', 'state_MA', 'state_MD', 'state_ME', 'state_MI',
       'state_MN', 'state_MO', 'state_MS', 'state_MT', 'state_NC', 'state_ND',
       'state_NE', 'state_NH', 'state_NJ', 'state_NM', 'state_NV', 'state_NY',
       'state_OH', 'state_OK', 'state_OR', 'state_PA', 'state_RI', 'state_SC',
       'state_SD', 'state_TN', 'state_TX', 'state_UT', 'state_VA', 'state_VT',
       'state_WA', 'state_WI', 'state_WV', 'state_WY', 'source_Home Rentals',
       'source_Listanza', 'source_ListedBuy', 'source_RENTCafé',
       'source_RENTOCULAR', 'source_Real Estate Agent', 'source_RealRentals',
       'source_RentDigs.com', 'source_RentLingo', 'source_rentbits',
       'source_tenantcloud']

# Route to render the input form and handle form submissions
@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        # Collect form data submitted by the user
        input_data = {
            'bathrooms': int(request.form.get('bathrooms')),
            'has_photo_Yes': int(request.form.get('has_photo')),
            'square_feet': int(request.form.get('square_feet')),
            'latitude': float(request.form.get('latitude')),
            'longitude': float(request.form.get('longitude')),
            'time': 1577015600
        }

        input_df = pd.DataFrame([input_data])
        
        colsToDrop = ['id','body', 'bedrooms','title', 'category', 'currency', 'fee', 'price_type', 'price_display', 'cityname', 'priceBin']
        input_df = input_df.drop(columns=colsToDrop, errors='ignore')
        
        for column in input_df.columns:
            if input_df[column].isnull().any():
                if input_df[column].dtype in ['int64', 'float64']:
                    input_df[column].fillna(0, inplace=True)
                else:
                    input_df[column].fillna('Unknown', inplace=True)
        
        input_df = pd.get_dummies(input_df, columns=['has_photo_Yes'], drop_first=True)
        
        input_df = input_df.reindex(columns=training_columns, fill_value=0)
        
        input_X = np.hstack([np.ones((input_df.shape[0], 1)), input_df.values])
        
        input_X_scaled_features = main_scaler.transform(input_X[:, 1:])
        input_X_scaled = np.hstack([np.ones((input_X_scaled_features.shape[0], 1)), input_X_scaled_features])
        
        predicted_price = input_X_scaled.dot(beta)
        
        return render_template('results.html', predicted_price=round(predicted_price[0],2))

    return render_template('form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
