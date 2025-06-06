# app.py - Main Flask application (Railway optimized)
from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
import os
from datetime import datetime
from fpdf import FPDF
import io
import tempfile

# Initialize Flask app
app = Flask(__name__)

# Configure Google Gemini API key from environment variable
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# List of available currencies
CURRENCIES = [
    'USDINR', 'EURUSD', 'USDJPY', 'USDAUD', 
    'USDPHP', 'USDZAR', 'USDMXN', 'USDBRL'
]

class PDF(FPDF):
    """Custom PDF class for generating currency reports"""
    
    def header(self):
        """Add header to each page"""
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Currency Report', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        """Add footer to each page"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

@app.route('/')
def home():
    """Main page with the form"""
    return render_template('index.html', currencies=CURRENCIES)

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate currency report using Gemini"""
    try:
        # Get form data
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        currency = request.form.get('currency')
        
        # Validate inputs
        if not all([start_date, end_date, currency]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if currency not in CURRENCIES:
            return jsonify({'error': 'Invalid currency selected'}), 400
        
        # Validate dates
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt >= end_dt:
                return jsonify({'error': 'End date must be after start date'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Create detailed prompt for Gemini
        prompt = f"""
        You are a professional financial analyst. Generate a comprehensive currency analysis report for {currency} covering the period from {start_date} to {end_date}.

        Please include the following sections in your report:

        1. EXECUTIVE SUMMARY
        - Brief overview of the currency pair's performance during this period
        - Key highlights and major trends

        2. MARKET ANALYSIS
        - Price movements and volatility analysis
        - Major support and resistance levels
        - Trading volume patterns (if applicable)

        3. FUNDAMENTAL FACTORS
        - Economic indicators that influenced the currency pair
        - Central bank policies and interest rate changes
        - Political and economic events that impacted the currencies

        4. TECHNICAL ANALYSIS
        - Trend analysis (bullish, bearish, or sideways)
        - Key technical indicators and patterns
        - Chart patterns observed during the period

        5. MARKET SENTIMENT
        - Overall market sentiment towards both currencies
        - Risk appetite and safe-haven flows
        - Institutional vs retail positioning

        6. FUTURE OUTLOOK
        - Short-term price projections
        - Key levels to watch
        - Potential catalysts for future movements

        7. RISK FACTORS
        - Potential risks and challenges
        - Scenarios that could impact the currency pair

        Please provide specific data points, percentages, and actionable insights where possible. 
        Make the report professional, informative, and suitable for both beginner and advanced traders.
        
        Currency Pair: {currency}
        Analysis Period: {start_date} to {end_date}
        """
        
        # Call Gemini API (try different model names)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
        except:
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content(prompt)
            except:
                # Fallback to older model name
                model = genai.GenerativeModel('models/gemini-pro')
                response = model.generate_content(prompt)
        
        # Extract the response text
        report_text = response.text.strip()
        
        return jsonify({
            'success': True,
            'report': report_text,
            'currency': currency,
            'start_date': start_date,
            'end_date': end_date
        })
        
    except Exception as e:
        # Handle various API errors
        error_message = str(e)
        if "API_KEY" in error_message.upper():
            return jsonify({'error': 'Gemini API key is invalid or missing'}), 500
        elif "QUOTA" in error_message.upper() or "LIMIT" in error_message.upper():
            return jsonify({'error': 'API quota exceeded. Please try again later.'}), 500
        else:
            return jsonify({'error': f'An error occurred: {error_message}'}), 500

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    """Convert report to PDF and download"""
    tmp_file_path = None
    try:
        # Get the report data from the request
        data = request.get_json()
        report_text = data.get('report', '')
        currency = data.get('currency', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        
        if not report_text:
            return jsonify({'error': 'No report text provided'}), 400
        
        # Create PDF
        pdf = PDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Currency Report: {currency}', 0, 1, 'C')
        pdf.cell(0, 10, f'Period: {start_date} to {end_date}', 0, 1, 'C')
        pdf.ln(10)
        
        # Add report content
        pdf.set_font('Arial', '', 12)
        
        # Split text into lines and add to PDF
        lines = report_text.split('\n')
        for line in lines:
            # Handle long lines by wrapping them
            if len(line) > 80:
                words = line.split(' ')
                current_line = ''
                for word in words:
                    if len(current_line + word) < 80:
                        current_line += word + ' '
                    else:
                        pdf.cell(0, 6, current_line.strip(), 0, 1)
                        current_line = word + ' '
                if current_line:
                    pdf.cell(0, 6, current_line.strip(), 0, 1)
            else:
                pdf.cell(0, 6, line, 0, 1)
        
        # Save PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # Generate filename
        filename = f"currency_report_{currency}_{start_date}_to_{end_date}.pdf"
        
        def cleanup_file():
            try:
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
            except:
                pass
        
        response = send_file(
            tmp_file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
        # Schedule cleanup after response
        response.call_on_close(cleanup_file)
        
        return response
        
    except Exception as e:
        # Clean up temp file on error
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Currency Report App is running'})

if __name__ == '__main__':
    # Check if Gemini API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("Warning: GEMINI_API_KEY environment variable is not set!")
        print("Please set your Google Gemini API key before running the app.")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
    
    # Run the Flask app - Railway compatible
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)