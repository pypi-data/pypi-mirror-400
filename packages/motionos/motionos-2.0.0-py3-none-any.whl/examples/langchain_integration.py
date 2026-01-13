"""
LangChain integration example for MotionOS Python SDK.

This demonstrates how to integrate MotionOS with LangChain.
"""

from typing import Dict, Any
from motionos import MotionOS


class MotionOSMemory:
    """LangChain-compatible memory store using MotionOS."""

    def __init__(self, client: MotionOS, agent_id: str = "langchain-agent"):
        self.client = client
        self.agent_id = agent_id

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]):
        """Save conversation context to MotionOS."""
        user_input = inputs.get("input", "")
        assistant_output = outputs.get("output", "")

        # Store conversation turn
        self.client.ingest(
            {
                "raw_text": f"User: {user_input}\nAssistant: {assistant_output}",
                "agent_id": self.agent_id,
                "tags": ["conversation", "langchain"],
                "type": "conversation",
            }
        )

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """Load relevant context from MotionOS."""
        query = inputs.get("input", "")

        # Retrieve relevant memories
        result = self.client.retrieve(
            {
                "query": query,
                "agent_id": self.agent_id,
                "mode": "inject",
                "limit": 5,
            }
        )

        return {"history": result.context}

    def clear(self):
        """Clear memory (not implemented - would require delete API)."""
        pass


# Example usage with LangChain
"""
from langchain import ConversationChain
from langchain.llms import OpenAI
from motionos import MotionOS

# Create MotionOS client
motionos_client = MotionOS(
    api_key="sb_secret_xxx",
    project_id="proj-123"
)

# Create memory
memory = MotionOSMemory(motionos_client)

# Create chain
llm = OpenAI(temperature=0)
chain = ConversationChain(llm=llm, memory=memory, verbose=True)

# Use chain
response = chain.run("What do I like?")
print(response)
"""

