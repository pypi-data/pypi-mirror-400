#!/usr/bin/env python3
"""
Email Extraction Script

This script extracts email addresses from text files using regular expressions.
"""

import re


def extract_emails(text):
    """
    Extract email addresses from the given text.
    
    Args:
        text (str): The text to search for email addresses
        
    Returns:
        list: A list of unique email addresses found in the text
    """
    # Email regex pattern that matches most common email formats
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Find all email addresses (case-insensitive)
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    
    # Return unique emails (preserve order)
    unique_emails = []
    for email in emails:
        if email.lower() not in [e.lower() for e in unique_emails]:
            unique_emails.append(email)
    
    return unique_emails


def main():
    """Main function to extract emails from text.txt and save results."""
    try:
        # Read the input text file
        with open('text.txt', 'r', encoding='utf-8') as file:
            text = file.read()
        
        print("Input text:")
        print(text)
        print("-" * 50)
        
        # Extract emails
        emails = extract_emails(text)
        
        # Display results
        print(f"Found {len(emails)} email address(es):")
        for i, email in enumerate(emails, 1):
            print(f"{i}. {email}")
        
        # Save results to file
        with open('extracted_emails.txt', 'w', encoding='utf-8') as output_file:
            output_file.write("Extracted Email Addresses:\n")
            output_file.write("=" * 30 + "\n\n")
            
            if emails:
                for i, email in enumerate(emails, 1):
                    output_file.write(f"{i}. {email}\n")
            else:
                output_file.write("No email addresses found.\n")
            
            output_file.write(f"\nTotal: {len(emails)} email(s)\n")
        
        print(f"\nResults saved to 'extracted_emails.txt'")
        
    except FileNotFoundError:
        print("Error: 'text.txt' file not found.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()