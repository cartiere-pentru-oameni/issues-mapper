# Intro
This is a small web application where employees of the city hall can upload pictures sent by citizens with various issues (illegal dumping, broken street lights, potholes, etc.). The pictures contain watemarks with GPS coordinates and sometimes timestamps. The application extracts this data and saves it to a database. 
The application also provides a map view where employees can see the locations of the reported issues, a tabular view with all repors , with filtering and export capabilities. 

# User stories
us1: As a city hall employee, I want to upload pictures sent by citizens so that I can document reported issues.
us2: As a city hall employee, I expect the application to extract GPS coordinates and timestamps from the pictures so that I can easily locate and time-stamp the reported issues.
us3: As a city hall employee, I want to choosee at upload time, for each picture, the type of issue being reported (e.g., illegal dumping, broken street lights, potholes) so that I can categorize the reports effectively. For convenience, I want to have also the option to set all pictures to a selected issue type in one go.
us4: As a city hall employee, I want to view the reported issues on a map so that I can visualize the locations of the problems.
us5: As a city hall employee, I want to see a tabular view of all reported issues so that I can easily review and manage them.
us6: As a city hall employee, I want to filter the reported issues based on various criteria (e.g., issue type, date range) so that I can quickly find specific reports
us7: As a city hall employee, I want to export the list of reported issues to a CSV file so that I can share the data with other departments or for record-keeping purposes.
us8: As a city hall employee, I want the application to handle errors gracefully during the upload and data extraction process so that I can be informed of any issues without losing my data.
The images with issues should be marked so an employee can review and edit the metadata (issue type, GPS coordinates, timestamp) if needed.
us9: As a city hall employee, I want the application to provide feedback during the upload process (e.g., progress indicators) so that I know the status of my uploads.
us10: As a city hall employee, I want to be able to edit the details of a reported issue (e.g., change issue type, correct GPS coordinates) so that I can ensure the accuracy of the data.
us11: As a city hall employee, I want to be able to delete reported issues from the database so that I can manage and maintain the quality of the data.
us12: As an admin, I want to be able to manage user accounts and permissions so that I can control access to the application.
us13: As an admin, I want to be able to add / modify / delete issue types so that I can keep the categorization relevant and up-to-date.
us14: As an employee, I want to see statistics and reports on the reported issues (e.g., number of issues per type, trends over time) so that I can gain insights into the common problems faced by citizens.

# Application
## User interfaces
### Employee interface
- Login page for authentication
- Upload page with multi file input, issue type selection, and upload button
- Map view displaying reported issues with markers and filter options
- Tabular view with sortable columns, filtering options, and export button
- Issue detail view for editing and deleting reported issues
- Statistics dashboard with charts and graphs showing issue trends
- A page where employees can see all images that failed to be processed, with error messages and options to edit metadata manually
### Admin interface
- All employee interfaces
- User management page for adding, modifying, and deleting user accounts
- Issue type management page for adding, modifying, and deleting issue types

# Technnologies
- Python
- Flask
- PostgreSQL from Supabase
- Supabase Storage
- Docker
- OpenStreetMap
- AdminLTE
- Hetzner VPS with Coolify 
- Gemini with VertexAi for watermark data extraction

