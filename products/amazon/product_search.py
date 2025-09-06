#!/usr/bin/env python3
"""
Product Search CLI Tool
Combines Gemini AI and SerpApi to search for products based on natural language specifications.
"""

import argparse
import sys
import os
from dotenv import load_dotenv
from product_search_gemini_client import GeminiClient
from serp_client import SerpApiClient

# Load environment variables from .env file
load_dotenv()

# Get API Keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def main():
    # Check if API keys are available
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        print("Please set GEMINI_API_KEY in your .env file or environment.")
        sys.exit(1)
    
    if not SERPAPI_API_KEY:
        print("Error: SERPAPI_API_KEY not found in environment variables.")
        print("Please set SERPAPI_API_KEY in your .env file or environment.")
        sys.exit(1)
    parser = argparse.ArgumentParser(
        description="Search for products using natural language specifications",
        epilog="Example: python product_search.py \"I need a wireless gaming headset under $100 with good reviews\""
    )
    
    parser.add_argument(
        "specification",
        help="Product specification in natural language"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of products to return (default: 5)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed processing information"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Processing specification: \"{args.specification}\"")
        print("=" * 60)
    
    # Initialize API clients
    try:
        gemini_client = GeminiClient(GEMINI_API_KEY)
        serp_client = SerpApiClient(SERPAPI_API_KEY)
    except Exception as e:
        print(f"Error initializing API clients: {e}")
        sys.exit(1)
    
    # Step 1: Extract search criteria using Gemini
    if args.verbose:
        print("Analyzing specification with Gemini AI...")
    
    search_criteria = gemini_client.extract_search_terms(args.specification)
    
    if not search_criteria:
        print("Failed to process specification with Gemini AI")
        sys.exit(1)
    
    if args.verbose:
        print(f"Extracted comprehensive search criteria:")
        print(f"   Primary query: {search_criteria.get('primary_query', 'N/A')}")
        if search_criteria.get('alternative_queries'):
            print(f"   Alternative queries: {', '.join(search_criteria.get('alternative_queries', []))}")
        print(f"   Price range: ${search_criteria.get('min_price', 'N/A')} - ${search_criteria.get('max_price', 'N/A')}")
        print(f"   Category: {search_criteria.get('category', 'N/A')}")
        if search_criteria.get('amazon_node'):
            print(f"   Amazon node: {search_criteria.get('amazon_node')}")
        print(f"   Must-have features: {', '.join(search_criteria.get('must_have_features', []))}")
        if search_criteria.get('preferred_brands'):
            print(f"   Preferred brands: {', '.join(search_criteria.get('preferred_brands', []))}")
        if search_criteria.get('excluded_terms'):
            print(f"   Excluded terms: {', '.join(search_criteria.get('excluded_terms', []))}")
        print(f"   Sort preference: {search_criteria.get('sort_preference', 'relevance')}")
        print(f"   Use case: {search_criteria.get('use_case', 'N/A')}")
        if search_criteria.get('quality_indicators'):
            print(f"   Quality indicators: {', '.join(search_criteria.get('quality_indicators', []))}")
        print()
    
    # Step 2: Search for products using SerpApi
    if args.verbose:
        print("Searching for products on Amazon...")
    
    products = serp_client.search_amazon_products(search_criteria, args.max_results)
    
    if not products:
        print("No products found or search failed")
        sys.exit(1)
    
    # Step 3: Display results
    if args.verbose:
        print(f"Found {len(products)} products")
        print()
    
    formatted_results = serp_client.format_products(products, show_scores=args.verbose)
    print(formatted_results)
    
    if args.verbose:
        print("\nTip: Use --max-results to get more products or --verbose for detailed processing info")

if __name__ == "__main__":
    main()
