# Orrin SDK v0.0.4
The Orrrin SDK v0.0.4 is the first revolution of the Orrin SDK, and brings forth a simple Python decorator for developers creating small-scale apps to be deployed on the Orrin platform.

Orrin SDK is the bridge behind backend action and UI manipulation.

## Why Python/Node.js mix?
Python is used for simplicity on the backend side of things and compatibility, and node.js is utilized for the frontend as it enables flexibility, and also compatibility.

Orrin Web is also based in node.js, so sustaining that stack for the web platform just simply makes sense.

## Orrin SDK actions
The current version offers only one decorator: `action`.
You call this on top of any given function that will be used in your front end code to perform an activity and manipulate the UI.

Example:
```python
from orrinsdk import action

@action('say_hi')
def say_hi():
    return {'message': 'Hello, world!'}
```

And now, in your UI, if you utilize this action (using a node.js based SDK) you can utilize the result from this function to determine how to manipulate your UI.

_New versions of Orrin SDK are in the working_