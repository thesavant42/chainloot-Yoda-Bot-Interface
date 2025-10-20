# Tasks: Cleanup the project directories

## Task 1 - Docker Files Cleanup

There are a handful of Dockerfiles in the main project root, without ocntext and cluttering up the workspace.

 - TTS-WebUI.Dockerfile
 - Dockerfile
 - docker-compose.yml

### Task:  Migrate the dockerfiles to the newly created docker folder.

- Use MCP Tools for context7 to obtain the latest documentation for these components
- Ensure that all necessary paths are updated to ensure that docker-compose, docker build, etc , all work as expected
- Create a readme.md in the root of the new folder describing its contents and how to best utilize them

Open Questions:

Q: What are all of the touchpoints for the effected files. They're used at install and setup, but beyond that I'm not sure they're used very much.

A:

Notes:

Progress: Completed - Files moved, paths updated, README created, build tested successfully


## Task 2 - Database Files Cleanup

There are database files all over the place, cluttering up the main workspace and not providing context. 

### Task: Create new database folder (done) and move all database related files to that folder.

- Use MCP Tools for context7 to obtain the latest documentation for these components
- Move these folders/files to the new database folder
    - schema.prisma
    - migrations
    - prisma
- Update Dockerfile and docker-compose files so that database seeding and migrations kickoff with the newly updated path information.
- Create a readme.md in the root of the new folder describing its contents and how to best utilize them

Open Questions:

Q: What are all of the touchpoints for the effected files. Installation of the database servers, installation of the prisma libraries, the migration files, the schema... Any others?

A:

Notes:

Progress: Completed - Files moved to database/ folder, paths updated in start.sh and documentation, README created, build tested successfully, database migrations and application startup verified working

## Task 3 - Config Folder Cleanup

Move all files that are edited by a user to a config directory

### Migrate the configurations

- Use MCP Tools for context7 to obtain the latest documentation for these components
- Move config.json
  - Will need to ensure the chainlit app polls that new path for config.json, reading & writing.
  - Will need to ensure that values are read, written, and persist restarts
- Move mcp_proxy_servers.json
  - update app code to reference new location
- move mcp_servers.json
  - update app code to reference new location

- Create a readme.md in the root of the new folder describing its contents and how to best utilize them

Open Questions:

Q: What are all of the touch points for the mcp configurations? We will want to make a checklist for every reference to the files, to ensure that they inheirit the new path properly.

A: All references identified and updated:
- lib/mcp_tool_processor.py: get_active_mcp_manager() function
- lib/dynamic_mcp_manager.py: default config_file parameter
- app.py: get_active_mcp_manager() and initialize_mcp_on_startup() functions

Notes:

Progress: Completed - Files moved to config/ folder, all code references updated, config loading and persistence tested successfully, README created and updated with latest documentation from Context7 MCP for all MCP server components

## Task 4: Update documentation and changelogs

### Task: Documentation

- Track the changes and update documentation

### Completed Updates:
- Updated README.md Docker setup instructions to use `install/docker/docker-compose.yml`
- Updated CHANGELOG.md with project structure reorganization entry
- Updated .github/copilot-instructions.md with new file paths
- Verified all documentation reflects the new folder structure

Progress: Completed - All documentation updated to reflect Tasks 1 and 2 changes

## General Recommendations

Based on a review of the task list, here are additional suggestions to ensure smooth execution and long-term maintainability:

- **Prioritize Testing**: After each task, run `docker-compose up --build` and test key features (e.g., Chainlit startup, TTS-WebUI API, database migrations) to catch path-related breaks early. Use the existing setup as a baseline.

- **Version Control Best Practices**: Commit changes incrementally (e.g., one task at a time) with clear messages. If something breaks, it's easier to revert. Also, update `.gitignore` if needed for the new folders.

- **Automation and Tools**: For path updates, use grep searches (e.g., `grep -r "old/path" .`) to find all references. Consider scripts to automate renames if there are many touchpoints.

- **Documentation Tips**: In the new READMEs, include examples (e.g., "Run `docker-compose -f docker/docker-compose.yml up`"). Link to external docs (e.g., Docker, Prisma) for users.

- **Potential Risks**: Watch for hardcoded paths in submodules or env files. If the app uses relative paths, ensure the working directory context is correct. Also, double-check permissions on moved files.

- **Order of Execution**: Start with Task 1 (Docker) since it's foundational, then Task 2 (Database), Task 3 (Config), and end with Task 4 (Docs). This minimizes dependencies.

- **Handoff Readiness**: This list is well-structured and ready for an agent (e.g., via `github-pull-request_copilot-coding-agent`). It has clear steps, open questions to resolve, and progress tracking. If you provide more details on the open questions (e.g., via code searches), it would be even stronger.