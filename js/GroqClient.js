class GroqClient {
  constructor() {
    this.apiKey = '';
    this.model  = 'llama-3.3-70b-versatile';
    this.url    = 'https://api.groq.com/openai/v1/chat/completions';
  }

  setApiKey(key) {
    this.apiKey = key;
  }

  buildSystemPrompt(dataContext) {
    return `You are a data analyst assistant embedded in a Tableau dashboard.
You have been given a dataset to analyze. Answer questions clearly and concisely.
When showing data, use markdown tables where helpful.
Be specific with numbers — cite actual values from the data.
If asked something the data cannot answer, say so clearly.

Here is the dataset you are working with:

${dataContext}`;
  }

  async chat(history, dataContext) {
    const messages = [
      { role: 'system', content: this.buildSystemPrompt(dataContext) },
      ...history.map(m => ({ role: m.role, content: m.content }))
    ];

    const response = await fetch(this.url, {
      method: 'POST',
      headers: {
        'Content-Type':  'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model:       this.model,
        messages,
        max_tokens:  1024,
        temperature: 0.2
      })
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error?.message || `Groq API error ${response.status}`);
    }

    const data = await response.json();
    return data.choices?.[0]?.message?.content || '(no response)';
  }
}