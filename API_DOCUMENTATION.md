# Feedback Portal API Documentation

## Overview

The Feedback Portal API is a Flask-based RESTful service that manages student feedback forms, user authentication, and administrative operations for educational institutions. The API provides comprehensive endpoints for authentication, feedback management, subject administration, batch handling, and user management.

**Base URL:** `http://localhost:5000/api`

**Authentication:** JWT (JSON Web Tokens) with access and refresh token support

---

## Authentication Endpoints

### 1. User Login
**Endpoint:** `POST /api/login`

**Description:** Authenticates a user with email and password credentials.

**Parameters:**
```json
{
  "email": "string (required) - User's email address",
  "password": "string (required) - User's password"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Login Successful",
  "tokens": {
    "access": "string - JWT access token",
    "refresh": "string - JWT refresh token"
  },
  "is_teacher": "boolean - Whether user is a teacher/staff",
  "is_superuser": "boolean - Whether user has admin privileges",
  "name": "string - User's full name",
  "email": "string - User's email",
  "canCreateBatch": "boolean - Permission to create batches (teachers only)",
  "canCreateSubject": "boolean - Permission to create subjects (teachers only)",
  "canCreateFeedbackForm": "boolean - Permission to create feedback forms (teachers only)"
}
```

### 2. Send OTP
**Endpoint:** `POST /api/sendOtp`

**Description:** Sends a one-time password (OTP) to the user's email for verification.

**Parameters:**
```json
{
  "email": "string (required) - User's email address"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "OTP sent successfully"
}
```

### 3. Verify OTP
**Endpoint:** `POST /api/verifyOtp`

**Description:** Verifies the OTP entered by the user and completes authentication.

**Parameters:**
```json
{
  "email": "string (required) - User's email address",
  "otp": "string (required) - 6-digit OTP received via email"
}
```

**Response:** Same as login endpoint upon successful verification.

### 4. Send Reset Password Email
**Endpoint:** `POST /api/resetPasswordMail`

**Description:** Sends a password reset email with a verification token.

**Parameters:**
```json
{
  "email": "string (required) - User's email address"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Reset password mail sent successfully"
}
```

### 5. Verify Password Reset Token
**Endpoint:** `POST /api/getPass`

**Description:** Verifies the password reset token received via email.

**Parameters:**
```json
{
  "email": "string (required) - User's email address",
  "pass": "string (required) - Password reset token"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Token verified successfully"
}
```

### 6. Reset Password
**Endpoint:** `POST /api/resetPassword`

**Description:** Resets the user's password using the verified token.

**Parameters:**
```json
{
  "email": "string (required) - User's email address",
  "pass": "string (required) - Password reset token",
  "new_pass": "string (required) - New password"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Password reset successfully"
}
```

### 7. Refresh Access Token
**Endpoint:** `POST /api/token/refresh`

**Description:** Refreshes the access token using a valid refresh token.

**Headers:** `Authorization: Bearer <refresh_token>`

**Response:**
```json
{
  "access": "string - New JWT access token"
}
```

### 8. Create Teacher Account
**Endpoint:** `POST /api/createTeacher`

**Description:** Creates a new teacher account using a secret code.

**Parameters:**
```json
{
  "secret_code": "string (required) - Admin-generated secret code",
  "email": "string (required) - Teacher's email address",
  "password": "string (required) - Teacher's password",
  "name": "string (required) - Teacher's full name"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Teacher account created successfully"
}
```

### 9. Get All Teacher Emails
**Endpoint:** `GET /api/getAllTeacherMails`

**Description:** Retrieves a list of all teacher email addresses.

**Authentication:** Required (Basic Auth)

**Response:**
```json
{
  "status_code": 200,
  "data": ["email1@example.com", "email2@example.com"]
}
```

---

## Feedback Management Endpoints

### 10. Create Feedback Form
**Endpoint:** `POST /api/createFeedbackForm`

**Description:** Creates a new feedback form for students to fill.

**Authentication:** Required (Teacher Auth)

**Parameters:**
```json
{
  "form_field": "object (required) - JSON object containing form questions and structure",
  "subject_id": "integer (required) - ID of the subject",
  "instance_id": "integer (optional) - ID of the feedback instance",
  "due_date": "string (required) - ISO format date when form expires",
  "year": "integer (required) - Academic year",
  "batch_list": "array (optional) - Array of batch IDs to assign form to",
  "is_theory": "boolean (optional) - Whether this is for theory or practical subject"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Feedback form created successfully",
  "form_id": "integer - ID of the created form"
}
```

### 11. Update Feedback Form
**Endpoint:** `POST /api/updateFeedbackform`

**Description:** Updates an existing feedback form.

**Authentication:** Required (Teacher Auth)

**Parameters:**
```json
{
  "form_id": "integer (required) - ID of the form to update",
  "form_field": "object (optional) - Updated form structure",
  "subject_id": "integer (optional) - Updated subject ID",
  "due_date": "string (optional) - Updated due date",
  "batch_list": "array (optional) - Updated batch assignments",
  "is_alive": "boolean (optional) - Whether form is active"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Feedback form updated successfully"
}
```

### 12. Delete Feedback Form
**Endpoint:** `POST /api/deleteFeedbackform`

**Description:** Deletes a feedback form and all associated data.

**Authentication:** Required (Teacher Auth)

**Parameters:**
```json
{
  "form_id": "integer (required) - ID of the form to delete"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Feedback form deleted successfully"
}
```

### 13. Get Feedback Forms
**Endpoint:** `GET /api/getFeedbackForm`

**Description:** Retrieves all feedback forms with optional instance filtering.

**Authentication:** Required (Basic Auth)

**Query Parameters:**
- `instance_id` (optional) - Filter forms by instance ID

**Response:**
```json
{
  "status_code": 200,
  "data": [
    {
      "id": "integer - Form ID",
      "subject_name": "string - Subject name",
      "is_alive": "boolean - Whether form is active",
      "is_theory": "boolean - Theory or practical subject",
      "year": "integer - Academic year",
      "due_date": "string - ISO format due date",
      "batch_list": "array - Assigned batch IDs",
      "is_selected": "boolean - Whether instance is selected"
    }
  ]
}
```

### 14. Get Feedback Data
**Endpoint:** `GET /api/getFeedbackData`

**Description:** Retrieves detailed feedback data for a specific form including student responses.

**Authentication:** Required (Basic Auth)

**Query Parameters:**
- `form_id` (required) - ID of the feedback form

**Response:**
```json
{
  "status_code": 200,
  "data": [
    {
      "student": "string - Student username",
      "student_name": "string - Student full name",
      "is_filled": "boolean - Whether student completed form",
      "user_feedback": "object - Student's feedback responses",
      "teacher_name": "string - Teacher's name",
      "teacher_email": "string - Teacher's email",
      "subject": "string - Subject name",
      "due_date": "string - Form due date",
      "year": "integer - Academic year",
      "is_theory": "boolean - Theory or practical",
      "form_id": "integer - Form ID",
      "subject_id": "integer - Subject ID"
    }
  ]
}
```

### 15. Save Feedback Form Result
**Endpoint:** `POST /api/saveFeedbackFormResult`

**Description:** Saves a student's feedback form submission.

**Authentication:** Required (Basic Auth)

**Parameters:**
```json
{
  "data": {
    "form_id": "integer (required) - ID of the feedback form",
    "form_data": "object (required) - Student's feedback responses"
  }
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Feedback submitted successfully"
}
```

### 16. Send Reminder
**Endpoint:** `POST /api/sendReminder`

**Description:** Sends reminder emails to students who haven't completed the feedback form.

**Authentication:** Required (Teacher Auth)

**Parameters:**
```json
{
  "data": {
    "form_id": "integer (required) - ID of the feedback form"
  }
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Reminder emails sent successfully"
}
```

### 17. Get Student Dashboard Data
**Endpoint:** `GET /api/getSDashData`

**Description:** Retrieves pending feedback forms for the current student.

**Authentication:** Required (Basic Auth)

**Response:**
```json
{
  "status_code": 200,
  "data": [
    {
      "subject": "string - Subject name",
      "is_filled": "boolean - Completion status",
      "teacher_name": "string - Teacher's name",
      "due_date": "string - Form due date",
      "year": "integer - Academic year",
      "is_theory": "boolean - Theory or practical",
      "is_alive": "boolean - Form active status",
      "form_id": "integer - Form ID",
      "subject_id": "integer - Subject ID"
    }
  ]
}
```

### 18. Get Student Dashboard Data (Filled)
**Endpoint:** `GET /api/getSDashDataFilled`

**Description:** Retrieves completed feedback forms for the current student.

**Authentication:** Required (Basic Auth)

**Response:** Same structure as getSDashData but for completed forms.

### 19. Get Student Dashboard Form Data
**Endpoint:** `GET /api/getSDashDataForm`

**Description:** Retrieves specific feedback form data for a student.

**Authentication:** Required (Basic Auth)

**Query Parameters:**
- `form_id` (required) - ID of the feedback form

**Response:**
```json
{
  "status_code": 200,
  "data": {
    "form_field": "object - Form questions and structure",
    "subject": "string - Subject name",
    "is_filled": "boolean - Completion status",
    "user_feedback": "object - Previous responses if any",
    "teacher_name": "string - Teacher's name",
    "due_date": "string - Form due date",
    "year": "integer - Academic year",
    "is_theory": "boolean - Theory or practical",
    "is_alive": "boolean - Form active status",
    "form_id": "integer - Form ID",
    "subject_id": "integer - Subject ID"
  }
}
```

---

## Subject Management Endpoints

### 20. Get All Subjects
**Endpoint:** `GET /api/getallsubjects`

**Description:** Retrieves all subjects with their theory and practical assignments.

**Authentication:** Required (Basic Auth)

**Query Parameters:**
- `instance_id` (optional) - Filter subjects by instance ID

**Response:**
```json
{
  "status_code": 200,
  "data": [
    {
      "id": "integer - Subject ID",
      "subject_name": "string - Subject name",
      "instance_name": "string - Instance name",
      "is_selected": "boolean - Whether instance is selected",
      "theory_subject": [
        {
          "id": "integer - Theory subject ID",
          "subject_name": "string - Subject name",
          "batch_id": "integer - Batch ID",
          "batch_name": "string - Batch name",
          "batch_year": "integer - Batch year",
          "sub_teacher_name": "array - Teacher names"
        }
      ],
      "practical_subject": [
        {
          "id": "integer - Practical subject ID",
          "subject_name": "string - Subject name",
          "batch_id": "integer - Batch ID",
          "batch_name": "string - Batch name",
          "batch_year": "integer - Batch year",
          "prac_teacher_name": "array - Teacher names"
        }
      ]
    }
  ]
}
```

### 21. Delete Subject
**Endpoint:** `DELETE /api/deletesubject/<subject_id>/`

**Description:** Deletes a subject and all associated theory/practical assignments.

**Authentication:** Required (Teacher Auth)

**Path Parameters:**
- `subject_id` (required) - ID of the subject to delete

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Subject deleted successfully"
}
```

### 22. Add Theory Subject
**Endpoint:** `POST /api/addTheorySubject`

**Description:** Creates a new theory subject assignment.

**Authentication:** Required (Teacher Auth)

**Parameters:**
```json
{
  "subject_name": "string (required) - Name of the subject",
  "batch_id": "integer (required) - ID of the batch",
  "teacher_ids": "array (required) - Array of teacher user IDs",
  "instance_id": "integer (optional) - ID of the feedback instance"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Theory subject added successfully",
  "subject_id": "integer - Subject ID",
  "theory_id": "integer - Theory assignment ID"
}
```

### 23. Add Practical Subject
**Endpoint:** `POST /api/addPractical`

**Description:** Creates a new practical subject assignment.

**Authentication:** Required (Teacher Auth)

**Parameters:**
```json
{
  "subject_name": "string (required) - Name of the subject",
  "batch_id": "integer (required) - ID of the batch",
  "teacher_ids": "array (required) - Array of teacher user IDs",
  "instance_id": "integer (optional) - ID of the feedback instance"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Practical subject added successfully",
  "subject_id": "integer - Subject ID",
  "practical_id": "integer - Practical assignment ID"
}
```

---

## Batch Management Endpoints

### 24. Get All Batches
**Endpoint:** `GET /api/getBatches`

**Description:** Retrieves all batches in a simplified format for dropdown lists.

**Authentication:** Required (Basic Auth)

**Query Parameters:**
- `instance_id` (optional) - Filter batches by instance ID

**Response:**
```json
{
  "status_code": 200,
  "data": [
    {
      "label": "string - Batch display name",
      "value": "integer - Batch ID",
      "year": "integer - Academic year"
    }
  ]
}
```

### 25. Get Batches by Year
**Endpoint:** `GET /api/getYrBatches`

**Description:** Retrieves batches for a specific academic year.

**Authentication:** Required (Basic Auth)

**Query Parameters:**
- `year` (required) - Academic year
- `instance_id` (optional) - Filter by instance ID

**Response:** Same structure as getBatches.

### 26. Get Year Batches Summary
**Endpoint:** `GET /api/getYearBatches`

**Description:** Retrieves all years with their respective batches and student counts.

**Authentication:** Required (Basic Auth)

**Query Parameters:**
- `instance_id` (optional) - Filter by instance ID

**Response:**
```json
{
  "status_code": 200,
  "data": [
    {
      "year": "integer - Academic year",
      "batches": [
        {
          "id": "integer - Batch ID",
          "batch_name": "string - Batch name",
          "batch_division": "string - Division/section",
          "student_count": "integer - Number of students in batch"
        }
      ]
    }
  ]
}
```

### 27. Create Batch
**Endpoint:** `POST /api/bac`

**Description:** Creates a new student batch.

**Authentication:** Required (Teacher Auth)

**Parameters:**
```json
{
  "batch_name": "string (required) - Name of the batch",
  "batch_division": "string (required) - Division or section",
  "year": "integer (required) - Academic year",
  "student_emails": "array (optional) - Array of student email addresses",
  "instance_id": "integer (optional) - ID of the feedback instance"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Batch created successfully",
  "batch_id": "integer - ID of the created batch"
}
```

### 28. Update Batch
**Endpoint:** `POST /api/bacUpdate`

**Description:** Updates an existing batch.

**Authentication:** Required (Teacher Auth)

**Parameters:**
```json
{
  "batch_id": "integer (required) - ID of the batch to update",
  "batch_name": "string (optional) - Updated batch name",
  "batch_division": "string (optional) - Updated division",
  "year": "integer (optional) - Updated academic year",
  "student_emails": "array (optional) - Updated student email list",
  "instance_id": "integer (optional) - Updated instance ID"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Batch updated successfully"
}
```

### 29. Delete Batch
**Endpoint:** `POST /api/delBatch`

**Description:** Deletes a batch and removes all student associations.

**Authentication:** Required (Teacher Auth)

**Parameters:**
```json
{
  "batch_id": "integer (required) - ID of the batch to delete"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Batch deleted successfully"
}
```

---

## User Management Endpoints

### 30. Get User Profile
**Endpoint:** `GET /api/getProfile`

**Description:** Retrieves the current user's profile information.

**Authentication:** Required (Basic Auth)

**Response:**
```json
{
  "status_code": 200,
  "data": {
    "name": "string - User's full name",
    "email": "string - User's email",
    "age": "integer - User's age",
    "gender": "string - User's gender",
    "sapId": "string - Student/Staff ID",
    "mobile": "integer - Mobile number",
    "year": "integer - Academic year (for students)",
    "is_staff": "boolean - Whether user is staff/teacher",
    "is_superuser": "boolean - Whether user has admin privileges",
    "canCreateBatch": "boolean - Permission to create batches",
    "canCreateSubject": "boolean - Permission to create subjects",
    "canCreateFeedbackForm": "boolean - Permission to create feedback forms"
  }
}
```

### 31. Save User Profile
**Endpoint:** `POST /api/saveProfile`

**Description:** Updates the current user's profile information.

**Authentication:** Required (Basic Auth)

**Parameters:**
```json
{
  "name": "string (optional) - Updated full name",
  "age": "integer (optional) - Updated age",
  "gender": "string (optional) - Updated gender",
  "sapId": "string (optional) - Updated ID",
  "mobile": "integer (optional) - Updated mobile number",
  "year": "integer (optional) - Updated academic year"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Profile updated successfully"
}
```

### 32. Get Teacher Details
**Endpoint:** `GET /api/getTUsers/<username>`

**Description:** Retrieves details of a specific teacher by username.

**Authentication:** Required (Basic Auth)

**Path Parameters:**
- `username` (required) - Teacher's username/email

**Response:**
```json
{
  "status_code": 200,
  "data": {
    "email": "string - Teacher's email",
    "id": "integer - User ID",
    "name": "string - Teacher's name",
    "is_staff": "boolean - Staff status"
  }
}
```

### 33. Get All Users List
**Endpoint:** `GET /api/getuserslist`

**Description:** Retrieves a list of all users in the system.

**Authentication:** Required (Basic Auth)

**Response:**
```json
{
  "status_code": 200,
  "data": [
    {
      "email": "string - User's email",
      "id": "integer - User ID",
      "is_staff": "boolean - Staff status",
      "name": "string - User's name"
    }
  ]
}
```

### 34. Update Teacher Settings
**Endpoint:** `POST /api/tSettings`

**Description:** Updates teacher permissions and settings.

**Authentication:** Required (Superuser Auth)

**Parameters:**
```json
{
  "user_id": "integer (required) - ID of the teacher user",
  "canCreateBatch": "boolean (optional) - Permission to create batches",
  "canCreateSubject": "boolean (optional) - Permission to create subjects",
  "canCreateFeedbackForm": "boolean (optional) - Permission to create feedback forms"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Teacher permissions updated successfully"
}
```

---

## Instance Management Endpoints

### 35. Create New Instance
**Endpoint:** `POST /api/createNewInst`

**Description:** Creates a new feedback instance for organizing forms and subjects.

**Authentication:** Required (Superuser Auth)

**Parameters:**
```json
{
  "instance_name": "string (required) - Name of the new instance"
}
```

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Instance created successfully",
  "instance_id": "integer - ID of the created instance"
}
```

### 36. Generate Secret Code
**Endpoint:** `POST /api/generateSecretCode`

**Description:** Generates a new secret code for teacher registration.

**Authentication:** Required (Superuser Auth)

**Response:**
```json
{
  "status_code": 200,
  "status_msg": "Secret code generated successfully",
  "secret_code": "string - 8-character secret code"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "status_code": 400,
  "status_msg": "Error description"
}
```

### 401 Unauthorized
```json
{
  "status_code": 401,
  "status_msg": "Invalid email or password"
}
```

### 403 Forbidden
```json
{
  "status_code": 403,
  "status_msg": "Access denied, Authentication header not found or invalid token"
}
```

### 404 Not Found
```json
{
  "status_code": 404,
  "status_msg": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "status_code": 500,
  "status_msg": "Internal server error description"
}
```

---

## Authentication Types

### Basic Auth
- Requires a valid JWT access token in the Authorization header
- Format: `Authorization: Bearer <access_token>`
- Used for general authenticated endpoints

### Teacher Auth
- Requires Basic Auth + user must have `is_staff = True`
- Used for teacher-specific operations

### Superuser Auth
- Requires Basic Auth + user must have `is_superuser = True`
- Used for administrative operations

---

## Data Models

### User Roles
- **Student**: Regular users who fill feedback forms
- **Teacher/Staff**: Can create and manage feedback forms, subjects, and batches
- **Superuser/Admin**: Has all teacher permissions plus user management and instance creation

### Feedback Form Structure
- Contains dynamic form fields as JSON
- Assigned to specific batches and subjects
- Has due dates and active status
- Links students to their responses via connectors

### Batch Organization
- Groups students by year and division
- Many-to-many relationship with students
- Used for assigning feedback forms

### Subject Management
- Supports both theory and practical subjects
- Links to batches and teachers
- Can be organized under instances

---

## Rate Limiting and Security

- JWT tokens expire after 6 hours (access) and 24 hours (refresh)
- OTP expires after 10 minutes
- Password reset tokens are single-use
- All sensitive operations require appropriate authentication levels
- Email verification required for new accounts

---

## Environment Variables Required

```
SECRET_KEY=your_secret_key
MONGODB_URI=your_mongodb_uri
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
FRONT_END_LINK=http://localhost:3000
DJ_LOGO=https://example.com/logo.png
```
