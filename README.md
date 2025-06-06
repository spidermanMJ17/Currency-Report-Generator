<<<<<<< HEAD
# Currency Report Generator

A Flask web application that generates AI-powered currency reports using OpenAI's API. Users can select date ranges and currency pairs to generate detailed reports, which can be downloaded as PDF files.

## Features

- **Interactive Web Interface**: Clean, user-friendly form for selecting currencies and date ranges
- **AI-Powered Reports**: Uses OpenAI's GPT model to generate detailed currency analysis
- **PDF Export**: Convert reports to downloadable PDF files
- **Multiple Currency Pairs**: Supports 8 major currency pairs (USDINR, EURUSD, USDJPY, etc.)
- **Date Validation**: Ensures logical date ranges and proper formatting
- **Error Handling**: Comprehensive error handling for API failures and validation issues

## Supported Currency Pairs

- USDINR (US Dollar to Indian Rupee)
- EURUSD (Euro to US Dollar)
- USDJPY (US Dollar to Japanese Yen)
- USDAUD (US Dollar to Australian Dollar)
- USDPHP (US Dollar to Philippine Peso)
- USDZAR (US Dollar to South African Rand)
- USDMXN (US Dollar to Mexican Peso)
- USDBRL (US Dollar to Brazilian Real)

## Prerequisites

- Python 3.7 or higher
- OpenAI API key (get one from [OpenAI Platform](https://platform.openai.com/api-keys))

## Local Setup and Installation

### Step 1: Clone or Download the Project

Create a new directory for your project and save all the provided files:

```
currency-report-app/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── README.md
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Navigate to your project directory
cd currency-report-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in your project root (optional) or set environment variable directly:

#### Option 1: Using .env file (recommended)
Create a file named `.env` in your project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And modify the top of `app.py` to include:
```python
from dotenv import load_dotenv
load_dotenv()
```

#### Option 2: Set environment variable directly

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your_openai_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

**macOS/Linux:**
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start and display:
```
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://[your-ip]:5000
```

### Step 6: Access the Application

Open your web browser and go to:
- `http://localhost:5000` or
- `http://127.0.0.1:5000`

## How to Use

1. **Select Start Date**: Choose the beginning date for your currency analysis
2. **Select End Date**: Choose the end date (must be after start date)
3. **Choose Currency Pair**: Select from the dropdown of available currency pairs
4. **Generate Report**: Click the "Generate Report" button
5. **Download PDF**: Once the report is generated, click "Download PDF" to save it

## File Structure

```
currency-report-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # HTML template with form and JavaScript
├── README.md             # This documentation
└── .env                  # Environment variables (you create this)
```

## Deployment Options

### Option 1: Deploy to Heroku

1. Install Heroku CLI
2. Create a `Procfile` in your project root:
   ```
   web: gunicorn app:app
   ```
3. Initialize git and Heroku:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your_openai_api_key_here
   git push heroku main
   ```

### Option 2: Deploy to Railway

1. Connect your GitHub repository to Railway
2. Set the `OPENAI_API_KEY` environment variable in Railway dashboard
3. Railway will automatically detect the Python app and deploy it

### Option 3: Deploy to Render

1. Connect your GitHub repository to Render
2. Set the environment variable `OPENAI_API_KEY` in Render dashboard
3. Use the build command: `pip install -r requirements.txt`
4. Use the start command: `python app.py`

### Option 4: Deploy to PythonAnywhere

1. Upload your files to PythonAnywhere
2. Create a new web app with Flask
3. Set the environment variable in the WSGI configuration file
4. Configure the web app to point to your app.py file

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key for generating reports | Yes |

## Troubleshooting

### Common Issues

1. **"OpenAI API key is invalid or missing"**
   - Make sure your API key is correctly set in the environment variable
   - Ensure your OpenAI account has sufficient credits

2. **"Module not found" errors**
   - Make sure you've activated your virtual environment
   - Run `pip install -r requirements.txt` to install all dependencies

3. **Date validation errors**
   - Ensure end date is after start date
   - Use the date picker or ensure dates are in YYYY-MM-DD format

4. **PDF generation fails**
   - Check that the report was generated successfully first
   - Ensure sufficient disk space for temporary files

### Debug Mode

The app runs in debug mode by default for local development. For production deployment, set `debug=False` in the `app.run()` call in `app.py`.

## API Usage and Costs

This application uses OpenAI's API, which charges based on token usage. The current setup uses the `gpt-3.5-turbo` model with a maximum of 1000 tokens per request. Monitor your OpenAI usage dashboard to track costs.

## Security Notes

- Never commit your API keys to version control
- Use environment variables for sensitive information
- Consider implementing rate limiting for production deployments
- The app runs on all interfaces (0.0.0.0) by default - change this for production

## Support

If you encounter any issues:

1. Check that all dependencies are installed correctly
2. Verify your OpenAI API key is valid and has credits
3. Ensure Python 3.7+ is being used
4. Check the console output for detailed error messages

## License

This project is provided as-is for educational and personal use.
=======
# Currency-Report-Generator
>>>>>>> f8a919437d125a95028fd32ca5082fb25bb97a18
