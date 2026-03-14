# RAG Q&A Integration Guide

## For Your Friend (Laravel + Next.js)

There are **two ways** to integrate the RAG Q&A system:

---

## Option 1: Static Q&A (Easiest - Recommended for Hackathon)

### Step 1: Generate Q&A Data (You do this)
```bash
python agents/rag_qa_system.py
```

This creates: `agents/data/rag_qa_results.json`

### Step 2: Laravel Backend (Your friend does this)
```php
// routes/api.php
Route::get('/neighborhood/qa', function() {
    $qa_data = json_decode(
        file_get_contents(base_path('agents/data/rag_qa_results.json')), 
        true
    );
    return response()->json($qa_data);
});
```

### Step 3: Next.js Frontend
```jsx
// components/NeighborhoodQA.jsx
import { useState, useEffect } from 'react';

export default function NeighborhoodQA() {
  const [qaData, setQaData] = useState([]);
  
  useEffect(() => {
    fetch('/api/neighborhood/qa')
      .then(res => res.json())
      .then(data => setQaData(data));
  }, []);
  
  return (
    <div className="qa-section">
      <h2>Neighborhood Q&A</h2>
      {qaData.map((item, i) => (
        <div key={i} className="qa-item">
          <h3>Q: {item.question}</h3>
          <p>A: {item.answer}</p>
          <small>{item.sources.length} sources</small>
        </div>
      ))}
    </div>
  );
}
```

**Pros:**
- ✅ No Python execution needed
- ✅ Fast (just JSON)
- ✅ No AWS credentials needed
- ✅ Perfect for demo

**Cons:**
- ❌ Fixed questions only
- ❌ Can't ask custom questions

---

## Option 2: Live Q&A API (Advanced)

### Step 1: Create Laravel API Endpoint
```php
// routes/api.php
Route::post('/neighborhood/ask', function(Request $request) {
    $question = $request->input('question');
    
    // Call Python RAG system
    $command = "python " . base_path('agents/rag_api.py') . " " . escapeshellarg($question);
    $output = shell_exec($command);
    
    $result = json_decode($output, true);
    
    return response()->json($result);
});
```

### Step 2: Next.js Chat Interface
```jsx
// components/NeighborhoodChat.jsx
import { useState } from 'react';

export default function NeighborhoodChat() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const askQuestion = async () => {
    setLoading(true);
    const response = await fetch('/api/neighborhood/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await response.json();
    setAnswer(data);
    setLoading(false);
  };
  
  return (
    <div className="chat-interface">
      <h2>Ask About Your Neighborhood</h2>
      <input 
        value={question}
        onChange={e => setQuestion(e.target.value)}
        placeholder="What's happening in Andheri?"
      />
      <button onClick={askQuestion} disabled={loading}>
        {loading ? 'Thinking...' : 'Ask'}
      </button>
      
      {answer && (
        <div className="answer">
          <p>{answer.answer}</p>
          <small>Based on {answer.sources.length} sources</small>
        </div>
      )}
    </div>
  );
}
```

**Pros:**
- ✅ Users can ask any question
- ✅ Interactive chat experience
- ✅ More impressive demo

**Cons:**
- ❌ Requires Python execution
- ❌ Needs AWS credentials on server
- ❌ Slower (~2 seconds per query)

---

## Recommendation for Hackathon

**Use Option 1 (Static Q&A)**

Why?
1. Simpler integration
2. No server-side Python needed
3. Faster response time
4. No AWS credentials needed in production
5. You can pre-generate impressive Q&A examples

### Pre-Generate These Questions:
```bash
# Edit agents/rag_qa_system.py to include these questions:
demo_questions = [
    "What construction projects are happening in Andheri?",
    "Are there any safety concerns in Mumbai?",
    "What new restaurants or businesses are opening?",
    "What are people discussing on social media?",
    "What investment opportunities are there?",
    "Tell me about recent permits filed",
    "What are the trending community topics?",
    "Are there any road closures or traffic issues?",
    "What's the development activity in Bandra?",
    "What's the community sentiment about the metro?"
]
```

Then run:
```bash
python agents/rag_qa_system.py
```

This creates `agents/data/rag_qa_results.json` with all answers.

---

## File Structure for Your Friend

```
agents/
├── data/
│   ├── news.json                  ← Existing (10 files)
│   ├── permits.json
│   ├── bmc_permits.json
│   ├── social.json
│   ├── smart_alerts.json
│   ├── safety_alerts.json
│   ├── investment_insights.json
│   ├── community_pulse.json
│   ├── morning_briefing.json
│   ├── images.json
│   └── rag_qa_results.json        ← NEW! Pre-generated Q&A
```

**Your friend treats `rag_qa_results.json` exactly like the other 10 files.**

---

## Example UI Components

### 1. Q&A List View
```jsx
<div className="qa-list">
  {qaData.map(item => (
    <div className="qa-card">
      <div className="question">{item.question}</div>
      <div className="answer">{item.answer}</div>
      <div className="meta">
        <span>{item.sources.length} sources</span>
        <span>${item.cost.toFixed(4)}</span>
      </div>
    </div>
  ))}
</div>
```

### 2. Search/Filter Q&A
```jsx
const [search, setSearch] = useState('');
const filtered = qaData.filter(item => 
  item.question.toLowerCase().includes(search.toLowerCase()) ||
  item.answer.toLowerCase().includes(search.toLowerCase())
);
```

### 3. Category Tabs
```jsx
const categories = ['Construction', 'Safety', 'Business', 'Community'];
const [activeCategory, setActiveCategory] = useState('All');

const filtered = activeCategory === 'All' 
  ? qaData 
  : qaData.filter(item => item.question.includes(activeCategory));
```

---

## Testing

### Test the API wrapper:
```bash
python agents/rag_api.py "What's happening in Andheri?"
```

Should output JSON:
```json
{
  "question": "What's happening in Andheri?",
  "answer": "Construction projects in Andheri include...",
  "sources": [...],
  "cost": 0.00023
}
```

### Test Laravel endpoint:
```bash
curl -X POST http://localhost:8000/api/neighborhood/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is happening in Andheri?"}'
```

---

## Summary

**For Hackathon Demo:**
1. You run `python agents/rag_qa_system.py` once
2. Generates `agents/data/rag_qa_results.json`
3. Your friend reads it like any other JSON file
4. No Python, no AWS, no complexity!

**The RAG system is just another data source** - like news.json or permits.json, but with Q&A format.
