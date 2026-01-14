# Amazon Connect L2 Construct library

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](https://github.com/netforbpo/aws-cdk-aws-construct-lib/blob/main/LICENSE)

This CDK Construct Library provides L2 constructs for Amazon Connect.

This is used in production internally. However, it is alpha and subject to breaking changes as better ways of managing resources are designed.

## Package Installation

### NPM

```
yarn add @netforbpo/aws-cdk-aws-connect-lib
# or
npm install @netforbpo/aws-cdk-aws-connect-lib
```

### PyPI

```
uv add netforbpo-aws-cdk-aws-connect-lib
# or
pip install netforbpo-aws-cdk-aws-connect-lib
```

## Basic Usage

### Typescript

```python
import * as connect from '@netforbpo/aws-cdk-aws-connect-lib';
import {
  aws_s3 as s3
} from '@aws-cdk';

// assuming `this` is your stack or other construct

const instance = new connect.Instance(this, 'myInstance', {
  identityManagementType: connect.IdentityManagementType.CONNECT_MANAGED,
  instanceAlias: 'my-instance-alias',
  telephonyConfig: {
    inboundCalls: true,
    outboundCalls: true,
  },
  otherConfig: {
    contactFlowLogs: true,
  }
});

const bucket = s3.Bucket(this, 'ConnectStorage');

instance.addStorageConfig(connect.SttorageConfig.buildS3(
    connect.StorageType.CALL_RECORDINGS,
    {
      bucket,
      prefix: 'call-recordings'
    }
));
```

### Python

```python
import aws_cdk_aws_connect_lib as connect
from aws_cdk import aws_s3 as s3

# Assuming `self` is your stack or other construct

self.instance = new connect.Instance(self, 'myInstance',
  identity_management_type=connect.IdentityManagementType.CONNECT_MANAGED,
  instance_alias='my-instance-alias',
  telephony_config=connect.TelephonyConfigProps(
    inbound_calls=True,
    outbound_calls=True,
  ),
  other_config=connect.OtherConfigProps(
    contact_flow_logs=True,
  )
)

self.bucket = s3.Bucket(stack, 'ConnectStorage')

self.instance.add_storage_config(
    connect.SttorageConfig.buildS3(
        resource_type=connect.StorageType.CALL_RECORDINGS,
        bucket=self.bucket,
        prefix='call-recordings'
    )
)
```

## locating resources

Currently only Instance has a fromLookup method to build an Instance object from an previousl created connect instance (from another stack, or manually).

All the other resources can be used against that looked-up instance.

The ability to look up other resources will be added in the future once a PR gets merged into core aws-cdk ( aws/aws-cdk-cli#1015 ).

### Example usage

```pthon
import aws_cdk_aws_connect_lib as connect

self.instance = connect.Instance.from_lookup(self, 'myInstance',
    instance_name='my-instance-alias'
    # instance_arn and instance_id are also available
)

# Assuming self.bucket is an S3 bucket
self.instance.add_storage_config(
    connect.SttorageConfig.buildS3(
        resource_type=connect.StorageType.CHAT_TRANSCRIPTS,
        bucket=self.bucket,
        prefix='chat-transcripts'
    )
)
```

## Associating Lex & Lambda bots

To associate a Lex Bot or Lambda Function to a connect instance there are two helper methods available on an instance (whether created or looked-up)

```python
import aws_cdk_aws_connect_lib as connect

# and to associate a Lex Bot or Lambda Function to the connect instance

# Assuming self.lex_bot is a Lex Bot Alias
self.instance.associate_lex_bot(self.lex_bot_alias)

# Assuming self.lambda_function is a Lambda Function or lambda function alias
self.instance.associate_function(self.lambda_function)
```
