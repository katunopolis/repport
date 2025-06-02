# 🧹 Code Cleanup Checklist - Repport Project

This file tracks the overarching strategy and practical tasks for cleaning up and refactoring the Repport codebase (FastAPI backend + React frontend). Cleanup is not just about prettier code—it’s about making the project easier to maintain, scale, and understand. Work through files and features incrementally, and follow the principles of clarity, safety, and consistency.

Strategy Overview

## 1. Assessment Phase

### Codebase Audit: Review the entire codebase to understand structure, identify patterns, and note inconsistencies.

Issue Identification:

- Duplicated code
- Inconsistent naming conventions
- Unused imports or variables
- High cyclomatic complexity
- Outdated dependencies
- Security vulnerabilities
- Poor error handling
- Inefficient database queries
- Missing type hints

## 2. Prioritization

Risk Categorization: Sort issues by risk (high, medium, low).
Impact Assessment: Identify most critical and high-usage parts of the codebase.
Cleanup Roadmap: Prioritize low-risk, high-impact improvements first.

## 3. Implementation Strategy

Incremental Approach: Focus on small, focused changes.
One-Category-at-a-Time: E.g., remove unused imports across the codebase before addressing naming.
Version Control: Use atomic commits, clear branch naming, and meaningful messages.
Documentation: Reflect any API or structural changes in relevant documentation.

## 4. Testing Protocol

Baseline Tests: Run tests before changes to verify existing behavior.
Test Coverage Analysis: Identify weak spots and add tests if needed.
Regression Testing: Confirm existing functionality after every change.
User Flow Testing: Validate key user journeys (e.g., login > dashboard > logout).

## 5. Target Areas for Repport Project

Backend (FastAPI):

- API consistency
- SQLModel query optimization
- Simplify auth flows
- Improve error handling
- Consolidate configuration patterns

Frontend (React):

- Component simplification
- State/prop cleanup
- Standardize API client logic
- Consistent styling
- Standardize form handling and validation

## 6. Task Flow for Each Change

- Create a branch for the specific cleanup task
- Add missing tests
- Make the change
- Test locally
- Commit with meaningful message
- Push and create PR (if applicable)

## 7. Documentation

- Improve inline code comments
- Update README or API docs if structure or behavior changes
- Create or update a style guide

---

## ✅ General Rules

- [ ] Create a **new branch** for every distinct cleanup task
- [ ] Ensure **tests run** before and after changes
- [ ] Avoid refactoring logic and structure at the same time
- [ ] Use atomic **commits** with clear messages
- [ ] Prefer **small pull requests** with good diffs

---

## 🔁 Backend (FastAPI)

### ⬜ Routes and Controllers
- [ ] Standardize response formats (e.g., `{"status": "ok", "data": ..., "error": null}`)
- [ ] Remove unused imports and variables
- [ ] Ensure type hints on all route parameters and return values
- [ ] Add or clarify error handling
- [ ] Break down long route functions

### ⬜ Models & Schemas
- [ ] Verify consistency between DB models and Pydantic schemas
- [ ] Add missing type hints and constraints
- [ ] Normalize naming (e.g., `user_id` vs `id_user`)
- [ ] Review relationships for clarity

### ⬜ Services / Logic
- [ ] Isolate repeated logic into helper functions or services
- [ ] Clean up authentication/authorization logic
- [ ] Improve logging and exception traceability

### ⬜ Configuration
- [ ] Centralize all env variables and secrets
- [ ] Replace hardcoded values with config lookups

---

## ⚛️ Frontend (React)

### ⬜ API Client
- [ ] Use a centralized Axios/fetch wrapper
- [ ] Standardize error handling and response parsing

### ⬜ State & Props
- [ ] Eliminate unnecessary prop drilling
- [ ] Migrate shared state to context/store if needed
- [ ] Avoid redundant local state in components

### ⬜ Components
- [ ] Break down large components
- [ ] Use consistent naming conventions (PascalCase for components, camelCase for props)
- [ ] Remove dead/unused components

### ⬜ Forms
- [ ] Use a consistent form validation library (e.g., React Hook Form + Zod/Yup)
- [ ] Standardize error display and field layout

### ⬜ Styling
- [ ] Remove unused or duplicated styles
- [ ] Use consistent CSS/SCSS or Tailwind classes

---

## 🧪 Testing

- [ ] Run all tests before any refactor
- [ ] Add unit tests for newly cleaned functions
- [ ] Ensure auth/user flows work (login > dashboard > logout)
- [ ] Manually test core API endpoints
- [ ] Use `npm run lint` or `black/flake8` as pre-commit

---

## 📚 Documentation

- [ ] Update README if API response structure changes
- [ ] Add/clean up inline comments where unclear
- [ ] Create/update a `STYLE_GUIDE.md` for future devs

---

## 🌱 Optional Enhancements

- [ ] Add CI for tests + lint checks
- [ ] Introduce pre-commit hooks for auto-formatting
- [ ] Add logging middleware (e.g., request/response logs for FastAPI)

---

## 💬 Tip

> Don’t refactor to be clever. Refactor to make the next developer say, “Ah, I get it.”

