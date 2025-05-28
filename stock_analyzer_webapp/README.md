# Stock Analyzer Web Application

This web application provides analysis reports for stock tickers using the Stock Analyzer Agent.

## Prerequisites

*   Docker installed and running on your system.

## Running the Application

1.  **Clone the repository (if you haven't already):**
    ```bash
    # git clone <repository_url>
    # cd <repository_directory>
    ```

2.  **Build the Docker image:**
    Navigate to the root directory of the repository (where the `Dockerfile` is located) and run:
    ```bash
    docker build -t stock-analyzer-webapp .
    ```

3.  **Run the Docker container:**
    ```bash
    docker run -p 5000:5000 stock-analyzer-webapp
    ```

4.  **Access the application:**
    Open your web browser and go to [http://localhost:5000/](http://localhost:5000/).

## Usage

*   Enter a valid stock ticker symbol (e.g., AAPL, MSFT).
*   Select the type of report you want (Day Trader, Portfolio Manager, Beginner Investor).
*   Click "Analyze".
*   The application will display the generated report.

## Project Structure

*   `Dockerfile`: Defines the Docker container for the application.
*   `stock_analyzer_webapp/`: Contains the Flask web application.
    *   `app.py`: The main Flask application file.
    *   `requirements.txt`: Python dependencies.
    *   `templates/`: HTML templates for the UI.
    *   `stock_analyzer_agent/`: The core agent logic for stock analysis.
    *   `README.md`: This file.
