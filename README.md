<div align="center">
  <h3 align="center">Lambda-Instructor</h3>
</div>

## About
__Lambda-Instructor__ is an experimental deployment of the text-embedding model [Instructor-Large](https://huggingface.co/hkunlp/instructor-large) on AWS Lambda.

_Instructor-Large_ is a model built by the NLP Group of The University of Hong Kong under the Apache-2.0 license and performs well on retrieval tasks (i.e. finding related documents for a given sentence). As of June-2023, it seems to be on a level with OpenAI's _text-embedding-ada-002_ across numerous benchmarks on the [Hugging Face leaderboard](https://huggingface.co/spaces/mteb/leaderboard).

__Potential Use Cases:__
* __Pair with local inference:__ Generate a large number of embeddings with _Instructor-Large_ on your local machine upfront (vs. paying for commercial APIs such as OpenAI's even for testing).
* __Data residency:__ Deploy the Lambda function in global AWS Regions such including Europe and the US.
* __Scalability:__ AWS Lambda scales virtually unlimited, without the overhead of managing servers.
* __Low-cost production inference:__ with AWS Lambda's per-request pricing vs. running a server 24/7.
* __Use with vector databases:__ such as [ChromaDB](https://github.com/chroma-core/chroma) or [Pinecone](https://www.pinecone.io/).

__Performance, Cost, and Limitations:__
* __Cold Start:__ The Lambda function has a cold start of about 150 seconds (with _instructor-base_ about 50s).
* __Inference:__ Consecutive request are processed in about 6 seconds per request (with _instructor-base_ about 3 seconds).
* __Max. Tokens:__ _Instructor-Large_ seems to be capped at a sequence length of 512 tokens (ca. 380 words), whereas OpenAI's _text-embedding-ada-002_ supports up to 8191 tokens (ca. 6000 words).
* __Cost:__ The AWS Lambda cost can be estimated at:
    * Configuration:
        * Region: eu-central-1 (Europe, Frankfurt)
        * Arm Price: $0.0000133334 for every GB-second
        * Requests: $0.20 per 1M requests
        * Memory Size: 10240 MB
    * Calculation:
        * Duration: $0.0000133334 * 10,24 GB * 6 seconds = 0.000819204096 / request
        * Requests: $0.20 / 1M requests = 0.0000002 / requests
        * Total = $0.0008194 / request
    * As of June 2023, that is pricier than OpenAI's Ada v2 at $0.0001/1K tokens after their [75% price reduction](https://openai.com/blog/function-calling-and-other-api-updates).

__Further improvements:__
Cost and Cold start could be further improved with [AWS Lambda Provisioned Concurrency](https://aws.amazon.com/lambda/pricing/#Provisioned_Concurrency_Pricing) and [AWS Compute Savings Plans](https://aws.amazon.com/savingsplans/compute-pricing/). Also check out the [AWS Calculator](https://calculator.aws/#/estimate?id=2d2b1f007079c40429f5e94c42f22c2af8003450) at 1M requests per month for this project.

## Deployment
### Prerequisites
* General AWS knowledge is helpful.
* You need to have [Docker](https://docs.docker.com/engine/install/) and [git-lfs](https://git-lfs.com/) installed locally.
* You need to have [aws-sam](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) installed locally and configured with your AWS account.
* An Arm-based local environment is recommended (Mac M1/M2). If you run into issues, try deploying via an Arm-based EC2 machine (guide below).

### Setup
We will download the instructor model locally, package the app in a Docker container and deploy it on an Arm-based Lambda function. We're using Arm as it is lower-cost with AWS and turned out to be faster.

1. Clone the repository
   ```sh
   git clone https://github.com/maxsagt/lambda-instructor.git
   ```
2. Clone the instructor-large model to the _./app/model_ folder (see https://huggingface.co/hkunlp/instructor-large?clone=true)
   ```sh
   git lfs install ./app/model
   git clone https://huggingface.co/hkunlp/instructor-large ./app/model
   ```
3. Build the docker container with aws-sam
    ```sh
    sam build --cached --parallel
    ```
4. Test locally with the sample payload in event.json.
    ```sh
    sam local invoke -e event.json
    ```
5. Deploy to AWS. Note that your AWS user or role needs (temporary) IAM permissions for AWS CloudFormation, Elastic Container Registry, S3, Lambda and IAM.
    ```sh
    sam deploy
    ```
6. Done. You will find a Lambda function in AWS that is ready for further configuration. For example:
    * Test the Lambda function in the Lambda console.
    * Configure a Lambda Function URL to directly use the Lambda function via a URL.
    * Add an API Gateway for more advanced API functionalities.

### Optional: Deploy via an Arm-based EC2 machine.
If you do not have an Arm machine at hand, or want to deploy within AWS for faster uploading of the docker container.

1. __Create an AWS instance:__
    * Tested on Ubuntu Server 22.04 LTS (HVM), SSD Volume Type, ami-0329d3839379bfd15, Architecture: 64-bit (Arm), Instance Type: t4g.medium, Storage: 20GiB gp3.
    * Make sure your VPC is public.
    * Start the instance.
    * Click on the instance and add an IAM role via Actions -> Security. The IAM Role needs IAM, S3, ECR, Cloudformation and Lambda access.
2. __Upload repository to remote AWS instance:__
    ```sh
    git clone https://github.com/maxsagt/lambda-instructor.git
    cd lambda-instructor
    zip -r deployment.zip . -x './app/model/*'
    PUBLIC_IPv4_DNS=ec2-x-xx-xxx-xxx.eu-central-1.compute.amazonaws.com
    scp -o StrictHostKeyChecking=no -i "../my_key.pem" ./deployment.zip ubuntu@$PUBLIC_IPv4_DNS:deployment.zip
    ```
3. __Log in to your instance and execute the sample deployment script.__
    ```sh
    ssh -o StrictHostKeyChecking=no -i "../my_key.pem" ubuntu@$PUBLIC_IPv4_DNS
    sudo apt install unzip
    unzip -o deployment.zip
    chmod +x sample_deployment.sh
    sudo bash -x sample_deployment.sh
    ```
4. __Build and deploy as per above.__ _If the command sam is not recognized, read the sam documentation [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)._
5. Don't forget to terminate the instance after use.

## Feedback
Feedback and contributions are welcome!
