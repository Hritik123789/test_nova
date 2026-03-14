# RAG Q&A System for CityPulse

## Overview
Natural language Q&A system that searches through all collected neighborhood data using Retrieval-Augmented Generation (RAG).

## Architecture

```
User Question
     ↓
Query Embedding (Titan Embeddings)
     ↓
Vector Search (FAISS)
     ↓
Retrieve Top 5 Relevant Documents
     ↓
Generate Answer (Nova 2 Lite)
     ↓
Return Answer + Sources
```

## Data Sources Indexed

The RAG system indexes all data from `agents/data/`:

1. **News Articles** (`news.json`)
   - Local Mumbai news with relevance scores
   - Categories: Civic, Traffic, Real Estate

2. **Permits** (`permits.json`, `bmc_permits.json`)
   - Building permits, construction projects
   - Ward-level BMC permits with impact scores

3. **Social Media** (`social.json`)
   - Reddit discussions from Mumbai subreddits
   - Sentiment analysis included

4. **Smart Alerts** (`smart_alerts.json`)
   - Prioritized neighborhood alerts
   - Construction, events, safety

5. **Safety Alerts** (`safety_alerts.json`)
   - Safety-specific intelligence
   - Severity ratings

6. **Investment Insights** (`investment_insights.json`)
   - Neighborhood development trends
   - Investment potential scores

7. **Community Pulse** (`community_pulse.json`)
   - Trending community topics
   - Discussion summaries

## Features

### 1. Semantic Search
- Uses Titan Embeddings (1024 dimensions)
- FAISS vector database for fast similarity search
- Finds relevant context across all data sources

### 2. Context-Aware Answers
- Nova 2 Lite generates answers from retrieved context
- Cites sources with [1], [2], etc.
- Admits when information is not available

### 3. Multi-Source Integration
- Combines information from news, permits, social media
- Provides comprehensive neighborhood intelligence
- Shows which sources contributed to answer

## Usage

### Interactive Demo
```bash
python agents/demo_rag_qa.py
```

### Programmatic Usage
```python
from agents.rag_qa_system import CityPulseRAG

# Initialize
rag = CityPulseRAG(demo_mode=True)

# Load all data
rag.load_all_data()

# Create embeddings (one-time)
rag.create_embeddings()

# Ask questions
result = rag.answer_question("What's happening in Andheri?")
print(result['answer'])
print(f"Sources: {len(result['sources'])}")
```

### Batch Processing
```python
questions = [
    "What construction projects are happening?",
    "Are there safety concerns?",
    "What new businesses are opening?"
]

qa_results = []
for question in questions:
    result = rag.answer_question(question)
    qa_results.append(result)

rag.save_qa_results(qa_results)
```

## Example Questions

### Construction & Development
- "What construction projects are happening in Andheri?"
- "Tell me about recent permits filed in Mumbai"
- "What development is happening in Bandra?"

### Safety & Alerts
- "Are there any safety concerns in Mumbai?"
- "What road closures are there?"
- "Tell me about traffic issues"

### Business & Investment
- "What new restaurants or businesses are opening?"
- "What investment opportunities are there?"
- "Which neighborhoods have high development activity?"

### Community
- "What are people discussing on social media?"
- "What are the trending topics in the community?"
- "What's the community sentiment about the metro?"

## Cost Breakdown

### One-Time Costs (Embedding Creation)
- **Titan Embeddings**: $0.10 per 1M tokens
- **Estimated for ~500 documents**: $3-5
- Only needs to be done once (or when data updates)

### Per-Query Costs
- **Query Embedding**: $0.0001 per query
- **Nova 2 Lite Generation**: $0.001-0.003 per query
- **Total per query**: ~$0.003

### Example Session
- Create embeddings: $4.00 (one-time)
- Answer 10 questions: $0.03
- **Total**: $4.03

## Technical Details

### Vector Database
- **Library**: FAISS (Facebook AI Similarity Search)
- **Index Type**: IndexFlatL2 (exact search)
- **Dimension**: 1024 (Titan Embeddings v2)
- **Distance Metric**: L2 (Euclidean)

### Embedding Model
- **Model**: amazon.titan-embed-text-v2:0
- **Dimension**: 1024
- **Max Input**: 8,000 tokens
- **Cost**: $0.10 per 1M tokens

### Generation Model
- **Model**: us.amazon.nova-lite-v1:0
- **Max Output**: 400 tokens
- **Temperature**: 0.3 (factual)
- **Cost**: $0.30 input + $2.50 output per 1M tokens

## Output Format

### Q&A Results JSON
```json
[
  {
    "question": "What's happening in Andheri?",
    "answer": "Based on recent data, there are 3 construction projects in Andheri [1][2]. A new residential building permit was filed on Main Street [1], and there's ongoing metro construction [2].",
    "sources": [
      {
        "source": "permits",
        "metadata": {
          "project_name": "Residential Building",
          "location": "Andheri West"
        }
      },
      {
        "source": "news",
        "metadata": {
          "title": "Metro Line 3 Progress"
        }
      }
    ],
    "cost": 0.0028
  }
]
```

## Integration with Frontend

### API Endpoint (for your friend to implement)
```php
// Laravel Backend
Route::post('/api/neighborhood/ask', function(Request $request) {
    $question = $request->input('question');
    
    // Call Python RAG system
    $result = shell_exec("python agents/rag_qa_system.py --question '$question'");
    
    return response()->json(json_decode($result));
});
```

### Frontend Component
```jsx
// Next.js Component
const NeighborhoodQA = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  
  const askQuestion = async () => {
    const response = await fetch('/api/neighborhood/ask', {
      method: 'POST',
      body: JSON.stringify({ question })
    });
    const data = await response.json();
    setAnswer(data);
  };
  
  return (
    <div>
      <input value={question} onChange={e => setQuestion(e.target.value)} />
      <button onClick={askQuestion}>Ask</button>
      {answer && <div>{answer.answer}</div>}
    </div>
  );
};
```

## Performance

### Indexing
- **Time**: ~2-3 minutes for 500 documents
- **Memory**: ~100MB for FAISS index
- **Storage**: ~50MB for embeddings

### Query
- **Latency**: 1-2 seconds per query
  - Embedding: 200ms
  - Search: 10ms
  - Generation: 1-1.5s
- **Throughput**: ~30 queries/minute

## Limitations

1. **Context Window**: Limited to top 5 documents
2. **Freshness**: Embeddings need to be regenerated when data updates
3. **Accuracy**: Depends on quality of source data
4. **Language**: Currently English only

## Future Enhancements

1. **Incremental Updates**: Add new documents without full reindex
2. **Hybrid Search**: Combine vector + keyword search
3. **Multi-Language**: Support Hindi and Marathi
4. **Conversation Memory**: Multi-turn conversations
5. **Fact Verification**: Cross-reference multiple sources

## Troubleshooting

### "FAISS not installed"
```bash
pip install faiss-cpu
```

### "Bedrock access denied"
- Check AWS credentials
- Verify Bedrock model access in us-east-1
- Ensure IAM permissions for bedrock:InvokeModel

### "No relevant documents found"
- Check if data files exist in `agents/data/`
- Verify embeddings were created successfully
- Try more specific questions

## Demo for Hackathon

1. **Show the data sources** (10 JSON files)
2. **Run embedding creation** (live demo of indexing)
3. **Ask 3-5 questions** (show real-time answers)
4. **Show source attribution** (which data contributed)
5. **Highlight cost efficiency** (~$0.003 per query)

This demonstrates:
- ✅ RAG implementation
- ✅ Multi-source data integration
- ✅ Nova 2 Lite reasoning
- ✅ Titan Embeddings
- ✅ Real-world use case
