# Packaging and Publishing ML Workbench to AWS CodeArtifact

This guide explains how to package `ml-workbench` as a Python package and publish it to AWS CodeArtifact for distribution within your organization.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Setup Review](#project-setup-review)
3. [Building the Package](#building-the-package)
4. [AWS CodeArtifact Setup](#aws-codeartifact-setup)
5. [Authentication Configuration](#authentication-configuration)
6. [Publishing to CodeArtifact](#publishing-to-codeartifact)
7. [Installing from CodeArtifact](#installing-from-codeartifact)
8. [Version Management](#version-management)
9. [CI/CD Integration](#cicd-integration)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12** installed (as specified in `pyproject.toml`)
- **AWS CLI** installed and configured with appropriate credentials
- **AWS Account** with CodeArtifact repository access
- **Build tools**: `hatchling` (already configured in `pyproject.toml`)
- **Package manager**: `uv` (already configured)

### Required AWS Permissions

Your AWS credentials need the following CodeArtifact permissions:
- `codeartifact:GetAuthorizationToken`
- `codeartifact:ReadFromRepository`
- `codeartifact:PublishPackageVersion`
- `codeartifact:PutPackageMetadata`

---

## Project Setup Review

The project is already configured for packaging:

- **Build backend**: `hatchling` (configured in `pyproject.toml`)
- **Package name**: `ml-workbench`
- **Current version**: `0.0.1` (defined in `pyproject.toml`)
- **Package structure**: `ml_workbench/` directory contains all source code
- **Entry points**: CLI script `cli-experiment` is configured

The `pyproject.toml` file already includes:
- Package metadata (name, version, description, authors)
- Dependencies and dev dependencies
- Build configuration for hatchling
- Package discovery settings

---

## Building the Package

Build the package using `uv`:

```bash
# Build only the wheel distribution (recommended)
uv build --wheel

# This will create only the wheel file in the dist/ directory:
# - dist/ml_workbench-0.0.1-py3-none-any.whl (wheel)

# To build both wheel and source distribution (if needed):
# uv build
```

### Verify the Build

After building, verify the package contents:

```bash
# List contents of the wheel
unzip -l dist/ml_workbench-*.whl

```

---

## AWS CodeArtifact Setup

### 1. Create a CodeArtifact Repository (if not exists)
**SKIP THIS STEP - REPOSITORY ALREADY EXISTS**

If your organization doesn't have a CodeArtifact repository yet:

```bash
# Assuming we are already login with `aws sso login`

# Set your AWS region and account details
export AWS_REGION="eu-west-1"  # Replace with your region
export AWS_ACCOUNT_ID="471112612782"  # Replace with your account ID
export REPOSITORY_NAME="pheno-pip"  # Or your preferred name
export DOMAIN_NAME="pheno"  # Or your organization domain name

# Create a domain (if it doesn't exist)
aws codeartifact create-domain \
    --domain $DOMAIN_NAME \
    --region $AWS_REGION  \
    --profile integration

# Create a repository
aws codeartifact create-repository \
    --domain $DOMAIN_NAME \
    --repository $REPOSITORY_NAME \
    --description "Python packages repository" \
    --region $AWS_REGION \
    --profile integration
```

### 2. Get Repository Details

You'll need the following information for publishing:

- **Domain name**: The CodeArtifact domain
- **Repository name**: The repository within the domain
- **AWS Region**: The region where CodeArtifact is hosted
- **Account ID**: Your AWS account ID

You can retrieve repository details:

```bash
aws codeartifact describe-repository \
    --domain $DOMAIN_NAME \
    --repository $REPOSITORY_NAME \
    --region $AWS_REGION \
    --query 'repository' \
    --profile integration
```

---

## Authentication Configuration

CodeArtifact requires authentication via AWS credentials. You have several options:

### Option 1: AWS CLI Login (Recommended for Local Development)

This configures pip/uv to use CodeArtifact:

```bash
# Login with SSO
aws sso login

# For uv, use: (authorization token to be stored in ~/.pypirc)
aws codeartifact login \
    --tool twine \
    --domain $DOMAIN_NAME \
    --domain-owner $AWS_ACCOUNT_ID \
    --repository $REPOSITORY_NAME \
    --region $AWS_REGION \
    --profile integration
```

This command:
- Retrieves an authorization token from CodeArtifact
- Configures credentials in `~/.pypirc` (for `uv-publish` wrapper)
- The token is valid for 12 hours

### Option 2: Manual Token Configuration

Get the authorization token manually for use with UV:

```bash
# Get the token
export CODEARTIFACT_TOKEN=$(aws codeartifact get-authorization-token \
    --domain $DOMAIN_NAME \
    --domain-owner $AWS_ACCOUNT_ID \
    --region $AWS_REGION \
    --query authorizationToken \
    --output text)
```

This token can then be used with `uv publish` (see Publishing section).

### Option 3: Using `.pypirc` Configuration File with `uv-publish` Wrapper

**Note:** UV does not natively read `.pypirc` files. To use `.pypirc` configuration, you need to use the `uv-publish` wrapper.

First, ensure your `~/.pypirc` file has a `[codeartifact]` section:

```ini
[distutils]
index-servers = 
    codeartifact

[codeartifact]
repository = https://pheno-471112612782.d.codeartifact.eu-west-1.amazonaws.com/pypi/pheno-pip/
username = aws
password = <YOUR_CODEARTIFACT_TOKEN>
```

**Note:** The `password` field should contain your CodeArtifact authorization token. You can get it with:

```bash
aws codeartifact get-authorization-token \
    --domain $DOMAIN_NAME \
    --domain-owner $AWS_ACCOUNT_ID \
    --repository $REPOSITORY_NAME \
    --region $AWS_REGION \
    --query authorizationToken \
    --output text
```

Then use the `uv-publish` wrapper which reads from `.pypirc`:

```bash
# Publish using .pypirc configuration (uv-publish wrapper reads .pypirc)
uvx uv-publish --repository codeartifact dist/ml_workbench-*.whl
```

**Important:** The standard `uv publish` command does not read `.pypirc` files. You must use `uvx uv-publish` (or install `uv-publish` separately) to use `.pypirc` configuration.

---

## Publishing to CodeArtifact

### Step 1: Build the Package

```bash
# Clean previous builds (optional)
rm -rf dist/ build/ *.egg-info

# Build only the wheel distribution (recommended)
uv build --wheel
```

### Step 2: Configure Authentication

Choose one of the following methods:

**Option A: Using `.pypirc` with `uv-publish` Wrapper**

Ensure your `~/.pypirc` file has a `[codeartifact]` section configured (see [Authentication Configuration](#authentication-configuration)). Note that you'll need to use `uvx uv-publish` (not `uv publish`) to read from `.pypirc`. Then skip to Step 3.

**Option B: Using AWS CLI Login**

```bash
# Login to CodeArtifact (configures .pypirc for uv-publish wrapper)
aws codeartifact login \
    --tool twine \
    --domain $DOMAIN_NAME \
    --domain-owner $AWS_ACCOUNT_ID \
    --repository $REPOSITORY_NAME \
    --region $AWS_REGION \
    --profile integration
```

### Step 3: Upload the Package

#### Using `uv-publish` Wrapper with `.pypirc` (Recommended)

If you have configured `~/.pypirc` with a `[codeartifact]` section (see [Authentication Configuration](#authentication-configuration)), use the `uv-publish` wrapper:

```bash
# uv-publish wrapper reads from .pypirc
uvx uv-publish --repository codeartifact dist/ml_workbench-*.whl
```

**Note:** The standard `uv publish` command does not read `.pypirc` files. Use `uvx uv-publish` to leverage your `.pypirc` configuration.

#### Using `uv publish` with Explicit Credentials

If you prefer not to use `.pypirc`, you can use `uv publish` directly with explicit credentials:

```bash
# Get the CodeArtifact token
export CODEARTIFACT_TOKEN=$(aws codeartifact get-authorization-token \
    --domain $DOMAIN_NAME \
    --domain-owner $AWS_ACCOUNT_ID \
    --repository $REPOSITORY_NAME \
    --region $AWS_REGION \
    --query authorizationToken \
    --output text)

# Publish using uv with explicit credentials (only wheel needed)
uv publish \
    --publish-url https://$DOMAIN_NAME-$AWS_ACCOUNT_ID.d.codeartifact.$AWS_REGION.amazonaws.com/pypi/$REPOSITORY_NAME/ \
    --username aws \
    --password $CODEARTIFACT_TOKEN \
    dist/ml_workbench-*.whl
```

**Note:** The `--publish-url` should point to the upload endpoint (not the simple index URL). For CodeArtifact, use the format: `https://<domain>-<account-id>.d.codeartifact.<region>.amazonaws.com/pypi/<repository-name>/`

### Step 4: Verify Upload

Check that your package was uploaded successfully:

```bash
aws codeartifact list-package-versions \
    --domain $DOMAIN_NAME \
    --repository $REPOSITORY_NAME \
    --format pypi \
    --package ml-workbench \
    --region $AWS_REGION \
    --profile integration
```

---

## Installing from CodeArtifact

### Step 1: Configure UV for CodeArtifact

Users need to authenticate before installing:

```bash
# Login to CodeArtifact (configures pip, which UV can use)
aws codeartifact login \
    --tool pip \
    --domain $DOMAIN_NAME \
    --domain-owner $AWS_ACCOUNT_ID \
    --repository $REPOSITORY_NAME \
    --region $AWS_REGION \
    --profile integration
```

### Step 2: Install the Package

```bash
# Install using uv
uv pip install ml-workbench

# Or install a specific version
uv pip install ml-workbench==0.0.1
```

### Step 3: Verify Installation

```bash
# Check if the package is installed
uv pip list | grep ml-workbench

# Test the CLI entry point
cli-experiment --help
```

### Alternative: Direct URL Installation

If you prefer not to configure globally:

```bash
# Get the repository URL
export REPO_URL="https://$DOMAIN_NAME-$AWS_ACCOUNT_ID.d.codeartifact.$AWS_REGION.amazonaws.com/pypi/$REPOSITORY_NAME/simple/"

# Install directly from the repository using uv
uv pip install ml-workbench --index-url $REPO_URL
```

---

## Version Management

### Updating the Version

Before publishing a new version, update the version in `pyproject.toml`:

```toml
[project]
name = "ml-workbench"
version = "0.0.2"  # Increment this
```

### Semantic Versioning

Follow semantic versioning (semver) principles:
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, backward compatible

### Version Tags in Git

Consider tagging releases in git:

```bash
# After updating version and publishing
git tag -a v0.0.2 -m "Release version 0.0.2"
git push origin v0.0.2
```

---

## CI/CD Integration

### GitHub Actions Example

Here's an example workflow for automated publishing:

```yaml
name: Publish to CodeArtifact

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install uv
        run: pip install uv
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1
      
      - name: Build package
        run: uv build --wheel
      
      - name: Get CodeArtifact token
        run: |
          export CODEARTIFACT_TOKEN=$(aws codeartifact get-authorization-token \
            --domain ${{ secrets.CODEARTIFACT_DOMAIN }} \
            --domain-owner ${{ secrets.AWS_ACCOUNT_ID }} \
            --repository ${{ secrets.CODEARTIFACT_REPOSITORY }} \
            --region eu-west-1 \
            --query authorizationToken \
            --output text)
          echo "CODEARTIFACT_TOKEN=$CODEARTIFACT_TOKEN" >> $GITHUB_ENV
      
      - name: Publish to CodeArtifact
        run: |
          uv publish \
            --publish-url https://${{ secrets.CODEARTIFACT_DOMAIN }}-${{ secrets.AWS_ACCOUNT_ID }}.d.codeartifact.us-east-1.amazonaws.com/pypi/${{ secrets.CODEARTIFACT_REPOSITORY }}/ \
            --username aws \
            --password $CODEARTIFACT_TOKEN \
            dist/ml_workbench-*.whl
```

---

## Troubleshooting

### Issue: Authentication Token Expired

**Error**: `401 Unauthorized` or `Invalid credentials`

**Solution**: CodeArtifact tokens expire after 12 hours. Re-run the login command:

```bash
aws codeartifact login \
    --tool twine \
    --domain $DOMAIN_NAME \
    --domain-owner $AWS_ACCOUNT_ID \
    --repository $REPOSITORY_NAME \
    --region $AWS_REGION \
    --profile integration
```

### Issue: Package Already Exists

**Error**: `409 Conflict` when uploading the same version

**Common Error Messages:**
- `Upload failed with status code 409 Conflict. Server says: Package Version '0.0.1' exists in externally connected repository.`
- `409 Conflict` when uploading the same version

**What This Means:**

This error occurs when:
1. **The package version already exists in your CodeArtifact repository** - You've already published this version before
2. **The package version exists in an upstream repository** - Your CodeArtifact repository is connected to an external repository (like PyPI upstream), and a package with the same name and version exists there
3. **Package name conflict** - Another package with the same name and version exists in a connected repository

**Why "Externally Connected Repository"?**

CodeArtifact repositories can be connected to upstream repositories (like PyPI). When you try to publish a package version that exists in an upstream repository, CodeArtifact prevents the upload to avoid conflicts and maintain package integrity.

**Solutions:**

**Option 1: Increment the Version (Recommended)**

Update the version in `pyproject.toml`:

```toml
[project]
version = "0.0.2"  # Increment from 0.0.1
```

Then rebuild and publish:
```bash
uv build --wheel
# Use uv-publish wrapper with .pypirc, or explicit credentials
uvx uv-publish --repository codeartifact dist/ml_workbench-*.whl
# OR with explicit credentials:
# uv publish --publish-url <URL> --username aws --password $TOKEN dist/ml_workbench-*.whl
```

**Option 2: Delete the Existing Version (If Allowed)**

If your repository policy allows deletion and the version exists in your repository (not upstream):

```bash
aws codeartifact delete-package-versions \
    --domain $DOMAIN_NAME \
    --repository $REPOSITORY_NAME \
    --format pypi \
    --package ml-workbench \
    --versions 0.0.1 \
    --region $AWS_REGION
    --profile integration
```

**Note:** You cannot delete versions that exist only in upstream repositories.

**Option 3: Use a Different Package Name**

If the conflict is due to a name collision with an upstream package, consider renaming your package in `pyproject.toml`:

```toml
[project]
name = "ml-workbench-pheno"  # Add organization prefix
```

**Option 4: Check Repository Connections**

If you need to publish a version that conflicts with upstream, you may need to:
- Disconnect the upstream repository (if allowed by your organization)
- Use a different repository without upstream connections
- Contact your CodeArtifact administrator

**Prevention:**

- Always increment version numbers for new releases
- Use semantic versioning (e.g., 0.0.1 → 0.0.2 → 0.1.0)
- Check existing versions before publishing:
  ```bash
  aws codeartifact list-package-versions \
      --domain $DOMAIN_NAME \
      --repository $REPOSITORY_NAME \
      --format pypi \
      --package ml-workbench \
      --region $AWS_REGION
  ```

### Issue: Permission Denied

**Error**: `AccessDenied` or `403 Forbidden`

**Solution**: 
- Verify your AWS credentials have the required CodeArtifact permissions
- Check repository resource policies
- Ensure you're using the correct domain and repository names

### Issue: Cannot Find Package After Installation

**Error**: `Could not find a version that satisfies the requirement ml-workbench`

**Solution**:
- Verify CodeArtifact authentication: `aws codeartifact login --tool pip ...`
- Check the repository URL is correct
- Ensure the package was uploaded successfully
- Try using the full repository URL with `uv pip install --index-url <URL> ml-workbench`

### Issue: Build Fails

**Error**: Build errors during `uv build`

**Solution**:
- Ensure all dependencies are listed in `pyproject.toml`
- Check that `ml_workbench/__init__.py` exists
- Verify Python version matches `requires-python` in `pyproject.toml`
- Clean build artifacts: `rm -rf dist/ build/ *.egg-info`
- Ensure `uv` is up to date: `uv self update`

### Issue: "No indexes were found, can't use index: `codeartifact`"

**Error**: `error: No indexes were found, can't use index: 'codeartifact'`

**What This Means:**

UV does not natively read `.pypirc` files. The `--index` option in `uv publish` refers to indexes configured in UV's own configuration format (in `pyproject.toml` or `uv.toml`), not `.pypirc`.

**Solutions:**

**Option 1: Use `uv-publish` Wrapper (Recommended)**

The `uv-publish` wrapper can read `.pypirc` files:

```bash
# Use uv-publish wrapper instead of uv publish
uvx uv-publish --repository codeartifact dist/ml_workbench-*.whl
```

**Option 2: Use Explicit URL and Credentials**

Instead of using `--index`, use explicit URL and credentials:

```bash
# Get token
export CODEARTIFACT_TOKEN=$(aws codeartifact get-authorization-token \
    --domain $DOMAIN_NAME \
    --domain-owner $AWS_ACCOUNT_ID \
    --repository $REPOSITORY_NAME \
    --region $AWS_REGION \
    --query authorizationToken \
    --output text)

# Publish with explicit URL
uv publish \
    --publish-url https://$DOMAIN_NAME-$AWS_ACCOUNT_ID.d.codeartifact.$AWS_REGION.amazonaws.com/pypi/$REPOSITORY_NAME/ \
    --username aws \
    --password $CODEARTIFACT_TOKEN \
    dist/ml_workbench-*.whl
```

**Option 3: Configure UV Index in `pyproject.toml`**

You can configure UV indexes in `pyproject.toml` (though this is less common):

```toml
[tool.uv.index]
codeartifact = { url = "https://...", username = "aws", password = "..." }
```

However, this requires storing credentials in the config file, which is not recommended.

**Recommendation:** Use `uvx uv-publish` with `.pypirc` or use explicit credentials with `uv publish`.

---

## Summary Checklist

Before publishing, ensure:

- [ ] Version number updated in `pyproject.toml`
- [ ] Package builds successfully (`uv build --wheel`)
- [ ] All tests pass
- [ ] AWS credentials configured
- [ ] CodeArtifact domain and repository names confirmed
- [ ] Authentication token obtained (`aws codeartifact login`)
- [ ] Package uploaded successfully
- [ ] Package verified in CodeArtifact console
- [ ] Installation tested from a clean environment

---

## Additional Resources

- [AWS CodeArtifact User Guide](https://docs.aws.amazon.com/codeartifact/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Hatchling Documentation](https://hatch.pypa.io/)
- [uv Documentation](https://github.com/astral-sh/uv)

