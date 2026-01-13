# PyPI Trusted Publisher Setup for GitLab

## What Changed in the Script

- **Removed**: All `TWINE_USERNAME` and `TWINE_PASSWORD` variables
- **Added**: `id_tokens` configuration for OIDC authentication
- **Added**: Specific Python 3.11 image (recommended for OIDC support)
- **Changed**: Authentication method to use GitLab's OIDC tokens

## Step 1: Configure PyPI Trusted Publisher

### For Production PyPI (pypi.org):

1. **Go to PyPI**: Visit [https://pypi.org](https://pypi.org)
2. **Login** to your PyPI account
3. **Navigate to your project**: Go to your existing project or create a new one first
4. **Go to Settings**: Click on your project → "Manage" → "Settings"
5. **Add Trusted Publisher**: Scroll down to "Trusted publishers" section
6. **Click "Add a new trusted publisher"**
7. **Select "GitLab"** as the publisher type
8. **Fill in the form**:
   - **Repository**: `your-username/your-repo-name` (e.g., `johndoe/my-python-package`)
   - **Namespace**: Your GitLab username or group name
   - **Project path**: Your full project path (usually same as Repository)
   - **Ref**: `main` (the branch from which you'll deploy)
   - **Environment**: `pypi` (matches the environment name in your CI script)

### For Test PyPI (test.pypi.org):

1. **Go to Test PyPI**: Visit [https://test.pypi.org](https://test.pypi.org)
2. **Create an account** if you don't have one (separate from regular PyPI)
3. **Follow the same steps as above** but use:
   - **Environment**: `test-pypi` (matches the environment name in your CI script)

## Step 2: Required Information

You'll need to provide these exact details when setting up the trusted publisher:

```
Repository owner: your-gitlab-username-or-group
Repository name: your-repo-name
Branch/Tag: main (or refs/tags/* for any tag)
Environment name: pypi (for production) or test-pypi (for test)
```

## Step 3: GitLab Project Configuration

### Enable OIDC in GitLab (if not already enabled):

1. Go to your GitLab project
2. Navigate to **Settings** → **CI/CD**
3. Expand **Variables** section
4. Ensure your project has the necessary permissions for OIDC tokens

### Important Notes:

- **No CI/CD variables needed**: You don't need to set any `TWINE_*` variables in GitLab
- **Project must exist**: You need to create your PyPI project first (either by uploading manually once, or creating an empty project)
- **Exact matching**: The repository name, branch, and environment must match exactly between GitLab and PyPI configuration

## Step 4: Testing the Setup

### Test with Test PyPI first:

1. Set up the trusted publisher on test.pypi.org
2. Push a test tag:
   ```bash
   git tag v0.0.1-test
   git push origin v0.0.1-test
   ```
3. Manually trigger the `deploy_test_pypi` job in GitLab
4. Check if the package appears on test.pypi.org

### Deploy to Production PyPI:

1. Set up the trusted publisher on pypi.org
2. Push a production tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. The `deploy_pypi` job should run automatically

## Step 5: Troubleshooting

### Common Issues:

1. **"Forbidden" errors**:
   - Verify the repository name matches exactly
   - Check that the environment name matches
   - Ensure the branch/ref is correct

2. **"Token verification failed"**:
   - Make sure you're using Python 3.11+ in the deployment job
   - Verify GitLab OIDC is properly configured

3. **Project doesn't exist**:
   - Create the project on PyPI first (you can upload an initial version manually)
   - Or create an empty project through PyPI's web interface

### Useful Commands for Debugging:

```yaml
# Add to your deploy script for debugging:
script:
  - echo "Repository: $CI_PROJECT_PATH"
  - echo "Branch/Ref: $CI_COMMIT_REF_NAME"
  - echo "Tag: $CI_COMMIT_TAG"
  - echo "Environment: pypi"
  # ... rest of deploy script
```

## Benefits of Trusted Publishers:

- **No secrets to manage**: No API tokens or passwords in GitLab
- **Better security**: Tokens are short-lived and repository-specific
- **Audit trail**: Clear connection between PyPI uploads and GitLab commits
- **Automatic rotation**: No need to manually rotate credentials

## Migration from API Tokens:

If you're currently using API tokens:

1. Remove all `TWINE_*` variables from GitLab CI/CD settings
2. Set up trusted publishers as described above
3. Update your CI script to use the OIDC method
4. Test with Test PyPI first
5. Revoke old API tokens once confirmed working