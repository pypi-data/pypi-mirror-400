# Publishing Voiceground

This guide explains how to publish Voiceground to PyPI using GitHub Actions.

## Publishing Process

Publishing is fully automated through GitHub Actions. Follow these steps:

### Step 1: Create and Push a Git Tag

Create a git tag with the version you want to publish. The tag name must start with `v`:

```bash
# For alpha releases
git tag v0.1.0a1
git push origin v0.1.0a1

# For stable releases
git tag v0.1.0
git push origin v0.1.0
```

**Version Format:**
- Use semantic versioning: `v0.1.0`, `v0.1.1`, `v1.0.0`
- For alpha/beta releases: `v0.1.0a1`, `v0.1.0b1`
- The `v` prefix is **required** (hatch-vcs expects it)

### Step 2: Create a GitHub Release

1. Go to: https://github.com/poseneror/voiceground/releases/new
2. **Select the tag** you just created from the "Choose a tag" dropdown
3. **Add release notes** describing what's in this release
4. Click **"Publish release"**

### Step 3: Monitor the Workflow

The GitHub Actions workflow will automatically:

1. ✅ Checkout the code with full git history (needed for version detection)
2. ✅ Build the React client
3. ✅ Build the Python package (version derived from git tag)
4. ✅ Publish to PyPI

**Monitor progress:**
- Go to: https://github.com/poseneror/voiceground/actions
- Click on the latest "Publish to PyPI" workflow run
- Watch the steps execute

### Step 4: Verify Publication

After the workflow completes successfully:

1. **Check PyPI**: https://pypi.org/project/voiceground/
2. **Test installation**:
   ```bash
   pip install voiceground
   ```
3. **Verify version**:
   ```bash
   pip show voiceground
   ```

## How It Works

- **Version Detection**: `hatch-vcs` automatically derives the package version from the git tag
- **Automated Build**: The workflow builds both the React client and Python package
- **PyPI Upload**: Uses `pypa/gh-action-pypi-publish` to securely upload to PyPI

## Troubleshooting

### Workflow Fails with "Invalid credentials"
- Verify `PYPI_API_TOKEN` secret is set correctly in GitHub
- Ensure the token has "Upload packages" scope
- Check that the token hasn't expired

### Workflow Fails with "File already exists"
- The version already exists on PyPI
- Create a new tag with an incremented version number

### Version Not Detected
- Ensure the tag starts with `v` (e.g., `v0.1.0`, not `0.1.0`)
- Verify `fetch-depth: 0` is set in the workflow (it is by default)
- Check that the tag was pushed to the remote repository

### Client Build Fails
- Ensure `node_modules` exists in the `client/` directory
- The workflow will install npm dependencies automatically
- Check the workflow logs for specific npm errors
