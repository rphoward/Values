# Values

A teaching-first agent skill for value-proposition design.

It grills you one question at a time, teaches the concept briefly, saves durable session state under `workproduct/value-proposition/<project-slug>/`, and produces milestone artifacts plus product, UX, and app briefs when module gates are satisfied or explicitly bypassed.

Developed in the [Value](https://github.com/rphoward/Value) monorepo; this repo is the minimal install surface for `npx skills add`.

## Install

From the project where you want the skill:

```bash
npx skills add rphoward/Values
```

Global install (all projects):

```bash
npx skills add rphoward/Values -g
```

### Useful options

```bash
# Preview what will install
npx skills add rphoward/Values -l

# Non-interactive
npx skills add rphoward/Values -y

# Cursor only
npx skills add rphoward/Values -a cursor -y

# Global + Cursor + non-interactive
npx skills add rphoward/Values -g -a cursor -y
```

## After install

In Cursor (or another supported agent), try:

> Grill me on a value proposition for my scheduling app.

The skill asks for a project slug and name, creates `session.json` with your consent, then walks **customer profile → value map → business model → experiments** — one atom per turn.

Session scripts (stdlib Python under `skills/value/scripts/`) own ledger updates and gate workflow. You can revisit prior answers with `--reopen`, or record an explicit module bypass when you need to jump ahead.

## Package layout

```
skills/value/
  SKILL.md              # orchestrator and activation rules
  references/           # module curriculum (def-ref atoms)
  assets/               # atoms, schema, templates, knowledge base
  scripts/              # init, status, next, accept, milestone, briefs
README.md
```

No app scaffold, no extra skills — just the package.

## License

Add a license file here if you want to clarify reuse terms.
