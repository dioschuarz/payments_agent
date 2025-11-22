# Prompts Directory

This directory contains all AI prompts used by the Send Money Agent. Prompts are stored as plain text files to enable:

- **Version Control**: Prompts can be versioned independently in Git
- **A/B Testing**: Easy to test different prompt versions
- **Non-developer Editing**: Prompts can be edited without touching code
- **Review Process**: Prompts can be reviewed separately in PRs
- **Localization**: Easier to create language-specific prompts

## File Structure

### `agent_instruction.txt`
Main instruction prompt for the ADK agent. This defines the agent's role, behavior, and conversation flow.

**Template Variables:**
- `{country_list}` - Will be replaced with the list of available countries at runtime

**Usage:**
```python
from src.infrastructure.ai.prompts.prompt_loader import PromptLoader

loader = PromptLoader()
instruction = loader.load_agent_instruction(country_list="...")
```

### `agent_description.txt`
Short description of the agent's purpose. Used for agent metadata.

**Usage:**
```python
from src.infrastructure.ai.prompts.prompt_loader import PromptLoader

loader = PromptLoader()
description = loader.load_agent_description()
```

## Versioning Strategy

1. **Major Changes**: Create new files with version suffix (e.g., `agent_instruction_v2.txt`)
2. **Minor Changes**: Update existing files and document changes in commit messages
3. **A/B Testing**: Use feature flags or environment variables to switch between versions

## Adding New Prompts

1. Create a new `.txt` file in this directory
2. Document template variables in this README
3. Update `PromptLoader` to load the new prompt
4. Update this README with usage instructions

## Template Variables

Prompts support template variables using Python's `.format()` syntax:
- `{variable_name}` - Will be replaced at runtime
- Use `{{` and `}}` to escape literal braces

Example:
```
Available countries: {country_list}
This is a literal brace: {{example}}
```

