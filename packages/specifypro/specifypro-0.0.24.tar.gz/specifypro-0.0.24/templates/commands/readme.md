---
description: Create or update professional and attractive README.md files with project documentation, setup instructions, and usage guides.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

# COMMAND: Create professional and attractive README.md files

## CONTEXT

The user wants to create or update a professional and attractive README.md file for their project that includes:

- Project title and description
- Features and capabilities
- Tech stack and dependencies
- Setup and installation instructions
- Usage examples
- Contributing guidelines
- License information
- Badges and visual elements

**User's additional input:**

$ARGUMENTS

## YOUR ROLE

Act as a documentation specialist with expertise in:

- Technical writing and documentation
- Markdown formatting and styling
- Professional README structure
- Project presentation and marketing

## OUTPUT STRUCTURE

Execute this workflow in 4 sequential steps:

## Step 1: Load Project Context

Run `{SCRIPT}` from repo root and parse JSON for PROJECT_ROOT, BRANCH_NAME, and AVAILABLE_DOCS.

Derive absolute paths:

- PROJECT_ROOT (current directory)
- SPEC_FILE = specs/[BRANCH_NAME]/spec.md (if exists)
- PLAN_FILE = specs/[BRANCH_NAME]/plan.md (if exists)
- RESEARCH_FILE = specs/[BRANCH_NAME]/research.md (if exists)

## Step 2: Gather Project Information

Load available project artifacts to extract:

- Project name and description from spec.md
- Tech stack and architecture from plan.md
- Dependencies and tools from research.md
- Any existing README content from README.md
- Project structure from file system

## Step 3: Create Professional README

Generate a comprehensive README.md file with the following structure:

```
# [PROJECT TITLE]

[PROJECT DESCRIPTION WITH KEY HIGHLIGHTS]

[VISUAL ELEMENTS: Logo, screenshots, diagrams if available]

## 🌟 Features

- Feature 1
- Feature 2
- Feature 3

## 🛠️ Tech Stack

- Frontend: [technologies]
- Backend: [technologies] 
- Database: [technologies]
- DevOps: [technologies]

## 📋 Prerequisites

- [List of system requirements]

## 🚀 Setup & Installation

### Quick Start
[Simple 3-step setup]

### Detailed Setup
[Step-by-step installation instructions]

## 💡 Usage

[Examples of how to use the project]

## 🤝 Contributing

[Guidelines for contributing to the project]

## 📄 License

[License information]

## 📞 Support

[How to get help or report issues]
```

Apply these formatting rules:

- Use emojis and visual elements to make the README attractive
- Include badges (build status, license, version, etc.) where appropriate
- Use proper markdown formatting (headers, lists, code blocks)
- Include tables for complex information when needed
- Add horizontal rules (---) to separate major sections
- Use bold and italic text for emphasis where appropriate

## Step 4: Apply Professional Styling

Enhance the README with:

- Consistent formatting and structure
- Professional language and tone
- Proper grammar and spelling
- Visual hierarchy with appropriate heading levels
- Code blocks with proper syntax highlighting
- Links to relevant documentation and resources
- Contact information for support

## Step 5: Report Completion

Output:

```
✅ README Creation Complete - Created/updated README.md
```

Display the path to the created/updated README file and highlight key sections that were generated.

## FORMATTING REQUIREMENTS

Present results in this exact structure:

```
✅ README Creation Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 File: {README_PATH}
📋 Sections Created: {count}
   - Title & Description
   - Features & Capabilities  
   - Tech Stack
   - Setup Instructions
   - Usage Examples
   - Contributing Guidelines
   - License Information

Next Steps:
→ Review the generated README for accuracy
→ Add any project-specific details
→ Update badges with actual project links

Acceptance Criteria (PASS only if all true)
- README follows professional documentation standards
- All sections are complete and accurate
- Formatting is clean and visually appealing
- Includes proper navigation and structure
```

## ERROR HANDLING

If project context cannot be loaded:

- Display: "⚠️ Warning: Could not load full project context. Creating basic README with provided information."
- Continue with basic README creation using user arguments

If README already exists:

- Display: "ℹ️ README.md already exists. This command will update the existing file while preserving custom content where possible."
- Merge new information with existing content appropriately

## TONE

Be professional, clear, and marketing-focused. Emphasize the project's value proposition and make it attractive to potential users and contributors.