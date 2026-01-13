from dataclasses import dataclass, asdict
import json

from hero.event import Event, TaskStartEvent

# Test the code
event = TaskStartEvent(workspace="example_workspace")

print(event.name)
print(event.to_json())