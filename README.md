# calendar-condenser

Ever wish you could just smush your calendar events together to save space? Well, now you can!

<p align="center">
    <i>Turn this...</i>
    <img src="./docs/assets/before-rescheduling.png" alt="Before rescheduling" width="600px" />
    <br />
    <i>Into this...</i>
    <img src="./docs/assets/after-rescheduling.png" alt="After rescheduling" width="600px" />
    <br />
    <i>Without lifting a finger!</i>
    <br />
    <img src="./docs/assets/after-analysis.png" alt="After analysis" width="600px" />
</p>

## Features
m
- Automagically determine the best way to move around your calendar events to save space
- Respects conflicts of any invitees to your events and your preferred working hours
- Integrates directly with your calendar provider like Google Calendar<sup>*</sup>
- Sends messages directly with Slack<sup>*</sup>

<sup>*</sup> These are currently mocked out for development purposes. This project was mostly
about LangGraph, so I skimped on the actual integrations. Instead, I focused on the interfaces
I would expeect to integrate into their 'real' counterparts.

## Setup

See [docs/setup.md](docs/setup.md) for instructions on how to set up the project.
