# Orrin SDK v0.0.6
The Orrrin SDK v0.0.6 is the first revolution of the Orrin SDK, and brings forth a simple Python decorator for developers creating small-scale apps to be deployed on the Orrin platform.

Orrin SDK is the bridge behind backend action and UI manipulation.

## Why Python/Node.js mix?
Python is used for simplicity on the backend side of things and compatibility, and node.js is utilized for the frontend as it enables flexibility, and also compatibility.

Orrin Web is also based in node.js, so sustaining that stack for the web platform just simply makes sense.

## Orrin SDK actions
The current version offers only one decorator: `action`.
You call this on top of any given function that will be used in your front end code to perform an activity and manipulate the UI.

Example:
```python
from orrinsdk import OrrinSDK

orrin_sdk = OrrinSDK(developer_api_key='<your_developer_api_key>')

@orrin_sdk.action('say_hi')
def say_hi():
    return {'message': 'Hello, world!'}
```

And now, in your UI, if you utilize this action (using a node.js based SDK) you can utilize the result from this function to determine how to manipulate your UI.

## Extra metadata
There will eventually be a elaborate developer platform for you to have direct access to all sorts of data regarding the apps you release and maintain.

With that, you might need to have extra metadata for actions in your backend, especially if your backend grows. (remember to keep your apps small scale; Orrin is not a platform for entire Instagram clones.)

You can add additional metadata about actions like so:
```python
from orrinsdk import OrrinSDK

orrin_sdk = OrrinSDK(developer_api_key='<your_developer_api_key>')

@orrin_sdk.action('say_hi', extra_metadata={'reason': 'This action is just a test. Do not use in production!'})
def say_hi():
    return {'message': 'Hello, World!'}
```

There is no limit or requirement to what is in `extra_metadata` dictionary. Have whatever you need to ensure you understand that action.

## One last thing!
Ensure you **run your script**. By running your script, you effectively register all actions and store the entirety of your backend code.

If you have no functions effectively decorated with `action`, your entire codebase will be _"dead"_ (have no applicable usability on the Orrin platform)

_New versions of Orrin SDK are in the working_