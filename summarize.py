#!/usr/bin/env python3
"""Batch summarize tech stories with Jatevo Qwen - Token Efficient"""
import json, os, urllib.request, re
from pathlib import Path

JATEVO_API_KEY = 'jk_53d910f23b78a51552ee53bb1a454ba812b96aab8dce93aa84eef11279a779a7'
JATEVO_URL = 'https://jatevo.id/api/open/v1/inference/chat/completions'

def call_jatevo(prompt):
    payload = json.dumps({
        'model': 'qwen3.5-plus',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 1500,
        'temperature': 0.3
    }).encode()
    
    req = urllib.request.Request(JATEVO_URL, data=payload, method='POST')
    req.add_header('Authorization', f'Bearer {JATEVO_API_KEY}')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read().decode())
    return resp['choices'][0]['message']['content']

def main():
    digest_path = Path(__file__).parent / 'digest.json'
    with open(digest_path) as f:
        data = json.load(f)
    
    print("Summarizing stories with AI (batch mode)...")
    
    for category, stories in data['stories'].items():
        print(f"\n  {category}: {len(stories)} stories")
        
        # Build prompt for this category
        titles_list = '\n'.join([f"{i+1}. {s['title']}" for i, s in enumerate(stories)])
        
        prompt = f"""Summarize these {category} news headlines. For each:
- Write exactly 1 sentence (max 15 words)
- **Bold** key terms: company names, AI/ML terms, $ amounts, security terms, product names
- Output ONLY a JSON array like: [{{"idx": 1, "summary": "**bold** text"}}, ...]

Headlines:
{titles_list}

JSON output:"""
        
        try:
            response = call_jatevo(prompt)
            
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                summaries = json.loads(json_match.group())
                for s in summaries:
                    idx = s.get('idx', 1) - 1
                    if 0 <= idx < len(stories):
                        stories[idx]['summary'] = s['summary']
            else:
                print(f"    No JSON found, using fallback")
                
        except Exception as e:
            print(f"    Error: {e}")
        
        # Fallback for any missing summaries
        for s in stories:
            if 'summary' not in s or 'pending' in s.get('summary', '').lower():
                s['summary'] = s['title'][:80] + ('...' if len(s['title']) > 80 else '')
    
    # Save updated digest
    with open(digest_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Summaries complete. Saved to digest.json")

if __name__ == '__main__':
    main()
