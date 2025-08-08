# Chatbot ALTEN - TDCA

A sophisticated Django-based web application featuring an AI-powered chatbot interface for ALTEN's Technical Documentation and Customer Assistance (TDCA) system with advanced data visualization capabilities.

## Features

### Core Functionality
- **AI-Powered Chatbot**: Interactive chatbot interface with natural language processing using Mistral AI
- **Advanced Data Visualization**: Dynamic chart generation with Chart.js and Plotly.js
- **Real-time Graph Generation**: Automatic chart creation from natural language queries
- **Request Management**: Complete ticketing system for customer requests
- **Multi-Application Support**: Handles multiple applications (DIL, PLM, Catia V5, etc.)
- **Audit System**: Comprehensive audit trail and quality control
- **Satisfaction Tracking**: Customer satisfaction scoring and analysis

### Data Visualization Features
- **Multiple Chart Types**: Bar charts, pie charts, doughnut charts, heatmaps
- **Interactive Heatmaps**: Priority/Criticality matrix with Plotly.js
- **Dynamic Data**: Real-time chart generation from PostgreSQL database
- **Smart Color Coding**: Intelligent color schemes based on data context
- **Download Functionality**: Export charts as images
- **Responsive Design**: Charts adapt to different screen sizes

### Available Chart Types
1. **Priority Distribution** - Bar chart showing test case priorities (High/Medium/Low)
2. **Project Distribution** - Pie chart showing test cases by project
3. **Status Distribution** - Bar chart showing test case statuses
4. **Test State Analysis** - Bar chart with color-coded test states (OK/KO/In Progress/etc.)
5. **Test Perimeter Analysis** - Doughnut chart showing test perimeters
6. **Profile Distribution** - Pie chart showing user profiles
7. **Criticality Analysis** - Bar chart showing criticality levels
8. **Priority/Criticality Matrix** - Interactive heatmap showing correlation

### Technical Features
- Modern responsive web interface with gradient design
- PostgreSQL database with comprehensive schema
- RESTful API endpoints for chart generation
- File upload and media handling
- Real-time data visualization with Chart.js and Plotly.js
- Django admin interface for data management
- Custom management commands for data population
- Intelligent query detection and chart routing

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
   cd TDCA-chabot
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure PostgreSQL Database**
   - Create a PostgreSQL database named `tdca_db`
   - Update database settings in `ChatbotAlten/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'tdca_db',
           'USER': 'postgres',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Populate database with test data**
   ```bash
   python generate_test_data.py
   ```
   This creates 50 realistic test cases with:
   - 5 projects (ProjetA, ProjetB, ProjetC, ProjetD, ProjetE)
   - 3 priority levels (High: 13, Medium: 17, Low: 20)
   - 3 criticality levels (High, Medium, Low)
   - 6 test states (OK, KO, In Progress, Not Started, Blocked, N/A)

7. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/Alten/Chatbot/` in your browser to access the chatbot interface.

## Using the Chart Generation Feature

### Activating Chart Mode
1. Click the **"Mode Génération de Graphiques"** button in the chatbot interface
2. The button will turn green and show "Actif"
3. Type your chart request in natural language

### Available Chart Commands
```bash
# Priority analysis
"graphique priorité"
"répartition des priorités"

# Project analysis  
"graphique projet"
"répartition par projet"

# Status analysis
"graphique statut" 
"répartition des statuts"

# Test state analysis
"graphique état"
"répartition des états de tests"

# Perimeter analysis
"graphique périmètre"
"répartition par périmètre"

# Profile analysis
"graphique profil"
"répartition des profils"

# Criticality analysis
"graphique criticité"
"répartition par criticité"

# Priority/Criticality matrix
"matrice priorité criticité"
"matrice de corrélation"
```

### Chart Features
- **Interactive Elements**: Hover for detailed information
- **Download Options**: Save charts as PNG images
- **Responsive Design**: Automatic resizing for different screens
- **Real-time Data**: Charts reflect current database state
- **Smart Colors**: Context-aware color schemes

## Utility Scripts

### View Database Data
```bash
python view_data.py
```
Displays all database records in a formatted table with statistics.

### Export to Excel (Advanced)
```bash
python export_data_to_excel.py
```
Creates a comprehensive Excel file with multiple sheets and professional formatting.

## Available Endpoints

- `/Alten/Chatbot/` - Main chatbot interface
- `/Alten/Chatbot/analyze/` - Chat analysis endpoint  
- `/Alten/Chatbot/generate-chart/` - Chart generation API
- `/admin/` - Django admin interface

## Project Structure

```
TDCA-chabot/
├── Chatbot/                    # Main app directory
│   ├── management/             # Custom Django commands
│   ├── migrations/             # Database migrations
│   ├── static/                 # Static files (CSS, JS, images)
│   │   ├── css/               # Stylesheets with gradient themes
│   │   ├── js/                # JavaScript with Chart.js/Plotly.js
│   │   └── analysis/          # Generated chart images (legacy)
│   ├── templates/             # HTML templates
│   │   └── chatbot.html       # Main interface with chart support
│   ├── models.py              # Database models
│   ├── views.py               # View functions with chart generation
│   └── urls.py                # URL patterns
├── ChatbotAlten/              # Project configuration
├── generate_test_data.py      # Test data generation script
├── view_data.py              # Simple data viewer
├── export_data_to_excel.py   # Excel export utility
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## Database Schema

The application uses a PostgreSQL database with the **CasDeTest** model:

```python
class CasDeTest(models.Model):
    projet = models.CharField(max_length=100)           # Project name
    test_perimeter = models.CharField(max_length=200)   # Test scope
    profile = models.CharField(max_length=100)          # User profile
    prio = models.CharField(max_length=50)              # Priority (High/Medium/Low)
    criticality = models.CharField(max_length=50)       # Criticality level
    test_state = models.CharField(max_length=100)       # Test status
    date_creation = models.DateTimeField()              # Creation date
```

## Chart Generation Architecture

### Backend Components
- **Direct Chart Functions**: Dedicated functions for each chart type
- **Smart Query Detection**: Natural language processing for chart requests
- **Data Aggregation**: Optimized database queries with Django ORM
- **JSON Response Format**: Standardized data format for frontend

### Frontend Components
- **Chart.js Integration**: Bar, pie, doughnut charts
- **Plotly.js Integration**: Interactive heatmaps and advanced visualizations
- **Dynamic Rendering**: Real-time chart creation and updates
- **Download Functionality**: Export charts as images

### Chart Types and Functions
```python
# Available chart generation functions
generate_priority_chart()              # Priority distribution
generate_project_chart()               # Project distribution  
generate_status_chart()                # Status distribution
generate_test_states_chart()           # Test state analysis
generate_test_perimeter_chart()        # Perimeter analysis
generate_profile_chart()               # Profile distribution
generate_criticality_chart()           # Criticality analysis
generate_priority_criticality_matrix() # Interactive heatmap
```

## API Endpoints

### POST `/Alten/Chatbot/generate-chart/`
Generates charts based on natural language queries.

**Request:**
```json
{
    "text": "graphique priorité"
}
```

**Response:**
```json
{
    "success": true,
    "chart_data": {
        "type": "bar",
        "data": {
            "labels": ["High", "Medium", "Low"],
            "datasets": [...]
        }
    },
    "title": "Répartition par Priorité",
    "description": "Nombre de cas de test par niveau de priorité",
    "is_heatmap": false
}
```

## Key Technologies

- **Backend**: Django 4.2.16, PostgreSQL, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Charts**: Chart.js 3.x, Plotly.js
- **AI**: Mistral AI for natural language processing
- **Database**: PostgreSQL with optimized queries
- **Styling**: Custom CSS with gradient themes

## Recent Improvements

### Chart System Overhaul
- **Fixed empty charts issue**: Replaced generic system with dedicated functions
- **Added Plotly.js support**: Interactive heatmaps for correlation analysis  
- **Implemented smart detection**: Natural language chart request processing
- **Enhanced color schemes**: Context-aware color coding
- **Added download functionality**: Export charts as images

### Performance Optimizations
- **Direct database access**: Eliminated intermediate data processing
- **Optimized queries**: Efficient Django ORM usage
- **Reduced load times**: Streamlined chart generation pipeline

### User Experience
- **Intuitive interface**: Clear chart mode activation
- **Responsive design**: Charts adapt to screen size
- **Error handling**: Graceful fallbacks for data issues
- **Real-time updates**: Charts reflect current data state

## Troubleshooting

### Common Issues

1. **Charts showing "Données indisponibles"**
   - Ensure database contains test data: `python generate_test_data.py`
   - Check PostgreSQL connection in settings.py

2. **Chart mode not activating**
   - Click the "Mode Génération de Graphiques" button
   - Ensure JavaScript is enabled in browser

3. **Database connection errors**
   - Verify PostgreSQL is running
   - Check database credentials in settings.py
   - Ensure database `tdca_db` exists

## Future Enhancements

- Additional chart types (radar, scatter plots)
- Real-time data streaming
- Advanced filtering options
- Custom color theme selection
- Chart annotation features
- Export to multiple formats (PDF, SVG)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is proprietary to ALTEN. All rights reserved.

---

**ALTEN TDCA Chatbot** - Advanced AI-powered assistance with comprehensive data visualization capabilities.
