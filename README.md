# Who Do I Vote With? - Sentiment Analysis Website for Political News Articles

## Overview

**Who Do I Vote With?** is a web application designed to help Romanian citizens navigate political news by aggregating articles from various sources and classifying them based on sentiment. The application leverages natural language processing (NLP) techniques, specifically the BERT model, to provide users with insights into the political landscape, including trends, biases, and emotional tones in media coverage.

## Features

- **Article Aggregation**: Automatically scrapes political news from 12 Romanian sources every 5 minutes.
- **Sentiment Classification**: Uses a pre-trained BERT model to classify articles as positive, negative, or neutral.
- **Statistics Generation**: Provides users with insightful data visualizations on news trends and article sentiments using Apache ECharts.
- **Search & Explore**: Users can search for specific political topics or entities, explore related news, and view detailed statistics.
- **User Personalization**: Users can track articles and entities of interest and receive personalized content recommendations.

## Technologies Used

### Backend
- **Python** (Flask framework): Manages server-side operations and processes requests.
- **BeautifulSoup**: Used for scraping content from Romanian news websites.
- **psycopg2**: A PostgreSQL adapter for Python for efficient database interactions.
- **Torch and Hugging Face Transformers**: Powers the sentiment analysis through a Romanian BERT model.
  
### Frontend
- **React**: Provides a dynamic and responsive user interface for real-time updates.
- **CSS**: Ensures a clean and visually appealing layout.
- **Apache ECharts**: Delivers interactive charts and statistics for users.

### Database
- **PostgreSQL**: Stores news articles, political entities, and other relevant data for fast and reliable access.

## Architecture

The application follows a **client-server model**:
1. **Client-Side (React)**: Delivers a user-friendly interface where users can search for political articles, view statistics, and explore insights.
2. **Server-Side (Flask)**: Handles web scraping, sentiment classification, and database management.
3. **Database (PostgreSQL)**: Stores articles, political entities, and users' preferences.

## Installation and Setup

### Prerequisites
- Python 3.x
- Node.js
- PostgreSQL

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/username/who-do-i-vote-with.git
   ```
2. Navigate to the backend directory and install the dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL and configure your database connection in `config.py`.

4. Run the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```

## Usage

- **Explore**: View aggregated political news articles from Romanian sources.
- **Analyze**: Check sentiment trends and statistics on various political entities.
- **Personalize**: Sign up and save your favorite political topics for tailored content recommendations.

## Future Improvements

- Expanding to include local news sources across Romania.
- Training a custom BERT model focused exclusively on political news headlines.
- Enhancing the user experience with more detailed article insights and advanced filtering options.
