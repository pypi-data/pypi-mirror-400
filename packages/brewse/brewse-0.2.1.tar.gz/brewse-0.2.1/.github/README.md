# GitHub Workflows

This directory contains GitHub Actions workflows for automating brewse releases.

## Workflows

### `update-homebrew-tap.yml`
Automatically updates the Homebrew tap when a new release is published.

**Triggers on**: GitHub release creation  
**Does**: Updates `Formula/brewse.rb` in the `homebrew-brewse` repository

See [AUTOMATION_SETUP.md](AUTOMATION_SETUP.md) for setup instructions.

## Quick Setup

1. Create a fine-grained PAT with access to `homebrew-brewse` repo
2. Add it as a secret named `TAP_UPDATE_TOKEN`
3. Create releases with `gh release create v0.1.3 --generate-notes`

The tap will update automatically! 🎉

