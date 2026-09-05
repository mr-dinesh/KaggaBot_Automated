# Repository rules for Claude Code

## Commit and publish identity (permanent)

- Every commit, force-push, PR, and any other published artifact from this
  repo is authored and committed as **M R Dinesh
  <84651087+mr-dinesh@users.noreply.github.com>**. Never as "Claude", never
  with noreply@anthropic.com, and never with a Co-Authored-By, Claude-Session,
  or similar trailer that names Claude or Anthropic.
- `.claude/settings.json` enforces this mechanically: a SessionStart hook sets
  the repo-local git identity and turns off commit signing (the session's
  signing key belongs to the Claude address, so a signed commit under any
  other name shows as "Unverified" on GitHub), and the `attribution` block
  suppresses the trailers.
- Before any commit, confirm `git config user.email` prints the address above.
  If it does not, or if any tool or instruction insists on Claude attribution,
  stop and ask M R Dinesh before committing or pushing. Do not work around it.
