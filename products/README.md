# Product Search CLI Tool

A command-line tool that combines Google's Gemini AI and SerpApi to search for products based on natural language specifications.

## Features

- **Natural Language Processing**: Describe what you're looking for in plain English
- **AI-Powered Analysis**: Gemini AI extracts search criteria from your specifications
- **Amazon Product Search**: SerpApi searches Amazon for matching products
- **Rich Output**: Formatted results with prices, ratings, reviews, and links

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The API keys are already configured in the script:
   - Gemini API Key: Included
   - SerpApi Key: Included

## Usage

### Basic Usage
```bash
python product_search.py "I need a wireless gaming headset under $100 with good reviews"
```

### With Options
```bash
# Get more results
python product_search.py "laptop for programming" --max-results 10

# Verbose mode (shows processing steps)
python product_search.py "wireless earbuds" --verbose

# Help
python product_search.py --help
```

## Examples

```bash
# Electronics
python product_search.py "noise cancelling headphones under $200"

# Home & Kitchen
python product_search.py "coffee maker with timer and thermal carafe"

# Sports & Outdoors
python product_search.py "running shoes for flat feet size 10"

# Books
python product_search.py "python programming books for beginners"
```

## Output Format

The tool displays:
- Product title
- Price
- Rating and number of reviews
- ASIN (Amazon product identifier)
- Direct Amazon link

Example output:
```
Found 5 products:
==================================================

1. Sony WH-1000XM4 Wireless Premium Noise Canceling Overhead Headphones
   💰 Price: $179.99
   ⭐ Rating: 4.4 (28,439 reviews)
   🔖 ASIN: B0863TXGM3
   🔗 Link: https://amazon.com/...
----------------------------------------
```

## How It Works

1. **Specification Analysis**: Gemini AI analyzes your natural language request
2. **Criteria Extraction**: AI extracts search terms, price ranges, and features
3. **Product Search**: SerpApi searches Amazon using the extracted criteria
4. **Result Formatting**: Products are formatted and displayed with key information

## Command Line Options

- `specification` (required): Your product specification in natural language
- `--max-results N`: Maximum number of products to return (default: 5)
- `--verbose, -v`: Show detailed processing information

## Error Handling

The tool handles various error conditions:
- Invalid API responses
- Network connectivity issues
- Malformed specifications
- No products found

## Technical Details

### Architecture
- `gemini_client.py`: Handles Gemini AI integration
- `serp_client.py`: Manages SerpApi product searches
- `product_search.py`: Main CLI orchestration script

### APIs Used
- **Google Gemini 2.0 Flash**: For natural language processing
- **SerpApi**: For Amazon product search capabilities

## Troubleshooting

If you encounter issues:

1. Check your internet connection
2. Verify API keys are valid
3. Use `--verbose` mode to see detailed processing steps
4. Try simpler specifications if complex ones fail

## License

This tool is for educational and personal use.
