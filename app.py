import requests, os, uuid, json
from dotenv import load_dotenv
#from flask_bcrypt import Bcrypt
from flask import Flask, redirect, url_for, request, flash ,render_template, session
import mysql.connector
import bcrypt



app = Flask(__name__, static_url_path='/static')
#bcrypt = Bcrypt(app)

# Use environment variable for Flask secret key
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'random')


# Configure MySQL connection

mydb = mysql.connector.connect(
       host="dbflask.mysql.database.azure.com",
       user="translatordb",
       password="admin@123",
       database="text_translate"
)


 # Load the values from .env    
key = "def0a9a087384e26be475a0294b7b09e"
endpoint = "https://api.cognitive.microsofttranslator.com/"
location = "westus2"

# Set up the header information, which includes our subscription key
headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }


    



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def index_post():
  
    # Read the values from the form
    original_text = request.form['text']
    target_language = request.form['language']

    
    # Indicate that we want to translate and the API version (3.0) and the target language
    path = '/translate?api-version=3.0'
    # Add the target language parameter
    target_language_parameter = '&to=' + target_language
    # Create the full URL
    constructed_url = endpoint + path + target_language_parameter


    # Create the body of the request with the text to be translated
    body = [{ 'text': original_text }]

    # Make the call using post
    translator_request = requests.post(constructed_url, headers=headers, json=body)
    # Retrieve the JSON response
    translator_response = translator_request.json()
    # Retrieve the translation
    translated_text = translator_response[0]['translations'][0]['text']
    
    # Fetch all translations from the database
    
    cur = mydb.cursor()
    insert_query = "INSERT INTO translation (original_text,translated_text,target_language) VALUES (%s,%s,%s)"
    data_to_insert = (original_text,translated_text,target_language)
    cur.execute(insert_query, data_to_insert)
    print('inserted successfully')
    mydb.commit()
    cur.close()

    # Fetch all translations from the database
    cur = mydb.cursor()
    cur.execute("SELECT * FROM translation")
    all_translations = cur.fetchall()
    print('all outputs')
    mydb.commit()
    cur.close()

    # Call render template, passing the translated text,
    # original text, and target language to the template
    return render_template(
        'results.html',
        original_text=original_text,
        translated_text=translated_text,
        target_language=target_language,
        all_translations=all_translations
    )



if __name__ == '__main__':
    app.run(debug=True)

    


    


    

    

    


    
