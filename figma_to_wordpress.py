from flask import Flask, render_template, request
import os
import csv
import requests
import base64

app = Flask(__name__)

# WordPress Authentication Details
USERNAME = "" 
APP_PASSWORD = ""

# Base directory path where the layouts are stored
BASE_DIR = 'Themer Layout'  # Update this path to your local folder structure
# Paths to the directories
TEMPLATES_DIR = 'templates'
THEMER_LAYOUTS_DIR = 'Themer Layout'

@app.route('/')
def index():
    # Read the CSV file
    csv_file_path = os.path.join(TEMPLATES_DIR, 'data.csv')
    layout_data = []
    
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            layout_data.append(row)

    return render_template('ui.html', layout_data=layout_data)

@app.route('/import', methods=['POST'])
def import_xml():
    selected_xml_files = request.form.getlist('selected_xml_files')
    selected_css_files = request.form.getlist('selected_css_files')
    wordpress_url = request.form['wordpress_url']
    global USERNAME
    USERNAME = request.form['username']
    global APP_PASSWORD
    APP_PASSWORD = request.form['app_password']

    # Generate Basic Auth token
    TOKEN = base64.b64encode(f'{USERNAME}:{APP_PASSWORD}'.encode()).decode()

    # Headers for authentication with WordPress
    HEADERS = {
        'Authorization': f'Basic {TOKEN}'
    }
    
    if not selected_xml_files or not wordpress_url:
        return 'Error: No XML files selected or WordPress URL is missing.'
    
    results = []
    
    # Process selected XML files
    for xml_file in selected_xml_files:
        # Construct the full file path
        full_file_path = os.path.join(BASE_DIR, xml_file)
        
        # Ensure the file exists
        if os.path.exists(full_file_path):
            # Read the XML file content
            with open(full_file_path, 'rb') as f:
                xml_file_content = ('import.xml', f.read(), 'application/xml')
                
                # Post the XML file to the WordPress import API
                import_endpoint = f'{wordpress_url}/wp-json/wp/v2/media'
                response = requests.post(import_endpoint, files={'file': xml_file_content}, headers=HEADERS)

                if response.status_code == 201:
                    results.append(f'Successfully imported {xml_file} to {wordpress_url}')
                else:
                    results.append(f'Error importing {xml_file}: {response.content}')
        else:
            results.append(f'File not found: {xml_file}')

    # Process selected CSS files (just listing as an example, you can process them as needed)
    for css_file in selected_css_files:
        results.append(f'Selected CSS file: {css_file}')
    
    return '<br>'.join(results)

if __name__ == '__main__':
    app.run(debug=True)
