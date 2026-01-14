# skill-manager-treeshell

TreeShell MCP for three-tier skill architecture in the GNOSYS compound intelligence ecosystem.

## Overview

skill-manager-treeshell provides skill, skillset, and persona management through a TreeShell interface. Skills are on-demand context injection - text that gets loaded into conversations when needed.

## Installation

```bash
pip install skill-manager-treeshell
```

## MCP Configuration

Add to your Claude Code `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "skill-manager-treeshell": {
      "command": "skill-manager-treeshell"
    }
  }
}
```

## Three-Tier Architecture

### 1. Global Catalog
All skills, searchable via RAG. The source of truth.

### 2. Equipped State
Currently loaded skills for this session. What's active right now.

### 3. Skillsets
Named groups of skills for batch loading. "Equip the web-dev skillset" loads multiple related skills at once.

## Actions

### Global Catalog
| Action | Description |
|--------|-------------|
| list_skills | List all skills in catalog |
| list_domains | List skill domains |
| list_by_domain | List skills in a domain |
| get_skill | Get full skill content |
| create_skill | Create a new skill |
| search_skills | RAG search over skills |

### Equipped State
| Action | Description |
|--------|-------------|
| list_equipped | List currently equipped skills |
| get_equipped_content | Get content of all equipped |
| equip | Equip a skill or skillset |
| unequip | Unequip a skill |
| unequip_all | Clear all equipped |

### Skillsets
| Action | Description |
|--------|-------------|
| list_skillsets | List all skillsets |
| create_skillset | Create a skillset |
| add_to_skillset | Add skill to skillset |
| match_skilllog | Match SkillLog prediction |

### Personas
| Action | Description |
|--------|-------------|
| list_personas | List all personas |
| create_persona | Create a persona |
| equip_persona | Equip a persona |
| get_active_persona | Get active persona |
| deactivate_persona | Deactivate current persona |

## Usage

```
# List available skills
list_skills.exec {}

# Search for skills
search_skills.exec {"query": "vue component patterns"}

# Equip a skill
equip.exec {"name": "make-mcp"}

# Get equipped content
get_equipped_content.exec {}
```

## Part of GNOSYS

This package is part of the [GNOSYS](https://github.com/sancovp/gnosys) compound intelligence system for Claude Code.

## License

GNOSYS Personal Builder License (GPBL) v1.0
