# AWS Setup Notes & Log

## Resource Identifiers
- **Region**: ap-south-1
- **AWS Account ID**: 049681811107
- **S3 Bucket**: image-classifier-dvc-ks-948215
- **IAM User**: dvc-ci-user
- **EC2 Key Pair**: image-classifier-key
- **EC2 Security Group**: sg-05266645655d69bda
- **EC2 Instance ID**: i-09a2e2d2bd3f29168
- **EC2 Public IPv4**: 13.232.17.213

---

## Commands Executed

### Step 0: Preflight Checks
- `aws --version` -> `aws-cli/2.37.0 Python/3.14.6 Windows/11 exe/AMD64`
- `aws sts get-caller-identity` -> Account `049681811107`, Root ARN
- `git --version` -> `git version 2.54.0.windows.1`
- `docker --version` -> `Docker version 29.6.2`

### Step 1: S3 Bucket & IAM User for DVC
- `aws s3api create-bucket --bucket image-classifier-dvc-ks-948215 --region ap-south-1 --create-bucket-configuration LocationConstraint=ap-south-1`
- `aws s3api put-public-access-block --bucket image-classifier-dvc-ks-948215 --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true`
- `aws s3api put-bucket-encryption --bucket image-classifier-dvc-ks-948215 --server-side-encryption-configuration ...` (AES256)
- `aws iam create-user --user-name dvc-ci-user`
- `aws iam put-user-policy --user-name dvc-ci-user --policy-name DvcS3AccessPolicy --policy-document ...`
- `aws iam create-access-key --user-name dvc-ci-user --output json | Out-File -FilePath C:\Users\krisha\.aws\dvc-ci-user-credentials.json -Encoding utf8`

### Step 2: Configure DVC Remote
- `dvc remote add -d s3remote s3://image-classifier-dvc-ks-948215/dvcstore`
- `dvc remote modify s3remote region ap-south-1`
- `dvc repro` (reproduced all pipeline stages with 97.22% test accuracy)
- `dvc push` (1,801 objects pushed to S3)
- `aws s3 ls s3://image-classifier-dvc-ks-948215/dvcstore --recursive`

### Step 3: EC2 Instance & Docker Setup
- `aws ec2 create-key-pair --key-name image-classifier-key --region ap-south-1 --query 'KeyMaterial' --output text | Set-Content -Path 'C:\Users\krisha\.ssh\image-classifier-key.pem' -Encoding ascii`
- `icacls C:\Users\krisha\.ssh\image-classifier-key.pem /reset && icacls ... /inheritance:r && icacls ... /grant:r krisha\krisha:R`
- `aws ec2 create-security-group --group-name image-classifier-sg --description 'Security group for image-classifier web app and SSH' --vpc-id vpc-015545d8060cdd043 --region ap-south-1` -> `sg-05266645655d69bda`
- `aws ec2 authorize-security-group-ingress --group-id sg-05266645655d69bda --region ap-south-1 --protocol tcp --port 22 --cidr 0.0.0.0/0`
- `aws ec2 authorize-security-group-ingress --group-id sg-05266645655d69bda --region ap-south-1 --protocol tcp --port 80 --cidr 0.0.0.0/0`
- `aws ec2 run-instances --image-id ami-0cede6fe40e6ac719 --instance-type t3.micro --key-name image-classifier-key --security-group-ids sg-05266645655d69bda ...` -> `i-09a2e2d2bd3f29168` (Public IP: `13.232.17.213`)
- `ssh -i C:\Users\krisha\.ssh\image-classifier-key.pem ec2-user@13.232.17.213 'sudo dnf install -y docker && sudo systemctl enable --now docker && sudo usermod -aG docker ec2-user'`
- `ssh -i C:\Users\krisha\.ssh\image-classifier-key.pem ec2-user@13.232.17.213 'docker ps'`

---

## Challenges Encountered & Fixes

1. **Missing Git refs directory**:
   - *Problem*: `git status` gave `fatal: not a git repository`.
   - *Cause*: `.git` was initialized without `refs/heads` and `refs/tags` directories.
   - *Fix*: Created the directories `.git/refs/heads` and `.git/refs/tags`, successfully recovering the repository on branch `main`.

2. **Application Control Policy blocking pip launcher**:
   - *Problem*: Running `.\.venv\Scripts\pip.exe` failed with `An Application Control policy has blocked this file`.
   - *Cause*: Windows Defender Application Control / AppLocker restricted unsigned/generic stub binaries inside user folders.
   - *Fix*: Executed Python module directly via `.\.venv\Scripts\python.exe -m pip`.

3. **Local Router DNS Failure for PyPI**:
   - *Problem*: `pip install` timed out with `getaddrinfo failed: /simple/fastapi/`.
   - *Cause*: Local network router (`192.168.0.1`) returned `RCODE_SERVER_FAILURE` for `pypi.org`, whereas public DNS (`8.8.8.8`) resolves `pypi.org` and `files.pythonhosted.org` instantly.
   - *Fix*: Documented need to update adapter DNS to `8.8.8.8` or install DVC standalone via winget.

4. **Missing GitHub CLI (`gh`) and DVC**:
   - *Problem*: Neither `gh` nor `dvc` were found in PATH.
   - *Fix*: Provided installation steps for GitHub CLI (`winget install --id GitHub.cli` or official installer) and DVC (`winget install --id Iterative.DVC`).

5. **Windows OpenSSH UNPROTECTED PRIVATE KEY FILE**:
   - *Problem*: SSH client failed with `Permissions for image-classifier-key.pem are too open: Bad permissions`.
   - *Cause*: Windows NTFS inheritance granted permissions to SYSTEM, Administrators, and generic machine groups.
   - *Fix*: Stripped inheritance and removed all principals except explicit read permission for user (`icacls ... /grant:r krisha\krisha:R`).

6. **GitHub Actions Runner Smoke Test IPv6 Resolution**:
   - *Problem*: CI job 2 (*Build and push Docker image*) failed at step *Smoke-test the container* with `curl: (7) Failed to connect to localhost port 8000`.
   - *Cause*: GitHub-hosted Ubuntu runners resolve `localhost` to IPv6 (`::1`), whereas Docker binds host ports to IPv4 (`0.0.0.0:8000`), rejecting IPv6 traffic.
   - *Fix*: Changed test URL from `http://localhost:8000/health` to explicit IPv4 `http://127.0.0.1:8000/health` and added `sleep 3` for graceful server startup.
