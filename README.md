# Issues Mapper

A web application for managing citizen-reported issues like illegal dumping, broken street lights, graffiti, and potholes. Built for city hall employees to efficiently track and visualize reported problems.

## Features

- **Upload Management**: Multi-file upload with AI-powered GPS and timestamp extraction from image watermarks using Google Gemini Vision AI
- **Map View**: Interactive OpenStreetMap visualization with color-coded markers by issue type, includes filtering by type and date range
- **Issues List**: Sortable, filterable DataTable with CSV export functionality
- **Issue Details**: Individual issue view with image display, location map, and deletion capability
- **Statistics Dashboard**:
  - Total issues count
  - Issues by type (pie chart)
  - Issue types over time (line chart showing trends)
- **Admin Panel**: User management and issue type configuration (admin-only)
- **Authentication**: Secure login system with password hashing (bcrypt)

## Tech Stack

- **Backend**: Python 3.11+, Flask 3.1.0
- **Database**: PostgreSQL (Supabase)
- **Storage**: Supabase Storage for image hosting
- **AI/ML**: Google Cloud Vertex AI with Gemini 2.0 Flash for image analysis
- **Frontend**: AdminLTE 3.2, Bootstrap 4, jQuery, Chart.js, DataTables
- **Maps**: Leaflet.js with OpenStreetMap tiles
- **Deployment**: Docker, Gunicorn

## Prerequisites

- Python 3.11 or higher
- Supabase account (free tier works)
- Google Cloud Platform account with Vertex AI API enabled
- GCP Service Account with Vertex AI User role

## Local Development Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd issues-heat-map
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
SUPABASE_DB_PASSWORD=your_db_password_here

# Database Configuration
DB_HOST=db.your-project.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres

# Flask Configuration
FLASK_SECRET_KEY=generate_a_strong_random_key_here
FLASK_ENV=development

# GCP Vertex AI Configuration
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/gcp-credentials.json
```

### 5. Set up GCP credentials

1. Download your GCP service account JSON key file
2. Save it as `gcp-credentials.json` in the project root
3. Update the path in `.env`

See [docs/gcp-setup.md](docs/gcp-setup.md) for detailed GCP setup instructions.

### 6. Run database migrations

1. Go to your Supabase dashboard (https://app.supabase.com)
2. Open SQL Editor
3. Run each migration file in order:
   - `migrations/001_create_users_table.sql`
   - `migrations/002_create_issue_types_table.sql`
   - `migrations/003_create_issues_table.sql`
   - `migrations/004_seed_issue_types.sql`
   - `migrations/005_remove_status_column.sql`

### 7. Configure Supabase Storage

1. In your Supabase dashboard, go to Storage
2. Create a new bucket called `issue-images`
3. Set it to **Public** (images need to be accessible via URL)

### 8. Start the application

```bash
python app.py
```

Access the application at `http://localhost:5000`

### 9. First-time setup

1. Navigate to `http://localhost:5000`
2. You'll be redirected to the setup page
3. Create your first admin account with email and password
4. Login with your credentials

## Production Deployment

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions including:
- Environment variable configuration
- Security best practices
- HTTPS setup
- Backup strategies

## Project Structure

```
issues-heat-map/
├── app/
│   ├── blueprints/          # Route blueprints (modular organization)
│   │   ├── auth/           # Authentication routes
│   │   ├── upload/         # File upload routes
│   │   ├── map/            # Map view routes
│   │   ├── issues/         # Issues management routes
│   │   ├── statistics/     # Statistics routes
│   │   └── admin/          # Admin panel routes
│   ├── models/             # Database models
│   ├── static/             # Static files (CSS, JS, images)
│   ├── templates/          # Jinja2 HTML templates
│   ├── utils/              # Utility functions
│   └── __init__.py         # Flask app factory
├── config.py               # Configuration management
├── app.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
└── README.md
```

## User Roles

- **Admin**: Full access including user management and issue type configuration
- **Employee**: Can upload issues, view all issues, export data, delete issues

## Security Features

- Password hashing using bcrypt
- Session-based authentication
- Login required decorators on all routes
- Role-based access control for admin features
- Environment variables for sensitive data
- HTTPS recommended for production

## Troubleshooting

### Database Connection Issues
- Verify Supabase credentials in `.env`
- Ensure migrations ran successfully
- Check that Supabase project is active

### Image Upload Fails
- Verify Supabase Storage bucket `issue-images` exists and is public
- Check GCP credentials are valid and Vertex AI API is enabled
- Ensure service account has Vertex AI User role

### AI Extraction Not Working
- Verify GCP_PROJECT_ID matches your actual project
- Check GOOGLE_APPLICATION_CREDENTIALS path is correct
- Ensure Gemini API is enabled in your GCP project
- Look for errors in console logs

### Login Issues
- Verify user exists in database: `SELECT * FROM users;`
- Check password was hashed correctly
- Clear browser cookies and try again
