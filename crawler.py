#!/usr/bin/env python3
"""Tech News Crawler - RSS fetch + filter + batch summarize"""
import json, os, hashlib, time
from datetime import datetime, timedelta
from pathlib import Path

# Simple RSS parser (no external deps)
def parse_rss(url):
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            content = r.read().decode('utf-8', errors='ignore')
        
        items = []
        for item in content.split('<item>')[1:]:
            title = extract_tag(item, '<title>', '</title>')
            link = extract_tag(item, '<link>', '</link>')
            pubdate = extract_tag(item, '<pubDate>', '</pubDate>')
            if title and link:
                items.append({'title': title.strip(), 'url': link.strip(), 'pubDate': pubdate})
        return items[:50]  # Limit per source
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def extract_tag(text, start, end):
    try:
        s = text.index(start) + len(start)
        e = text.index(end, s)
        return text[s:e]
    except: return None

# Sources (RSS feeds - all free)
SOURCES = [
    'http://feeds.feedburner.com/TechCrunch/',
    'https://www.theverge.com/rss/index.xml',
    'https://arstechnica.com/feed/',
    'https://hnrss.org/frontpage',  # Hacker News
    'https://www.wired.com/feed/rss',
]

# Keywords for filtering
KEYWORDS = ['ai', 'machine learning', 'llm', 'security', 'breach', 'hack', 
            'cloud', 'devops', 'kubernetes', 'docker', 'startup', 'funding',
            'launch', 'apple', 'google', 'microsoft', 'tesla', 'spacex']

def filter_stories(items):
    filtered = []
    seen = set()
    for item in items:
        title_lower = item['title'].lower()
        if any(kw in title_lower for kw in KEYWORDS):
            # Dedupe by title hash
            h = hashlib.md5(item['title'].encode()).hexdigest()[:8]
            if h not in seen:
                seen.add(h)
                filtered.append(item)
    return filtered

def categorize(story):
    title = story['title'].lower()
    if any(x in title for x in ['ai', 'ml', 'llm', 'model', 'neural']): return 'AI/ML'
    if any(x in title for x in ['security', 'breach', 'hack', 'vulnerability']): return 'Security'
    if any(x in title for x in ['cloud', 'devops', 'k8s', 'kubernetes', 'aws', 'azure']): return 'Cloud/DevOps'
    if any(x in title for x in ['startup', 'funding', 'series', 'investment']): return 'Startups'
    if any(x in title for x in ['chip', 'cpu', 'gpu', 'iphone', 'pixel', 'hardware']): return 'Hardware'
    return 'General Tech'

def main():
    print("Fetching RSS feeds...")
    all_items = []
    for src in SOURCES:
        items = parse_rss(src)
        all_items.extend(items)
        print(f"  {src[:40]}... → {len(items)} items")
    
    print(f"\nTotal raw: {len(all_items)} stories")
    
    # Filter
    filtered = filter_stories(all_items)
    print(f"After filter: {len(filtered)} relevant stories")
    
    # Categorize
    categorized = {}
    for story in filtered[:15]:  # Top 15
        cat = categorize(story)
        if cat not in categorized: categorized[cat] = []
        categorized[cat].append({
            'title': story['title'],
            'url': story['url'],
            'summary': 'Summary pending AI generation...'  # Placeholder
        })
    
    # Output
    output = {
        'generatedAt': datetime.utcnow().isoformat() + 'Z',
        'stories': categorized
    }
    
    out_path = Path(__file__).parent / 'digest.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Digest saved to {out_path}")
    print(f"   Categories: {list(categorized.keys())}")
    print(f"   Total stories: {sum(len(v) for v in categorized.values())}")

if __name__ == '__main__':
    main()
