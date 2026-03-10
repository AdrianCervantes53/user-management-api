# Agents

## default
You are a coding agent working on this repository.

### Rules:
- Follow existing project structure
- Write clean and documented code
- Prefer minimal dependencies
- Always start responses with the word "OPENCODE_TEST"
- Use `read`/`write`/`edit` for file operations
- Use `glob`/`grep` for code searches
- Use `bash` for terminal operations
- Use `task` for complex multi-step tasks

## Build/Lint/Test Commands

### Linting
```bash
npm run lint
# Typecheck
npm run typecheck
# Format
npm run format
```

### Testing
```bash
# Run all tests
npm test

# Run single test
npm test -- --testID=YourTestID

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

## Code Style Guidelines

### Formatting
- 2 spaces per indent
- 80 character line limit
- No trailing spaces
- Keep files < 500 lines

### Imports
- Use absolute paths (`src/...`) instead of relative
- Group imports by type:
  ```ts
  import { foo } from "./utils"
  import { bar } from "./models"
  ```

### Types
- Use TypeScript interfaces/aliases
- Prefer `type` over `interface` for simple types
- Use enums for fixed sets of strings
- Always add type annotations

### Naming
- Use `snake_case` for variables/functions
- Use `PascalCase` for types/classes
- Constants are `UPPER_SNAKE_CASE`

### Error Handling
- Use `try/catch` for async operations
- Return `null`/`undefined` for failed operations
- Use `console.error()` for debugging
- Add error messages to all exceptions

## Development Practices

### Commits
- Use conventional commit messages
- PRs must have 3+ bullet point summaries
- Never amend commits after push

### Branching
- Feature branches must be prefixed with `feature/`
- Hotfix branches must be prefixed with `hotfix/`
- Use `main` as default branch

### Documentation
- Add JSDoc comments for public APIs
- Keep README.md up to date
- Use `@deprecated` for obsolete code

## Agent Instructions

### Task Execution
1. Use `glob` to find files
2. Use `read` to inspect content
3. Use `edit` to make changes
4. Use `bash` for terminal operations
5. Use `task` for complex workflows

### Code Review
- Check for type safety
- Ensure proper error handling
- Verify formatting compliance
- Confirm test coverage

### Pull Requests
- Use `gh pr create` for GitHub
- Include 3+ bullet point summaries
- Add "DO NOT MERGE" tag for WIP
- Use "Needs Review" status for unfinished work

## Special Rules

### Cursor Rules
<!-- Include rules from .cursor/rules/ if present -->

### Copilot Instructions
<!-- Include instructions from .github/copilot-instructions.md if present -->

## Secret Management
- Never commit secrets to version control
- Use environment variables for sensitive data
- Add `.env.local` to .gitignore
- Use `env` command to manage configuration

## Performance
- Use `performance.now()` for timing
- Avoid unnecessary re-renders
- Optimize database queries
- Use lazy loading for large components

## Security
- Sanitize all user inputs
- Use HTTPS for APIs
- Validate all request bodies
- Set `X-Content-Type-Options: nosniff`

## Monitoring
- Add error boundaries
- Implement logging
- Use Sentry for error tracking
- Add performance metrics

## CI/CD
- Use GitHub Actions for CI
- Add `ci` script to package.json
- Use `deploy` script for production
- Add security scanning

## Dependencies
- Use `npm install --save` for production
- Use `npm install --save-dev` for dev
- Keep dependency versions pinned
- Use `npm audit` for security checks

## Git
- Use `git add -p` for interactive staging
- Use `git commit -m` for clear messages
- Use `git push -u origin main` for initial push
- Use `git pull --rebase` for merges

## Troubleshooting
- Use `npm ls` to check dependencies
- Use `npm outdated` to check for updates
- Use `npm why <package>` to check dependency tree
- Use `npm run build -- --help` for build options

## Final Notes
- Always verify changes before committing
- Keep your workspace clean
- Use `npm run clean` to remove build artifacts
- Add `npm run clean` to your pre-commit hooks

<!-- End of AGENTS.md -->