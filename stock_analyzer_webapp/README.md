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

## AI Chatbot Feature (Basic Implementation)

A new AI Chatbot feature has been added to the application. This is a basic implementation and serves as a foundation for future interactive AI capabilities.

### How to Use
1.  Navigate to the main page of the application (/).
2.  Below the stock analysis form, you will find an "AI Chat" section.
3.  Type your query into the input box labeled "Ask the AI...".
4.  Click the "Send" button or press Enter.
5.  The AI's response will appear in the chat area above the input box.

### Current Capabilities
*   The chat interface allows for sending messages to a backend AI service.
*   Currently, the AI responses are placeholders (e.g., "This is a placeholder AI response. You asked: [your query]").
*   The chat messages are logged by the server.

### Running Notes
*   The application can still be run using the Docker instructions provided (`docker build` and `docker run`) or directly with `flask run` (after installing requirements from `requirements.txt` in a virtual environment).
*   While `Flask-Sockets` and `gevent` have been added to dependencies for future WebSocket integration, the current HTTP-based chat does not require a special server setup beyond what Flask's development server provides. Full WebSocket functionality will require running the app with a gevent-compatible server.

## Project Structure

*   `Dockerfile`: Defines the Docker container for the application.
*   `stock_analyzer_webapp/`: Contains the Flask web application.
    *   `app.py`: The main Flask application file.
    *   `requirements.txt`: Python dependencies.
    *   `templates/`: HTML templates for the UI.
    *   `stock_analyzer_agent/`: The core agent logic for stock analysis.
    *   `README.md`: This file.
