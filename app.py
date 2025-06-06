# app.py - Main Flask application (Render optimized)
from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
import os
from datetime import datetime
from fpdf import FPDF
import io
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure Google Gemini API key from environment variable
try:
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        logger.info("Gemini API configured successfully")
    else:
        logger.warning("GEMINI_API_KEY not found in environment variables")
except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")

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
    try:
        return render_template('index.html', currencies=CURRENCIES)
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        return f"Error loading page: {str(e)}", 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate currency report using Gemini"""
    try:
        logger.info("Generating report request received")
        
        # Check if API key is configured
        if not os.getenv('GEMINI_API_KEY'):
            logger.error("GEMINI_API_KEY not configured")
            return jsonify({'error': 'Gemini API key is not configured'}), 500
        
        # Get form data
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        currency = request.form.get('currency')
        
        logger.info(f"Report request: {currency} from {start_date} to {end_date}")
        
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

        The goal is to output a **clean, well-formatted currency performance summary**, including price movement, news highlights, macroeconomic calendar events, and technical indicators. Follow the instructions step-by-step and output in the exact structure described.

        [SECTION 1: Report Header]
        Output this first:
        Month and Year of end_date
        Comprehensive Currency Report

        [SECTION 2: Market Performance]
        In 3–4 sentences, summarize the overall economic and financial conditions that affected the currency pair during the time period.
        - Mention interest rate decisions, inflation reports, central bank tone, geopolitical tensions, or global events that had an impact.
        - Summarize the tone (e.g., hawkish/dovish), market reaction, and notable shifts.

        [SECTION 3: Market Last Month]
        Present a 1-row table showing the price movement:

        Date           start_date     end_date     % Change  
        currency_pair     starting_price     ending_price     percent_change

        Note:
        - Get prices from Reuters (https://www.reuters.com/markets/currencies/)
        - If date is a holiday/weekend, use the nearest available previous trading day.
        - Calculate % change as ((end - start) / start) * 100, rounded to 2 decimal places.

        [SECTION 4: Currency Movement Summary]
        Write a 3–5 sentence summary explaining how the currency pair moved during the month.
        Include:
        - Key dates and events (e.g., “On Jun 5, Fed held rates steady...”, “On Jun 12, CPI data surprised markets...”)
        - Include any major news items or releases that caused volatility or trend shifts.
        - Cite actual vs forecast values for major indicators if available (e.g., “Core CPI y/y came in at 2.3% vs 2.4% forecast”).
        - Use data from Reuters and economic calendar from https://www.forexfactory.com/calendar.

        [SECTION 5: Key Technical Indications]
        Write 2–3 bullet points describing the technical chart setup and indicators for this currency pair:
        • Mention any visible patterns (e.g., triangle, head-and-shoulders, channel) and their breakout levels (with price levels).
        • Describe indicator readings such as RSI, MACD, EMA (e.g., “RSI at 62, indicating bullish momentum”), and what they suggest.
        • Suggest trend direction if supported by technicals.

        [SECTION 6: Expected Range and Key Levels]
        Conclude with expected range and support/resistance:
        Month      Expected Range       Key Levels  
        Month name of end_date   lower_bound–upper_bound     Support at support_level ; Resistance at resistance_level

        - Choose levels based on current volatility, recent highs/lows, and event risks.
        -    All values must reflect realistic price zones (2 decimal places).

        [IMPORTANT RULES]
        - Be concise, factual, and data-driven.
        - Use a structured layout: use sections and formatting as described.
        - No extra commentary, no casual tone—this is a financial report.
        - Do not skip any section.

        here is the example if need to go through
        example:USDINR 
        In the month of May 2025, the Indian rupee experienced a sharp shift in momentum, beginning the 
        month on a strong note before weakening significantly. On May 2, the rupee surged to a seven-month 
        high of 83.76/USD, driven by robust foreign inflows into Indian equities, falling global oil prices, and 
        strength in other Asian currencies amid optimism around potential U.S. trade policy shifts. India's solid 
        macroeconomic backdrop—including stronger-than-expected Q4 GDP growth of 7.4% and a record 
        ₹2.7 lakh crore dividend transfer from the RBI—further bolstered investor sentiment. However, this 
        positive trend reversed sharply from May 3 onward as dollar demand surged, partly due to RBI’s efforts 
        to replenish forex reserves and increased hedging activity by importers and corporates. The rupee 
        depreciated to nearly 85.90 by May 9, also pressured by geopolitical tensions and global risk aversion. 
        The depreciation continued into mid-May, driven by the U.S.-China 90-day tariff truce, which 
        supported the dollar, and rising uncertainty over the Fed’s policy stance. 
        Looking ahead although India's disinflation trend, with CPI easing to 3.16%, gave the RBI room to cut 
        rates, rupee showing signs of stability supported by lower global oil prices, expected foreign inflows & 
        expectations of the Fed holding rates steady kept the USD strong. While the Reserve Bank of India is 
        likely to manage volatility through interventions and maintain a growth-supportive policy stance, dollar demand from corporates and global uncertainties could limit rupee appreciation. Overall, the bias 
        remains sideways with a slight bullish tilt for INR if external conditions remain favorable.  Key Technical Indications: 
        USD/INR has formed an inverse head and shoulders pattern, a bullish reversal setup, with the neckline 
        recently being tested around 85.90–86.00. The breakout above the neckline signals a shift in market 
        sentiment from bearish to bullish. If sustained, this breakout may lead to further upside, potentially 
        targeting previous swing highs near 86.70–87.00.  
        ▪ MACD (Moving Average Convergence Divergence): The MACD line has crossed above the 
        signal line and is moving upward, with green histogram bars expanding. This crossover 
        confirms bullish momentum and supports the breakout's strength. 
        ▪ 200-day EMA: The price has reclaimed the EMA (Blue Line), which is now acting as dynamic 
        support around 85.25. Sustained trading above this level reinforces the bullish bias and 
        confirms the trend reversal. 
        USD/INR shows a bullish reversal confirmed by the inverse head and shoulders breakout and a 
        supportive MACD crossover. As long as the price remains above the 200 EMA and neckline, the 
        outlook remains positive.
        
        Currency Pair: {currency}
        Analysis Period: {start_date} to {end_date}
        """
        
        # Call Gemini API with better error handling
        try:
            logger.info("Calling Gemini API")
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            logger.info("Gemini API call successful")
        except Exception as gemini_error:
            logger.error(f"Gemini API error: {gemini_error}")
            try:
                logger.info("Trying alternative model")
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content(prompt)
                logger.info("Alternative model successful")
            except Exception as fallback_error:
                logger.error(f"Fallback model error: {fallback_error}")
                try:
                    logger.info("Trying legacy model")
                    model = genai.GenerativeModel('models/gemini-pro')
                    response = model.generate_content(prompt)
                    logger.info("Legacy model successful")
                except Exception as legacy_error:
                    logger.error(f"All models failed: {legacy_error}")
                    return jsonify({'error': 'Unable to generate report. Please try again later.'}), 500
        
        # Extract the response text
        if hasattr(response, 'text') and response.text:
            report_text = response.text.strip()
            logger.info("Report generated successfully")
        else:
            logger.error("Empty response from Gemini")
            return jsonify({'error': 'Empty response from AI service'}), 500
        
        return jsonify({
            'success': True,
            'report': report_text,
            'currency': currency,
            'start_date': start_date,
            'end_date': end_date
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in generate_report: {str(e)}")
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
        logger.info("PDF download request received")
        
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
                        if current_line.strip():
                            pdf.cell(0, 6, current_line.strip(), 0, 1)
                        current_line = word + ' '
                if current_line.strip():
                    pdf.cell(0, 6, current_line.strip(), 0, 1)
            else:
                pdf.cell(0, 6, line, 0, 1)
        
        # Save PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # Generate filename
        filename = f"currency_report_{currency}_{start_date}_to_{end_date}.pdf"
        
        logger.info(f"PDF generated: {filename}")
        
        def cleanup_file():
            try:
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    logger.info("Temporary PDF file cleaned up")
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up temp file: {cleanup_error}")
        
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
        logger.error(f"Error generating PDF: {str(e)}")
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
    return jsonify({
        'status': 'healthy', 
        'message': 'Currency Report App is running',
        'gemini_configured': bool(os.getenv('GEMINI_API_KEY'))
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check if Gemini API key is set
    if not os.getenv('GEMINI_API_KEY'):
        logger.warning("GEMINI_API_KEY environment variable is not set!")
        print("Warning: GEMINI_API_KEY environment variable is not set!")
        print("Please set your Google Gemini API key before running the app.")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
    
    # Run the Flask app - Render compatible
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)