
const url = 'http://localhost:8000/a2a/app';

const payload = {
  jsonrpc: '2.0',
  id: 'worker-req-' + Date.now(),
  method: 'message/send',
  params: {
    message: {
      messageId: 'msg-' + Date.now(),
      role: 'user',
      parts: [
        {
          text: 'India'
        }
      ]
    }
  }
};

async function runWorker() {
  console.log('Sending request to AI_Reporter for "India"...');
  console.log('URL:', url);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    
    // Check for JSON-RPC errors
    if (data.error) {
        console.error('Agent Error:', data.error);
        return;
    }

    console.log('--- Agent Response ---');
    
    // A2A message/send returns a Task object in 'result'
    const task = data.result;
    if (task && task.artifacts) {
        task.artifacts.forEach((artifact, i) => {
            const text = artifact.parts.map(p => p.text).join('\n');
            console.log(`Artifact ${i + 1}:\n${text}`);
        });
    } else {
        console.log(JSON.stringify(data, null, 2));
    }
    
    console.log('----------------------');
    
  } catch (error) {
    console.error('Worker failed to connect:', error.message);
    console.log('\nTip: Make sure your agent is running with:');
    console.log('uv run uvicorn app.fast_api_app:app --port 8000');
  }
}

runWorker();
