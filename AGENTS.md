# InsightAI — Agent Instructions

## 1. Project Overview

InsightAI is an AI-powered data analysis application designed to allow business users to interact with structured data using natural language.

The initial goal is to build a system that can receive a user's question, understand the intent, generate or execute the appropriate data query, analyze the result, and return a clear response.

The project is being developed as both a learning project and a professional portfolio project focused on AI Engineering.

---

## 2. Project Goals

The project should demonstrate practical AI Engineering capabilities, including:

* LLM integration
* AI agents and tool calling
* Structured data analysis
* SQL generation and execution
* Backend API development
* Frontend integration
* Data validation
* Testing
* Docker
* Cloud deployment
* Security and responsible handling of credentials

The final application should be understandable, maintainable, testable, and deployable.

---

## 3. Technology Stack

### Backend

* Python 3.12+
* FastAPI
* Pydantic
* Uvicorn

### AI

* Groq API
* LLM-based reasoning
* Tool calling
* Structured outputs

### Data

* PostgreSQL
* SQL

### Frontend

* Angular
* TypeScript

### Infrastructure

* Docker
* Docker Compose
* Git / GitHub

---

## 4. Python Environment

The project must use a project-specific Python virtual environment whenever possible.

Prefer:

```powershell
python -m pip install <package>
```

instead of calling `pip` directly.

Before installing dependencies, verify:

```powershell
python --version
python -m pip --version
```

Do NOT mix the global/system Python installation with the project's virtual environment.

Do NOT install project dependencies into the global Python environment if a project `.venv` exists.

If multiple Python installations or virtual environments exist, identify the correct one before continuing.

When a `.venv` exists, prefer activating and using that environment rather than creating another one.

On Windows PowerShell, the expected activation command is:

```powershell
.\.venv\Scripts\Activate.ps1
```

Do not assume that a virtual environment is active merely because the `.venv` directory exists. Verify the active Python environment when necessary.

---

## 5. Operating System and Shell

The primary development environment for InsightAI is Windows.

The AI coding agent must assume Windows unless the environment explicitly indicates otherwise.

The primary shell is PowerShell.

Commands must be compatible with Windows PowerShell.

Do NOT assume a Unix/macOS/Linux shell.

Do NOT automatically use Unix commands such as:

```text
ls
pwd
cat
grep
rm
cp
mv
touch
which
```

when a Windows/PowerShell equivalent is appropriate.

Prefer PowerShell commands such as:

```powershell
Get-ChildItem
Get-Location
Get-Content
Select-String
Remove-Item
Copy-Item
Move-Item
New-Item
Get-Command
```

For example:

```powershell
Get-ChildItem
```

should be preferred over:

```text
ls
```

and:

```powershell
Get-Location
```

should be preferred over:

```text
pwd
```

The agent may use commands that are available through Git Bash, WSL, or other environments only when the active environment explicitly indicates that shell.

Do not repeatedly retry Unix commands after a PowerShell command failure.

If a command fails because it is incompatible with PowerShell, replace it with the appropriate Windows/PowerShell equivalent.

When providing commands to the user, clearly indicate the expected shell when necessary.

---

## 6. Docker Environment

Docker is used through Docker Desktop on Windows.

Do NOT assume Docker Desktop is running.

Before creating or starting containers, verify Docker with:

```powershell
docker version
docker info
```

If Docker is unavailable:

* do not simulate successful Docker behavior;
* do not claim that a container is running;
* do not claim that PostgreSQL is integrated;
* report the actual problem.

Docker should be introduced progressively.

Do not create unnecessary containers or services.

For a feature that only requires PostgreSQL, use only PostgreSQL.

Do NOT automatically add:

* Redis
* Celery
* n8n
* nginx
* frontend containers
* workers
* monitoring systems
* additional databases
* unnecessary microservices

If PostgreSQL is provided through Docker Compose, the agent should verify that the PostgreSQL container is actually running before claiming database connectivity.

Starting Docker Desktop alone does not necessarily mean that the project's PostgreSQL container is running.

The agent must distinguish between:

1. Docker Desktop running.
2. Docker daemon available.
3. Project containers created.
4. Project containers running.
5. PostgreSQL accepting connections.
6. The application successfully connecting to PostgreSQL.

These are separate verification states.

---

## 7. Database Environment

PostgreSQL is the primary relational database for InsightAI.

The agent must understand that PostgreSQL itself does not require the user to manually open a graphical database application for the application to connect.

If PostgreSQL runs inside Docker, the PostgreSQL server is provided by the container.

A GUI such as pgAdmin, DBeaver, or another SQL client is optional and should not be required unless the current task specifically needs it.

When PostgreSQL is running through Docker, prefer application/database connectivity through the configured connection string rather than requiring the user to manually open a database GUI.

Before assuming PostgreSQL is available, verify the actual container and connection state when the task requires integration.

---

## 8. Architecture Principles

Follow clear separation of responsibilities.

The application should be organized into logical layers such as:

* API layer
* Business/application logic
* AI/agent logic
* Data access
* Configuration
* Tests

Avoid putting unrelated responsibilities into a single file or module.

Prefer simple and explicit architecture over unnecessary abstractions.

Do not introduce architectural patterns unless they solve a real problem in the project.

Do not create generic repositories, factories, services, managers, or abstractions unless they are actually justified by the current requirements.

---

## 9. Development Rules

Before implementing a significant feature:

1. Inspect the current project state.
2. Understand the existing architecture.
3. Inspect relevant files before modifying them.
4. Inspect the current Git state.
5. Explain the proposed approach.
6. Identify affected files.
7. Consider possible edge cases.
8. Implement the smallest reasonable change.
9. Test the change.
10. Verify that existing functionality still works.

Do not rewrite working code without a clear reason.

Do not refactor unrelated code.

Do not introduce dependencies unless they provide a meaningful benefit.

When introducing a dependency:

* verify whether an existing dependency already solves the problem;
* explain why the new dependency is needed;
* explain what problem it solves;
* add only the minimum required dependency.

If something is already correctly implemented:

DO NOT implement it again.

---

## 10. Incremental Development Rule

InsightAI is being developed incrementally.

Each development task will define a specific scope.

The agent must respect the scope of the current task.

Do NOT implement future roadmap features early simply because they are part of the final architecture.

For example, if the current task is only:

```text
PostgreSQL
+
data access
+
Python analysis
```

do NOT introduce:

* Agents
* Tool Calling
* LLM → SQL
* RAG
* embeddings
* vector databases
* Angular
* charts
* n8n
* deployment
* additional infrastructure

unless explicitly requested by the current task.

The existence of a feature in the long-term roadmap does not authorize implementing it in the current increment.

---

## 11. Verification Before Completion

The agent must distinguish between:

* code prepared for a feature;
* code partially implemented;
* code actually verified and working.

Never claim a feature is fully implemented unless the relevant behavior has been actually tested.

For infrastructure integrations, configuration alone is NOT sufficient evidence.

For example:

```text
Docker configuration exists
```

does NOT prove:

```text
PostgreSQL is running
```

Likewise:

```text
Python contains PostgreSQL connection code
```

does NOT prove:

```text
Python successfully connected to PostgreSQL
```

When verification is impossible because an external service is unavailable:

* report the limitation;
* do not simulate success;
* do not use fallback behavior to falsely prove the integration;
* do not declare the feature complete.

A fallback may exist for controlled tests, but it must never silently hide an infrastructure failure during integration verification.

---

## 12. AI Coding Rules

The AI coding agent must behave as a development assistant, not as an autonomous decision maker.

For significant changes:

* Explain the reasoning before implementation.
* Do not make assumptions about undocumented requirements.
* Do not invent APIs, SDK behavior, or library features.
* Prefer official documentation when verifying external libraries.
* Clearly identify uncertainty.
* Keep implementations understandable to a developer learning the technology.
* Avoid unnecessary complexity.
* Do not generate large amounts of code when a smaller implementation is sufficient.

When there are multiple valid approaches, briefly compare them and recommend one.

Do not continue into another development phase merely because the current phase is blocked.

If a prerequisite is missing, report it clearly and stop when appropriate.

---

## 13. Security Rules

Never hardcode API keys, passwords, tokens, or credentials.

Secrets must be stored in environment variables.

The `.env` file must never be committed to Git.

Use `.env.example` to document required environment variables without exposing real credentials.

Do not expose secrets through:

* API responses;
* logs;
* error messages;
* source code;
* test output;
* documentation.

Validate and sanitize external input before using it.

SQL generated by an LLM must never be trusted blindly.

Database access must use appropriate safeguards and permissions.

---

## 14. Database Safety

AI-generated SQL must be treated as untrusted input.

The system must:

* restrict database permissions;
* prevent destructive operations where appropriate;
* validate generated queries;
* avoid exposing sensitive database information;
* handle SQL errors safely.

The AI must not be given unrestricted destructive database access.

The LLM must not have direct unrestricted access to the database.

---

## 15. Testing

New functionality should include appropriate tests.

Prefer testing:

* business logic;
* API behavior;
* validation;
* AI/tool integration boundaries;
* database interactions where practical.

Tests should be understandable and maintainable.

Do not remove or disable tests merely to make a feature pass.

Tests must verify the actual intended data source when the task requires integration testing.

For example, if the task requires PostgreSQL integration, tests using only hardcoded sample data do NOT prove PostgreSQL integration.

When infrastructure is required for a test:

1. Verify the infrastructure is available.
2. Run the test against the actual intended service.
3. Record whether the integration was actually verified.
4. Clearly distinguish unit tests from integration tests.

---

## 16. Git Rules

Before modifying code, inspect:

```powershell
git status
git diff --name-only
git diff
```

Do not commit automatically.

Do not execute destructive Git operations unless explicitly authorized.

Never execute without explicit authorization:

* `git reset`
* `git restore`
* `git checkout`
* destructive branch operations

Do NOT execute:

```powershell
git add
git commit
```

unless the user explicitly asks for a commit.

Do not commit:

* `.env`
* secrets
* API keys
* passwords
* private credentials
* generated virtual environments
* unnecessary build artifacts

Use meaningful commit messages when commits are explicitly requested.

Keep commits focused on coherent changes.

---

## 17. Documentation

Important architectural or technical decisions should be documented.

The README should remain useful to someone discovering the project for the first time.

Documentation should explain:

* what the project does;
* why it exists;
* how it works;
* how to run it locally;
* required environment variables;
* how to test it;
* how the AI architecture works;
* how it can be deployed.

Do not add documentation for functionality that has not actually been implemented.

---

## 18. Learning Mode

This project is also being used to develop practical AI Engineering skills.

When implementing unfamiliar concepts:

* explain the concept briefly;
* explain why it is being used;
* show how it fits into the architecture;
* avoid hiding important implementation details behind abstractions.

The goal is not only to produce working software, but to understand the system being built.

Prefer simple implementations that make the underlying engineering concepts visible.

---

## 19. Command Execution Rules

Before executing commands:

1. Identify the operating system.
2. Identify the shell.
3. Use commands compatible with that environment.
4. Verify the working directory when paths matter.
5. Avoid chaining commands unnecessarily.
6. If a command fails because it is incompatible with PowerShell, correct the command rather than repeatedly retrying the same Unix syntax.

Do not repeatedly execute failed commands using the same incompatible syntax.

When a command is potentially destructive, explain what it will do before executing it.

For Windows PowerShell environments:

* prefer `Get-ChildItem` over `ls`;
* prefer `Get-Location` over `pwd`;
* prefer `Get-Content` over `cat`;
* prefer `Select-String` over `grep`;
* prefer `Remove-Item` over `rm`;
* prefer `Copy-Item` over `cp`;
* prefer `Move-Item` over `mv`;
* prefer `New-Item` over `touch`;
* prefer `Get-Command` over `which`.

Do not assume command syntax from macOS or Linux.

---

## 20. Environment and Credential Integrity

Never overwrite `.env` merely to make a test pass.

Before modifying environment configuration:

1. Inspect the existing configuration.
2. Identify which variables already exist.
3. Preserve existing secrets.
4. Modify only what is required.
5. Never expose secret values in output.

If a real API key or credential is accidentally exposed in terminal output, source code, or logs, do not reproduce it in subsequent messages or documentation.

---

## 21. Dependency and Package Integrity

Before installing a package:

1. Verify whether it is already installed.
2. Verify whether it is actually required.
3. Prefer the project's existing dependency strategy.
4. Use the project virtual environment when one exists.
5. Use `python -m pip` rather than relying on a global `pip` command.

Do not upgrade unrelated dependencies simply because newer versions exist.

Do not perform broad dependency upgrades unless explicitly requested or necessary to resolve a documented problem.

When changing dependencies, update the appropriate dependency file and verify the application still works.

---

## 22. Project Startup and Local Development

Before attempting to run the application:

1. Inspect the project structure.
2. Identify the backend entry point.
3. Identify the frontend entry point if applicable.
4. Identify required environment variables.
5. Identify whether Docker services are required.
6. Verify Python environment.
7. Verify Docker availability if Docker is required.
8. Start only the services required by the current increment.

Do not assume that every component must be started manually.

If PostgreSQL is managed by Docker Compose, the expected workflow should normally be:

```powershell
docker compose up -d
```

followed by verification of the actual container state.

Do not open pgAdmin, DBeaver, or another database GUI unless the task requires a graphical database client.

---

## 23. AI Agent Tool Usage

When the project introduces AI agents or tool calling, tools must have clearly defined responsibilities.

Tools should:

* have explicit inputs;
* validate inputs;
* return structured outputs where practical;
* expose only the minimum required capabilities;
* handle failures explicitly.

The agent must not receive unnecessary access to:

* the filesystem;
* the database;
* shell commands;
* credentials;
* external services.

Tool permissions should follow the principle of least privilege.

---

## 24. Error Handling

Errors must be handled explicitly.

Do not silently ignore exceptions.

Do not replace real errors with generic successful responses.

Error messages should provide useful debugging information without exposing:

* credentials;
* tokens;
* passwords;
* sensitive database information;
* internal secrets.

When an external dependency fails, preserve the distinction between:

* application error;
* configuration error;
* dependency error;
* infrastructure error;
* validation error.

---

## 25. Final Reporting

When completing a significant task, provide a concise report containing:

1. Status
2. Architecture
3. Changes made
4. Dependencies
5. Tests performed
6. Verification results
7. Git status
8. Known limitations
9. Conclusion

The conclusion must accurately reflect the verification state.

Use:

```text
READY FOR NEXT INCREMENT
```

only when the current increment has been successfully implemented and verified.

Use:

```text
NEEDS CORRECTION
```

when relevant functionality remains unverified, broken, or incomplete.

Never mark an integration as complete solely because the code was written.

---

### Windows / PowerShell

When the project is running on Windows and the active shell is PowerShell:

- Use PowerShell syntax exclusively.
- Do NOT use Bash, sh, zsh, cmd.exe, or Unix shell syntax unless the user explicitly requests it.
- Do NOT use Unix commands such as:
  - ls
  - cat
  - rm
  - del
  - export
  - source
  - &&
  - <<
  - heredocs
- Prefer PowerShell equivalents:
  - Get-ChildItem instead of ls
  - Get-Content instead of cat
  - Remove-Item instead of rm
  - $env:VARIABLE="value" instead of export
  - Set-Location instead of cd when clarity is needed
- When executing multiple commands, prefer separate PowerShell commands rather than shell-specific chaining.
- Never retry a failed Unix command by changing only its arguments. Rewrite it using valid PowerShell syntax.
- If a command is copied from documentation that assumes Bash/Linux/macOS, translate it to PowerShell before execution.

# End of Agent Instructions
