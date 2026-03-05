#!/usr/bin/env python3
"""
Script to detect new videos by comparing current RSS feeds with stored URLs in output.csv
Creates a CSV file with new videos and an HTML file for easy viewing.
"""

import csv
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os

def parse_youtube_rss_for_latest(rss_url, channel_name="Unknown", row_index=0):
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
        print(f"  ✗ {channel_name}: Error - {str(e)}")
        return row_index, None, None

def check_for_new_videos(csv_file_path, max_workers=20):
    """
    Check for new videos by comparing current RSS feeds with stored URLs.
    
    Args:
        csv_file_path (str): Path to the output.csv file
        max_workers (int): Maximum number of concurrent threads
    
    Returns:
        list: List of dictionaries containing new video information
    """
    try:
        # Read the CSV file
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        # Prepare tasks for concurrent execution
        tasks = []
        channel_data = {}
        
        for i, row in enumerate(rows):
            xml_url = row.get('xmlUrl', '').strip()
            stored_url = row.get('LastUrl', '').strip()
            channel_name = row.get('Channel', 'Unknown')
            
            # Skip header row or rows without valid XML URL
            if not xml_url or 'ID des chaînes' in xml_url:
                continue
            
            tasks.append((xml_url, channel_name, i))
            channel_data[i] = {
                'channel': channel_name,
                'stored_url': stored_url,
                'xml_url': xml_url
            }
        
        total_channels = len(tasks)
        print(f"🔍 Checking {total_channels} channels for new videos...")
        print(f"Using {max_workers} concurrent workers for maximum speed!\n")
        
        completed = 0
        lock = threading.Lock()
        
        def progress_callback():
            nonlocal completed
            with lock:
                completed += 1
                if completed % 10 == 0 or completed == total_channels:
                    print(f"Progress: {completed}/{total_channels} channels checked")
        
        # Process channels concurrently
        new_videos = []
        updated_rows = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(parse_youtube_rss_for_latest, xml_url, channel_name, i): i 
                for xml_url, channel_name, i in tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_index):
                row_index, video_title, video_url = future.result()
                progress_callback()
                
                if video_title and video_url and row_index in channel_data:
                    channel_info = channel_data[row_index]
                    stored_url = channel_info['stored_url']
                    channel_name = channel_info['channel']
                    
                    # Check if this is a new video (URL doesn't match)
                    if video_url != stored_url:
                        print(f"  🆕 NEW VIDEO: {channel_name} - {video_title}")
                        new_videos.append({
                            'Channel': channel_name,
                            'VideoTitle': video_title,
                            'VideoUrl': video_url,
                            'xmlUrl': channel_info['xml_url']
                        })
                        
                        # Prepare updated row for output.csv
                        updated_rows.append({
                            'Channel': channel_name,
                            'xmlUrl': channel_info['xml_url'],
                            'LastVideo': video_title,
                            'LastUrl': video_url
                        })
                    else:
                        # No new video, keep existing data
                        updated_rows.append({
                            'Channel': channel_name,
                            'xmlUrl': channel_info['xml_url'],
                            'LastVideo': rows[row_index].get('LastVideo', ''),
                            'LastUrl': stored_url
                        })
        
        print(f"\n✅ Found {len(new_videos)} new videos!")
        return new_videos, updated_rows
        
    except Exception as e:
        print(f"Error checking for new videos: {str(e)}")
        sys.exit(1)

def create_new_videos_csv(new_videos, filename="new_videos.csv"):
    """
    Create a CSV file with the new videos found.
    
    Args:
        new_videos (list): List of new video dictionaries
        filename (str): Name of the output CSV file
    """
    if not new_videos:
        print("No new videos to save to CSV.")
        return
    
    fieldnames = ['Channel', 'VideoTitle', 'VideoUrl', 'xmlUrl']
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_videos)
    
    print(f"📄 Created CSV file: {filename}")

def update_output_csv(updated_rows, csv_file_path):
    """
    Update the output.csv file with new video information.
    
    Args:
        updated_rows (list): List of updated row dictionaries
        csv_file_path (str): Path to the output.csv file
    """
    # Read original file to preserve header row and any skipped rows
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        original_rows = list(reader)
    
    # Update the original rows with new data
    updated_dict = {row['Channel']: row for row in updated_rows}
    
    for i, row in enumerate(original_rows):
        channel = row.get('Channel', '')
        if channel in updated_dict:
            original_rows[i] = updated_dict[channel]
    
    # Write back to file
    fieldnames = ['Channel', 'xmlUrl', 'LastVideo', 'LastUrl']
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(original_rows)
    
    print(f"📄 Updated original CSV file: {csv_file_path}")

def create_html_file(new_videos, filename="new_videos.html"):
    """
    Create an HTML file with the new videos found, similar to to_be_watched.html.
    
    Args:
        new_videos (list): List of new video dictionaries
        filename (str): Name of the output HTML file
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""<html>
<head>
    <title>New Videos to Watch</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin: 10px 0; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }}
        a {{ text-decoration: none; color: #1a73e8; }}
        a:hover {{ text-decoration: underline; }}
        b {{ color: #333; }}
        .timestamp {{ color: #666; font-style: italic; }}
        .count {{ color: #28a745; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>🆕 New Videos to Watch</h1>
    <p class="timestamp">Generated on: {current_time}</p>
    <p class="count">Found {len(new_videos)} new videos</p>
    <ul>
"""
    
    if new_videos:
        for video in new_videos:
            html_content += f"""        <li><b>{video['Channel']}</b>: <a href="{video['VideoUrl']}" target="_blank">{video['VideoTitle']}</a></li>
"""
    else:
        html_content += "        <li>No new videos found.</li>\n"
    
    html_content += """    </ul>
</body>
</html>"""
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print(f"🌐 Created HTML file: {filename}")

def main():
    """Main function to run the new video detection script."""
    # csv_file_path = 'output.csv'
    csv_file_path = 'output_valid_only.csv'
    
    # Fallback to output.csv if output_valid_only.csv doesn't exist
    if not os.path.exists(csv_file_path):
        csv_file_path = 'output.csv'
    
    if not os.path.exists(csv_file_path):
        print(f"Error: {csv_file_path} not found!")
        print("Please run checkLastVideo.py first to generate the initial data.")
        sys.exit(1)
    
    print("🔍 NEW VIDEO DETECTOR")
    print("Comparing current RSS feeds with stored data to find new videos...\n")
    
    start_time = time.time()
    
    # Check for new videos
    new_videos, updated_rows = check_for_new_videos(csv_file_path)
    
    # Create outputs
    create_new_videos_csv(new_videos, "new_videos.csv")
    update_output_csv(updated_rows, csv_file_path)
    create_html_file(new_videos, "new_videos.html")
    
    end_time = time.time()
    
    print(f"\n⏱️  Total execution time: {end_time - start_time:.2f} seconds")
    print(f"🎉 Process completed! Check 'new_videos.csv' and 'new_videos.html' for results.")

if __name__ == "__main__":
    main()
