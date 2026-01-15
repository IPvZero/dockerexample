from flask import Flask, request, jsonify, render_template_string
import redis
import os

app = Flask(__name__)

# Connect to Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Flask Redis App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .container {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        input, button {
            padding: 10px;
            margin: 5px;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
        button {
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 10px;
            background-color: #e8f5e9;
            border-radius: 4px;
        }
        h2 {
            color: #333;
        }
    </style>
</head>
<body>
    <h1>Flask Redis Data Manager</h1>
    
    <div class="container">
        <h2>Store Data</h2>
        <input type="text" id="storeKey" placeholder="Key">
        <input type="text" id="storeValue" placeholder="Value">
        <button onclick="storeData()">Store</button>
        <div id="storeResult" class="result" style="display:none;"></div>
    </div>
    
    <div class="container">
        <h2>Retrieve Data</h2>
        <input type="text" id="getKey" placeholder="Key">
        <button onclick="getData()">Get</button>
        <div id="getResult" class="result" style="display:none;"></div>
    </div>
    
    <div class="container">
        <h2>Get All Keys</h2>
        <button onclick="getAllKeys()">List All Keys</button>
        <div id="keysResult" class="result" style="display:none;"></div>
    </div>
    
    <div class="container">
        <h2>Delete Data</h2>
        <input type="text" id="deleteKey" placeholder="Key">
        <button onclick="deleteData()">Delete</button>
        <div id="deleteResult" class="result" style="display:none;"></div>
    </div>

    <script>
        async function storeData() {
            const key = document.getElementById('storeKey').value;
            const value = document.getElementById('storeValue').value;
            const resultDiv = document.getElementById('storeResult');
            
            const response = await fetch('/api/store', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key, value})
            });
            
            const data = await response.json();
            resultDiv.style.display = 'block';
            resultDiv.textContent = data.message || data.error;
        }
        
        async function getData() {
            const key = document.getElementById('getKey').value;
            const resultDiv = document.getElementById('getResult');
            
            const response = await fetch(`/api/get/${key}`);
            const data = await response.json();
            
            resultDiv.style.display = 'block';
            if (data.value) {
                resultDiv.textContent = `Value: ${data.value}`;
            } else {
                resultDiv.textContent = data.error || 'Key not found';
            }
        }
        
        async function getAllKeys() {
            const resultDiv = document.getElementById('keysResult');
            
            const response = await fetch('/api/keys');
            const data = await response.json();
            
            resultDiv.style.display = 'block';
            if (data.keys && data.keys.length > 0) {
                resultDiv.innerHTML = '<strong>Keys:</strong><br>' + data.keys.join('<br>');
            } else {
                resultDiv.textContent = 'No keys found';
            }
        }
        
        async function deleteData() {
            const key = document.getElementById('deleteKey').value;
            const resultDiv = document.getElementById('deleteResult');
            
            const response = await fetch(`/api/delete/${key}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            resultDiv.style.display = 'block';
            resultDiv.textContent = data.message || data.error;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/store', methods=['POST'])
def store_data():
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        
        if not key or not value:
            return jsonify({'error': 'Key and value are required'}), 400
        
        redis_db.set(key, value)
        return jsonify({'message': f'Data stored successfully: {key} = {value}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get/<key>', methods=['GET'])
def get_data(key):
    try:
        value = redis_db.get(key)
        if value is None:
            return jsonify({'error': 'Key not found'}), 404
        return jsonify({'key': key, 'value': value}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keys', methods=['GET'])
def get_all_keys():
    try:
        keys = redis_db.keys('*')
        return jsonify({'keys': keys}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete/<key>', methods=['DELETE'])
def delete_data(key):
    try:
        result = redis_db.delete(key)
        if result == 0:
            return jsonify({'error': 'Key not found'}), 404
        return jsonify({'message': f'Key {key} deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
