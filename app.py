# app.py - Main Flask application (Vercel optimized)
from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
import os
from datetime import datetime
from fpdf import FPDF
import io

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

               The report should include the following sections:
        1. Overview: Summarize the currency pair’s performance over the month, including price
        trends, appreciation or depreciation, and overall sentiment.

        2. Technical Analysis: Describe key technical indicators such as support and resistance
        levels, trend direction, RSI or MACD signals, and volatility.

        3. Key Events: Highlight important global or domestic economic events, central bank
        decisions, inflation data, geopolitical events, or any policy changes that affected this
        currency pair during the month.

        4. Conclusion: Provide a summary of the pair’s overall behavior, key takeaways from the
        month, and if applicable, an outlook or sentiment for the near future.
        Write the report in plain text, formatted with headings for each section. Avoid HTML or
        unnecessary symbols. Make sure the tone is suitable for a financial report.

        try make same replication as below example:

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
        
        # Create in-memory PDF buffer for Vercel (serverless friendly)
        pdf_buffer = io.BytesIO()
        pdf_string = pdf.output(dest='S')
        
        # Handle different fpdf versions
        if isinstance(pdf_string, str):
            pdf_string = pdf_string.encode('latin-1')
        
        pdf_buffer.write(pdf_string)
        pdf_buffer.seek(0)
        
        # Generate filename
        filename = f"currency_report_{currency}_{start_date}_to_{end_date}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

# Health check endpoint for Vercel
@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Currency Report App is running'})

# Error handlers for better debugging
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Main execution block - Vercel compatible
if __name__ == '__main__':
    # Check if Gemini API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("Warning: GEMINI_API_KEY environment variable is not set!")
        print("Please set your Google Gemini API key before running the app.")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
    
    # Run the Flask app - Vercel handles port and host automatically
    app.run(debug=False)