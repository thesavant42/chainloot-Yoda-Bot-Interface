TODO: Configuration Library Migration
Phase I: Create New Configuration Handler
[x] Create a new file named config_handler.py inside the lib/ folder.

Phase II: Migrate Configuration Logic
[x] Cut all setup and configuration code from the top of app.py and paste it into lib/config_handler.py. This includes:

Phase III: Update app.py
[ ] Delete all the configuration code that was moved from app.py in Phase II.
[ ] Add a new, single import statement at the top of app.py to import all the necessary objects from the new config_handler.py.
[ ] Ensure all references in app.py to the moved objects (like client, config, prompt_catalog, etc.) work correctly.