# Interior Designer AI

A simple image-to-product recommendation system that uses Gemini AI to analyze room images and provide interior design recommendations with specific product purchasing ideas.

## How It Works

The system follows a 4-step process:

1. **Image Analysis**: Analyze room layout, objects, colors, and current style
2. **Design Critique**: Apply interior design fundamentals to identify issues and opportunities
3. **User Input Parsing**: Extract budget and preferences from unstructured text
4. **Product Recommendations**: Generate specific product lists with Amazon links

## Installation

1. Make sure you have the required dependencies:
```bash
pip install -r ../requirements.txt
```

2. Ensure API keys are configured in the `.env` file (located in the parent directory):
```
GEMINI_API_KEY=your_gemini_api_key
SERPAPI_API_KEY=your_serpapi_key
```

## Usage

### Basic Usage
```bash
python designer_cli.py <image_path> "<budget and preferences>"
```

### Examples

**Scandinavian Style Living Room:**
```bash
python designer_cli.py room.jpg "Budget 800 dollars, love scandinavian style, need more storage and plants"
```

**Modern Minimalist with Lighting Focus:**
```bash
python designer_cli.py living_room.png "1200 budget modern minimalist lighting plants"
```

**Bohemian Bedroom Makeover:**
```bash
python designer_cli.py bedroom.jpg "$500 boho style need more color and plants"
```

**Verbose Mode (Shows detailed analysis):**
```bash
python designer_cli.py room.jpg "Budget 1000 industrial style storage" --verbose
```

### Command Line Options

- `image_path` (required): Path to the room image file
- `preferences` (required): Budget and design preferences in natural language
- `-v, --verbose`: Show detailed analysis and processing steps
- `-h, --help`: Show help message

## Supported Image Formats

- `.jpg`, `.jpeg`
- `.png`
- `.gif`
- `.bmp`

## Input Format

The system accepts unstructured natural language input for budget and preferences. You can mention:

### Budget
- "Budget 800 dollars"
- "$1200"
- "spend up to 500"
- "1000 budget"

### Style Preferences
- modern, contemporary
- minimalist, scandinavian
- bohemian, boho
- industrial, rustic
- traditional, classic

### Specific Needs
- storage, shelving
- lighting, lamps
- seating, chairs
- plants, greenery
- color changes

### Example Inputs
- "Budget $800, scandinavian style, need storage and better lighting"
- "1200 dollars modern minimalist plants lighting"
- "$500 boho need more color and plants rental apartment"
- "Budget 1000 industrial style lots of storage small space"

## Output

The system provides:

1. **Room Analysis**: Type, size, current style, furniture inventory
2. **Design Critique**: Issues identified using interior design principles
3. **User Preferences**: Parsed budget and style preferences
4. **Product Recommendations**: Specific products with:
   - Product name and description
   - Category (lighting, storage, furniture, decor)
   - Price and rating
   - Reasoning for recommendation
   - Amazon purchase link
   - Budget tracking

## Interior Design Principles Applied

The system uses these core design principles in its analysis:

- **Balance**: Visual weight distribution
- **Proportion & Scale**: Relationship between objects and space
- **Rhythm**: Repetition of colors, patterns, textures
- **Emphasis**: Focal points and visual hierarchy
- **Harmony & Unity**: Cohesive style and color palette
- **Functionality**: Space efficiency and practical use
- **Lighting**: Natural and artificial light optimization
- **Flow**: Traffic patterns and space navigation

## Example Output

```
============================================================
INTERIOR DESIGNER AI ANALYSIS
============================================================

🔍 STEP 1: Analyzing room image...
✅ Room analyzed: Living Room (Mixed contemporary style)

🎨 STEP 2: Applying interior design principles...
✅ Design issues identified. Priority improvements: 3 items
   1. Improve lighting with warmer ambient options
   2. Add vertical storage solutions to reduce clutter
   3. Create a cohesive color palette

💬 STEP 3: Parsing your preferences...
✅ Preferences parsed. Budget: $800, Style: scandinavian

🛍️ STEP 4: Finding product recommendations...
✅ Found 6 product recommendations!

============================================================
FINAL RECOMMENDATIONS
============================================================

📊 QUICK SUMMARY:
Room: Living Room
Style: Mixed contemporary
Main Issues: Improve lighting with warmer ambient options, Add vertical storage solutions
Budget: $800

PRODUCT RECOMMENDATIONS:
========================
Budget: USD 800.00
Estimated Total: USD 645.00
Remaining Budget: USD 155.00

RECOMMENDED PRODUCTS:

1. IKEA FOTO Table Lamp with Warm LED Bulb
   Category: lighting
   Price: $49.99
   Rating: 4.3 (1,250 reviews)
   Why: Addresses lighting issues identified in critique
   Link: https://amazon.com/...
   ---

2. VASAGLE Ladder Shelf, 4-Tier Bookshelf
   Category: storage
   Price: $85.99
   Rating: 4.5 (3,420 reviews)
   Why: Provides vertical storage while maintaining scandinavian aesthetic
   Link: https://amazon.com/...
   ---
```

## Error Handling

The system handles common issues:

- **Invalid image files**: Checks file existence and format
- **API failures**: Provides fallback parsing and recommendations
- **Budget constraints**: Prioritizes products within budget
- **Missing preferences**: Requests clarification

## File Structure

```
designer/
├── __init__.py                 # Package initialization
├── image_analyzer.py          # Step 1: Image analysis using Gemini Vision
├── design_critic.py           # Step 2: Design fundamentals critique
├── input_parser.py            # Step 3: Parse user budget/preferences
├── product_finder.py          # Step 4: Generate product recommendations
├── designer_cli.py            # Main CLI interface
└── README.md                  # This documentation
```

## Dependencies

The system integrates with the existing product search infrastructure:

- **Gemini AI**: Image analysis and text processing
- **SerpApi**: Amazon product search
- **Existing modules**: `amazon/product_search_gemini_client.py` and `amazon/serp_client.py`

## Troubleshooting

**"Image file not found"**
- Check the image path is correct
- Ensure the file exists and is readable

**"API key not found"**
- Check `.env` file in parent directory
- Verify `GEMINI_API_KEY` and `SERPAPI_API_KEY` are set

**"Failed to analyze image"**
- Ensure image is clear and shows interior space
- Try a different image format
- Check internet connection for API calls

**"No product recommendations found"**
- Try increasing budget amount
- Simplify style preferences
- Use more common furniture/decor terms

For additional help, run with `--verbose` flag to see detailed processing steps.
