const DIGEST_URL = 'digest.json';
const CATEGORY_EMOJIS = {
  'AI/ML': '🤖',
  'Security': '🔒',
  'Cloud/DevOps': '☁️',
  'Startups': '🚀',
  'Hardware': '💻',
  'General Tech': '📱'
};

async function loadDigest() {
  const container = document.getElementById('digest');
  const lastUpdated = document.getElementById('lastUpdated');
  
  try {
    const res = await fetch(DIGEST_URL + '?t=' + Date.now());
    if (!res.ok) throw new Error('Failed to load');
    const data = await res.json();
    
    lastUpdated.textContent = `Last updated: ${new Date(data.generatedAt).toLocaleString('en-US', { 
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
    })}`;
    
    container.innerHTML = '';
    
    for (const [category, stories] of Object.entries(data.stories)) {
      const catEl = document.createElement('div');
      catEl.className = 'category';
      
      const title = document.createElement('div');
      title.className = 'category-title';
      title.textContent = `${CATEGORY_EMOJIS[category] || '📌'} ${category}`;
      catEl.appendChild(title);
      
      stories.forEach(story => {
        const storyEl = document.createElement('div');
        storyEl.className = 'story';
        
        const highlighted = highlightKeywords(story.title);
        storyEl.innerHTML = `
          <div class="story-title">${highlighted}</div>
          <div class="story-summary">${story.summary}</div>
          <a href="${story.url}" target="_blank" rel="noopener" class="story-link">Read more →</a>
        `;
        catEl.appendChild(storyEl);
      });
      
      container.appendChild(catEl);
    }
    
  } catch (err) {
    container.innerHTML = `<div class="error">Failed to load digest. Pull to refresh.</div>`;
    console.error(err);
  }
}

function highlightKeywords(text) {
  // Bold important tech terms
  const keywords = ['AI', 'LLM', 'model', 'security', 'breach', 'launch', 'startup', '$', 'billion', 'million', 'new', 'first', 'breakthrough'];
  let result = text;
  keywords.forEach(kw => {
    const regex = new RegExp(`\\b(${kw})\\b`, 'gi');
    result = result.replace(regex, '<strong>$1</strong>');
  });
  return result;
}

// Load on start
loadDigest();
