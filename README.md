# Feedback Portal Server (Flask)

This is a Flask implementation of the Feedback Portal Server, providing the same API functionality as the original Django version.

## Setup Instructions

### 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=your_secret_key
MONGODB_URI=your_mongodb_uri

# Email settings
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password

# Frontend URL
FRONT_END_LINK=http://localhost:3000
DJ_LOGO=https://example.com/logo.png
```

### 4. Run the Application

```bash
python run.py
```

The server will start at `http://localhost:5000`.

## API Endpoints

The API endpoints match the original Django implementation:

### Authentication
- `POST /api/login` - User login
- `POST /api/sendOtp` - Send OTP for verification
- `POST /api/verifyOtp` - Verify OTP
- `POST /api/resetPasswordMail` - Send reset password email
- `POST /api/getPass` - Verify reset password token
- `POST /api/resetPassword` - Reset password
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/createTeacher` - Create a teacher account
- `GET /api/getAllTeacherMails` - Get all teacher emails

### Feedback Forms
- `POST /api/createFeedbackForm` - Create a feedback form
- `POST /api/updateFeedbackform` - Update a feedback form
- `POST /api/deleteFeedbackform` - Delete a feedback form
- `GET /api/getFeedbackForm` - Get feedback forms
- `GET /api/getFeedbackData` - Get feedback data
- `POST /api/saveFeedbackFormResult` - Save feedback form result
- `POST /api/sendReminder` - Send reminder to students
- `GET /api/getSDashData` - Get student dashboard data
- `GET /api/getSDashDataFilled` - Get filled feedback data
- `GET /api/getSDashDataForm` - Get specific form data

### Subjects
- `GET /api/getallsubjects` - Get all subjects
- `DELETE /api/deletesubject/<subject_id>/` - Delete a subject
- `POST /api/addTheorySubject` - Add a theory subject
- `POST /api/addPractical` - Add a practical subject

### Batches
- `GET /api/getBatches` - Get all batches
- `GET /api/getYrBatches` - Get batches for a specific year
- `GET /api/getYearBatches` - Get all years and their batches
- `POST /api/bac` - Create a batch
- `POST /api/bacUpdate` - Update a batch
- `POST /api/delBatch` - Delete a batch

### Users
- `GET /api/getProfile` - Get user profile
- `POST /api/saveProfile` - Update user profile
- `GET /api/getTUsers/<username>` - Get teacher details
- `GET /api/getuserslist` - Get all users
- `POST /api/tSettings` - Update teacher permissions

### Instances
- `POST /api/createNewInst` - Create a new feedback instance
- `POST /api/generateSecretCode` - Generate a secret code for teacher registration 