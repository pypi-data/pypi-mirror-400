# GitHub Action Automation Setup

This GitHub Action automatically updates the Homebrew tap (`homebrew-brewse`) whenever you create a new release.

## Setup Instructions

### 1. Create a Personal Access Token (PAT)

The action needs permission to push to the `homebrew-brewse` repository.

1. Go to https://github.com/settings/tokens?type=beta
2. Click "Generate new token" (Fine-grained tokens)
3. Configure:
   - **Token name**: `brewse-tap-updater`
   - **Expiration**: 1 year (or custom)
   - **Repository access**: Select "Only select repositories"
     - Choose: `your-username/homebrew-brewse`
   - **Permissions** → Repository permissions:
     - Contents: **Read and write**
4. Click "Generate token"
5. **Copy the token** (you won't see it again!)

### 2. Add the token to your repository secrets

1. Go to https://github.com/your-username/brewse/settings/secrets/actions
2. Click "New repository secret"
3. Configure:
   - **Name**: `TAP_UPDATE_TOKEN`
   - **Value**: Paste your PAT from step 1
4. Click "Add secret"

### 3. Update the workflow file

The workflow is already configured to use the secret. Just make sure line 31 uses:

```yaml
token: ${{ secrets.TAP_UPDATE_TOKEN }}
```

Instead of:

```yaml
token: ${{ secrets.GITHUB_TOKEN }}
```

## How to Use

Once set up, your release workflow is:

```bash
# 1. Update version and build
# (already done in your code)

# 2. Build and publish to PyPI
uv build
uv publish

# 3. Create a GitHub release (triggers the automation!)
gh release create v0.1.3 --generate-notes

# Or manually create the release on GitHub
```

That's it! The GitHub Action will:
1. ✅ Extract the version from the tag
2. ✅ Download the tarball from PyPI
3. ✅ Calculate the SHA256 hash
4. ✅ Update `Formula/brewse.rb` in the tap repo
5. ✅ Commit and push the changes

Users can then update with:
```bash
brew update
brew upgrade brewse
```

## Troubleshooting

### Action fails with "permission denied"
- Check that the PAT has "Contents: Read and write" permission
- Verify the secret name is exactly `TAP_UPDATE_TOKEN`

### Action fails with "tarball not found"
- Wait a few minutes after `uv publish` for PyPI to process the upload
- Check the version number matches exactly (no 'v' prefix in pyproject.toml)

### Check action logs
View logs at: https://github.com/jonasjancarik/brewse/actions

## Manual Fallback

If the automation fails, you can still update manually:

```bash
cd ~/homebrew-brewse
./update-formula.sh 0.1.3
```

