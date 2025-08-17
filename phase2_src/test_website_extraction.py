#!/usr/bin/env python3
"""
Test script to verify website information extraction from RAG chunks
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from rag_kb import RAGKB
import json

def test_website_extraction():
    """Test website information extraction from chunks"""
    print("Testing website information extraction from RAG chunks...")
    
    try:
        # Initialize RAG KB
        kb = RAGKB()
        
        # Test chunk creation
        chunks = kb._create_chunks()
        if not chunks:
            print("No chunks created!")
            return
        
        print(f"Created {len(chunks)} chunks")
        
        # Find chunks with website information
        website_chunks = []
        for chunk in chunks:
            if chunk.get('website_info') or chunk.get('contact_info'):
                website_chunks.append(chunk)
        
        if website_chunks:
            print(f"\nFound {len(website_chunks)} chunks with website information:")
            for i, chunk in enumerate(website_chunks, 1):
                print(f"\nChunk {i}: {chunk['chunk_id']}")
                print(f"HMO: {chunk['hmo_hebrew']}")
                
                if chunk.get('website_info'):
                    websites = chunk['website_info']
                    print(f"Websites found: {websites}")
                else:
                    print("No website information in this chunk")
        else:
            print("\nNo website information found in any chunks!")
        
        # Test search functionality
        print("\nTesting search functionality...")
        search_results = kb.search_services("dental services", top_k=3, language="en")
        
        if search_results:
            # Extract website information from search results
            websites = []
            for result in search_results:
                if 'website_info' in result:
                    websites.extend(result['website_info'])
            
            if websites:
                print("Website information found in search results!")
                print(f"Websites found in search results: {len(websites)}")
                for website in websites:
                    print(f"  - {website}")
            else:
                print("No website information found in search results")
        else:
            print("No search results found or search failed")
        
        # Test specific HMO chunk
        print("\nTesting Maccabi chunk specifically...")
        maccabi_chunks = [c for c in chunks if c.get('hmo_hebrew') == 'מכבי']
        
        if maccabi_chunks:
            chunk = maccabi_chunks[0]
            if chunk.get('website_info'):
                websites = chunk['website_info']
                print("Website information found in Maccabi chunk!")
                print(f"Websites in Maccabi chunk: {len(websites)}")
                for website in websites:
                    print(f"  - {website}")
            else:
                print("No website information found in Maccabi chunk")
        else:
            print("No Maccabi chunks found")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_website_extraction()
