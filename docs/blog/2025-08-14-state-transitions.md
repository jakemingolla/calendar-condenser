# State Transitions

Author: [@jakemingolla](https://github.com/jakemingolla)

Published: 2025-08-14

## Overview

Rather than maintaining a single monolithic state class, we can use inheritance to create a hierarchy of state classes. As the [LangGraph][langgraph] graph progresses we can track meaningful changes applied on a per-node basis to lessen developer's mental burden and facilitate UI tracking.

## Background

In previous projects I've worked on (and lots of online documentation surrounding LangGraph) you'll see all operations in a graph applied to a single state class:

```python
from pydantic import BaseModel
from langgraph.graph import StateGraph

class State(BaseModel):
    started_at: datetime
    user_id: str
    user_name: str
    user_age: int
    user_timezone: str
    garage: list[Car]
    shopping_cart: list[GroceryStoreItem]

graph = StateGraph(State)
```

In various nodes operating on the state, it sometimes becomes difficult to track:

1. Where a particular property in the state is first set
2. What is the significance of a particular property in the state
3. How does a particular property change over time

In addition, having a single monolithic state class makes it difficult to test a particular node in isolation - you need to define the _entire_ state class in order to test one particular state change.

## An Improvement

Luckily, LangGraphs [documentation on multiple schemas for state](https://langchain-ai.github.io/langgraph/concepts/low_level/#multiple-schemas) is a good starting point for us. Take some time to read through the example and important takeaways they provide.

For the example above, we could create a hierarchy of state classes, each inheriting from the previous state class in order of node transitions (like a [hermit crab trading shells](https://www.youtube.com/watch?v=f1dnocPQXDQ)):

```python

from pydantic import BaseModel

class InitialState(BaseModel):
    started_at: datetime

class StateWithUserInformation(InitialState):
    user_id: str
    user_name: str
    user_age: int
    user_timezone: str

class StateWithGarage(StateWithUserInformation):
    garage: list[Car]

class StateWithShoppingCart(StateWithGarage):
    shopping_cart: list[GroceryStoreItem]

graph = StateGraph(InitialState)
```

The names of the state classes are chosen to reflect the order of node transitions. At any arbitrary location in your code a developer can understand the significance of how the graph has progressed up until that point.

There are a couple of improvements we can make to the above approach:

### 1. Serialize the type of the state as a `@property`

In our `InitialState` class (the root of our inheritance) we can add a [`@property`][property] to return the name of the type of the state. This is useful for tracking changes to the state from a front-end or some other consumer of the state who has access to atomic updates to the state but may not be able to track the invocations of each node.

```python
from pydantic import BaseModel, computed_field

class InitialState(BaseModel):
    started_at: datetime
    type: str = ""

    def model_post_init(self, __context: Any, /) -> None:  # noqa: ANN401
        """Set the type field to the actual class name after initialization."""
        object.__setattr__(self, "type", self.__class__.__name__)

class StateWithUserInformation(InitialState):
    ...

my_state = StateWithUserInformation(...)

print(my_state.model_dump_json())
```

The output of the `model_dump_json` method now includes the type of the state:

```json
{
    "type": "StateWithUserInformation",
    "started_at": "2025-08-14T10:00:00",
    "user_id": "123",
    "user_name": "John Doe",
    "user_age": 42,
    "user_timezone": "America/New_York"
}
```

The `type` field will constantly update as the state progresses through the graph. You do not need to re-define the `type` property for each inheriting state class.

### 2. Instantiating subsequent states

One of the initial problems we're trying to solve is we want each state class to be as isolated as possible from other state class definitions. Right now we have a problem - if you add a property to a state class you need to update all subsequent state instantiations to include the new property:

```python
from pydantic import BaseModel

class StateWithUserInformation(BaseModel):
    user_id: str
    user_name: str
    user_age: int
    user_timezone: str
    user_birthday: datetime # <-- New property!

class StateWithGarage(StateWithUserInformation):
    ...

user_state = StateWithUserInformation(..., user_birthday=datetime(1970, 1, 1))
my_garage = [Car(name="Honda Civic"), Car(name="Toyota Camry")]
garage_state = StateWithGarage(
    garage=my_garage,
    user_birthday=datetime(1970, 1, 1),
    ... # All other `user_` properties also need to be included here :(
)

```

Even though we only made updates to the `StateWithUserInformation` class, we still need to modify the instantiations of the `StateWithGarage` objects in a totally different part of the code.

We can solve this by adding a `from_previous_state` method to the parent `InitialState` class which will be propagated to all subsequent state classes:

```python
from pydantic import BaseModel

class InitialState(BaseModel):
    ...

    @classmethod
    def from_previous_state(cls: type[Self], previous_state: BaseModel, **kwargs: Any) -> Self:
        return cls.model_validate(dict(previous_state, **kwargs))

    # Because the `from_previous_state` method has `kwargs` typed as `Any`, we can't check for extra
    # fields during type checking. This makes sure we don't leave behind any extra fields (done at runtime).
    model_config = ConfigDict(extra="forbid")

class StateWithUserInformation(InitialState):
    ...

class StateWithGarage(StateWithUserInformation):
    ...

class StateWithShoppingCart(StateWithGarage):
    ...

initial_state = InitialState(started_at=datetime(2025, 1, 1))
user_state = StateWithUserInformation.from_previous_state(
    initial_state,
    user_id="123",
    user_name="John Doe",
    user_age=42,
    user_timezone="America/New_York",
)
garage_state = StateWithGarage.from_previous_state(
    user_state,
    garage=[Car(name="Honda Civic"), Car(name="Toyota Camry")],
)
shopping_cart_state = StateWithShoppingCart.from_previous_state(
    garage_state,
    shopping_cart=[
        GroceryStoreItem(name="Milk", price=3.99),
        GroceryStoreItem(name="Bread", price=2.99),
    ],
)
```

This is great! We can now isolate _only_ the changes each state transition makes to the state class when we're instantiating the state in our nodes. It requires a little bit of 'magic' via [`pydantic`][pydantic] to do the copy (and isn't a very performant operation, but we didn't get into LangGraph to make rocketships) but I think in this case it's a worthwhile trade-off to provide clarity to the developer each step of the way.

## Conclusion

I've found this approach to be a great way to make my state classes more readable and testable.

If you have any feedback or suggestions, please let me know!




<!-- References -->
[langgraph]: https://langchain-ai.github.io/langgraph/
[property]: https://docs.python.org/3/library/functions.html#property
[pydantic]: https://docs.pydantic.dev/latest/
