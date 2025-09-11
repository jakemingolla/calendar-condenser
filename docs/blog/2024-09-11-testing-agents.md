# Testing Agents

Author: [@jakemingolla](https://github.com/jakemingolla)

Published: 2024-09-11

## Overview

This document describes my approach to integration testing agents using _real_ LLM responses to validate correct behavior.

## Background

I think most people consider testing and LLMs to be relatively incompatible with each other - and they aren't 100% wrong. With agents, I think there are three different types of tests integral to their success:

> [!NOTE]
> I know some people start to boil when you use particular words like 'integration' and 'unit'
> when it comes to testing if you deviate slightly from what they expect. Feel free to skip this
> section and just focus on happy thoughts of 'automated testing' if it's too much :)

1. Unit tests

These are functional tests of tools exposed to the agent. These are generally easiest to write and have fixed inputs and outputs.

2. Integration tests

These are tests of the agent as whole, validating expected output given fixed inputs. These are what I'll be discussing in this document.

3. Qualitative tests

These are tests of the agent's behavior and 'how correct' it is. These are a higher level of testing and need to be based on a foundation of unit and integration tests. I should write a separate blog post about this topic at some point - at a high level, this is 'grading' the responses of the agent.

Now, let's focus on integration tests.

## Example Scenario

Our agent is a mechanic that can help with car repairs. I'm going to skip some of the
[LangGraph](https://langchain-ai.github.io/langgraph/) boilerplate and focus on some
higher-level concepts - this code won't run as-is but should give you an idea of what we're
trying to accomplish.

Our mechanic can fix cars, but should only fix what's broken. Given a particular car,
it should make any fixes and return a detailed report of the repairs made.

```python

class Car(BaseModel):
    make: str
    model: str
    year: int

    broken_tire: bool
    broken_transmission: bool

class UnnecessaryFix(Exception):
    pass

@tool
def fix_tire(car: Car) -> int:
    """
    Fix a broken tire.
    Returns the cost of the repair.
    If the tire is not broken, raise an UnnecessaryFix exception.
    """
    if car.broken_tire:
        car.broken_tire = False
        return 100
    else:
        raise UnnecessaryFix

@tool
def fix_transmission(car: Car) -> int:
    """
    Fix a broken transmission.
    Returns the cost of the repair.
    If the transmission is not broken, raise an UnnecessaryFix exception.
    """
    if car.broken_transmission:
        car.broken_transmission = False
        return 300
    else:
        raise UnnecessaryFix

class CustomerReport(BaseModel):
    total_bill: int = Field(description="The total cost of the repairs.")
    fixes: list[Literal["tire", "transmission"]] = Field(description="The list of repairs made.")
    detailed_report: str = Field(description="A detailed report of the repairs made.")

model = ChatOpenAI(model="...")
agent = create_react_agent(
    model=model,
    tools=[fix_tire, fix_transmission],
    prompt="You are a mechanic that can help with car repairs. You should only fix what's broken.",
    response_format=CustomerReport,
)

def fix_car(car: Car) -> CustomerReport:
    return agent.invoke({"input": car})["structured_output"]
```

## Testing

We can now test our agent by passing in a car with a broken tire and a broken transmission
and validate the output. Here's an example using pytest (and `pytest-asyncio` plugin).

```python
@pytest.fixture
def clanker() -> Car:
    return Car(
        make="Chevrolet", # It's always the Chevys...
        model="Vega",
        year=1971,
        broken_tire=True,
        broken_transmission=True,
    )

@pytest.fixture
def perfect_car() -> Car:
    return Car(
        make="Toyota",
        model="Camry",
        year=2024,
        broken_tire=False,
        broken_transmission=False,
    )

@pytest.mark.asyncio
async def test_fix_clanker(clanker: Car):
    report = await fix_car(clanker)
    assert report.total_bill == 400
    assert report.fixes == ["tire", "transmission"]

@pytest.mark.asyncio
async def test_fix_perfect_car(perfect_car: Car):
    report = await fix_car(perfect_car)
    assert report.total_bill == 0
    assert report.fixes == []
```

We can now be confident in our agent's behavior given a particular input. You can now be confident
of its correctness when integrated into a multi-agent system or graph.

## Note: Response Correctness

You'll notice in the above example, we didn't check the `detailed_report` field. It's _very_
difficult to consistently validate string responses from the LLM without making a flaky test.

I've occasionally had success using keyword-based searching to see if the response contains
words you'd 100% expect to see in the response. This can be useful for basic checks,
but it can sometimes result in failures if the LLM generates an unexpected response.

```python
assert "tire" in report.detailed_report.lower() # Always make sure to use case-insensitive searching
assert "transmission" in report.detailed_report.lower()
```

If the `detailed_report` field is important to you, consider running a more comprehensive
'grading' test suite which uses a separate LLM to grade the responses. This is the next
step in terms of delivering quality results to stakeholders of your application.

## Note: Flaky Tests

Even the above tests can be flaky sometimes - if the LLM is having a bad day, you may
generate `UnnecessaryFix` exceptions. Depending on your use case and its significance, I'd
recommend one of the following approaches:

1. Use a tool like `pytest-retry` to automatically retry the test one or more times.
   Only use this approach if failures of your test are _relatively_ insignificant
   in the scope of your application, or if some other form of error handling is in place.

2. Adjust the underlying tool the agent calls to avoid making `UnnecessaryFix` in the
   first place - the above is a contrived example and shows how giving the reins over
   to the LLM can result in unexpected behavior.

3. Tune your prompt to try and avoid bad behavior. This is a never-ending effort.

## Conclusion

This is a simple approach to integration testing agents, but it's a powerful one. When developing
a multi-agent system, it's important to isolate each individual agent's behavior and ensure it's
functioning correctly. Otherwise, you may end up with a spaghetti of interconnected agents which
may be hard to reason about when failures occur.


