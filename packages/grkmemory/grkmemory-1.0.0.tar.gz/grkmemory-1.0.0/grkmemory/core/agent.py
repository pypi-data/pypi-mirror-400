"""
Knowledge Agent for GRKMemory.

This module provides the AI agent for processing and structuring conversations.
"""

import json
import uuid
import datetime
from typing import Dict, List, Optional

from agents import Agent, Runner


# Default agent instructions (Berkano protocol)
DEFAULT_INSTRUCTIONS = """
You are the GRKMemory Knowledge Assistant, an intelligent assistant specialized in retrieving and structuring knowledge from conversations.

YOUR FUNCTIONS:

1. ANSWER QUESTIONS: Use knowledge from previous conversations to answer user questions
2. PROCESS SESSIONS: When requested, analyze complete sessions and extract structured information

FOR USER QUESTIONS:
- Use the provided background context to answer based on previous conversations
- Be helpful and informative
- Cite specific information when relevant
- If you don't know something, be honest about it

FOR SESSION PROCESSING:
- Analyze the entire session conversation
- Extract structured information in JSON format

OUTPUT STRUCTURE (JSON):

{
  "language": "pt-BR",
  "summary": "conversation summary in up to 200 characters",
  "params": {},
  "tags": ["tag1", "tag2", "tag3"],
  "entities": ["entity1", "entity2"],
  "key_points": ["important point 1", "important point 2"],
  "participants": ["participant1", "participant2"],
  "sentiment": "positive/neutral/negative",
  "confidence": 0.0,
  "sensitivity": "low",
  "notes": "observations about the conversation"
}

INSTRUCTIONS:

1. ANALYZE the entire session conversation
2. CREATE a concise summary of the conversation
3. IDENTIFY the main topics discussed
4. EXTRACT the key points mentioned
5. LIST the participants in the conversation
6. EVALUATE the overall sentiment (positive/neutral/negative)
7. ADD relevant observations
8. IDENTIFY mentioned entities (people, places, products, etc.)
9. EVALUATE the analysis confidence (0.0 to 1.0)
10. DEFINE the sensitivity level (low/medium/high)
11. RETURN ONLY the structured JSON
12. IMPORTANT: All tags should be in LOWERCASE and WITHOUT ACCENTS for easier searching

ALWAYS PROCESS THE COMPLETE SESSION AND RETURN THE STRUCTURED JSON.
"""


class KnowledgeAgent:
    """
    AI agent for processing and analyzing conversations.
    
    Uses OpenAI's Agents framework to analyze conversations and extract
    structured information following the Berkano protocol.
    
    Example:
        agent = KnowledgeAgent(model="gpt-4o")
        
        # Process a conversation
        result = agent.process_conversation([
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ])
        
        # Chat with context
        response = agent.chat("What did we discuss?", context="Previous discussion about AI")
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        name: str = "GRKMemory Knowledge Assistant",
        instructions: Optional[str] = None
    ):
        """
        Initialize the knowledge agent.
        
        Args:
            model: OpenAI model to use.
            name: Name for the agent.
            instructions: Custom instructions (uses default if not provided).
        """
        self.model = model
        self.name = name
        self.instructions = instructions or DEFAULT_INSTRUCTIONS
        
        self._agent = Agent(
            name=name,
            model=model,
            instructions=self.instructions
        )
    
    @property
    def agent(self) -> Agent:
        """Get the underlying OpenAI Agent."""
        return self._agent
    
    def chat(self, message: str, context: Optional[str] = None) -> str:
        """
        Send a message and get a response.
        
        Args:
            message: User message.
            context: Optional background context to include.
        
        Returns:
            Agent response text.
        """
        prompt = message
        if context:
            prompt = f"{message}\n\n{context}"
        
        result = Runner.run_sync(self._agent, prompt)
        return result.final_output or ""
    
    def chat_with_history(self, messages: List[Dict]) -> str:
        """
        Continue a conversation with message history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
        
        Returns:
            Agent response text.
        """
        result = Runner.run_sync(self._agent, messages)
        return result.final_output or ""
    
    def process_conversation(self, messages: List[Dict]) -> Optional[Dict]:
        """
        Process a conversation and extract structured information.
        
        Args:
            messages: List of conversation messages.
        
        Returns:
            Dictionary with structured conversation data, or None if failed.
        """
        if not messages:
            return None
        
        try:
            # Format conversation
            conversation_text = ""
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    conversation_text += f"User: {content}\n"
                elif role == "assistant":
                    conversation_text += f"Assistant: {content}\n"
            
            prompt = f"""
Process the following complete conversation session and return the structured JSON following the Berkano protocol:

COMPLETE SESSION:
{conversation_text}

Return ONLY the structured JSON according to the format defined in the instructions.
"""
            
            result = Runner.run_sync(self._agent, prompt)
            response_text = result.final_output or ""
            
            # Extract JSON from response
            if "{" not in response_text or "}" not in response_text:
                return None
            
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start == -1 or end <= start:
                return None
            
            data = json.loads(response_text[start:end])
            if not isinstance(data, dict):
                return None
            
            # Add defaults
            data.setdefault("language", "pt-BR")
            data.setdefault("summary", "")
            data.setdefault("params", {})
            data.setdefault("tags", [])
            data.setdefault("entities", [])
            data.setdefault("key_points", [])
            data.setdefault("participants", [])
            data.setdefault("sentiment", "neutral")
            data.setdefault("confidence", 0.0)
            data.setdefault("sensitivity", "low")
            data.setdefault("notes", "")
            
            # Add conversation
            data["conversation"] = messages
            
            # Add metadata
            if "id" not in data:
                data["id"] = str(uuid.uuid4())
            
            source = data.get("source") or {}
            source.setdefault("type", "session")
            source.setdefault("session_id", str(uuid.uuid4()))
            data["source"] = source
            
            data["created_at"] = data.get("created_at") or datetime.datetime.now().isoformat()
            
            if "embedding" not in data or not isinstance(data["embedding"], list):
                data["embedding"] = []
            
            return data
            
        except Exception as e:
            print(f"⚠️ Error processing conversation: {e}")
            return None
