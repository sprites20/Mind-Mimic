import asyncio

class AsyncNode:
    def __init__(self, name=None, inputs = None, targets=None, function = None):
        self.name = name
        self.trigger_event = asyncio.Event()
        self.targets = targets or []  # Ensure targets is initialized as a list
        self.function = function
        self.inputs_from = inputs
        self.outputs = {}
        self.inputs = inputs
        
    async def run_when_triggered(self):
        #print(f"{self.name}: Waiting for trigger...")
        #await self.trigger_event.wait()  # Wait for the trigger event
        print(f"{self.name}: Running function...")
        # Call your function here
        await asyncio.sleep(1)  # Simulate some async operation
        
        result = self.function(self.inputs)
        print(f"{self.name}: Function complete")
        print(f"Result: {result}")
        return self.targets
    
    def take_input(self, input_from, input_to):
        self.inputs_from["input_to"] = input_from
    
    def trigger(self):
        self.trigger_event.set()  # Set the trigger event

async def trigger_node(node):
    targets = await node.run_when_triggered()

def add(inputs):
    results = {}
    a = inputs["a"]
    b = inputs["b"]
    
    results["sum"] = a + b
    return results

def newNode():
    data = {
    
    }
async def main():
    # Example usage
    nodes_data = {}
    
    nodes = {
        "node_1": AsyncNode(name="Node 1", inputs = {"a" : 3, "b" : 5}, function = add, targets=["node_2"]),
        "node_2": AsyncNode(name="Node 2", targets=["node_3"]),
        "node_3": AsyncNode(name="Node 3", targets=["node_4"]),
        "node_4": AsyncNode(name="Node 4")
    }

    # Trigger node_1
    await trigger_node(nodes["node_1"])
    # Run node_1
    

# Run the main coroutine
if __name__ == "__main__":
    asyncio.run(main())
