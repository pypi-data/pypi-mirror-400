r'''
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
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_directoryservice as _aws_cdk_aws_directoryservice_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


class MicrosoftAD(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-managed-ad.MicrosoftAD",
):
    '''L2 Construct for AWS Managed Microsoft AD.'''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        domain_name: builtins.str,
        vpc: "_aws_cdk_aws_ec2_ceddda9d.IVpc",
        edition: typing.Optional[builtins.str] = None,
        enable_directory_data_access: typing.Optional[builtins.bool] = None,
        password: typing.Optional["_aws_cdk_aws_secretsmanager_ceddda9d.Secret"] = None,
        register_with_work_spaces: typing.Optional[builtins.bool] = None,
        short_name: typing.Optional[builtins.str] = None,
        vpc_subnets: typing.Optional[typing.Union["_aws_cdk_aws_ec2_ceddda9d.SubnetSelection", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: The fully qualified domain name for the AD directory (e.g. corp.example.com).
        :param vpc: VPC where the Microsoft AD will be created.
        :param edition: Edition of Microsoft AD (Standard or Enterprise). Default: Standard
        :param enable_directory_data_access: Enable Directory Data Service Access. Default: false
        :param password: The password for the directory administrator. If not provided, a secure random password will be generated. Default: - A secure random password is generated
        :param register_with_work_spaces: Register AD with WorkSpaces. Default: false
        :param short_name: Short name for the directory (e.g. CORP). Default: - derived from domain name
        :param vpc_subnets: Default: - Two subnets will be selected from different AZs
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91bbda56e3cca814e8ddc69395b1fb7a90c46704160f891f37d9073017a87eef)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MicrosoftADProps(
            domain_name=domain_name,
            vpc=vpc,
            edition=edition,
            enable_directory_data_access=enable_directory_data_access,
            password=password,
            register_with_work_spaces=register_with_work_spaces,
            short_name=short_name,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="directory")
    def directory(self) -> "_aws_cdk_aws_directoryservice_ceddda9d.CfnMicrosoftAD":
        '''The underlying CfnMicrosoftAD resource.'''
        return typing.cast("_aws_cdk_aws_directoryservice_ceddda9d.CfnMicrosoftAD", jsii.get(self, "directory"))

    @builtins.property
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        '''The ID of the directory.'''
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @builtins.property
    @jsii.member(jsii_name="dnsIps")
    def dns_ips(self) -> typing.List[builtins.str]:
        '''The DNS addresses of the directory.'''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsIps"))

    @builtins.property
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> builtins.str:
        '''The secret containing the directory administrator password.'''
        return typing.cast(builtins.str, jsii.get(self, "secretArn"))


@jsii.data_type(
    jsii_type="cdk-managed-ad.MicrosoftADProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "vpc": "vpc",
        "edition": "edition",
        "enable_directory_data_access": "enableDirectoryDataAccess",
        "password": "password",
        "register_with_work_spaces": "registerWithWorkSpaces",
        "short_name": "shortName",
        "vpc_subnets": "vpcSubnets",
    },
)
class MicrosoftADProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        vpc: "_aws_cdk_aws_ec2_ceddda9d.IVpc",
        edition: typing.Optional[builtins.str] = None,
        enable_directory_data_access: typing.Optional[builtins.bool] = None,
        password: typing.Optional["_aws_cdk_aws_secretsmanager_ceddda9d.Secret"] = None,
        register_with_work_spaces: typing.Optional[builtins.bool] = None,
        short_name: typing.Optional[builtins.str] = None,
        vpc_subnets: typing.Optional[typing.Union["_aws_cdk_aws_ec2_ceddda9d.SubnetSelection", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for MicrosoftAD.

        :param domain_name: The fully qualified domain name for the AD directory (e.g. corp.example.com).
        :param vpc: VPC where the Microsoft AD will be created.
        :param edition: Edition of Microsoft AD (Standard or Enterprise). Default: Standard
        :param enable_directory_data_access: Enable Directory Data Service Access. Default: false
        :param password: The password for the directory administrator. If not provided, a secure random password will be generated. Default: - A secure random password is generated
        :param register_with_work_spaces: Register AD with WorkSpaces. Default: false
        :param short_name: Short name for the directory (e.g. CORP). Default: - derived from domain name
        :param vpc_subnets: Default: - Two subnets will be selected from different AZs
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1f229b8372ad15049a55d9813128b157d2902b5bf7c42a7880e2a29a57538e0)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument edition", value=edition, expected_type=type_hints["edition"])
            check_type(argname="argument enable_directory_data_access", value=enable_directory_data_access, expected_type=type_hints["enable_directory_data_access"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument register_with_work_spaces", value=register_with_work_spaces, expected_type=type_hints["register_with_work_spaces"])
            check_type(argname="argument short_name", value=short_name, expected_type=type_hints["short_name"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_name": domain_name,
            "vpc": vpc,
        }
        if edition is not None:
            self._values["edition"] = edition
        if enable_directory_data_access is not None:
            self._values["enable_directory_data_access"] = enable_directory_data_access
        if password is not None:
            self._values["password"] = password
        if register_with_work_spaces is not None:
            self._values["register_with_work_spaces"] = register_with_work_spaces
        if short_name is not None:
            self._values["short_name"] = short_name
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''The fully qualified domain name for the AD directory (e.g. corp.example.com).'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> "_aws_cdk_aws_ec2_ceddda9d.IVpc":
        '''VPC where the Microsoft AD will be created.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast("_aws_cdk_aws_ec2_ceddda9d.IVpc", result)

    @builtins.property
    def edition(self) -> typing.Optional[builtins.str]:
        '''Edition of Microsoft AD (Standard or Enterprise).

        :default: Standard
        '''
        result = self._values.get("edition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_directory_data_access(self) -> typing.Optional[builtins.bool]:
        '''Enable Directory Data Service Access.

        :default: false
        '''
        result = self._values.get("enable_directory_data_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def password(
        self,
    ) -> typing.Optional["_aws_cdk_aws_secretsmanager_ceddda9d.Secret"]:
        '''The password for the directory administrator.

        If not provided, a secure random password will be generated.

        :default: - A secure random password is generated
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional["_aws_cdk_aws_secretsmanager_ceddda9d.Secret"], result)

    @builtins.property
    def register_with_work_spaces(self) -> typing.Optional[builtins.bool]:
        '''Register AD with WorkSpaces.

        :default: false
        '''
        result = self._values.get("register_with_work_spaces")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def short_name(self) -> typing.Optional[builtins.str]:
        '''Short name for the directory (e.g. CORP).

        :default: - derived from domain name
        '''
        result = self._values.get("short_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_subnets(
        self,
    ) -> typing.Optional["_aws_cdk_aws_ec2_ceddda9d.SubnetSelection"]:
        '''
        :default: - Two subnets will be selected from different AZs
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional["_aws_cdk_aws_ec2_ceddda9d.SubnetSelection"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftADProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "MicrosoftAD",
    "MicrosoftADProps",
]

publication.publish()

def _typecheckingstub__91bbda56e3cca814e8ddc69395b1fb7a90c46704160f891f37d9073017a87eef(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    edition: typing.Optional[builtins.str] = None,
    enable_directory_data_access: typing.Optional[builtins.bool] = None,
    password: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret] = None,
    register_with_work_spaces: typing.Optional[builtins.bool] = None,
    short_name: typing.Optional[builtins.str] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1f229b8372ad15049a55d9813128b157d2902b5bf7c42a7880e2a29a57538e0(
    *,
    domain_name: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    edition: typing.Optional[builtins.str] = None,
    enable_directory_data_access: typing.Optional[builtins.bool] = None,
    password: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.Secret] = None,
    register_with_work_spaces: typing.Optional[builtins.bool] = None,
    short_name: typing.Optional[builtins.str] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
