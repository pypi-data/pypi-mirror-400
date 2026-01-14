# cdk-managed-ad

This is a level 2ish/3ish cdk construct library for deployment and management of a AWS Managed Microsoft AD.

## Usage

The `MicrosoftAD` construct creates an AWS Managed Microsoft AD directory in your VPC. Here's how to use it:

```python
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as sm from 'aws-cdk-lib/aws-secretsmanager';
import { MicrosoftAD } from 'cdk-managed-ad';

const stack = new cdk.Stack();

// Create a VPC (or use an existing one)
const vpc = new ec2.Vpc(stack, 'VPC', {
  maxAzs: 2,
});

// Existing Secret ARN of password as string (not JSON). Username will be NETBIOS\admin
const EXISTING_SECRET_ARN = string "arn:aws:secretsmanager:YOUR_REGION:YOUR_ACCOUNT_ID:secret:YOUR_EXISTING_SECRET_ARN"

// Create the Microsoft AD
const ad = new MicrosoftAD(stack, 'CorporateAD', {
  domainName: 'corp.example.com',
  password: sm.Secret.fromSecretCompleteArn(self, "ExistingSecret", EXISTING_SECRET_ARN),
  vpc: vpc,
  edition: 'Standard', // or 'Enterprise'
  shortName: 'CORP', // optional. This would be your NetBIOS name.
  enableDirectoryDataAccess: true, // optional, . Enables Directory Service Data Access
});

// The directory ID and DNS IPs are available as properties
console.log('Directory ID:', ad.directoryId);
console.log('DNS IPs:', ad.dnsIps);
console.log('Admin Password Secret ARN:', ad.secretArn);
```

### Properties

* `domainName` (required): The fully qualified domain name for the AD directory (e.g., corp.example.com)
* `password` (optional): The an AWS Secrets Manager ARN for the directory administrator (if not provided, a secure random password will be generated)
* `vpc` (required): VPC where the Microsoft AD will be created (must have at least 2 subnets in different AZs)
* `edition` (optional): Edition of Microsoft AD ('Standard' or 'Enterprise', defaults to 'Standard')
* `shortName` (optional): Short name for the directory (e.g., CORP)
* `vpcSubnets` (optional): Specific subnet selection for the AD (defaults to two subnets from different AZs)
* `enableDirectoryDataAccess` (optional) - Deploy custom resource to enable the Directory Service Data API. Default is false.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
