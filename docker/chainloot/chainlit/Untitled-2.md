1. I want the container reporting stats to be based on some kind of polling. For the sake of discussoin, let's say every 60 seconds, poll the Docker API from Chainlit container.
Parse the WHOLE fucking JSON. ALL of it.

You had this working! It was great, I said good job! It was perfect, except that you broke the other core function, the persona.

For some reason, to make the container reporting work, you broke the persona reporting. Then, whrn you fixed the persona reporting, you broke the container reporting. 


2. The persona classifier and state machine is the entire reason mqtt is in the stack AT ALL. 

When the bot is online, and responsive and available for chat, the bot is online. If the bot is not engaged in a chat, the bot should shift into an "idle" status after the idle counter exceeds 5 minutes. It should reset when the user engages the bot in a chat.
The bot's emotional state will be "neutral" on start. Only after the user engages the bot in conversation will the classifier engine parse the message content and set a new emotional state.


All of this is independant of the container_stats, it has nothing at all to do with the container stats, except that the container stats uses the same mqtt setup.

Both processes need to begin their loops on application start. The bot is "active" on application start, regardless of chat because it has "logged in".  this let's me know as the admin that all systems are functional and operating per spec.

The container stats must be updated on a regular cadence so that I can track resource utilizartion, like vram, memory, cpu spikes, etc. So that way when I need to trouble shoot or load balance I have good metrics.


Summary:
1. Container Monitor should begin when the app is launched, asyncronously and non blocking. Every 60 seconds, the chainloot application requests an update from Docker. If it can't connect to the Docker API, it should back off and wait 5 seconds, then try again. If it still can't it should wait 15 seconds, and try again. If after the that 15 second wait and a third and final connection attempt it STILL can't connect it should exit non 0. CONTAINER = REQUIRED
2. Persona function needs to be launched asynrounously on app launch. It's considered "online", with dominant_emotion set to neutral until it's superceded by a "dominant" emotion. Going idle should reset the dominant emotion to neutral. If the chainlit container is not up, or the bot service is somehow broken the presence should be set to not be displayed.

Both are mandatory. Each has slightly different requirements for fequency and triggering event.
 