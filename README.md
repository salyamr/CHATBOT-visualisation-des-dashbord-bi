# Chatbot ALTEN - TDCA

A sophisticated Django-based web application featuring an AI-powered chatbot interface for ALTEN's Technical Documentation and Customer Assistance (TDCA) system.

## Features

### Core Functionality
- **AI-Powered Chatbot**: Interactive chatbot interface with natural language processing
- **Data Analytics**: Dynamic chart generation and visualization
- **Request Management**: Complete ticketing system for customer requests
- **Multi-Application Support**: Handles multiple applications (DIL, PLM, Catia V5, etc.)
- **Audit System**: Comprehensive audit trail and quality control
- **Satisfaction Tracking**: Customer satisfaction scoring and analysis

### Technical Features
- Modern responsive web interface
- PostgreSQL database with comprehensive schema
- RESTful API endpoints
- File upload and media handling
- Real-time data visualization with Chart.js
- Django admin interface for data management
- Custom management commands for data population

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database (version 12+)
- pip (Python package manager)
- Git for version control
- Virtual environment support

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ChatbotAlten
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure PostgreSQL Database**
   - Create a PostgreSQL database named `chatbotalten`
   - Update database settings in `ChatbotAlten/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'chatbotalten',
           'USER': 'postgres',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5431',  # or your PostgreSQL port
       }
   }
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Populate database with sample data**
   ```bash
   python manage.py populate_db
   ```
   This creates:
   - 10 sample users (USER001-USER010)
   - 5 applications (DIL, PLM, Catia V5, etc.)
   - 100 sample requests with realistic data
   - Associated audits, transfers, and satisfaction scores

7. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

## Running the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/Alten/Chatbot/` in your browser to access the chatbot interface.

### Available Endpoints
- `/Alten/Chatbot/` - Main chatbot interface
- `/Alten/Chatbot/analyze/` - Chat analysis endpoint
- `/Alten/Chatbot/generate-chart/` - Chart generation API
- `/admin/` - Django admin interface

## Project Structure

```
Chatbot/
├── Chatbot/                    # Main app directory
│   ├── management/             # Custom Django commands
│   │   └── commands/
│   │       └── populate_db.py  # Database population script
│   ├── migrations/             # Database migrations
│   ├── static/                 # Static files (CSS, JS, images)
│   │   ├── css/               # Stylesheets
│   │   ├── js/                # JavaScript files
│   │   └── images/            # Image assets
│   ├── templates/             # HTML templates
│   │   └── Chatbot/          # App-specific templates
│   ├── admin.py              # Admin interface configuration
│   ├── apps.py               # App configuration
│   ├── models.py             # Database models (7 tables)
│   ├── tests.py              # Test cases
│   ├── urls.py               # App URL patterns
│   └── views.py              # View functions and API endpoints
├── ChatbotAlten/             # Project configuration
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py               # WSGI configuration
├── database/                 # SQL import files
│   ├── insertion_applications.sql
│   ├── insertion_demandes.sql
│   └── other SQL files...
├── media/                    # User uploaded files
├── manage.py                 # Django management script
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## Database Schema

The application uses a comprehensive PostgreSQL schema with the following models:

- **Responsable**: Users (requesters, auditors, experts, support)
- **Application**: Software applications being supported
- **Demande**: Customer requests/tickets
- **Transfert**: Request transfers between teams
- **Audit**: Quality audits of resolved requests
- **Satisfaction**: Customer satisfaction scores
- **Historique**: Chat conversation history

## API Endpoints

### POST `/Alten/Chatbot/analyze/`
Analyzes chat input and returns AI-generated responses.

**Request:**
```json
{
    "message": "Show me statistics for DIL application"
}
```

**Response:**
```json
{
    "response": "Here are the statistics for DIL application..."
}
```

### POST `/Alten/Chatbot/generate-chart/`
Generates chart data based on database queries.

**Request:**
```json
{
    "query": "requests by application"
}
```

**Response:**
```json
{
    "chart_data": {
        "labels": ["DIL", "PLM", "Catia V5"],
        "data": [25, 30, 20]
    }
}
```

## Usage Examples

### Populate Database with Test Data
```bash
python manage.py populate_db
```

### Query Database via Django Shell
```bash
python manage.py shell
```
```python
from Chatbot.models import Demande, Application

# Get all requests for DIL application
dil_requests = Demande.objects.filter(application__nom_application='DIL')
print(f"DIL requests: {dil_requests.count()}")

# Get satisfaction scores
from Chatbot.models import Satisfaction
avg_satisfaction = Satisfaction.objects.aggregate(avg_score=models.Avg('score'))
print(f"Average satisfaction: {avg_satisfaction['avg_score']}")
```

## Development

### Adding New Features
1. Create new models in `models.py`
2. Generate migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Update views and templates as needed

### Testing
```bash
python manage.py test
```

### Debugging
Enable Django Debug Toolbar by setting `DEBUG = True` in settings.py

## Technologies Used

- **Backend**: Django 4.2.16, Python 3.12
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **AI/ML**: LangChain, Mistral AI
- **Styling**: Bootstrap, Custom CSS
- **Development**: Django Debug Toolbar

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check database credentials in settings.py
   - Verify database exists: `createdb chatbotalten`

2. **Migration Issues**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic
   ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please contact the ALTEN development team.

---

**Last Updated**: August 2025  
**Version**: 1.0.0  
**Django Version**: 4.2.16
