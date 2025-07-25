# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the mx-next-bridge repository containing the miXshift neXt Services platform with integrated vBridge analytics.

## Application Development

For vBridge application development tasks, refer to:

- `@vBridge/CLAUDE.md` - Contains detailed vBridge development practices, architecture, and methodology

## Git & Deployment Commands

### Git Workflow

- Main branch: `trunk` (use for PRs)
- Remote: `git@github.com:miXshift/mx-next-bridge.git`

### Feature Development Process

**IMPORTANT**: Always follow this workflow when implementing features:

1. **Before starting a new feature**:
   - Ask the user: "I'll create a new branch for this feature. Would `feature/[descriptive-name]` be an appropriate branch name?"
   - Wait for user confirmation before creating the branch
   - Create branch from `trunk`: `git checkout -b feature/[name]`

2. **After completing feature implementation**:
   - Run tests and linting to ensure code quality
   - Ask the user: "I've completed the feature implementation. Should I create a commit with the message: '[descriptive commit message]'?"
   - Wait for user confirmation before committing
   - Create atomic commits that represent logical units of work

3. **When ready to merge**:
   - Ensure all tests pass and code is properly documented
   - Ask the user: "The feature is ready. Should I open a PR to `trunk` with the title: '[PR title]' and description: '[PR description]'?"
   - Wait for user confirmation before creating the PR
   - Use `gh pr create` to open the pull request

### Build & Development Commands

```bash
# Next.js + Express development
pnpm dev              # Run both Next.js and Express server concurrently
pnpm dev:next         # Run Next.js only
pnpm dev:server       # Run Express server only

# Production build
pnpm build            # Build Next.js app (also builds server)
pnpm build:server     # Build Express server separately
pnpm start            # Start production server

# Code quality
pnpm lint             # Run Next.js linter
```

### vBridge Commands

```bash
# vBridge operations
pnpm vbridge:install  # Install/update Python dependencies
pnpm vbridge:clean    # Clean output directory (preserves README.md)
pnpm vbridge:run      # Run vBridge campaign bridge analysis (src.core.campaign_bridge)
pnpm vbridge:full     # Clean + run (most common workflow)
pnpm vbridge:test     # Run vBridge tests
pnpm vbridge:demo     # Run demo with improved output formatting
```

## Project Structure

### Top-Level Architecture

- `/src` - Next.js application code
  - `/app` - App Router pages and API routes
  - `/lib` - Shared libraries (auth, db)
  - `/models` - Database models
  - `/server` - Express server components
- `/vBridge` - vBridge analytics application (see vBridge/CLAUDE.md)
- `/public` - Static assets
- `/server.ts` - Express server entry point

### Technology Stack

- Frontend: Next.js 15 with App Router, React 18, TypeScript
- Backend: Express.js with TypeScript
- Database: MongoDB with Mongoose
- Authentication: NextAuth.js
- Python: vBridge analytics (Python 3 with virtual environment)

## Deployment Considerations

### Environment Setup

- Ensure MongoDB connection is configured
- Set up environment variables (see `.env.example` if available)
- Python virtual environment is included in `/vBridge/venv`

### Build Process

1. TypeScript server compilation happens automatically via `prebuild` script
2. Next.js build includes static optimization
3. Production starts with `NODE_ENV=production`

### vBridge Integration

- vBridge runs as a separate Python process
- Output files are generated in `/vBridge/output/`
- Latest results always in `/vBridge/output/current/LATEST_mixbridge.csv`
