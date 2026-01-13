"""
DriftAdvisor - AI Powered Drift Analysis & Recommendations
This module provides integration with LLMs (local or cloud) to provide 
actionable insights based on drift analysis results.
"""

import requests
import json
from typing import Dict, Optional, List
import pandas as pd

class DriftAdvisor:
    """
    Connects drift results with LLMs to generate recommendations.
    
    Supports OpenAI-compatible APIs (Ollama, vLLM, LM Studio, OpenAI, etc.)
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:11434/v1", 
        api_key: str = "ollama",
        model: str = "qwen2.5",
        timeout: int = 120
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def _prepare_context(self, results: Dict[str, pd.DataFrame]) -> str:
        """Summarizes drift results into a compact string for LLM context."""
        context = []
        
        # 1. Summary Header
        if 'data_drift' in results:
            df = results['data_drift']
            total = len(df)
            drifted_mask = df['Drift Detected'] == True
            drifted = df[drifted_mask]['Column'].unique().tolist()
            context.append(f"DATA DRIFT: {len(drifted)} out of {total} features drifted. Affected features: {', '.join(drifted) if drifted else 'None'}")

        # 2. Key Statistical Details
        if 'data_drift' in results:
            drifted_details = results['data_drift'][results['data_drift']['Drift Detected'] == True]
            if not drifted_details.empty:
                context.append("\nTop Drift Details:")
                for _, row in drifted_details.head(10).iterrows():
                    context.append(f"- {row['Column']}: {row['Test']} (p={row['P-Value']:.4f})")

        # 3. Concept Drift
        if 'concept_drift' in results:
            df = results['concept_drift']
            drifted_concepts = df[df['Drift_Detected'] == True]['Feature'].unique().tolist()
            if drifted_concepts:
                context.append(f"\nCONCEPT DRIFT: Relationship between features and target has changed for: {', '.join(drifted_concepts)}")

        return "\n".join(context)

    def get_advice(self, results: Dict[str, pd.DataFrame], language: str = 'en', custom_prompt: str = None) -> str:
        """
        Sends summarized results to LLM and returns actionable advice.
        """
        context = self._prepare_context(results)
        
        system_prompt = (
            "You are an expert Data Scientist and ML Reliability Engineer. "
            "Your task is to analyze model drift results and provide a technical roadmap to fix them."
        )
        
        lang_target = "Turkish" if language == 'tr' else "English"
        
        user_prompt = f"""
I have detected drift in my machine learning project. Here is the summary of the analysis results:

---
{context}
---

Please provide your technical response in the following structure:

### 1. Understanding of the Current Situation
Briefly summarize the provided drift results as you understand them and explain their potential impact on the model's reliability.

### 2. Actionable Recommendations & Roadmap
- **Root Cause Analysis**: Provide technical hypotheses on why this drift might be occurring.
- **Data & Preprocessing**: Practical steps for data cleaning, normalization, or distribution adjustment.
- **Retraining Strategy**: Recommendations on retraining (e.g., sliding window, cumulative, or subset-based).
- **Feature Engineering**: Suggestions to improve model resilience and stability.

IMPORTANT: Please respond only in {lang_target} language. Keep it technical, professional, and practical. 
DO NOT provide any Python code snippets. Focus entirely on methodology and strategic recommendations.
"""
        if custom_prompt:
            user_prompt = f"{custom_prompt}\n\nContext:\n{context}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error connecting to LLM: {str(e)}\n\n(Make sure your LLM provider is running at {self.base_url} and model '{self.model}' is downloaded.)"
