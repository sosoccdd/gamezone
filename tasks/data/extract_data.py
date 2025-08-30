#!/usr/bin/env python3
import re
import sys

def extract_korean_text(file_path):
    """Extract Korean text from binary file"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Decode as UTF-8, ignoring errors
        text = data.decode('utf-8', errors='ignore')
        
        # Find Korean text patterns
        korean_pattern = r'[가-힣]{2,}[가-힣\s\d\-\(\)]*'
        korean_matches = re.findall(korean_pattern, text)
        
        # Find addresses (Korean text with numbers)
        address_pattern = r'[가-힣]{2,}[가-힣\s\d\-\(\)\.]*\d+[가-힣\s\d\-\(\)\.]*'
        address_matches = re.findall(address_pattern, text)
        
        # Find phone numbers
        phone_pattern = r'\d{2,3}-\d{3,4}-\d{4}'
        phone_matches = re.findall(phone_pattern, text)
        
        # Find potential store names (Korean text that might be business names)
        store_pattern = r'[가-힣]{2,}[가-힣\s]*(?:오락실|게임장|인형뽑기|크레인|플레이|존|랜드|타운|센터|월드|파크|스테이션)'
        store_matches = re.findall(store_pattern, text, re.IGNORECASE)
        
        print("=== Korean Text Found ===")
        for match in set(korean_matches):
            if len(match.strip()) > 2:
                print(match.strip())
        
        print("\n=== Potential Addresses ===")
        for match in set(address_matches):
            if len(match.strip()) > 5:
                print(match.strip())
        
        print("\n=== Phone Numbers ===")
        for match in set(phone_matches):
            print(match)
        
        print("\n=== Potential Store Names ===")
        for match in set(store_matches):
            print(match.strip())
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 extract_data.py <file_path>")
        sys.exit(1)
    
    extract_korean_text(sys.argv[1])