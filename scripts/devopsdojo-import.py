#!/usr/bin/env python3
import requests
import argparse
import sys
import json
from datetime import datetime

def upload_to_defectdojo(args):
    """Upload scan results to DefectDojo"""
    
    # Read the ZAP report
    try:
        with open(args.report, 'r') as f:
            report_data = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Report file not found: {args.report}")
        sys.exit(1)
    
    # Prepare the upload
    url = f"{args.url.rstrip('/')}/api/v2/import-scan/"
    
    headers = {
        'Authorization': f'Token {args.api_key}'
    }
    
    # Prepare multipart form data
    files = {
        'file': (args.report.split('/')[-1], report_data, 'application/json')
    }
    
    data = {
        'engagement': args.engagement_id,
        'scan_type': args.scan_type,
        'active': 'true',
        'verified': 'true',
        'close_old_findings': 'true',
        'test_title': f"{args.app_name} - {args.service_name} - {args.environment}",
        'scan_date': datetime.now().strftime('%Y-%m-%d'),
        'minimum_severity': 'Info',
        'environment': args.environment,
        'tags': f"{args.app_name},{args.service_name},{args.environment}"
    }
    
    print(f"📤 Uploading scan results to DefectDojo...")
    print(f"   URL: {url}")
    print(f"   Engagement ID: {args.engagement_id}")
    print(f"   Test Title: {data['test_title']}")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data,
            timeout=120
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            test_id = result.get('test', 'N/A')
            print(f"✅ Successfully uploaded to DefectDojo")
            print(f"   Test ID: {test_id}")
            print(f"   View at: {args.url}/test/{test_id}")
            return 0
        else:
            print(f"❌ Upload failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return 1
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error uploading to DefectDojo: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='Upload ZAP scan results to DefectDojo')
    parser.add_argument('--report', required=True, help='Path to ZAP JSON report')
    parser.add_argument('--url', required=True, help='DefectDojo URL')
    parser.add_argument('--api-key', required=True, help='DefectDojo API key')
    parser.add_argument('--engagement-id', required=True, help='DefectDojo engagement ID')
    parser.add_argument('--scan-type', default='ZAP Scan', help='Scan type')
    parser.add_argument('--environment', required=True, help='Environment name')
    parser.add_argument('--app-name', required=True, help='Application name')
    parser.add_argument('--service-name', required=True, help='Service name')
    
    args = parser.parse_args()
    
    sys.exit(upload_to_defectdojo(args))

if __name__ == '__main__':
    main()