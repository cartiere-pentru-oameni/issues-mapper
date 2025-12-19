# Setup Instructions

## Prerequisites

- Python 3.11 or higher
- Supabase account (free tier works)
- Google Cloud Platform account
- Git installed

## Step 1: Configure Supabase

### 1.1 Create Supabase Storage Bucket

1. Log in to your Supabase dashboard at https://app.supabase.com
2. Select your project
3. Navigate to **Storage** from the left sidebar
4. Click **New bucket**
5. Create a bucket named `issue-images`
6. Set it to **Public** (required for image URLs to work)
7. Click **Create bucket**

### 1.2 Run Database Migrations

1. In Supabase dashboard, navigate to **SQL Editor** from the left sidebar
2. Run each migration file in order:

   **Migration 001 - Users Table:**
   - Copy the contents of `migrations/001_create_users_table.sql`
   - Paste into SQL Editor and click **RUN**

   **Migration 002 - Issue Types Table:**
   - Copy the contents of `migrations/002_create_issue_types_table.sql`
   - Paste into SQL Editor and click **RUN**

   **Migration 003 - Issues Table:**
   - Copy the contents of `migrations/003_create_issues_table.sql`
   - Paste into SQL Editor and click **RUN**

   **Migration 004 - Seed Issue Types:**
   - Copy the contents of `migrations/004_seed_issue_types.sql`
   - Paste into SQL Editor and click **RUN**

   **Migration 005 - Remove Status Column:**
   - Copy the contents of `migrations/005_remove_status_column.sql`
   - Paste into SQL Editor and click **RUN**

3. Verify tables were created:
   ```sql
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
   ORDER BY table_name;
   ```

   You should see: `issue_types`, `issues`, `users`

## Step 2: Set Up Google Cloud Platform (GCP)

### 2.1 Create GCP Project

1. Go to [GCP Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your Project ID (e.g., `issue-heat-map`)

### 2.2 Enable Vertex AI API

1. In GCP Console, navigate to **APIs & Services > Library**
2. Search for "Vertex AI API"
3. Click on it and click **Enable**
4. Wait for the API to be enabled

### 2.3 Create Service Account

1. Go to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Fill in the details:
   - **Name**: `issues-mapper-sa`
   - **Service account ID**: `issues-mapper-sa`
   - **Description**: Service account for Gemini Vision AI
4. Click **Create and Continue**
5. Add role: **Vertex AI User** (`roles/aiplatform.user`)
6. Click **Continue** then **Done**

### 2.4 Generate Service Account Key

1. Click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key > Create new key**
4. Choose **JSON** format
5. Click **Create**
6. The JSON file will be downloaded automatically
7. **Save it as `gcp-credentials.json` in your project root directory**

**⚠️ IMPORTANT**: Keep this file secure. Never commit it to git. It's already in `.gitignore`.

## Step 3: Clone Repository and Install Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd issues-heat-map

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your credentials:

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
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# GCP Vertex AI Configuration
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/gcp-credentials.json
```

**Finding your Supabase credentials:**
1. Go to your Supabase project dashboard
2. Click **Settings** (gear icon) > **API**
3. Copy:
   - Project URL → `SUPABASE_URL`
   - `anon` `public` key → `SUPABASE_ANON_KEY`
   - `service_role` `secret` key → `SUPABASE_SERVICE_KEY`
4. For database password, go to **Settings > Database** and find your password

## Step 5: Start the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Step 6: First-Time Setup

1. Navigate to `http://localhost:5000`
2. You'll be automatically redirected to `/auth/setup`
3. Create your first admin account
4. Login with your credentials

## Troubleshooting

### Storage/Image Upload Issues
- Verify Supabase Storage bucket `issue-images` exists and is **Public**

### GCP/AI Extraction Issues
- Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct and absolute
- Check that Vertex AI API is enabled in GCP Console
- Ensure service account has "Vertex AI User" role

### Login Issues
- Clear browser cookies and try again
- Verify user exists: `SELECT * FROM users;`
