import unittest
from state import AgentState
from langchain_core.agents import AgentAction, AgentFinish
from typing import cast, Any
 
class TestAgentState(unittest.TestCase):
    def test_state_operations_and_type_behavior(self):
        """Test that AgentState properly handles operations and type behavior."""
        # Create test actions
        action1 = AgentAction(
            tool="search_products",
            tool_input="smartphone",
            log="Searching for smartphones"
        )
         
        action2 = AgentAction(
            tool="get_promotions",
            tool_input="electronics",
            log="Looking for electronics promotions"
        )
         
        # Create initial state
        state1 = AgentState(
            input="I need a new smartphone with good promotions",
            agent_outcome=None,
            intermediate_steps=[]
        )
         
        # Create a second state that builds upon the first
        state2 = AgentState(
            input=state1["input"],
            agent_outcome=action1,
            intermediate_steps=[
                (action1, "Found Samsung Galaxy S21, iPhone 13, Google Pixel 6")
            ]
        )
         
        # Test the append operation on intermediate_steps
        # This tests the Annotated[..., operator.add] behavior
        combined_state = AgentState(
            input=state2["input"],
            agent_outcome=action2,
            intermediate_steps=state2["intermediate_steps"] + [
                (action2, "Found 20% discount on electronics")
            ]
        )
         
        # Verify intermediate steps were properly combined
        self.assertEqual(len(combined_state["intermediate_steps"]), 2)
        self.assertEqual(combined_state["intermediate_steps"][0][0].tool, "search_products")
        self.assertEqual(combined_state["intermediate_steps"][1][0].tool, "get_promotions")
         
        # Test state conversion to AgentFinish
        final_state = AgentState(
            input=combined_state["input"],
            agent_outcome=AgentFinish(
                return_values={"output": "I recommend the Samsung Galaxy S21 which has a 20% discount"},
                log="Finalizing recommendation based on search and promotions"
            ),
            intermediate_steps=combined_state["intermediate_steps"]
        )
         
        # Verify we can check if agent_outcome is an AgentFinish
        self.assertIsInstance(final_state["agent_outcome"], AgentFinish)
         
        # Test extracting the final answer from AgentFinish
        if isinstance(final_state["agent_outcome"], AgentFinish):
            recommendation = final_state["agent_outcome"].return_values["output"]
            self.assertIn("Samsung Galaxy S21", recommendation)
            self.assertIn("20% discount", recommendation)
 
if __name__ == "__main__":
    unittest.main()