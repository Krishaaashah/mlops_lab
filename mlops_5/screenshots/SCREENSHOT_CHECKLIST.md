# Report Evidence & Screenshot Guide

This folder contains pre-captured terminal evidence and exact links/commands for the screenshots required in your report.

---

### Screenshot Checklist

| # | Evidence Item | Exact Console URL or Command | What to Capture in Screenshot | Pre-Captured Evidence File |
|---|---|---|---|---|
| **1** | **DVC Pipeline** | `dvc dag`<br>`dvc metrics show` | Terminal showing the ASCII pipeline graph and accuracy metrics (97.22%). | [01_dvc_pipeline_dag_metrics.txt](01_dvc_pipeline_dag_metrics.txt) |
| **2** | **GitHub Actions CI/CD** | [Workflow Run #38723494150](https://github.com/Krishaaashah/mlops_lab/actions/runs/38723494150) | The GitHub Actions workflow run page displaying the 3 green checkmarks (`pipeline`, `docker`, `deploy`). | [02_github_actions_green_run.png](02_github_actions_green_run.png) |
| **3** | **AWS S3 Remote Storage** | [AWS S3 Console](https://ap-south-1.console.aws.amazon.com/s3/buckets/image-classifier-dvc-ks-948215?region=ap-south-1&bucketType=general&tab=objects)<br>Or: `aws s3 ls s3://image-classifier-dvc-ks-948215/dvcstore/ --recursive` | S3 console showing the `dvcstore/` prefix with 1,801 objects, or terminal listing. | [03_aws_s3_bucket_contents.txt](03_aws_s3_bucket_contents.txt) |
| **4** | **Docker Build & Run (Local)** | `docker build -t image-classifier .`<br>`docker images`<br>`docker run --rm -p 8000:8000 image-classifier` | Terminal showing the Docker image build steps, tagged image list, and container startup. | Local terminal output / CI Runner |
| **5** | **AWS EC2 Instance & Remote Docker** | [AWS EC2 Console](https://ap-south-1.console.aws.amazon.com/ec2/home?region=ap-south-1#InstanceDetails:instanceId=i-09a2e2d2bd3f29168)<br>SSH: `ssh -i ~/.ssh/image-classifier-key.pem ec2-user@13.232.17.213 "docker ps"` | EC2 Console details showing Instance ID `i-09a2e2d2bd3f29168`, Public IP `13.232.17.213`, and terminal showing `docker ps` over SSH. | [05_ec2_details_and_ssh_docker.txt](05_ec2_details_and_ssh_docker.txt) |
| **6** | **Live Web App & Prediction** | [http://13.232.17.213](http://13.232.17.213)<br>Swagger: [http://13.232.17.213/docs](http://13.232.17.213/docs) | Browser showing the handwritten digit canvas/upload interface with a prediction and probability bars. | [06_web_app_home.png](06_web_app_home.png), [06_web_app_prediction.png](06_web_app_prediction.png) |

---

### Cloud Resource Reference
- **AWS Region**: `ap-south-1` (Mumbai)
- **S3 Bucket**: `image-classifier-dvc-ks-948215`
- **IAM User**: `dvc-ci-user`
- **EC2 Instance ID**: `i-09a2e2d2bd3f29168`
- **EC2 Public IPv4**: `13.232.17.213`
- **EC2 Key Pair**: `image-classifier-key` (saved at `C:\Users\krisha\.ssh\image-classifier-key.pem`)
- **Security Group**: `sg-05266645655d69bda` (`image-classifier-sg`)
