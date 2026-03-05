#!/usr/bin/env python3
"""
Script to fetch the latest video titles and URLs from YouTube RSS feeds
and update the output.csv file with this information.
"""

import csv
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def parse_youtube_rss(rss_url, channel_name="Unknown", row_index=0):
    """
    Fetch and parse YouTube RSS feed to get the latest video.
    
    Args:
        rss_url (str): The RSS feed URL
        channel_name (str): Name of the channel for logging
        row_index (int): Index of the row for tracking progress
    
    Returns:
        tuple: (row_index, video_title, video_url) or (row_index, None, None) if no valid video found
    """
    try:
        # Reduced timeout for faster processing
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(rss_url, headers=headers, timeout=5)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # YouTube RSS feeds use Atom namespace
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Find all entries (videos)
        entries = root.findall('atom:entry', namespace)
        
        for entry in entries:
            # Get video URL
            link_elem = entry.find('atom:link', namespace)
            if link_elem is not None:
                video_url = link_elem.get('href')
                
                # Skip if this is a YouTube short
                if video_url and '/shorts/' not in video_url:
                    # Get video title
                    title_elem = entry.find('atom:title', namespace)
                    if title_elem is not None:
                        video_title = title_elem.text
                        return row_index, video_title, video_url
        
        return row_index, None, None
        
    except Exception as e:
        return row_index, None, None

def update_csv_with_latest_videos(csv_file_path, max_workers=20):
    """
    Read the CSV file, fetch latest videos for each channel concurrently, and update the file.
    
    Args:
        csv_file_path (str): Path to the CSV file
        max_workers (int): Maximum number of concurrent threads
    """
    try:
        # Read the CSV file
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        # Prepare tasks for concurrent execution
        tasks = []
        valid_rows = []
        
        for i, row in enumerate(rows):
            xml_url = row.get('xmlUrl', '').strip()
            
            # Skip header row or rows without valid XML URL
            if not xml_url or 'ID des chaînes' in xml_url:
                continue
            
            channel_name = row.get('Channel', 'Unknown')
            tasks.append((xml_url, channel_name, i))
            valid_rows.append((i, row))
        
        total_channels = len(tasks)
        print(f"Processing {total_channels} channels concurrently with {max_workers} workers...")
        print("This should be much faster than sequential processing!\n")
        
        completed = 0
        lock = threading.Lock()
        
        def progress_callback():
            nonlocal completed
            with lock:
                completed += 1
                if completed % 20 == 0 or completed == total_channels:
                    print(f"Progress: {completed}/{total_channels} channels completed")
        
        # Process channels concurrently
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(parse_youtube_rss, xml_url, channel_name, i): i 
                for xml_url, channel_name, i in tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_index):
                row_index, video_title, video_url = future.result()
                results[row_index] = (video_title, video_url)
                progress_callback()
        
        # Update rows with results
        for row_index, row in valid_rows:
            if row_index in results:
                video_title, video_url = results[row_index]
                if video_title and video_url:
                    row['LastVideo'] = video_title
                    row['LastUrl'] = video_url
        
        # Write the updated data back to CSV
        fieldnames = ['Channel', 'xmlUrl', 'LastVideo', 'LastUrl']
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        # Create a second CSV file with only channels that have valid videos
        valid_channels_file = csv_file_path.replace('.csv', '_valid_only.csv')
        valid_rows = []
        
        for row in rows:
            # Keep header row and rows with valid video data
            if (row.get('Channel') == 'Titres des chaînes' or 
                (row.get('LastVideo') and row.get('LastUrl'))):
                valid_rows.append(row)
        
        with open(valid_channels_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(valid_rows)
        
        print(f"\n✓ Successfully updated {csv_file_path}")
        print(f"✓ Created filtered file: {valid_channels_file}")
        successful_updates = sum(1 for _, (title, url) in results.items() if title and url)
        print(f"✓ Found videos for {successful_updates}/{total_channels} channels")
        print(f"✓ Valid channels file contains {len(valid_rows)-1} channels with videos")
        
    except Exception as e:
        print(f"Error updating CSV file: {str(e)}")
        sys.exit(1)

def main():
    """Main function to run the script."""
    csv_file_path = 'output.csv'
    
    print("🚀 OPTIMIZED VERSION - Fetching latest videos from YouTube RSS feeds...")
    print("Using concurrent processing for maximum speed!\n")
    
    start_time = time.time()
    update_csv_with_latest_videos(csv_file_path)
    end_time = time.time()
    
    print(f"\n⏱️  Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
