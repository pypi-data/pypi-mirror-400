# Team Workspace

This is the collaborative workspace for your team. Files here should be committed to version control and shared with team members.

## Structure

```
team-workspace/
├── README.md              # This file
├── notebooks/             # Shared Jupyter notebooks
├── scripts/               # Reusable Python scripts
├── skills/                # Team-specific agent skills
│   └── skill-upload-registry.json
└── rules/                 # Team-specific agent rules
```

## Usage

### Notebooks
Place shared analysis notebooks in the `notebooks/` directory. These should be:
- Well-documented with markdown cells
- Include clear titles and explanations
- Use proper visualizations with labels
- Include data sources and assumptions

### Scripts
Reusable Python modules and scripts go in `scripts/`:
- ETL pipelines
- Data transformations
- Utility functions
- Common calculations

### Skills
Team-specific agent skills that extend default capabilities. Skills placed here override default skills with the same name.

### Rules
Team-specific agent behavior rules. Rules here take precedence over default rules but can be overridden by user workspace rules.

## Best Practices

1. **Commit often**: Keep the team in sync with regular commits
2. **Document everything**: Future you (and teammates) will thank you
3. **Use .gitignore**: Don't commit data files, credentials, or outputs
4. **Review changes**: Use pull requests for significant changes
5. **Follow conventions**: Maintain consistent naming and structure

## Git Configuration

Recommended `.gitignore` patterns:
```
# Data files
*.csv
*.parquet
*.xlsx
data/

# Notebook outputs (optional)
*.ipynb_checkpoints/

# Python
__pycache__/
*.pyc
*.pyo

# OS files
.DS_Store
Thumbs.db
```

## Collaboration

When working on shared notebooks:
- Create a branch for experiments
- Merge back to main when stable
- Clear outputs before committing (optional)
- Document significant changes in commit messages

## Need Help?

- Check [SignalPilot Documentation](https://signalpilot.dev/docs)
- Review default skills in `../default-skills/`
- Review default rules in `../default-rules/`
