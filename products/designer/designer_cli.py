#!/usr/bin/env python3
"""
Interior Designer CLI
A simple image-to-product recommendation system using Gemini AI

Usage:
    python designer_cli.py <image_path> "<budget and preferences>"

Example:
    python designer_cli.py room.jpg "Budget 800 dollars, love scandinavian style, need more storage and plants"
"""

import sys
import os
import argparse
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from designer.image_analyzer import ImageAnalyzer
from designer.design_critic import DesignCritic
from designer.input_parser import InputParser
from designer.product_finder import ProductFinder

def load_api_keys():
    """Load API keys from .env file"""
    # Look for .env file in parent directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_path)
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    serpapi_key = os.getenv('SERPAPI_API_KEY')
    
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    if not serpapi_key:
        raise ValueError("SERPAPI_API_KEY not found in .env file")
    
    return gemini_key, serpapi_key

def validate_image_file(image_path):
    """Validate that the image file exists and is a supported format"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    _, ext = os.path.splitext(image_path.lower())
    
    if ext not in valid_extensions:
        raise ValueError(f"Unsupported image format: {ext}. Supported formats: {', '.join(valid_extensions)}")
    
    return True

def run_interior_designer(image_path, user_input, verbose=False):
    """
    Main function that runs the 4-step interior design process
    """
    try:
        # Load API keys
        if verbose:
            print("Loading API keys...")
        gemini_key, serpapi_key = load_api_keys()
        
        # Validate image
        if verbose:
            print(f"Validating image file: {image_path}")
        validate_image_file(image_path)
        
        # Initialize components
        if verbose:
            print("Initializing AI components...")
        image_analyzer = ImageAnalyzer(gemini_key)
        design_critic = DesignCritic(gemini_key)
        input_parser = InputParser(gemini_key)
        product_finder = ProductFinder(gemini_key, serpapi_key)
        
        print("=" * 60)
        print("INTERIOR DESIGNER AI ANALYSIS")
        print("=" * 60)
        
        # Step 1: Analyze Image
        print("\n🔍 STEP 1: Analyzing room image...")
        if verbose:
            print(f"Processing image: {image_path}")
        
        room_analysis = image_analyzer.analyze_room_image(image_path)
        if not room_analysis:
            print("❌ Failed to analyze image. Please check the image file and try again.")
            return False
        
        if verbose:
            print(image_analyzer.format_analysis(room_analysis))
        else:
            print(f"✅ Room analyzed: {room_analysis.get('room_type', 'Unknown')} ({room_analysis.get('current_style', 'Unknown style')})")
        
        # Step 2: Design Critique
        print("\n🎨 STEP 2: Applying interior design principles...")
        
        design_critique = design_critic.critique_design(room_analysis)
        if not design_critique:
            print("❌ Failed to generate design critique.")
            return False
        
        if verbose:
            print(design_critic.format_critique(design_critique))
        else:
            priority_improvements = design_critique.get('priority_improvements', [])
            print(f"✅ Design issues identified. Priority improvements: {len(priority_improvements)} items")
            for i, improvement in enumerate(priority_improvements[:3], 1):
                print(f"   {i}. {improvement}")
        
        # Step 3: Parse User Input
        print("\n💬 STEP 3: Parsing your preferences...")
        if verbose:
            print(f"User input: '{user_input}'")
        
        user_preferences = input_parser.parse_user_input(user_input)
        if not user_preferences or not user_preferences.get('parsed_successfully'):
            print("❌ Failed to parse user preferences. Please provide budget and style preferences.")
            return False
        
        if verbose:
            print(input_parser.format_parsed_input(user_preferences))
        else:
            budget = user_preferences.get('budget_amount', 0)
            style = ', '.join(user_preferences.get('style_preferences', ['Not specified']))
            print(f"✅ Preferences parsed. Budget: ${budget:,.0f}, Style: {style}")
        
        # Step 4: Generate Product Recommendations
        print("\n🛍️  STEP 4: Finding product recommendations...")
        
        products = product_finder.generate_product_recommendations(
            room_analysis, design_critique, user_preferences
        )
        
        if not products:
            print("❌ No product recommendations found. Please try adjusting your budget or preferences.")
            return False
        
        print(f"✅ Found {len(products)} product recommendations!")
        
        # Display Results
        print("\n" + "=" * 60)
        print("FINAL RECOMMENDATIONS")
        print("=" * 60)
        
        if not verbose:
            print("\n📊 QUICK SUMMARY:")
            print(f"Room: {room_analysis.get('room_type', 'Unknown')}")
            print(f"Style: {room_analysis.get('current_style', 'Unknown')}")
            print(f"Main Issues: {', '.join(design_critique.get('priority_improvements', [])[:2])}")
            print(f"Budget: ${user_preferences.get('budget_amount', 0):,.0f}")
        
        print(product_finder.format_recommendations(products, user_preferences))
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Interior Designer AI - Analyze room images and get product recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python designer_cli.py room.jpg "Budget 800 dollars, scandinavian style, need storage"
  python designer_cli.py living_room.png "1200 budget modern minimalist lighting plants"
  python designer_cli.py bedroom.jpg "$500 boho style need more color and plants" --verbose
        """
    )
    
    parser.add_argument('image_path', help='Path to the room image file')
    parser.add_argument('preferences', help='Budget and design preferences (unstructured text)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Show detailed analysis and processing steps')
    
    args = parser.parse_args()
    
    # Run the interior designer
    success = run_interior_designer(args.image_path, args.preferences, args.verbose)
    
    if success:
        print("\n✨ Interior design analysis complete! Happy decorating! ✨")
        sys.exit(0)
    else:
        print("\n❌ Interior design analysis failed. Please check your inputs and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
