Great question! There are several ways to manually trigger the `deploy_test_pypi` job. Let me show you the different methods:

## Method 1: GitLab Web UI (Easiest)

1. **Go to your GitLab project**
2. **Navigate to CI/CD → Pipelines**
3. **Find the pipeline** that ran when you pushed your tag
4. **Click on the pipeline** to open it
5. **Look for the `deploy_test_pypi` job** in the deploy stage
6. **Click the "Play" button** (▶️) next to the job name

The job will show as "manual" with a play button since we set `when: manual`.

## Method 2: GitLab API (Programmatic)

```bash
# Get your project ID and pipeline ID first
curl --request POST \
  --header "PRIVATE-TOKEN: your-gitlab-token" \
  "https://gitlab.com/api/v4/projects/PROJECT_ID/pipelines/PIPELINE_ID/jobs/JOB_ID/play"
```

## Method 3: GitLab CLI (if you have it installed)

```bash
glab ci play deploy_test_pypi --pipeline-id PIPELINE_ID
```

## Method 4: Modify the CI Script for Easier Testing

You might want to make the Test PyPI deployment easier to trigger. Here are some options:## Alternative: Create a Dedicated Test Job

If you want even easier testing, you could add a separate job that runs on any branch:

```yaml
# Add this as an additional job for easy testing
deploy_test_pypi_any_branch:
  stage: deploy
  image: python:3.11
  id_tokens:
    TEST_PYPI_ID_TOKEN:
      aud: testpypi
  before_script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - export PATH="$HOME/.local/bin:$PATH"
    - uv venv
    - source .venv/bin/activate
  script:
    - uv add --dev build twine
    - uv run python -m build
    - uv run twine check dist/*
    - uv run twine upload --repository testpypi dist/*
  rules:
    - when: manual  # Available on any branch, any time
  environment:
    name: test-pypi-dev
    url: https://test.pypi.org/project/your-package-name/
```

## Step-by-Step Testing Process

Here's the complete workflow for testing:

1. **Make your changes** and commit to a feature branch
2. **Create a test tag**:
   ```bash
   git tag v0.1.0-test
   git push origin v0.1.0-test
   ```
3. **Go to GitLab UI** → Pipelines
4. **Find your pipeline** (should show the tag name)
5. **Click the pipeline** to open it
6. **Look for the deploy stage** and find `deploy_test_pypi`
7. **Click the play button** (▶️) to trigger it manually

## Useful Tips

### Check Pipeline Status:
- **Blue dot** = Job is waiting to be run
- **Play button** = Manual job ready to trigger
- **Green checkmark** = Job completed successfully
- **Red X** = Job failed

### Testing Different Versions:
```bash
# Test with pre-release versions
git tag v1.0.0-alpha.1
git tag v1.0.0-beta.1
git tag v1.0.0-rc.1
git push origin --tags
```

### View Job Logs:
Click on the job name (not just the play button) to see the full logs and debug any issues.

The key is that `when: manual` makes the job available but requires you to explicitly trigger it, giving you full control over when test deployments happen.