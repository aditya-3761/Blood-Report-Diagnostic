# Blood Report Disease Detection System

A Flask-based web application that uses machine learning to detect blood diseases from blood test parameters.

## Features

- ✅ User Registration and Login (with MongoDB)
- ✅ Form validation on login and registration pages
- ✅ Blood test parameter input (WBC, RBC, HGB, PLT, NEUT, LYMPH, MONO, EO, BASO)
- ✅ Disease detection using Random Forest ML model
- ✅ Disease information and possible causes
- ✅ User test history with timestamps
- ✅ PDF export of test history
- ✅ Delete individual test records
- ✅ Secure password hashing

## Detected Diseases

The system can detect 14 different conditions:
- Anemia
- Polycythemia
- Leukocytosis
- Leukopenia
- Thrombocytopenia
- Thrombocytosis
- Neutropenia
- Neutrophilia
- Lymphocytopenia
- Lymphocytosis
- Monocytes High
- Eosinophil High
- Basophil High
- Normal

## Prerequisites

- Python 3.8 or higher
- MongoDB installed and running

## MongoDB Setup

### Option 1: Local MongoDB Installation

1. **Download and Install MongoDB:**
   - Visit: https://www.mongodb.com/try/download/community
   - Download MongoDB Community Server for your OS
   - Install MongoDB with default settings

2. **Start MongoDB Service:**
   
   **Windows:**
   ```bash
   # MongoDB should auto-start as a service
   # Or start it manually:
   net start MongoDB
   ```
   
   **Mac:**
   ```bash
   brew services start mongodb-community
   ```
   
   **Linux:**
   ```bash
   sudo systemctl start mongod
   sudo systemctl enable mongod
   ```

3. **Verify MongoDB is running:**
   ```bash
   mongosh
   # or
   mongo
   ```

### Option 2: MongoDB Atlas (Cloud)

1. Create a free account at https://www.mongodb.com/cloud/atlas
2. Create a new cluster
3. Get your connection string
4. Update `main.py` line 26 with your connection string:
   ```python
   MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/"
   ```

### MongoDB Compass (GUI Tool - Optional)

1. Download from: https://www.mongodb.com/try/download/compass
2. Connect to `mongodb://localhost:27017/`
3. You'll see the `blood_diagnostic_db` database after first user registration

## Installation

1. **Clone or download this project**

2. **Navigate to project directory:**
   ```bash
   cd blood_diagnostic_project
   ```

3. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Activate virtual environment:
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify MongoDB is running:**
   ```bash
   mongosh
   # or
   mongo
   ```

6. **Update MongoDB connection (if needed):**
   - Open `main.py`
   - Line 26: Update `MONGO_URI` if using MongoDB Atlas or different host

7. **Run the application:**
   ```bash
   python main.py
   ```

8. **Open your browser:**
   - Navigate to: `http://127.0.0.1:5000/`

## Usage Workflow

1. **Register a new account:**
   - Click "Register here" on login page
   - Fill in all details (username, email, password, age, gender)
   - Submit registration

2. **Login:**
   - Enter username and password
   - Form will validate before submission
   - Click "Login"

3. **Enter blood test parameters:**
   - Fill in all 9 blood parameter values
   - Click "Submit" to get disease prediction

4. **View result:**
   - See detected disease
   - Read possible causes and information
   - Result is automatically saved to history

5. **View history:**
   - Click "View History" to see all past tests
   - Each record shows all parameters and detected disease
   - Click "Download PDF" to export history
   - Click "Delete" to remove individual records

6. **Logout:**
   - Click "Logout" to end session

## File Structure

```
blood_diagnostic_project/
├── templates/
│   ├── login.html          # Login page with validation
│   ├── register.html       # Registration page
│   ├── afterlogin.html     # Blood parameter input form
│   ├── result.html         # Disease result display
│   └── history.html        # Test history page
├── Training.csv            # ML training dataset
├── main.py                 # Flask application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Database Structure

### MongoDB Collections:

**users collection:**
```json
{
  "_id": ObjectId,
  "username": "string",
  "email": "string",
  "password": "hashed_string",
  "age": int,
  "gender": "string",
  "created_at": datetime
}
```

**user_history collection:**
```json
{
  "_id": ObjectId,
  "user_id": "string",
  "username": "string",
  "WBC": float,
  "RBC": float,
  "HGB": float,
  "PLT": float,
  "NEUT": float,
  "LYMPH": float,
  "MONO": float,
  "EO": float,
  "BASO": float,
  "disease_code": int,
  "disease_name": "string",
  "created_at": "string"
}
```

## Security Notes

⚠️ **Important for Production:**
1. Change the `secret_key` in `main.py` (line 23)
2. Use environment variables for sensitive data
3. Enable HTTPS
4. Implement rate limiting
5. Add CSRF protection
6. Use strong MongoDB authentication

## Troubleshooting

**Issue: "Connection refused to MongoDB"**
- Solution: Make sure MongoDB service is running
- Check: `mongosh` or `mongo` command works

**Issue: "No module named 'pymongo'"**
- Solution: Install dependencies: `pip install -r requirements.txt`

**Issue: "Template not found"**
- Solution: Make sure all HTML files are in the `templates/` folder

**Issue: "Training.csv not found"**
- Solution: Ensure Training.csv is in the same directory as main.py

**Issue: PDF download not working**
- Solution: Check reportlab installation: `pip install reportlab==4.0.5`

## Credits

- ML Model: Random Forest Classifier (scikit-learn)
- Web Framework: Flask
- Database: MongoDB
- PDF Generation: ReportLab

## License

This project is for educational purposes.
