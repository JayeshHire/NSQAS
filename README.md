# Streamlit Pro - Data Science Platform

## Overview
A comprehensive data science platform built with Streamlit that allows users to manage datasets, upload models, and perform data analysis. The platform features OAuth authentication with Google and provides different functionalities for authenticated and non-authenticated users.

## Features
- **User Authentication**: Google OAuth integration for secure user access
- **Dataset Management**:
  - Upload and manage your datasets
  - Search through available datasets
  - Select and track datasets of interest
- **Model Management**:
  - Upload and manage your machine learning models
- **Resource Pages**:
  - About Us information
  - Frequently Asked Questions (FAQ)

## Project Structure
```
streamlit-pro/
├── project/
│   ├── main.py                    # Main application entry point
│   ├── data_consumer_dashboard.py # Dashboard for data consumers
│   ├── oauth.py                   # OAuth configuration
│   ├── pages/                    # Different pages of the application
│   ├── database/                 # Database related files
│   ├── forms/                    # Form components
│   ├── scripts/                  # Utility scripts
│   ├── batch/                    # Batch processing scripts
│   └── Datasetfilter/           # Dataset filtering functionality
├── requirements.txt              # Project dependencies
└── .streamlit/                  # Streamlit configuration
```

## Technology Stack
- **Frontend**: Streamlit (v1.45.1)
- **Backend**: Python 3.x
- **Database**: SQLAlchemy with SQLModel
- **Authentication**: Google OAuth via Authlib
- **Data Processing**:
  - pandas (v2.2.3)
  - numpy (v2.2.5)
  - scikit-learn (v1.6.1)
  - xgboost (v3.0.2)
- **Visualization**:
  - matplotlib (v3.10.3)
  - seaborn (v0.13.2)
  - altair (v5.5.0)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration
1. Set up Google OAuth credentials
2. Configure the `.streamlit/secrets.toml` file with your credentials
3. Ensure database connection settings are properly configured

## Usage

1. Start the application:
```bash
streamlit run project/main.py
```

2. Access the application through your web browser at `http://localhost:8501`

## User Guide

### For Unauthenticated Users
- Access to About Us page
- Access to FAQs
- Ability to log in using Google authentication

### For Authenticated Users
1. **Dataset Management**
   - Upload your datasets
   - Browse and search available datasets
   - Select datasets of interest

2. **Model Management**
   - Upload and manage your machine learning models
   - Track model performance

3. **User Profile**
   - Manage your account settings
   - Track your uploaded content

## Security Features
- Google OAuth integration for secure authentication
- Secure session management
- Database security with SQLAlchemy

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support and questions, please create an issue in the repository or contact the development team. 