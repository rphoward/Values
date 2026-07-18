# Value

A teaching-first agent skill for value-proposition design.

It grills you one question at a time, teaches the concept briefly, saves durable session state, and can produce product and UX brief artifacts when the gates are ready.

## Install

### Project (local to one repo)

From the project you want the skill available in:

```bash
npx skills add rphoward/Values
```

This installs into that project's agent skills directory (for example `.agents/skills/` / Cursor project skills).

### Global (all your projects)

```bash
npx skills add rphoward/Values -g
```

### Useful options

```bash
# See what will install
npx skills add rphoward/Values -l

# Non-interactive
npx skills add rphoward/Values -y

# Cursor only
npx skills add rphoward/Values -a cursor -y

# Global + Cursor + non-interactive
npx skills add rphoward/Values -g -a cursor -y
```

## After install

In Cursor (or another supported agent), say something like:

> Grill me on a value proposition for my scheduling app.

The skill asks for a project slug/name first, then walks customer profile → value map → business model → experiments, one atom at a time.

## What's in this repo

```
skills/value/
  SKILL.md
  references/
  assets/
  scripts/
README.md
```

That is the whole package. No app scaffold, no extra skills.

## License

Add a license if you want to clarify reuse terms.
