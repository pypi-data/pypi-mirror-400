r'''
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_connect as _aws_cdk_aws_connect_ceddda9d
import aws_cdk.aws_kinesis as _aws_cdk_aws_kinesis_ceddda9d
import aws_cdk.aws_kinesisfirehose as _aws_cdk_aws_kinesisfirehose_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.interfaces.aws_lex as _aws_cdk_interfaces_aws_lex_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ContactFlowLookupOptions",
    jsii_struct_bases=[],
    name_mapping={
        "contact_flow_arn": "contactFlowArn",
        "contact_flow_name": "contactFlowName",
        "instance_arn": "instanceArn",
    },
)
class ContactFlowLookupOptions:
    def __init__(
        self,
        *,
        contact_flow_arn: typing.Optional[builtins.str] = None,
        contact_flow_name: typing.Optional[builtins.str] = None,
        instance_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param contact_flow_arn: 
        :param contact_flow_name: 
        :param instance_arn: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__612add7e7784dbb2fdd2d884a3166a6f11ec1ab27dcd6a16d3a3f7c4437013fb)
            check_type(argname="argument contact_flow_arn", value=contact_flow_arn, expected_type=type_hints["contact_flow_arn"])
            check_type(argname="argument contact_flow_name", value=contact_flow_name, expected_type=type_hints["contact_flow_name"])
            check_type(argname="argument instance_arn", value=instance_arn, expected_type=type_hints["instance_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if contact_flow_arn is not None:
            self._values["contact_flow_arn"] = contact_flow_arn
        if contact_flow_name is not None:
            self._values["contact_flow_name"] = contact_flow_name
        if instance_arn is not None:
            self._values["instance_arn"] = instance_arn

    @builtins.property
    def contact_flow_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("contact_flow_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contact_flow_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("contact_flow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContactFlowLookupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ContactFlowModuleLookupOptions",
    jsii_struct_bases=[],
    name_mapping={
        "contact_flow_module_arn": "contactFlowModuleArn",
        "contact_flow_module_name": "contactFlowModuleName",
        "instance_arn": "instanceArn",
    },
)
class ContactFlowModuleLookupOptions:
    def __init__(
        self,
        *,
        contact_flow_module_arn: typing.Optional[builtins.str] = None,
        contact_flow_module_name: typing.Optional[builtins.str] = None,
        instance_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param contact_flow_module_arn: 
        :param contact_flow_module_name: 
        :param instance_arn: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30462058666bbbe70edb9e8e93fdd0b547c930d10abd2e220810139342294c55)
            check_type(argname="argument contact_flow_module_arn", value=contact_flow_module_arn, expected_type=type_hints["contact_flow_module_arn"])
            check_type(argname="argument contact_flow_module_name", value=contact_flow_module_name, expected_type=type_hints["contact_flow_module_name"])
            check_type(argname="argument instance_arn", value=instance_arn, expected_type=type_hints["instance_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if contact_flow_module_arn is not None:
            self._values["contact_flow_module_arn"] = contact_flow_module_arn
        if contact_flow_module_name is not None:
            self._values["contact_flow_module_name"] = contact_flow_module_name
        if instance_arn is not None:
            self._values["instance_arn"] = instance_arn

    @builtins.property
    def contact_flow_module_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("contact_flow_module_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contact_flow_module_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("contact_flow_module_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContactFlowModuleLookupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ContactFlowModuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "instance": "instance",
        "name": "name",
        "description": "description",
        "state": "state",
    },
)
class ContactFlowModuleProps:
    def __init__(
        self,
        *,
        content: builtins.str,
        instance: "IInstance",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        state: typing.Optional["ContactFlowModuleState"] = None,
    ) -> None:
        '''
        :param content: 
        :param instance: 
        :param name: 
        :param description: 
        :param state: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b31e7ecb7c01891c8e66356be42d6f920eaa88baba508eeaa92678ebe46c93dc)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
            "instance": instance,
            "name": name,
        }
        if description is not None:
            self._values["description"] = description
        if state is not None:
            self._values["state"] = state

    @builtins.property
    def content(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance(self) -> "IInstance":
        '''
        :stability: experimental
        '''
        result = self._values.get("instance")
        assert result is not None, "Required property 'instance' is missing"
        return typing.cast("IInstance", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional["ContactFlowModuleState"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("state")
        return typing.cast(typing.Optional["ContactFlowModuleState"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContactFlowModuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ContactFlowModuleState")
class ContactFlowModuleState(enum.Enum):
    '''
    :stability: experimental
    '''

    ACTIVE = "ACTIVE"
    '''
    :stability: experimental
    '''
    ARCHIVED = "ARCHIVED"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ContactFlowProps",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "instance": "instance",
        "name": "name",
        "type": "type",
        "description": "description",
        "state": "state",
    },
)
class ContactFlowProps:
    def __init__(
        self,
        *,
        content: builtins.str,
        instance: "IInstance",
        name: builtins.str,
        type: "ContactFlowType",
        description: typing.Optional[builtins.str] = None,
        state: typing.Optional["ContactFlowState"] = None,
    ) -> None:
        '''
        :param content: 
        :param instance: 
        :param name: 
        :param type: 
        :param description: 
        :param state: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__840f428237fdaa4d433c15ac2450573484f0b9d381e51f0f5c49818f6a902552)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
            "instance": instance,
            "name": name,
            "type": type,
        }
        if description is not None:
            self._values["description"] = description
        if state is not None:
            self._values["state"] = state

    @builtins.property
    def content(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance(self) -> "IInstance":
        '''
        :stability: experimental
        '''
        result = self._values.get("instance")
        assert result is not None, "Required property 'instance' is missing"
        return typing.cast("IInstance", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> "ContactFlowType":
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("ContactFlowType", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional["ContactFlowState"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("state")
        return typing.cast(typing.Optional["ContactFlowState"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContactFlowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ContactFlowState")
class ContactFlowState(enum.Enum):
    '''
    :stability: experimental
    '''

    ACTIVE = "ACTIVE"
    '''
    :stability: experimental
    '''
    ARCHIVED = "ARCHIVED"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ContactFlowType")
class ContactFlowType(enum.Enum):
    '''
    :stability: experimental
    '''

    CONTACT_FLOW = "CONTACT_FLOW"
    '''
    :stability: experimental
    '''
    CUSTOMER_QUEUE = "CUSTOMER_QUEUE"
    '''
    :stability: experimental
    '''
    CUSTOMER_HOLD = "CUSTOMER_HOLD"
    '''
    :stability: experimental
    '''
    CUSTOMER_WHISPER = "CUSTOMER_WHISPER"
    '''
    :stability: experimental
    '''
    AGENT_HOLD = "AGENT_HOLD"
    '''
    :stability: experimental
    '''
    AGENT_WHISPER = "AGENT_WHISPER"
    '''
    :stability: experimental
    '''
    OUTBOUND_WHISPER = "OUTBOUND_WHISPER"
    '''
    :stability: experimental
    '''
    AGENT_TRANSFER = "AGENT_TRANSFER"
    '''
    :stability: experimental
    '''
    QUEUE_TRANSFER = "QUEUE_TRANSFER"
    '''
    :stability: experimental
    '''
    CAMPAIGN = "CAMPAIGN"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.EmailAddressProps",
    jsii_struct_bases=[],
    name_mapping={
        "email_address": "emailAddress",
        "instance": "instance",
        "aliases": "aliases",
        "description": "description",
        "display_name": "displayName",
    },
)
class EmailAddressProps:
    def __init__(
        self,
        *,
        email_address: builtins.str,
        instance: "IInstance",
        aliases: typing.Optional[typing.Sequence["IEmailAddress"]] = None,
        description: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param email_address: (experimental) The email address.
        :param instance: (experimental) The AWS connect instance to attach the email address to.
        :param aliases: (experimental) The aliases for the email address.
        :param description: (experimental) A description of the email address.
        :param display_name: (experimental) The display name of the email address.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab1e0b61936fc552f9cdf849545caa3f1818ce11a90da643054e86d5bbc552c8)
            check_type(argname="argument email_address", value=email_address, expected_type=type_hints["email_address"])
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
            check_type(argname="argument aliases", value=aliases, expected_type=type_hints["aliases"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email_address": email_address,
            "instance": instance,
        }
        if aliases is not None:
            self._values["aliases"] = aliases
        if description is not None:
            self._values["description"] = description
        if display_name is not None:
            self._values["display_name"] = display_name

    @builtins.property
    def email_address(self) -> builtins.str:
        '''(experimental) The email address.

        :stability: experimental
        '''
        result = self._values.get("email_address")
        assert result is not None, "Required property 'email_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance(self) -> "IInstance":
        '''(experimental) The AWS connect instance to attach the email address to.

        :stability: experimental
        '''
        result = self._values.get("instance")
        assert result is not None, "Required property 'instance' is missing"
        return typing.cast("IInstance", result)

    @builtins.property
    def aliases(self) -> typing.Optional[typing.List["IEmailAddress"]]:
        '''(experimental) The aliases for the email address.

        :stability: experimental
        '''
        result = self._values.get("aliases")
        return typing.cast(typing.Optional[typing.List["IEmailAddress"]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description of the email address.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The display name of the email address.

        :stability: experimental
        '''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmailAddressProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.HoursOfOperationDayOfWeek")
class HoursOfOperationDayOfWeek(enum.Enum):
    '''
    :stability: experimental
    '''

    SUNDAY = "SUNDAY"
    '''
    :stability: experimental
    '''
    MONDAY = "MONDAY"
    '''
    :stability: experimental
    '''
    TUESDAY = "TUESDAY"
    '''
    :stability: experimental
    '''
    WEDNESDAY = "WEDNESDAY"
    '''
    :stability: experimental
    '''
    THURSDAY = "THURSDAY"
    '''
    :stability: experimental
    '''
    FRIDAY = "FRIDAY"
    '''
    :stability: experimental
    '''
    SATURDAY = "SATURDAY"
    '''
    :stability: experimental
    '''


class HoursOfOperationDefinition(
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.HoursOfOperationDefinition",
):
    '''
    :stability: experimental
    '''

    @jsii.member(jsii_name="dayOfWeek")
    @builtins.classmethod
    def day_of_week(
        cls,
        day: "HoursOfOperationDayOfWeek",
        start_time: builtins.str,
        end_time: builtins.str,
    ) -> "HoursOfOperationDefinition":
        '''
        :param day: -
        :param start_time: -
        :param end_time: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e2a14b3b922288969469f29db5056b9c306fc5210950f68fdf4695585aac863)
            check_type(argname="argument day", value=day, expected_type=type_hints["day"])
            check_type(argname="argument start_time", value=start_time, expected_type=type_hints["start_time"])
            check_type(argname="argument end_time", value=end_time, expected_type=type_hints["end_time"])
        return typing.cast("HoursOfOperationDefinition", jsii.sinvoke(cls, "dayOfWeek", [day, start_time, end_time]))

    @jsii.member(jsii_name="asConfig")
    def as_config(
        self,
    ) -> typing.Union["_aws_cdk_aws_connect_ceddda9d.CfnHoursOfOperation.HoursOfOperationConfigProperty", "_aws_cdk_aws_connect_ceddda9d.CfnHoursOfOperation.HoursOfOperationOverrideConfigProperty"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Union["_aws_cdk_aws_connect_ceddda9d.CfnHoursOfOperation.HoursOfOperationConfigProperty", "_aws_cdk_aws_connect_ceddda9d.CfnHoursOfOperation.HoursOfOperationOverrideConfigProperty"], jsii.invoke(self, "asConfig", []))

    @jsii.member(jsii_name="splitTime")
    def split_time(
        self,
        time: builtins.str,
    ) -> "_aws_cdk_aws_connect_ceddda9d.CfnHoursOfOperation.HoursOfOperationTimeSliceProperty":
        '''
        :param time: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a0d730f5d911cfdb1ca8e31ea08431cd37de560378361b10d9b6963a7493fb1)
            check_type(argname="argument time", value=time, expected_type=type_hints["time"])
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnHoursOfOperation.HoursOfOperationTimeSliceProperty", jsii.invoke(self, "splitTime", [time]))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "type"))


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.HoursOfOperationLookupOptions",
    jsii_struct_bases=[],
    name_mapping={
        "instance_arn": "instanceArn",
        "hours_of_operation_arn": "hoursOfOperationArn",
        "hours_of_operation_name": "hoursOfOperationName",
    },
)
class HoursOfOperationLookupOptions:
    def __init__(
        self,
        *,
        instance_arn: builtins.str,
        hours_of_operation_arn: typing.Optional[builtins.str] = None,
        hours_of_operation_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance_arn: 
        :param hours_of_operation_arn: 
        :param hours_of_operation_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c58bd826778475e54a81b53753c3b0be186cec7b65ba62eca6af04b12fedba3)
            check_type(argname="argument instance_arn", value=instance_arn, expected_type=type_hints["instance_arn"])
            check_type(argname="argument hours_of_operation_arn", value=hours_of_operation_arn, expected_type=type_hints["hours_of_operation_arn"])
            check_type(argname="argument hours_of_operation_name", value=hours_of_operation_name, expected_type=type_hints["hours_of_operation_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_arn": instance_arn,
        }
        if hours_of_operation_arn is not None:
            self._values["hours_of_operation_arn"] = hours_of_operation_arn
        if hours_of_operation_name is not None:
            self._values["hours_of_operation_name"] = hours_of_operation_name

    @builtins.property
    def instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_arn")
        assert result is not None, "Required property 'instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hours_of_operation_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("hours_of_operation_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hours_of_operation_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("hours_of_operation_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HoursOfOperationLookupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.HoursOfOperationProps",
    jsii_struct_bases=[],
    name_mapping={
        "instance": "instance",
        "name": "name",
        "definitions": "definitions",
        "time_zone": "timeZone",
    },
)
class HoursOfOperationProps:
    def __init__(
        self,
        *,
        instance: "IInstance",
        name: builtins.str,
        definitions: typing.Optional[typing.Sequence["HoursOfOperationDefinition"]] = None,
        time_zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance: (experimental) The AWS connect instance to attach the hours of operation to.
        :param name: (experimental) The name of the hours of operation.
        :param definitions: (experimental) the set of definitions for the hours of operation.
        :param time_zone: (experimental) Timezone to define the hours of operation in. Defaults to UTC.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebc62e22f5715fb189129a4377a59686c2ff01421d1ab7ced6b38ca63d8e8085)
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument definitions", value=definitions, expected_type=type_hints["definitions"])
            check_type(argname="argument time_zone", value=time_zone, expected_type=type_hints["time_zone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance": instance,
            "name": name,
        }
        if definitions is not None:
            self._values["definitions"] = definitions
        if time_zone is not None:
            self._values["time_zone"] = time_zone

    @builtins.property
    def instance(self) -> "IInstance":
        '''(experimental) The AWS connect instance to attach the hours of operation to.

        :stability: experimental
        '''
        result = self._values.get("instance")
        assert result is not None, "Required property 'instance' is missing"
        return typing.cast("IInstance", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the hours of operation.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def definitions(self) -> typing.Optional[typing.List["HoursOfOperationDefinition"]]:
        '''(experimental) the set of definitions for the hours of operation.

        :stability: experimental
        '''
        result = self._values.get("definitions")
        return typing.cast(typing.Optional[typing.List["HoursOfOperationDefinition"]], result)

    @builtins.property
    def time_zone(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timezone to define the hours of operation in.

        Defaults to UTC.

        :stability: experimental
        '''
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HoursOfOperationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IContactFlow")
class IContactFlow(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="contactFlowArn")
    def contact_flow_arn(self) -> builtins.str:
        '''(experimental) The ARN of the flow.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="contactFlowName")
    def contact_flow_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...


class _IContactFlowProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IContactFlow"

    @builtins.property
    @jsii.member(jsii_name="contactFlowArn")
    def contact_flow_arn(self) -> builtins.str:
        '''(experimental) The ARN of the flow.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "contactFlowArn"))

    @builtins.property
    @jsii.member(jsii_name="contactFlowName")
    def contact_flow_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "contactFlowName"))

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IContactFlow).__jsii_proxy_class__ = lambda : _IContactFlowProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IContactFlowModule")
class IContactFlowModule(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="contactFlowModuleArn")
    def contact_flow_module_arn(self) -> builtins.str:
        '''(experimental) The ARN of the flow.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="contactFlowModuleName")
    def contact_flow_module_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...


class _IContactFlowModuleProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IContactFlowModule"

    @builtins.property
    @jsii.member(jsii_name="contactFlowModuleArn")
    def contact_flow_module_arn(self) -> builtins.str:
        '''(experimental) The ARN of the flow.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "contactFlowModuleArn"))

    @builtins.property
    @jsii.member(jsii_name="contactFlowModuleName")
    def contact_flow_module_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "contactFlowModuleName"))

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IContactFlowModule).__jsii_proxy_class__ = lambda : _IContactFlowModuleProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IEmailAddress")
class IEmailAddress(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="emailAddressArn")
    def email_address_arn(self) -> builtins.str:
        '''(experimental) The ARN of the email address.

        :stability: experimental
        '''
        ...


class _IEmailAddressProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IEmailAddress"

    @builtins.property
    @jsii.member(jsii_name="emailAddressArn")
    def email_address_arn(self) -> builtins.str:
        '''(experimental) The ARN of the email address.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "emailAddressArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEmailAddress).__jsii_proxy_class__ = lambda : _IEmailAddressProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IHierarchyGroup")
class IHierarchyGroup(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="hierarchyGroupArn")
    def hierarchy_group_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...


class _IHierarchyGroupProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IHierarchyGroup"

    @builtins.property
    @jsii.member(jsii_name="hierarchyGroupArn")
    def hierarchy_group_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "hierarchyGroupArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHierarchyGroup).__jsii_proxy_class__ = lambda : _IHierarchyGroupProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IHoursOfOperation")
class IHoursOfOperation(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="hoursOfOperationArn")
    def hours_of_operation_arn(self) -> builtins.str:
        '''(experimental) The ARN of the hours of operation.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''(experimental) The ARN of the attached instance.

        :stability: experimental
        '''
        ...


class _IHoursOfOperationProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IHoursOfOperation"

    @builtins.property
    @jsii.member(jsii_name="hoursOfOperationArn")
    def hours_of_operation_arn(self) -> builtins.str:
        '''(experimental) The ARN of the hours of operation.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "hoursOfOperationArn"))

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''(experimental) The ARN of the attached instance.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IHoursOfOperation).__jsii_proxy_class__ = lambda : _IHoursOfOperationProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IInstance")
class IInstance(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''(experimental) The ARN of the instance.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        '''(experimental) The instance identifier.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="instanceName")
    def instance_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The instance name.

        May not always be available

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addStorageConfig")
    def add_storage_config(
        self,
        config: "StorageConfig",
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: -
        :param id: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="associateFunction")
    def associate_function(
        self,
        func: "_aws_cdk_aws_lambda_ceddda9d.IFunction",
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param func: -
        :param id: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="associateLexBot")
    def associate_lex_bot(
        self,
        bot: "_aws_cdk_interfaces_aws_lex_ceddda9d.IBotAliasRef",
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bot: -
        :param id: -

        :stability: experimental
        '''
        ...


class _IInstanceProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IInstance"

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''(experimental) The ARN of the instance.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceArn"))

    @builtins.property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        '''(experimental) The instance identifier.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @builtins.property
    @jsii.member(jsii_name="instanceName")
    def instance_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The instance name.

        May not always be available

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceName"))

    @jsii.member(jsii_name="addStorageConfig")
    def add_storage_config(
        self,
        config: "StorageConfig",
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__408938508c4b72245f0fb331acf58a74b88ad5bf6e024cf2147a5a60074db772)
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(None, jsii.invoke(self, "addStorageConfig", [config, id]))

    @jsii.member(jsii_name="associateFunction")
    def associate_function(
        self,
        func: "_aws_cdk_aws_lambda_ceddda9d.IFunction",
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param func: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f02b04749de22f2fbe9c10ec899e58cc0b47949c3685b89f1ea3e4deed402daf)
            check_type(argname="argument func", value=func, expected_type=type_hints["func"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(None, jsii.invoke(self, "associateFunction", [func, id]))

    @jsii.member(jsii_name="associateLexBot")
    def associate_lex_bot(
        self,
        bot: "_aws_cdk_interfaces_aws_lex_ceddda9d.IBotAliasRef",
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bot: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01bdeccf53b04c5691b183c8b4b2d4bab29fad4a4ea84063187b95d9740ea861)
            check_type(argname="argument bot", value=bot, expected_type=type_hints["bot"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(None, jsii.invoke(self, "associateLexBot", [bot, id]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IInstance).__jsii_proxy_class__ = lambda : _IInstanceProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IPhoneNumber")
class IPhoneNumber(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="phoneNumberArn")
    def phone_number_arn(self) -> builtins.str:
        '''(experimental) The ARN of the phone number.

        :stability: experimental
        '''
        ...


class _IPhoneNumberProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IPhoneNumber"

    @builtins.property
    @jsii.member(jsii_name="phoneNumberArn")
    def phone_number_arn(self) -> builtins.str:
        '''(experimental) The ARN of the phone number.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "phoneNumberArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPhoneNumber).__jsii_proxy_class__ = lambda : _IPhoneNumberProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IQueue")
class IQueue(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="queueArn")
    def queue_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...


class _IQueueProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IQueue"

    @builtins.property
    @jsii.member(jsii_name="queueArn")
    def queue_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "queueArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IQueue).__jsii_proxy_class__ = lambda : _IQueueProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IQuickConnect")
class IQuickConnect(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="quickConnectArn")
    def quick_connect_arn(self) -> builtins.str:
        '''(experimental) The ARN of the quick connect.

        :stability: experimental
        '''
        ...


class _IQuickConnectProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IQuickConnect"

    @builtins.property
    @jsii.member(jsii_name="quickConnectArn")
    def quick_connect_arn(self) -> builtins.str:
        '''(experimental) The ARN of the quick connect.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "quickConnectArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IQuickConnect).__jsii_proxy_class__ = lambda : _IQuickConnectProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IRoutingProfile")
class IRoutingProfile(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="routingProfileArn")
    def routing_profile_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...


class _IRoutingProfileProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IRoutingProfile"

    @builtins.property
    @jsii.member(jsii_name="routingProfileArn")
    def routing_profile_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "routingProfileArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRoutingProfile).__jsii_proxy_class__ = lambda : _IRoutingProfileProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ISecurityProfile")
class ISecurityProfile(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="securityProfileArn")
    def security_profile_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...


class _ISecurityProfileProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.ISecurityProfile"

    @builtins.property
    @jsii.member(jsii_name="securityProfileArn")
    def security_profile_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "securityProfileArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISecurityProfile).__jsii_proxy_class__ = lambda : _ISecurityProfileProxy


@jsii.interface(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ITrafficDistributionGroup"
)
class ITrafficDistributionGroup(
    _aws_cdk_ceddda9d.IResource,
    typing_extensions.Protocol,
):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="trafficDistributionGroupArn")
    def traffic_distribution_group_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...


class _ITrafficDistributionGroupProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.ITrafficDistributionGroup"

    @builtins.property
    @jsii.member(jsii_name="trafficDistributionGroupArn")
    def traffic_distribution_group_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "trafficDistributionGroupArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITrafficDistributionGroup).__jsii_proxy_class__ = lambda : _ITrafficDistributionGroupProxy


@jsii.interface(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IUser")
class IUser(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> builtins.str:
        '''(experimental) The ARN of the connect user.

        :stability: experimental
        '''
        ...


class _IUserProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@netforbpo/aws-cdk-aws-connect-lib.IUser"

    @builtins.property
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> builtins.str:
        '''(experimental) The ARN of the connect user.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "userArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IUser).__jsii_proxy_class__ = lambda : _IUserProxy


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.IdentityManagementType")
class IdentityManagementType(enum.Enum):
    '''
    :stability: experimental
    '''

    SAML = "SAML"
    '''
    :stability: experimental
    '''
    CONNECT_MANAGED = "CONNECT_MANAGED"
    '''
    :stability: experimental
    '''
    EXISTING_DIRECTORY = "EXISTING_DIRECTORY"
    '''
    :stability: experimental
    '''


@jsii.implements(IInstance)
class Instance(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.Instance",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        identity_type: "IdentityManagementType",
        telephony_config: typing.Union["TelephonyConfigProps", typing.Dict[builtins.str, typing.Any]],
        directory_id: typing.Optional[builtins.str] = None,
        instance_alias: typing.Optional[builtins.str] = None,
        other_config: typing.Optional[typing.Union["OtherConfigProps", typing.Dict[builtins.str, typing.Any]]] = None,
        polly_config: typing.Optional[typing.Union["PollyConfigProps", typing.Dict[builtins.str, typing.Any]]] = None,
        storage_configs: typing.Optional[typing.Sequence["StorageConfig"]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param identity_type: (experimental) The identity type for this instance.
        :param telephony_config: (experimental) Telephony properties. Required (due to required setting of inbound & outbound call configuration)
        :param directory_id: (experimental) The identifier of a simpleAD or Microsoft AD (^d-[0-9a-f]{10}$), required when identityType is set to EXISTING_DIRECTORY.
        :param instance_alias: (experimental) The instance alias, required when identityType is set to CONNECT_MANAGED or SAML.
        :param other_config: (experimental) Other configuration settings.
        :param polly_config: (experimental) Polly configuration settings.
        :param storage_configs: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d4ca1ccc95e1fd44217cf0d3d24eb076784056088d595f21c857899af7b8e28)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = InstanceProps(
            identity_type=identity_type,
            telephony_config=telephony_config,
            directory_id=directory_id,
            instance_alias=instance_alias,
            other_config=other_config,
            polly_config=polly_config,
            storage_configs=storage_configs,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromLookup")
    @builtins.classmethod
    def from_lookup(
        cls,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        instance_arn: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
        instance_name: typing.Optional[builtins.str] = None,
    ) -> "IInstance":
        '''
        :param scope: -
        :param id: -
        :param instance_arn: (experimental) The instance Arn.
        :param instance_id: (experimental) the ID of the connect instance.
        :param instance_name: (experimental) The connect instance name.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c53d68a4360f5b158c85f6e90de7aca880c357aa4e901f4cb0d442a107c3b68d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = InstanceLookupOptions(
            instance_arn=instance_arn,
            instance_id=instance_id,
            instance_name=instance_name,
        )

        return typing.cast("IInstance", jsii.sinvoke(cls, "fromLookup", [scope, id, options]))

    @jsii.member(jsii_name="addStorageConfig")
    def add_storage_config(
        self,
        config: "StorageConfig",
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9843491e91dbc13a26d18eff5b8410790856145a2b9fc93614e69e34df7a3b6)
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(None, jsii.invoke(self, "addStorageConfig", [config, id]))

    @jsii.member(jsii_name="associateFunction")
    def associate_function(
        self,
        func: "_aws_cdk_aws_lambda_ceddda9d.IFunction",
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param func: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88a34a45e0f2cef26c539c2a6ee3467dc330a4c2d5d14b74c98c7f6a7944481b)
            check_type(argname="argument func", value=func, expected_type=type_hints["func"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(None, jsii.invoke(self, "associateFunction", [func, id]))

    @jsii.member(jsii_name="associateLexBot")
    def associate_lex_bot(
        self,
        bot: "_aws_cdk_interfaces_aws_lex_ceddda9d.IBotAliasRef",
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bot: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a260f868e1acef3b2c069c4c84e1365d5fcafa08a7e749dc939a759c49604ea3)
            check_type(argname="argument bot", value=bot, expected_type=type_hints["bot"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(None, jsii.invoke(self, "associateLexBot", [bot, id]))

    @builtins.property
    @jsii.member(jsii_name="instance")
    def instance(self) -> "_aws_cdk_aws_connect_ceddda9d.CfnInstance":
        '''
        :stability: experimental
        '''
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnInstance", jsii.get(self, "instance"))

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''(experimental) The ARN of the instance.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceArn"))

    @builtins.property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        '''(experimental) The instance identifier.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @builtins.property
    @jsii.member(jsii_name="instanceName")
    def instance_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The instance name.

        May not always be available

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceName"))


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.InstanceLookupOptions",
    jsii_struct_bases=[],
    name_mapping={
        "instance_arn": "instanceArn",
        "instance_id": "instanceId",
        "instance_name": "instanceName",
    },
)
class InstanceLookupOptions:
    def __init__(
        self,
        *,
        instance_arn: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
        instance_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance_arn: (experimental) The instance Arn.
        :param instance_id: (experimental) the ID of the connect instance.
        :param instance_name: (experimental) The connect instance name.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c2ac0b77614759f52400f4e3b5705e02f36450ea9fb0e7a287113cf90e480c8)
            check_type(argname="argument instance_arn", value=instance_arn, expected_type=type_hints["instance_arn"])
            check_type(argname="argument instance_id", value=instance_id, expected_type=type_hints["instance_id"])
            check_type(argname="argument instance_name", value=instance_name, expected_type=type_hints["instance_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if instance_arn is not None:
            self._values["instance_arn"] = instance_arn
        if instance_id is not None:
            self._values["instance_id"] = instance_id
        if instance_name is not None:
            self._values["instance_name"] = instance_name

    @builtins.property
    def instance_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The instance Arn.

        :stability: experimental
        '''
        result = self._values.get("instance_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) the ID of the connect instance.

        :stability: experimental
        '''
        result = self._values.get("instance_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The connect instance name.

        :stability: experimental
        '''
        result = self._values.get("instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceLookupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.InstanceProps",
    jsii_struct_bases=[],
    name_mapping={
        "identity_type": "identityType",
        "telephony_config": "telephonyConfig",
        "directory_id": "directoryId",
        "instance_alias": "instanceAlias",
        "other_config": "otherConfig",
        "polly_config": "pollyConfig",
        "storage_configs": "storageConfigs",
    },
)
class InstanceProps:
    def __init__(
        self,
        *,
        identity_type: "IdentityManagementType",
        telephony_config: typing.Union["TelephonyConfigProps", typing.Dict[builtins.str, typing.Any]],
        directory_id: typing.Optional[builtins.str] = None,
        instance_alias: typing.Optional[builtins.str] = None,
        other_config: typing.Optional[typing.Union["OtherConfigProps", typing.Dict[builtins.str, typing.Any]]] = None,
        polly_config: typing.Optional[typing.Union["PollyConfigProps", typing.Dict[builtins.str, typing.Any]]] = None,
        storage_configs: typing.Optional[typing.Sequence["StorageConfig"]] = None,
    ) -> None:
        '''
        :param identity_type: (experimental) The identity type for this instance.
        :param telephony_config: (experimental) Telephony properties. Required (due to required setting of inbound & outbound call configuration)
        :param directory_id: (experimental) The identifier of a simpleAD or Microsoft AD (^d-[0-9a-f]{10}$), required when identityType is set to EXISTING_DIRECTORY.
        :param instance_alias: (experimental) The instance alias, required when identityType is set to CONNECT_MANAGED or SAML.
        :param other_config: (experimental) Other configuration settings.
        :param polly_config: (experimental) Polly configuration settings.
        :param storage_configs: 

        :stability: experimental
        '''
        if isinstance(telephony_config, dict):
            telephony_config = TelephonyConfigProps(**telephony_config)
        if isinstance(other_config, dict):
            other_config = OtherConfigProps(**other_config)
        if isinstance(polly_config, dict):
            polly_config = PollyConfigProps(**polly_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24ec8441d8b3275943bb5034b7d2a90b8151b49cf837c06c930c772bbd4fbe16)
            check_type(argname="argument identity_type", value=identity_type, expected_type=type_hints["identity_type"])
            check_type(argname="argument telephony_config", value=telephony_config, expected_type=type_hints["telephony_config"])
            check_type(argname="argument directory_id", value=directory_id, expected_type=type_hints["directory_id"])
            check_type(argname="argument instance_alias", value=instance_alias, expected_type=type_hints["instance_alias"])
            check_type(argname="argument other_config", value=other_config, expected_type=type_hints["other_config"])
            check_type(argname="argument polly_config", value=polly_config, expected_type=type_hints["polly_config"])
            check_type(argname="argument storage_configs", value=storage_configs, expected_type=type_hints["storage_configs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identity_type": identity_type,
            "telephony_config": telephony_config,
        }
        if directory_id is not None:
            self._values["directory_id"] = directory_id
        if instance_alias is not None:
            self._values["instance_alias"] = instance_alias
        if other_config is not None:
            self._values["other_config"] = other_config
        if polly_config is not None:
            self._values["polly_config"] = polly_config
        if storage_configs is not None:
            self._values["storage_configs"] = storage_configs

    @builtins.property
    def identity_type(self) -> "IdentityManagementType":
        '''(experimental) The identity type for this instance.

        :stability: experimental
        '''
        result = self._values.get("identity_type")
        assert result is not None, "Required property 'identity_type' is missing"
        return typing.cast("IdentityManagementType", result)

    @builtins.property
    def telephony_config(self) -> "TelephonyConfigProps":
        '''(experimental) Telephony properties.

        Required (due to required setting of inbound & outbound call configuration)

        :stability: experimental
        '''
        result = self._values.get("telephony_config")
        assert result is not None, "Required property 'telephony_config' is missing"
        return typing.cast("TelephonyConfigProps", result)

    @builtins.property
    def directory_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identifier of a simpleAD or Microsoft AD (^d-[0-9a-f]{10}$), required when identityType is set to EXISTING_DIRECTORY.

        :stability: experimental
        '''
        result = self._values.get("directory_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_alias(self) -> typing.Optional[builtins.str]:
        '''(experimental) The instance alias, required when identityType is set to CONNECT_MANAGED or SAML.

        :stability: experimental
        '''
        result = self._values.get("instance_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def other_config(self) -> typing.Optional["OtherConfigProps"]:
        '''(experimental) Other configuration settings.

        :stability: experimental
        '''
        result = self._values.get("other_config")
        return typing.cast(typing.Optional["OtherConfigProps"], result)

    @builtins.property
    def polly_config(self) -> typing.Optional["PollyConfigProps"]:
        '''(experimental) Polly configuration settings.

        :stability: experimental
        '''
        result = self._values.get("polly_config")
        return typing.cast(typing.Optional["PollyConfigProps"], result)

    @builtins.property
    def storage_configs(self) -> typing.Optional[typing.List["StorageConfig"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("storage_configs")
        return typing.cast(typing.Optional[typing.List["StorageConfig"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.OtherConfigProps",
    jsii_struct_bases=[],
    name_mapping={
        "contactflow_logs": "contactflowLogs",
        "contact_lens": "contactLens",
        "enhanced_chat_monitoring": "enhancedChatMonitoring",
        "enhanced_contact_monitoring": "enhancedContactMonitoring",
        "high_volume_out_bound": "highVolumeOutBound",
    },
)
class OtherConfigProps:
    def __init__(
        self,
        *,
        contactflow_logs: typing.Optional[builtins.bool] = None,
        contact_lens: typing.Optional[builtins.bool] = None,
        enhanced_chat_monitoring: typing.Optional[builtins.bool] = None,
        enhanced_contact_monitoring: typing.Optional[builtins.bool] = None,
        high_volume_out_bound: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) All other config props.

        :param contactflow_logs: (experimental) Whether contact flow logs are enabled. (CONTACTFLOW_LOGS)
        :param contact_lens: (experimental) Whether contact lens is enabled. (CONTACT_LENS)
        :param enhanced_chat_monitoring: (experimental) Whether enhanced chat monitoring is enabled. (ENHANCED_CHAT_MONITORING)
        :param enhanced_contact_monitoring: (experimental) Whether enhanced contact monitoring is enabled. (ENHANCED_CONTACT_MONITORING)
        :param high_volume_out_bound: (experimental) Whether high volume outbound is enabled. (HIGH_VOLUME_OUTBOUND)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84716c68401fa6516bffd90f0f78d0c162f73bb7f10d9e410378eacaab0d9a25)
            check_type(argname="argument contactflow_logs", value=contactflow_logs, expected_type=type_hints["contactflow_logs"])
            check_type(argname="argument contact_lens", value=contact_lens, expected_type=type_hints["contact_lens"])
            check_type(argname="argument enhanced_chat_monitoring", value=enhanced_chat_monitoring, expected_type=type_hints["enhanced_chat_monitoring"])
            check_type(argname="argument enhanced_contact_monitoring", value=enhanced_contact_monitoring, expected_type=type_hints["enhanced_contact_monitoring"])
            check_type(argname="argument high_volume_out_bound", value=high_volume_out_bound, expected_type=type_hints["high_volume_out_bound"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if contactflow_logs is not None:
            self._values["contactflow_logs"] = contactflow_logs
        if contact_lens is not None:
            self._values["contact_lens"] = contact_lens
        if enhanced_chat_monitoring is not None:
            self._values["enhanced_chat_monitoring"] = enhanced_chat_monitoring
        if enhanced_contact_monitoring is not None:
            self._values["enhanced_contact_monitoring"] = enhanced_contact_monitoring
        if high_volume_out_bound is not None:
            self._values["high_volume_out_bound"] = high_volume_out_bound

    @builtins.property
    def contactflow_logs(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether contact flow logs are enabled.

        (CONTACTFLOW_LOGS)

        :stability: experimental
        '''
        result = self._values.get("contactflow_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def contact_lens(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether contact lens is enabled.

        (CONTACT_LENS)

        :stability: experimental
        '''
        result = self._values.get("contact_lens")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enhanced_chat_monitoring(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether enhanced chat monitoring is enabled.

        (ENHANCED_CHAT_MONITORING)

        :stability: experimental
        '''
        result = self._values.get("enhanced_chat_monitoring")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enhanced_contact_monitoring(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether enhanced contact monitoring is enabled.

        (ENHANCED_CONTACT_MONITORING)

        :stability: experimental
        '''
        result = self._values.get("enhanced_contact_monitoring")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def high_volume_out_bound(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether high volume outbound is enabled.

        (HIGH_VOLUME_OUTBOUND)

        :stability: experimental
        '''
        result = self._values.get("high_volume_out_bound")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OtherConfigProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPhoneNumber)
class PhoneNumber(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.PhoneNumber",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        target: typing.Union["IInstance", "ITrafficDistributionGroup"],
        country_code: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        source_phone_number_arn: typing.Optional[builtins.str] = None,
        type: typing.Optional["PhoneNumberType"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param target: (experimental) The AWS connect instance or traffic distribution node to attach the phone number to.
        :param country_code: (experimental) The ISO 2-letter country code of the phone number.
        :param description: (experimental) A description of the phone number.
        :param prefix: (experimental) The phone number prefix with the + country code.
        :param source_phone_number_arn: (experimental) the ARN of an externally imported phone number (e.g. from AWS End User Messaging).
        :param type: (experimental) The phone number type.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a759311bb7fca42f6e295e529cee0557768c3410ed33b911e3492126a3285aa1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PhoneNumberProps(
            target=target,
            country_code=country_code,
            description=description,
            prefix=prefix,
            source_phone_number_arn=source_phone_number_arn,
            type=type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="phoneNumber")
    def phone_number(self) -> "_aws_cdk_aws_connect_ceddda9d.CfnPhoneNumber":
        '''
        :stability: experimental
        '''
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnPhoneNumber", jsii.get(self, "phoneNumber"))

    @builtins.property
    @jsii.member(jsii_name="phoneNumberArn")
    def phone_number_arn(self) -> builtins.str:
        '''(experimental) The ARN of the phone number.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "phoneNumberArn"))


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.PhoneNumberProps",
    jsii_struct_bases=[],
    name_mapping={
        "target": "target",
        "country_code": "countryCode",
        "description": "description",
        "prefix": "prefix",
        "source_phone_number_arn": "sourcePhoneNumberArn",
        "type": "type",
    },
)
class PhoneNumberProps:
    def __init__(
        self,
        *,
        target: typing.Union["IInstance", "ITrafficDistributionGroup"],
        country_code: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        source_phone_number_arn: typing.Optional[builtins.str] = None,
        type: typing.Optional["PhoneNumberType"] = None,
    ) -> None:
        '''
        :param target: (experimental) The AWS connect instance or traffic distribution node to attach the phone number to.
        :param country_code: (experimental) The ISO 2-letter country code of the phone number.
        :param description: (experimental) A description of the phone number.
        :param prefix: (experimental) The phone number prefix with the + country code.
        :param source_phone_number_arn: (experimental) the ARN of an externally imported phone number (e.g. from AWS End User Messaging).
        :param type: (experimental) The phone number type.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__831f7cf9bf3db596ec7b8a8e73c054160c221bbaac018bbd0d8608a561a4566f)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument country_code", value=country_code, expected_type=type_hints["country_code"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument source_phone_number_arn", value=source_phone_number_arn, expected_type=type_hints["source_phone_number_arn"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target": target,
        }
        if country_code is not None:
            self._values["country_code"] = country_code
        if description is not None:
            self._values["description"] = description
        if prefix is not None:
            self._values["prefix"] = prefix
        if source_phone_number_arn is not None:
            self._values["source_phone_number_arn"] = source_phone_number_arn
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def target(self) -> typing.Union["IInstance", "ITrafficDistributionGroup"]:
        '''(experimental) The AWS connect instance or traffic distribution node to attach the phone number to.

        :stability: experimental
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(typing.Union["IInstance", "ITrafficDistributionGroup"], result)

    @builtins.property
    def country_code(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ISO 2-letter country code of the phone number.

        :stability: experimental
        '''
        result = self._values.get("country_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description of the phone number.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) The phone number prefix with the + country code.

        :stability: experimental
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_phone_number_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) the ARN of an externally imported phone number (e.g. from AWS End User Messaging).

        :stability: experimental
        '''
        result = self._values.get("source_phone_number_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional["PhoneNumberType"]:
        '''(experimental) The phone number type.

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["PhoneNumberType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PhoneNumberProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.PhoneNumberType")
class PhoneNumberType(enum.Enum):
    '''
    :stability: experimental
    '''

    TOLL_FREE = "TOLL_FREE"
    '''
    :stability: experimental
    '''
    DID = "DID"
    '''
    :stability: experimental
    '''
    UIFN = "UIFN"
    '''
    :stability: experimental
    '''
    SHARED = "SHARED"
    '''
    :stability: experimental
    '''
    THIRD_PARTY_DID = "THIRD_PARTY_DID"
    '''
    :stability: experimental
    '''
    THIRD_PARTY_TF = "THIRD_PARTY_TF"
    '''
    :stability: experimental
    '''
    SHORT_CODE = "SHORT_CODE"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.PollyConfigProps",
    jsii_struct_bases=[],
    name_mapping={
        "auto_resolve_best_voices": "autoResolveBestVoices",
        "use_custom_tts_voices": "useCustomTtsVoices",
    },
)
class PollyConfigProps:
    def __init__(
        self,
        *,
        auto_resolve_best_voices: typing.Optional[builtins.bool] = None,
        use_custom_tts_voices: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param auto_resolve_best_voices: (experimental) Whether to automatically resolve best voices. (AUTO_RESOLVE_BEST_VOICES)
        :param use_custom_tts_voices: (experimental) Whether useCustomTtsVoices is enabled (USE_CUSTOM_TTS_VOICES).

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b263cb24cbf99c98cad20e61187924e03e8fbab6c737d87a7e25ae94e0b290)
            check_type(argname="argument auto_resolve_best_voices", value=auto_resolve_best_voices, expected_type=type_hints["auto_resolve_best_voices"])
            check_type(argname="argument use_custom_tts_voices", value=use_custom_tts_voices, expected_type=type_hints["use_custom_tts_voices"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_resolve_best_voices is not None:
            self._values["auto_resolve_best_voices"] = auto_resolve_best_voices
        if use_custom_tts_voices is not None:
            self._values["use_custom_tts_voices"] = use_custom_tts_voices

    @builtins.property
    def auto_resolve_best_voices(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to automatically resolve best voices.

        (AUTO_RESOLVE_BEST_VOICES)

        :stability: experimental
        '''
        result = self._values.get("auto_resolve_best_voices")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def use_custom_tts_voices(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether useCustomTtsVoices is enabled (USE_CUSTOM_TTS_VOICES).

        :stability: experimental
        '''
        result = self._values.get("use_custom_tts_voices")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PollyConfigProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IQueue)
class Queue(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.Queue",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        hours_of_operation: "IHoursOfOperation",
        instance: "IInstance",
        name: builtins.str,
        quick_connects: typing.Sequence["IQuickConnect"],
        description: typing.Optional[builtins.str] = None,
        max_queue_size: typing.Optional[jsii.Number] = None,
        outbound_caller_config: typing.Optional[typing.Union["QueueOutboundCallerConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        outbound_email: typing.Optional["IEmailAddress"] = None,
        status: typing.Optional["QueueStatus"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hours_of_operation: (experimental) The hours of operation to associate with the queue.
        :param instance: (experimental) The AWS connect instance to attach the queue to.
        :param name: (experimental) The name of the hours of operation.
        :param quick_connects: 
        :param description: (experimental) A description of the queue.
        :param max_queue_size: (experimental) The maximum number of contacts that can be in the queue before it is considered full (default 0/unlimited).
        :param outbound_caller_config: 
        :param outbound_email: 
        :param status: (experimental) The status of the queue. Default QueueStats.ENABLED

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df1bf4f0dc9b67355d036f308b6547a29fadb0873bc99de78048f206373054ce)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = QueueProps(
            hours_of_operation=hours_of_operation,
            instance=instance,
            name=name,
            quick_connects=quick_connects,
            description=description,
            max_queue_size=max_queue_size,
            outbound_caller_config=outbound_caller_config,
            outbound_email=outbound_email,
            status=status,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="hoursOfOperation")
    def hours_of_operation(self) -> "IHoursOfOperation":
        '''
        :stability: experimental
        '''
        return typing.cast("IHoursOfOperation", jsii.get(self, "hoursOfOperation"))

    @builtins.property
    @jsii.member(jsii_name="instance")
    def instance(self) -> "IInstance":
        '''
        :stability: experimental
        '''
        return typing.cast("IInstance", jsii.get(self, "instance"))

    @builtins.property
    @jsii.member(jsii_name="queue")
    def queue(self) -> "_aws_cdk_aws_connect_ceddda9d.CfnQueue":
        '''
        :stability: experimental
        '''
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnQueue", jsii.get(self, "queue"))

    @builtins.property
    @jsii.member(jsii_name="queueArn")
    def queue_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "queueArn"))


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.QueueOutboundCallerConfig",
    jsii_struct_bases=[],
    name_mapping={
        "caller_id_name": "callerIdName",
        "caller_id_number": "callerIdNumber",
        "flow": "flow",
    },
)
class QueueOutboundCallerConfig:
    def __init__(
        self,
        *,
        caller_id_name: builtins.str,
        caller_id_number: "IPhoneNumber",
        flow: "IContactFlow",
    ) -> None:
        '''
        :param caller_id_name: 
        :param caller_id_number: 
        :param flow: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a1ba3ee3d693e1124f5d1db08fea9d2abc5c1c552618878a5867e558b5d9895)
            check_type(argname="argument caller_id_name", value=caller_id_name, expected_type=type_hints["caller_id_name"])
            check_type(argname="argument caller_id_number", value=caller_id_number, expected_type=type_hints["caller_id_number"])
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "caller_id_name": caller_id_name,
            "caller_id_number": caller_id_number,
            "flow": flow,
        }

    @builtins.property
    def caller_id_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("caller_id_name")
        assert result is not None, "Required property 'caller_id_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def caller_id_number(self) -> "IPhoneNumber":
        '''
        :stability: experimental
        '''
        result = self._values.get("caller_id_number")
        assert result is not None, "Required property 'caller_id_number' is missing"
        return typing.cast("IPhoneNumber", result)

    @builtins.property
    def flow(self) -> "IContactFlow":
        '''
        :stability: experimental
        '''
        result = self._values.get("flow")
        assert result is not None, "Required property 'flow' is missing"
        return typing.cast("IContactFlow", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueueOutboundCallerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.QueueProps",
    jsii_struct_bases=[],
    name_mapping={
        "hours_of_operation": "hoursOfOperation",
        "instance": "instance",
        "name": "name",
        "quick_connects": "quickConnects",
        "description": "description",
        "max_queue_size": "maxQueueSize",
        "outbound_caller_config": "outboundCallerConfig",
        "outbound_email": "outboundEmail",
        "status": "status",
    },
)
class QueueProps:
    def __init__(
        self,
        *,
        hours_of_operation: "IHoursOfOperation",
        instance: "IInstance",
        name: builtins.str,
        quick_connects: typing.Sequence["IQuickConnect"],
        description: typing.Optional[builtins.str] = None,
        max_queue_size: typing.Optional[jsii.Number] = None,
        outbound_caller_config: typing.Optional[typing.Union["QueueOutboundCallerConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        outbound_email: typing.Optional["IEmailAddress"] = None,
        status: typing.Optional["QueueStatus"] = None,
    ) -> None:
        '''
        :param hours_of_operation: (experimental) The hours of operation to associate with the queue.
        :param instance: (experimental) The AWS connect instance to attach the queue to.
        :param name: (experimental) The name of the hours of operation.
        :param quick_connects: 
        :param description: (experimental) A description of the queue.
        :param max_queue_size: (experimental) The maximum number of contacts that can be in the queue before it is considered full (default 0/unlimited).
        :param outbound_caller_config: 
        :param outbound_email: 
        :param status: (experimental) The status of the queue. Default QueueStats.ENABLED

        :stability: experimental
        '''
        if isinstance(outbound_caller_config, dict):
            outbound_caller_config = QueueOutboundCallerConfig(**outbound_caller_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa519a3ad62f67876eb28ebd135dbc254f97babc66a55ddf298d17177d8ac6ef)
            check_type(argname="argument hours_of_operation", value=hours_of_operation, expected_type=type_hints["hours_of_operation"])
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument quick_connects", value=quick_connects, expected_type=type_hints["quick_connects"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument max_queue_size", value=max_queue_size, expected_type=type_hints["max_queue_size"])
            check_type(argname="argument outbound_caller_config", value=outbound_caller_config, expected_type=type_hints["outbound_caller_config"])
            check_type(argname="argument outbound_email", value=outbound_email, expected_type=type_hints["outbound_email"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hours_of_operation": hours_of_operation,
            "instance": instance,
            "name": name,
            "quick_connects": quick_connects,
        }
        if description is not None:
            self._values["description"] = description
        if max_queue_size is not None:
            self._values["max_queue_size"] = max_queue_size
        if outbound_caller_config is not None:
            self._values["outbound_caller_config"] = outbound_caller_config
        if outbound_email is not None:
            self._values["outbound_email"] = outbound_email
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def hours_of_operation(self) -> "IHoursOfOperation":
        '''(experimental) The hours of operation to associate with the queue.

        :stability: experimental
        '''
        result = self._values.get("hours_of_operation")
        assert result is not None, "Required property 'hours_of_operation' is missing"
        return typing.cast("IHoursOfOperation", result)

    @builtins.property
    def instance(self) -> "IInstance":
        '''(experimental) The AWS connect instance to attach the queue to.

        :stability: experimental
        '''
        result = self._values.get("instance")
        assert result is not None, "Required property 'instance' is missing"
        return typing.cast("IInstance", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the hours of operation.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def quick_connects(self) -> typing.List["IQuickConnect"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("quick_connects")
        assert result is not None, "Required property 'quick_connects' is missing"
        return typing.cast(typing.List["IQuickConnect"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description of the queue.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_queue_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of contacts that can be in the queue before it is considered full (default 0/unlimited).

        :stability: experimental
        '''
        result = self._values.get("max_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def outbound_caller_config(self) -> typing.Optional["QueueOutboundCallerConfig"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("outbound_caller_config")
        return typing.cast(typing.Optional["QueueOutboundCallerConfig"], result)

    @builtins.property
    def outbound_email(self) -> typing.Optional["IEmailAddress"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("outbound_email")
        return typing.cast(typing.Optional["IEmailAddress"], result)

    @builtins.property
    def status(self) -> typing.Optional["QueueStatus"]:
        '''(experimental) The status of the queue.

        Default QueueStats.ENABLED

        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["QueueStatus"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueueProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.QueueStatus")
class QueueStatus(enum.Enum):
    '''
    :stability: experimental
    '''

    ENABLED = "ENABLED"
    '''
    :stability: experimental
    '''
    DISABLED = "DISABLED"
    '''
    :stability: experimental
    '''


@jsii.implements(IQuickConnect)
class QuickConnect(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.QuickConnect",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        instance: "IInstance",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        phone_number: typing.Optional[builtins.str] = None,
        queue_config: typing.Optional[typing.Union["QuickConnectQueueConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        user_config: typing.Optional[typing.Union["QuickConnectUserConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance: (experimental) The AWS connect instance to attach the quick connect to.
        :param name: (experimental) The name of the quick connect.
        :param description: (experimental) The description of the quick connect.
        :param phone_number: (experimental) the phone number to use for this quick connect. Cannot be set with queueConfig or userConfig
        :param queue_config: (experimental) the queue and flow to use for this quick connect. Cannot be set with phoneNumber or userConfig
        :param user_config: (experimental) the user to use for this quick connect. Cannot be set with phoneNumber or queueConfig

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4ad015cef0a9423a9d350148a4c17b3bd58f9b1d807d14e064e5221a6e840f6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = QuickConnectProps(
            instance=instance,
            name=name,
            description=description,
            phone_number=phone_number,
            queue_config=queue_config,
            user_config=user_config,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="quickConnect")
    def quick_connect(self) -> "_aws_cdk_aws_connect_ceddda9d.CfnQuickConnect":
        '''
        :stability: experimental
        '''
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnQuickConnect", jsii.get(self, "quickConnect"))

    @builtins.property
    @jsii.member(jsii_name="quickConnectArn")
    def quick_connect_arn(self) -> builtins.str:
        '''(experimental) The ARN of the quick connect.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "quickConnectArn"))


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.QuickConnectProps",
    jsii_struct_bases=[],
    name_mapping={
        "instance": "instance",
        "name": "name",
        "description": "description",
        "phone_number": "phoneNumber",
        "queue_config": "queueConfig",
        "user_config": "userConfig",
    },
)
class QuickConnectProps:
    def __init__(
        self,
        *,
        instance: "IInstance",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        phone_number: typing.Optional[builtins.str] = None,
        queue_config: typing.Optional[typing.Union["QuickConnectQueueConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        user_config: typing.Optional[typing.Union["QuickConnectUserConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param instance: (experimental) The AWS connect instance to attach the quick connect to.
        :param name: (experimental) The name of the quick connect.
        :param description: (experimental) The description of the quick connect.
        :param phone_number: (experimental) the phone number to use for this quick connect. Cannot be set with queueConfig or userConfig
        :param queue_config: (experimental) the queue and flow to use for this quick connect. Cannot be set with phoneNumber or userConfig
        :param user_config: (experimental) the user to use for this quick connect. Cannot be set with phoneNumber or queueConfig

        :stability: experimental
        '''
        if isinstance(queue_config, dict):
            queue_config = QuickConnectQueueConfig(**queue_config)
        if isinstance(user_config, dict):
            user_config = QuickConnectUserConfig(**user_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94f1fb4aaf1c08212fff677008c00287c6a869e8d0b841a0967a32c04ef17cbd)
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument phone_number", value=phone_number, expected_type=type_hints["phone_number"])
            check_type(argname="argument queue_config", value=queue_config, expected_type=type_hints["queue_config"])
            check_type(argname="argument user_config", value=user_config, expected_type=type_hints["user_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance": instance,
            "name": name,
        }
        if description is not None:
            self._values["description"] = description
        if phone_number is not None:
            self._values["phone_number"] = phone_number
        if queue_config is not None:
            self._values["queue_config"] = queue_config
        if user_config is not None:
            self._values["user_config"] = user_config

    @builtins.property
    def instance(self) -> "IInstance":
        '''(experimental) The AWS connect instance to attach the quick connect to.

        :stability: experimental
        '''
        result = self._values.get("instance")
        assert result is not None, "Required property 'instance' is missing"
        return typing.cast("IInstance", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the quick connect.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the quick connect.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def phone_number(self) -> typing.Optional[builtins.str]:
        '''(experimental) the phone number to use for this quick connect.

        Cannot be set with queueConfig or userConfig

        :stability: experimental
        '''
        result = self._values.get("phone_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queue_config(self) -> typing.Optional["QuickConnectQueueConfig"]:
        '''(experimental) the queue and flow to use for this quick connect.

        Cannot be set with phoneNumber or userConfig

        :stability: experimental
        '''
        result = self._values.get("queue_config")
        return typing.cast(typing.Optional["QuickConnectQueueConfig"], result)

    @builtins.property
    def user_config(self) -> typing.Optional["QuickConnectUserConfig"]:
        '''(experimental) the user to use for this quick connect.

        Cannot be set with phoneNumber or queueConfig

        :stability: experimental
        '''
        result = self._values.get("user_config")
        return typing.cast(typing.Optional["QuickConnectUserConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuickConnectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.QuickConnectQueueConfig",
    jsii_struct_bases=[],
    name_mapping={"flow": "flow", "queue": "queue"},
)
class QuickConnectQueueConfig:
    def __init__(self, *, flow: "IContactFlow", queue: "IQueue") -> None:
        '''
        :param flow: 
        :param queue: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4612b1d08466e062f3e2f2f1f23b186b1064b60aec86a19fd51aa91622bce30f)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
            check_type(argname="argument queue", value=queue, expected_type=type_hints["queue"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "flow": flow,
            "queue": queue,
        }

    @builtins.property
    def flow(self) -> "IContactFlow":
        '''
        :stability: experimental
        '''
        result = self._values.get("flow")
        assert result is not None, "Required property 'flow' is missing"
        return typing.cast("IContactFlow", result)

    @builtins.property
    def queue(self) -> "IQueue":
        '''
        :stability: experimental
        '''
        result = self._values.get("queue")
        assert result is not None, "Required property 'queue' is missing"
        return typing.cast("IQueue", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuickConnectQueueConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.QuickConnectType")
class QuickConnectType(enum.Enum):
    '''
    :stability: experimental
    '''

    PHONE_NUMBER = "PHONE_NUMBER"
    '''
    :stability: experimental
    '''
    QUEUE = "QUEUE"
    '''
    :stability: experimental
    '''
    USER = "USER"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.QuickConnectUserConfig",
    jsii_struct_bases=[],
    name_mapping={"flow": "flow", "user": "user"},
)
class QuickConnectUserConfig:
    def __init__(self, *, flow: "IContactFlow", user: "IUser") -> None:
        '''
        :param flow: 
        :param user: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40391ee66807d4c7da85cdf08dc043c052c8d84971387a70e1ef04106d05bd90)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
            check_type(argname="argument user", value=user, expected_type=type_hints["user"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "flow": flow,
            "user": user,
        }

    @builtins.property
    def flow(self) -> "IContactFlow":
        '''
        :stability: experimental
        '''
        result = self._values.get("flow")
        assert result is not None, "Required property 'flow' is missing"
        return typing.cast("IContactFlow", result)

    @builtins.property
    def user(self) -> "IUser":
        '''
        :stability: experimental
        '''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast("IUser", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QuickConnectUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StorageConfig(
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.StorageConfig",
):
    '''
    :stability: experimental
    '''

    @jsii.member(jsii_name="buildKinesisFirehose")
    @builtins.classmethod
    def build_kinesis_firehose(
        cls,
        resource_type: "StorageResourceType",
        *,
        firehose: "_aws_cdk_aws_kinesisfirehose_ceddda9d.IDeliveryStream",
    ) -> "StorageConfig":
        '''
        :param resource_type: -
        :param firehose: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96192c7bebafbf59e5c33ceee4d17690a4bce248436ba705aa655a4959a4d488)
            check_type(argname="argument resource_type", value=resource_type, expected_type=type_hints["resource_type"])
        props = StorageConfigKinesisFirehose(firehose=firehose)

        return typing.cast("StorageConfig", jsii.sinvoke(cls, "buildKinesisFirehose", [resource_type, props]))

    @jsii.member(jsii_name="buildKinesisStream")
    @builtins.classmethod
    def build_kinesis_stream(
        cls,
        resource_type: "StorageResourceType",
        *,
        stream: "_aws_cdk_aws_kinesis_ceddda9d.IStream",
    ) -> "StorageConfig":
        '''
        :param resource_type: -
        :param stream: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__573a3a4671d626227bf31bccb0ea9d955b93c94091f00b3a83949a176d4590df)
            check_type(argname="argument resource_type", value=resource_type, expected_type=type_hints["resource_type"])
        props = StorageConfigKinesisStream(stream=stream)

        return typing.cast("StorageConfig", jsii.sinvoke(cls, "buildKinesisStream", [resource_type, props]))

    @jsii.member(jsii_name="buildKinesisVideoStream")
    @builtins.classmethod
    def build_kinesis_video_stream(
        cls,
        resource_type: "StorageResourceType",
        *,
        encryption_config: typing.Union["StorageEncryptionConfig", typing.Dict[builtins.str, typing.Any]],
        prefix: builtins.str,
        retention_period_hours: typing.Optional[jsii.Number] = None,
    ) -> "StorageConfig":
        '''
        :param resource_type: -
        :param encryption_config: (experimental) The encryption configuration for the Kinesis Video Stream.
        :param prefix: (experimental) The prefix of the video stream.
        :param retention_period_hours: (experimental) Kinesis Video Streams retains the data in a data store that is associated with the stream. The default value is 0, indicating that the stream does not persist data.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06bd88047b1340ad9fdbbb62b68dbb151d90a284e6456aa45aa07d83ff153f72)
            check_type(argname="argument resource_type", value=resource_type, expected_type=type_hints["resource_type"])
        props = StorageConfigKinesisVideoStream(
            encryption_config=encryption_config,
            prefix=prefix,
            retention_period_hours=retention_period_hours,
        )

        return typing.cast("StorageConfig", jsii.sinvoke(cls, "buildKinesisVideoStream", [resource_type, props]))

    @jsii.member(jsii_name="buildS3")
    @builtins.classmethod
    def build_s3(
        cls,
        resource_type: "StorageResourceType",
        *,
        bucket: "_aws_cdk_aws_s3_ceddda9d.IBucket",
        prefix: builtins.str,
        encryption_config: typing.Optional[typing.Union["StorageEncryptionConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "StorageConfig":
        '''
        :param resource_type: -
        :param bucket: (experimental) The bucket where the data will be stored.
        :param prefix: (experimental) The prefix within the bucket.
        :param encryption_config: (experimental) The optional encryption configuration.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b058c995809d45432a29ad56b83533d75a0d464706c3ff623f38fec215b58218)
            check_type(argname="argument resource_type", value=resource_type, expected_type=type_hints["resource_type"])
        props = StorageConfigS3(
            bucket=bucket, prefix=prefix, encryption_config=encryption_config
        )

        return typing.cast("StorageConfig", jsii.sinvoke(cls, "buildS3", [resource_type, props]))

    @jsii.member(jsii_name="asStorageConfigProps")
    def as_storage_config_props(
        self,
        instance_arn: builtins.str,
    ) -> "_aws_cdk_aws_connect_ceddda9d.CfnInstanceStorageConfigProps":
        '''
        :param instance_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b03dfc18b41f9f422f5179273c5a1998433e6ee745fe4bb1a6601ca4f51dae8c)
            check_type(argname="argument instance_arn", value=instance_arn, expected_type=type_hints["instance_arn"])
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnInstanceStorageConfigProps", jsii.invoke(self, "asStorageConfigProps", [instance_arn]))

    @jsii.member(jsii_name="checkConfig")
    def check_config(self) -> builtins.bool:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "checkConfig", []))

    @builtins.property
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> "StorageResourceType":
        '''
        :stability: experimental
        '''
        return typing.cast("StorageResourceType", jsii.get(self, "resourceType"))

    @builtins.property
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> "StorageConfigType":
        '''
        :stability: experimental
        '''
        return typing.cast("StorageConfigType", jsii.get(self, "storageType"))

    @builtins.property
    @jsii.member(jsii_name="kinesisFirehose")
    def kinesis_firehose(
        self,
    ) -> typing.Optional["_aws_cdk_aws_kinesisfirehose_ceddda9d.IDeliveryStream"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["_aws_cdk_aws_kinesisfirehose_ceddda9d.IDeliveryStream"], jsii.get(self, "kinesisFirehose"))

    @builtins.property
    @jsii.member(jsii_name="kinesisStream")
    def kinesis_stream(
        self,
    ) -> typing.Optional["_aws_cdk_aws_kinesis_ceddda9d.IStream"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["_aws_cdk_aws_kinesis_ceddda9d.IStream"], jsii.get(self, "kinesisStream"))

    @builtins.property
    @jsii.member(jsii_name="kinesisVideoStreamConfig")
    def kinesis_video_stream_config(
        self,
    ) -> typing.Optional["StorageConfigKinesisVideoStream"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["StorageConfigKinesisVideoStream"], jsii.get(self, "kinesisVideoStreamConfig"))

    @builtins.property
    @jsii.member(jsii_name="s3Config")
    def s3_config(self) -> typing.Optional["StorageConfigS3"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional["StorageConfigS3"], jsii.get(self, "s3Config"))


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.StorageConfigKinesisFirehose",
    jsii_struct_bases=[],
    name_mapping={"firehose": "firehose"},
)
class StorageConfigKinesisFirehose:
    def __init__(
        self,
        *,
        firehose: "_aws_cdk_aws_kinesisfirehose_ceddda9d.IDeliveryStream",
    ) -> None:
        '''
        :param firehose: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ea13485e504ac921557e0160b99895f9350adfd2eb0a4b1fcbb1089c7bc13ca)
            check_type(argname="argument firehose", value=firehose, expected_type=type_hints["firehose"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "firehose": firehose,
        }

    @builtins.property
    def firehose(self) -> "_aws_cdk_aws_kinesisfirehose_ceddda9d.IDeliveryStream":
        '''
        :stability: experimental
        '''
        result = self._values.get("firehose")
        assert result is not None, "Required property 'firehose' is missing"
        return typing.cast("_aws_cdk_aws_kinesisfirehose_ceddda9d.IDeliveryStream", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageConfigKinesisFirehose(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.StorageConfigKinesisStream",
    jsii_struct_bases=[],
    name_mapping={"stream": "stream"},
)
class StorageConfigKinesisStream:
    def __init__(self, *, stream: "_aws_cdk_aws_kinesis_ceddda9d.IStream") -> None:
        '''
        :param stream: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7dcf1d70d6cfaad8de61d1b28e5f928e580a29bc9556bd2d456cbfe5bca99ac)
            check_type(argname="argument stream", value=stream, expected_type=type_hints["stream"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stream": stream,
        }

    @builtins.property
    def stream(self) -> "_aws_cdk_aws_kinesis_ceddda9d.IStream":
        '''
        :stability: experimental
        '''
        result = self._values.get("stream")
        assert result is not None, "Required property 'stream' is missing"
        return typing.cast("_aws_cdk_aws_kinesis_ceddda9d.IStream", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageConfigKinesisStream(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.StorageConfigKinesisVideoStream",
    jsii_struct_bases=[],
    name_mapping={
        "encryption_config": "encryptionConfig",
        "prefix": "prefix",
        "retention_period_hours": "retentionPeriodHours",
    },
)
class StorageConfigKinesisVideoStream:
    def __init__(
        self,
        *,
        encryption_config: typing.Union["StorageEncryptionConfig", typing.Dict[builtins.str, typing.Any]],
        prefix: builtins.str,
        retention_period_hours: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param encryption_config: (experimental) The encryption configuration for the Kinesis Video Stream.
        :param prefix: (experimental) The prefix of the video stream.
        :param retention_period_hours: (experimental) Kinesis Video Streams retains the data in a data store that is associated with the stream. The default value is 0, indicating that the stream does not persist data.

        :stability: experimental
        '''
        if isinstance(encryption_config, dict):
            encryption_config = StorageEncryptionConfig(**encryption_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b20d86be6495f57a1361ff6b0d24ef8033bb958580a458a5f4fc4dca8f0648ae)
            check_type(argname="argument encryption_config", value=encryption_config, expected_type=type_hints["encryption_config"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument retention_period_hours", value=retention_period_hours, expected_type=type_hints["retention_period_hours"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "encryption_config": encryption_config,
            "prefix": prefix,
        }
        if retention_period_hours is not None:
            self._values["retention_period_hours"] = retention_period_hours

    @builtins.property
    def encryption_config(self) -> "StorageEncryptionConfig":
        '''(experimental) The encryption configuration for the Kinesis Video Stream.

        :stability: experimental
        '''
        result = self._values.get("encryption_config")
        assert result is not None, "Required property 'encryption_config' is missing"
        return typing.cast("StorageEncryptionConfig", result)

    @builtins.property
    def prefix(self) -> builtins.str:
        '''(experimental) The prefix of the video stream.

        :stability: experimental
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_period_hours(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Kinesis Video Streams retains the data in a data store that is associated with the stream.

        The default value is 0, indicating that the stream does not persist data.

        :stability: experimental
        '''
        result = self._values.get("retention_period_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageConfigKinesisVideoStream(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.StorageConfigS3",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "prefix": "prefix",
        "encryption_config": "encryptionConfig",
    },
)
class StorageConfigS3:
    def __init__(
        self,
        *,
        bucket: "_aws_cdk_aws_s3_ceddda9d.IBucket",
        prefix: builtins.str,
        encryption_config: typing.Optional[typing.Union["StorageEncryptionConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bucket: (experimental) The bucket where the data will be stored.
        :param prefix: (experimental) The prefix within the bucket.
        :param encryption_config: (experimental) The optional encryption configuration.

        :stability: experimental
        '''
        if isinstance(encryption_config, dict):
            encryption_config = StorageEncryptionConfig(**encryption_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0128197d9ef83f86e8fb494ed9b456f460f7c3bad3da43edd2db355c8fbc9ea)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument encryption_config", value=encryption_config, expected_type=type_hints["encryption_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "prefix": prefix,
        }
        if encryption_config is not None:
            self._values["encryption_config"] = encryption_config

    @builtins.property
    def bucket(self) -> "_aws_cdk_aws_s3_ceddda9d.IBucket":
        '''(experimental) The bucket where the data will be stored.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast("_aws_cdk_aws_s3_ceddda9d.IBucket", result)

    @builtins.property
    def prefix(self) -> builtins.str:
        '''(experimental) The prefix within the bucket.

        :stability: experimental
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_config(self) -> typing.Optional["StorageEncryptionConfig"]:
        '''(experimental) The optional encryption configuration.

        :stability: experimental
        '''
        result = self._values.get("encryption_config")
        return typing.cast(typing.Optional["StorageEncryptionConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageConfigS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.StorageConfigType")
class StorageConfigType(enum.Enum):
    '''
    :stability: experimental
    '''

    S3_BUCKET = "S3_BUCKET"
    '''
    :stability: experimental
    '''
    KINESIS_VIDEO_STREAM = "KINESIS_VIDEO_STREAM"
    '''
    :stability: experimental
    '''
    KINESIS_STREAM = "KINESIS_STREAM"
    '''
    :stability: experimental
    '''
    KINESIS_FIREHOSE = "KINESIS_FIREHOSE"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.StorageEncryptionConfig",
    jsii_struct_bases=[],
    name_mapping={
        "encryption_key": "encryptionKey",
        "encryption_type": "encryptionType",
    },
)
class StorageEncryptionConfig:
    def __init__(
        self,
        *,
        encryption_key: "_aws_cdk_aws_kms_ceddda9d.IKey",
        encryption_type: "StorageEncryptionType",
    ) -> None:
        '''
        :param encryption_key: (experimental) The KMS key used for encryption.
        :param encryption_type: (experimental) The type of encryption used on the stream.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__564ff8d21820f3b0ae50abff4c8d83da62a0d1d2b8836f923b6ddceeba2f44d1)
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument encryption_type", value=encryption_type, expected_type=type_hints["encryption_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "encryption_key": encryption_key,
            "encryption_type": encryption_type,
        }

    @builtins.property
    def encryption_key(self) -> "_aws_cdk_aws_kms_ceddda9d.IKey":
        '''(experimental) The KMS key used for encryption.

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        assert result is not None, "Required property 'encryption_key' is missing"
        return typing.cast("_aws_cdk_aws_kms_ceddda9d.IKey", result)

    @builtins.property
    def encryption_type(self) -> "StorageEncryptionType":
        '''(experimental) The type of encryption used on the stream.

        :stability: experimental
        '''
        result = self._values.get("encryption_type")
        assert result is not None, "Required property 'encryption_type' is missing"
        return typing.cast("StorageEncryptionType", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageEncryptionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.StorageEncryptionType")
class StorageEncryptionType(enum.Enum):
    '''
    :stability: experimental
    '''

    KMS = "KMS"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.StorageResourceType")
class StorageResourceType(enum.Enum):
    '''
    :stability: experimental
    '''

    CHAT_TRANSCRIPTS = "CHAT_TRANSCRIPTS"
    '''
    :stability: experimental
    '''
    CALL_RECORDINGS = "CALL_RECORDINGS"
    '''
    :stability: experimental
    '''
    SCHEDULED_REPORTS = "SCHEDULED_REPORTS"
    '''
    :stability: experimental
    '''
    MEDIA_STREAMS = "MEDIA_STREAMS"
    '''
    :stability: experimental
    '''
    CONTACT_TRACE_RECORDS = "CONTACT_TRACE_RECORDS"
    '''
    :stability: experimental
    '''
    AGENT_EVENTS = "AGENT_EVENTS"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.TelephonyConfigProps",
    jsii_struct_bases=[],
    name_mapping={
        "inbound_calls": "inboundCalls",
        "outbound_calls": "outboundCalls",
        "early_media_enabled": "earlyMediaEnabled",
        "multi_party_chat_conference": "multiPartyChatConference",
        "multi_party_conference": "multiPartyConference",
    },
)
class TelephonyConfigProps:
    def __init__(
        self,
        *,
        inbound_calls: builtins.bool,
        outbound_calls: builtins.bool,
        early_media_enabled: typing.Optional[builtins.bool] = None,
        multi_party_chat_conference: typing.Optional[builtins.bool] = None,
        multi_party_conference: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param inbound_calls: (experimental) Whether inbound calls are allowed. (INBOUND_CALLS)
        :param outbound_calls: (experimental) Whether outbound calls are allowed. (OUTBOUND_CALLS)
        :param early_media_enabled: (experimental) Whether early media is enabled.
        :param multi_party_chat_conference: (experimental) Whether multi party chat is enabled. (MULTI_PARTY_CHAT_CONFERENCE)
        :param multi_party_conference: (experimental) Whether multi party conference is enabled. (MULTI_PARTY_CONFERENCE)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a36f508c5ab4605ae7cbcff9da972b0373f3feb5397ded6929bfa5bc83c4b47)
            check_type(argname="argument inbound_calls", value=inbound_calls, expected_type=type_hints["inbound_calls"])
            check_type(argname="argument outbound_calls", value=outbound_calls, expected_type=type_hints["outbound_calls"])
            check_type(argname="argument early_media_enabled", value=early_media_enabled, expected_type=type_hints["early_media_enabled"])
            check_type(argname="argument multi_party_chat_conference", value=multi_party_chat_conference, expected_type=type_hints["multi_party_chat_conference"])
            check_type(argname="argument multi_party_conference", value=multi_party_conference, expected_type=type_hints["multi_party_conference"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "inbound_calls": inbound_calls,
            "outbound_calls": outbound_calls,
        }
        if early_media_enabled is not None:
            self._values["early_media_enabled"] = early_media_enabled
        if multi_party_chat_conference is not None:
            self._values["multi_party_chat_conference"] = multi_party_chat_conference
        if multi_party_conference is not None:
            self._values["multi_party_conference"] = multi_party_conference

    @builtins.property
    def inbound_calls(self) -> builtins.bool:
        '''(experimental) Whether inbound calls are allowed.

        (INBOUND_CALLS)

        :stability: experimental
        '''
        result = self._values.get("inbound_calls")
        assert result is not None, "Required property 'inbound_calls' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def outbound_calls(self) -> builtins.bool:
        '''(experimental) Whether outbound calls are allowed.

        (OUTBOUND_CALLS)

        :stability: experimental
        '''
        result = self._values.get("outbound_calls")
        assert result is not None, "Required property 'outbound_calls' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def early_media_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether early media is enabled.

        :stability: experimental
        '''
        result = self._values.get("early_media_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def multi_party_chat_conference(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether multi party chat is enabled.

        (MULTI_PARTY_CHAT_CONFERENCE)

        :stability: experimental
        '''
        result = self._values.get("multi_party_chat_conference")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def multi_party_conference(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether multi party conference is enabled.

        (MULTI_PARTY_CONFERENCE)

        :stability: experimental
        '''
        result = self._values.get("multi_party_conference")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TelephonyConfigProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ITrafficDistributionGroup)
class TrafficDistributionGroup(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.TrafficDistributionGroup",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        instance: "IInstance",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance: (experimental) The AWS connect instance to attach the traffic distribution group to.
        :param name: (experimental) The name of the traffic distribution group.
        :param description: (experimental) A description of the traffic distribution group.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27192f3316e42fd457fd61be44d4c1def160c2cf3ae98366858a7319e1627e14)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TrafficDistributionGroupProps(
            instance=instance, name=name, description=description
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="trafficDistributionGroup")
    def traffic_distribution_group(
        self,
    ) -> "_aws_cdk_aws_connect_ceddda9d.CfnTrafficDistributionGroup":
        '''
        :stability: experimental
        '''
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnTrafficDistributionGroup", jsii.get(self, "trafficDistributionGroup"))

    @builtins.property
    @jsii.member(jsii_name="trafficDistributionGroupArn")
    def traffic_distribution_group_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "trafficDistributionGroupArn"))


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.TrafficDistributionGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "instance": "instance",
        "name": "name",
        "description": "description",
    },
)
class TrafficDistributionGroupProps:
    def __init__(
        self,
        *,
        instance: "IInstance",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance: (experimental) The AWS connect instance to attach the traffic distribution group to.
        :param name: (experimental) The name of the traffic distribution group.
        :param description: (experimental) A description of the traffic distribution group.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__862d50ab6f2cd1936b5695dec0d1a01846ad48d59993c5167dc53f780a559cc9)
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance": instance,
            "name": name,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def instance(self) -> "IInstance":
        '''(experimental) The AWS connect instance to attach the traffic distribution group to.

        :stability: experimental
        '''
        result = self._values.get("instance")
        assert result is not None, "Required property 'instance' is missing"
        return typing.cast("IInstance", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the traffic distribution group.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description of the traffic distribution group.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TrafficDistributionGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IUser)
class User(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.User",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        instance: "IInstance",
        phone_config: typing.Union["UserPhoneConfigProps", typing.Dict[builtins.str, typing.Any]],
        proficiencies: typing.Sequence[typing.Union["UserProficiencyProps", typing.Dict[builtins.str, typing.Any]]],
        routing_profile: "IRoutingProfile",
        security_profiles: typing.Sequence["ISecurityProfile"],
        username: builtins.str,
        directory_user_id: typing.Optional[builtins.str] = None,
        hierarchy_group: typing.Optional["IHierarchyGroup"] = None,
        identity_info: typing.Optional[typing.Union["UserIdentityInfoProps", typing.Dict[builtins.str, typing.Any]]] = None,
        password: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance: 
        :param phone_config: 
        :param proficiencies: 
        :param routing_profile: 
        :param security_profiles: (experimental) The security profiles to associate with the user. At least one must be specified
        :param username: 
        :param directory_user_id: 
        :param hierarchy_group: 
        :param identity_info: 
        :param password: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01db7b40096e5865646ef25642423d66ddb1959f8ac41925fec407ab0b31bc5a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = UserProps(
            instance=instance,
            phone_config=phone_config,
            proficiencies=proficiencies,
            routing_profile=routing_profile,
            security_profiles=security_profiles,
            username=username,
            directory_user_id=directory_user_id,
            hierarchy_group=hierarchy_group,
            identity_info=identity_info,
            password=password,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromLookup")
    @builtins.classmethod
    def from_lookup(
        cls,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        instance_arn: builtins.str,
        user_arn: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> "IUser":
        '''
        :param scope: -
        :param id: -
        :param instance_arn: 
        :param user_arn: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__765b8268338bf771470d6b2cfd5960a852ea8c2085544fe8f8d8e478984583c1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = UserLookupOptions(
            instance_arn=instance_arn, user_arn=user_arn, username=username
        )

        return typing.cast("IUser", jsii.sinvoke(cls, "fromLookup", [scope, id, options]))

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> "_aws_cdk_aws_connect_ceddda9d.CfnUser":
        '''
        :stability: experimental
        '''
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnUser", jsii.get(self, "user"))

    @builtins.property
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> builtins.str:
        '''(experimental) The ARN of the connect user.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "userArn"))


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.UserIdentityInfoProps",
    jsii_struct_bases=[],
    name_mapping={
        "email": "email",
        "first_name": "firstName",
        "last_name": "lastName",
        "mobile_number": "mobileNumber",
        "secondary_email": "secondaryEmail",
    },
)
class UserIdentityInfoProps:
    def __init__(
        self,
        *,
        email: typing.Optional[builtins.str] = None,
        first_name: typing.Optional[builtins.str] = None,
        last_name: typing.Optional[builtins.str] = None,
        mobile_number: typing.Optional[builtins.str] = None,
        secondary_email: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param email: 
        :param first_name: 
        :param last_name: 
        :param mobile_number: 
        :param secondary_email: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d3bcff9b917338b2dd494d3fe904c9b56362e73d74165c85cc84e5872a9dbfc)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument first_name", value=first_name, expected_type=type_hints["first_name"])
            check_type(argname="argument last_name", value=last_name, expected_type=type_hints["last_name"])
            check_type(argname="argument mobile_number", value=mobile_number, expected_type=type_hints["mobile_number"])
            check_type(argname="argument secondary_email", value=secondary_email, expected_type=type_hints["secondary_email"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if email is not None:
            self._values["email"] = email
        if first_name is not None:
            self._values["first_name"] = first_name
        if last_name is not None:
            self._values["last_name"] = last_name
        if mobile_number is not None:
            self._values["mobile_number"] = mobile_number
        if secondary_email is not None:
            self._values["secondary_email"] = secondary_email

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def first_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("first_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("last_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mobile_number(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("mobile_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secondary_email(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("secondary_email")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserIdentityInfoProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.UserLookupOptions",
    jsii_struct_bases=[],
    name_mapping={
        "instance_arn": "instanceArn",
        "user_arn": "userArn",
        "username": "username",
    },
)
class UserLookupOptions:
    def __init__(
        self,
        *,
        instance_arn: builtins.str,
        user_arn: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance_arn: 
        :param user_arn: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61e13a1115e14d7a58860d33076002cd49d813cedb8d05f3fa28fa7bd0cb09b8)
            check_type(argname="argument instance_arn", value=instance_arn, expected_type=type_hints["instance_arn"])
            check_type(argname="argument user_arn", value=user_arn, expected_type=type_hints["user_arn"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_arn": instance_arn,
        }
        if user_arn is not None:
            self._values["user_arn"] = user_arn
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_arn")
        assert result is not None, "Required property 'instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_arn(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("user_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserLookupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.UserPhoneConfigProps",
    jsii_struct_bases=[],
    name_mapping={
        "phone_type": "phoneType",
        "after_contact_work_time_limit": "afterContactWorkTimeLimit",
        "auto_accept": "autoAccept",
        "desk_phone_number": "deskPhoneNumber",
        "persistent_connection": "persistentConnection",
    },
)
class UserPhoneConfigProps:
    def __init__(
        self,
        *,
        phone_type: "UserPhoneType",
        after_contact_work_time_limit: typing.Optional[jsii.Number] = None,
        auto_accept: typing.Optional[builtins.bool] = None,
        desk_phone_number: typing.Optional[builtins.str] = None,
        persistent_connection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param phone_type: 
        :param after_contact_work_time_limit: 
        :param auto_accept: 
        :param desk_phone_number: 
        :param persistent_connection: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9784773eb34f1a932aa156e42364cf78f1ead935624a2ba1afaf2d8b73a8d5f1)
            check_type(argname="argument phone_type", value=phone_type, expected_type=type_hints["phone_type"])
            check_type(argname="argument after_contact_work_time_limit", value=after_contact_work_time_limit, expected_type=type_hints["after_contact_work_time_limit"])
            check_type(argname="argument auto_accept", value=auto_accept, expected_type=type_hints["auto_accept"])
            check_type(argname="argument desk_phone_number", value=desk_phone_number, expected_type=type_hints["desk_phone_number"])
            check_type(argname="argument persistent_connection", value=persistent_connection, expected_type=type_hints["persistent_connection"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "phone_type": phone_type,
        }
        if after_contact_work_time_limit is not None:
            self._values["after_contact_work_time_limit"] = after_contact_work_time_limit
        if auto_accept is not None:
            self._values["auto_accept"] = auto_accept
        if desk_phone_number is not None:
            self._values["desk_phone_number"] = desk_phone_number
        if persistent_connection is not None:
            self._values["persistent_connection"] = persistent_connection

    @builtins.property
    def phone_type(self) -> "UserPhoneType":
        '''
        :stability: experimental
        '''
        result = self._values.get("phone_type")
        assert result is not None, "Required property 'phone_type' is missing"
        return typing.cast("UserPhoneType", result)

    @builtins.property
    def after_contact_work_time_limit(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("after_contact_work_time_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def auto_accept(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("auto_accept")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def desk_phone_number(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("desk_phone_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def persistent_connection(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("persistent_connection")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserPhoneConfigProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@netforbpo/aws-cdk-aws-connect-lib.UserPhoneType")
class UserPhoneType(enum.Enum):
    '''
    :stability: experimental
    '''

    SOFT_PHONE = "SOFT_PHONE"
    '''
    :stability: experimental
    '''
    DESK_PHONE = "DESK_PHONE"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.UserProficiencyProps",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_name": "attributeName",
        "attribute_value": "attributeValue",
        "proficiency_level": "proficiencyLevel",
    },
)
class UserProficiencyProps:
    def __init__(
        self,
        *,
        attribute_name: builtins.str,
        attribute_value: builtins.str,
        proficiency_level: jsii.Number,
    ) -> None:
        '''
        :param attribute_name: 
        :param attribute_value: 
        :param proficiency_level: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6cdc625fbcfa0165f0f4b9abaca8e94a97c9b7137673a973f56e1857123c1f4)
            check_type(argname="argument attribute_name", value=attribute_name, expected_type=type_hints["attribute_name"])
            check_type(argname="argument attribute_value", value=attribute_value, expected_type=type_hints["attribute_value"])
            check_type(argname="argument proficiency_level", value=proficiency_level, expected_type=type_hints["proficiency_level"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "attribute_name": attribute_name,
            "attribute_value": attribute_value,
            "proficiency_level": proficiency_level,
        }

    @builtins.property
    def attribute_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("attribute_name")
        assert result is not None, "Required property 'attribute_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_value(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("attribute_value")
        assert result is not None, "Required property 'attribute_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def proficiency_level(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("proficiency_level")
        assert result is not None, "Required property 'proficiency_level' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserProficiencyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.UserProps",
    jsii_struct_bases=[],
    name_mapping={
        "instance": "instance",
        "phone_config": "phoneConfig",
        "proficiencies": "proficiencies",
        "routing_profile": "routingProfile",
        "security_profiles": "securityProfiles",
        "username": "username",
        "directory_user_id": "directoryUserId",
        "hierarchy_group": "hierarchyGroup",
        "identity_info": "identityInfo",
        "password": "password",
    },
)
class UserProps:
    def __init__(
        self,
        *,
        instance: "IInstance",
        phone_config: typing.Union["UserPhoneConfigProps", typing.Dict[builtins.str, typing.Any]],
        proficiencies: typing.Sequence[typing.Union["UserProficiencyProps", typing.Dict[builtins.str, typing.Any]]],
        routing_profile: "IRoutingProfile",
        security_profiles: typing.Sequence["ISecurityProfile"],
        username: builtins.str,
        directory_user_id: typing.Optional[builtins.str] = None,
        hierarchy_group: typing.Optional["IHierarchyGroup"] = None,
        identity_info: typing.Optional[typing.Union["UserIdentityInfoProps", typing.Dict[builtins.str, typing.Any]]] = None,
        password: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance: 
        :param phone_config: 
        :param proficiencies: 
        :param routing_profile: 
        :param security_profiles: (experimental) The security profiles to associate with the user. At least one must be specified
        :param username: 
        :param directory_user_id: 
        :param hierarchy_group: 
        :param identity_info: 
        :param password: 

        :stability: experimental
        '''
        if isinstance(phone_config, dict):
            phone_config = UserPhoneConfigProps(**phone_config)
        if isinstance(identity_info, dict):
            identity_info = UserIdentityInfoProps(**identity_info)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93271760644f43e84292ddf06145230f941db89bac0eb5fdf67b4e50c6896d51)
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
            check_type(argname="argument phone_config", value=phone_config, expected_type=type_hints["phone_config"])
            check_type(argname="argument proficiencies", value=proficiencies, expected_type=type_hints["proficiencies"])
            check_type(argname="argument routing_profile", value=routing_profile, expected_type=type_hints["routing_profile"])
            check_type(argname="argument security_profiles", value=security_profiles, expected_type=type_hints["security_profiles"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument directory_user_id", value=directory_user_id, expected_type=type_hints["directory_user_id"])
            check_type(argname="argument hierarchy_group", value=hierarchy_group, expected_type=type_hints["hierarchy_group"])
            check_type(argname="argument identity_info", value=identity_info, expected_type=type_hints["identity_info"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance": instance,
            "phone_config": phone_config,
            "proficiencies": proficiencies,
            "routing_profile": routing_profile,
            "security_profiles": security_profiles,
            "username": username,
        }
        if directory_user_id is not None:
            self._values["directory_user_id"] = directory_user_id
        if hierarchy_group is not None:
            self._values["hierarchy_group"] = hierarchy_group
        if identity_info is not None:
            self._values["identity_info"] = identity_info
        if password is not None:
            self._values["password"] = password

    @builtins.property
    def instance(self) -> "IInstance":
        '''
        :stability: experimental
        '''
        result = self._values.get("instance")
        assert result is not None, "Required property 'instance' is missing"
        return typing.cast("IInstance", result)

    @builtins.property
    def phone_config(self) -> "UserPhoneConfigProps":
        '''
        :stability: experimental
        '''
        result = self._values.get("phone_config")
        assert result is not None, "Required property 'phone_config' is missing"
        return typing.cast("UserPhoneConfigProps", result)

    @builtins.property
    def proficiencies(self) -> typing.List["UserProficiencyProps"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("proficiencies")
        assert result is not None, "Required property 'proficiencies' is missing"
        return typing.cast(typing.List["UserProficiencyProps"], result)

    @builtins.property
    def routing_profile(self) -> "IRoutingProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("routing_profile")
        assert result is not None, "Required property 'routing_profile' is missing"
        return typing.cast("IRoutingProfile", result)

    @builtins.property
    def security_profiles(self) -> typing.List["ISecurityProfile"]:
        '''(experimental) The security profiles to associate with the user.

        At least one must be specified

        :stability: experimental
        '''
        result = self._values.get("security_profiles")
        assert result is not None, "Required property 'security_profiles' is missing"
        return typing.cast(typing.List["ISecurityProfile"], result)

    @builtins.property
    def username(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def directory_user_id(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("directory_user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hierarchy_group(self) -> typing.Optional["IHierarchyGroup"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("hierarchy_group")
        return typing.cast(typing.Optional["IHierarchyGroup"], result)

    @builtins.property
    def identity_info(self) -> typing.Optional["UserIdentityInfoProps"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("identity_info")
        return typing.cast(typing.Optional["UserIdentityInfoProps"], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IContactFlow)
class ContactFlow(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ContactFlow",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        content: builtins.str,
        instance: "IInstance",
        name: builtins.str,
        type: "ContactFlowType",
        description: typing.Optional[builtins.str] = None,
        state: typing.Optional["ContactFlowState"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param content: 
        :param instance: 
        :param name: 
        :param type: 
        :param description: 
        :param state: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b810a02c04b50b94dbb2dd9e96be32f5539ccef31001c553172386ccb4749af)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ContactFlowProps(
            content=content,
            instance=instance,
            name=name,
            type=type,
            description=description,
            state=state,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromLookup")
    @builtins.classmethod
    def from_lookup(
        cls,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        contact_flow_arn: typing.Optional[builtins.str] = None,
        contact_flow_name: typing.Optional[builtins.str] = None,
        instance_arn: typing.Optional[builtins.str] = None,
    ) -> "IContactFlow":
        '''
        :param scope: -
        :param id: -
        :param contact_flow_arn: 
        :param contact_flow_name: 
        :param instance_arn: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97b2711f59b0901eeeea703d940648e7d4f104916e2cc6eac17ce0a374c0e97c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = ContactFlowLookupOptions(
            contact_flow_arn=contact_flow_arn,
            contact_flow_name=contact_flow_name,
            instance_arn=instance_arn,
        )

        return typing.cast("IContactFlow", jsii.sinvoke(cls, "fromLookup", [scope, id, options]))

    @builtins.property
    @jsii.member(jsii_name="contactFlowArn")
    def contact_flow_arn(self) -> builtins.str:
        '''(experimental) The ARN of the flow.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "contactFlowArn"))

    @builtins.property
    @jsii.member(jsii_name="contactFlowName")
    def contact_flow_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "contactFlowName"))

    @builtins.property
    @jsii.member(jsii_name="flow")
    def flow(self) -> "_aws_cdk_aws_connect_ceddda9d.CfnContactFlow":
        '''
        :stability: experimental
        '''
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnContactFlow", jsii.get(self, "flow"))

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceArn"))


@jsii.implements(IContactFlowModule)
class ContactFlowModule(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.ContactFlowModule",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        content: builtins.str,
        instance: "IInstance",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        state: typing.Optional["ContactFlowModuleState"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param content: 
        :param instance: 
        :param name: 
        :param description: 
        :param state: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__513266e9e1aef658eb757f8df85bb94a8704484ef884737119ac10fc8e3d8bcd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ContactFlowModuleProps(
            content=content,
            instance=instance,
            name=name,
            description=description,
            state=state,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromLookup")
    @builtins.classmethod
    def from_lookup(
        cls,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        contact_flow_module_arn: typing.Optional[builtins.str] = None,
        contact_flow_module_name: typing.Optional[builtins.str] = None,
        instance_arn: typing.Optional[builtins.str] = None,
    ) -> "IContactFlowModule":
        '''
        :param scope: -
        :param id: -
        :param contact_flow_module_arn: 
        :param contact_flow_module_name: 
        :param instance_arn: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa1418c6984aae5dde375f4529b9ffd45bd47064b64e26b7d19f7d325599fff7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = ContactFlowModuleLookupOptions(
            contact_flow_module_arn=contact_flow_module_arn,
            contact_flow_module_name=contact_flow_module_name,
            instance_arn=instance_arn,
        )

        return typing.cast("IContactFlowModule", jsii.sinvoke(cls, "fromLookup", [scope, id, options]))

    @builtins.property
    @jsii.member(jsii_name="contactFlowModuleArn")
    def contact_flow_module_arn(self) -> builtins.str:
        '''(experimental) The ARN of the flow.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "contactFlowModuleArn"))

    @builtins.property
    @jsii.member(jsii_name="contactFlowModuleName")
    def contact_flow_module_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "contactFlowModuleName"))

    @builtins.property
    @jsii.member(jsii_name="flowModule")
    def flow_module(self) -> "_aws_cdk_aws_connect_ceddda9d.CfnContactFlowModule":
        '''
        :stability: experimental
        '''
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnContactFlowModule", jsii.get(self, "flowModule"))

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceArn"))


@jsii.implements(IEmailAddress)
class EmailAddress(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.EmailAddress",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        email_address: builtins.str,
        instance: "IInstance",
        aliases: typing.Optional[typing.Sequence["IEmailAddress"]] = None,
        description: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param email_address: (experimental) The email address.
        :param instance: (experimental) The AWS connect instance to attach the email address to.
        :param aliases: (experimental) The aliases for the email address.
        :param description: (experimental) A description of the email address.
        :param display_name: (experimental) The display name of the email address.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66d5a14a4fda9a3ed2cfaf518f12fef5322aa79237597a4937f0ae7b57a99337)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EmailAddressProps(
            email_address=email_address,
            instance=instance,
            aliases=aliases,
            description=description,
            display_name=display_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="emailAddress")
    def email_address(self) -> "_aws_cdk_aws_connect_ceddda9d.CfnEmailAddress":
        '''
        :stability: experimental
        '''
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnEmailAddress", jsii.get(self, "emailAddress"))

    @builtins.property
    @jsii.member(jsii_name="emailAddressArn")
    def email_address_arn(self) -> builtins.str:
        '''(experimental) The ARN of the email address.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "emailAddressArn"))


@jsii.implements(IHoursOfOperation)
class HoursOfOperation(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@netforbpo/aws-cdk-aws-connect-lib.HoursOfOperation",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        instance: "IInstance",
        name: builtins.str,
        definitions: typing.Optional[typing.Sequence["HoursOfOperationDefinition"]] = None,
        time_zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance: (experimental) The AWS connect instance to attach the hours of operation to.
        :param name: (experimental) The name of the hours of operation.
        :param definitions: (experimental) the set of definitions for the hours of operation.
        :param time_zone: (experimental) Timezone to define the hours of operation in. Defaults to UTC.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0af1a70b2a81b4677284597a3d4bf4e662007e533dba385b2527ca3cf1373068)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HoursOfOperationProps(
            instance=instance, name=name, definitions=definitions, time_zone=time_zone
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromLookup")
    @builtins.classmethod
    def from_lookup(
        cls,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        instance_arn: builtins.str,
        hours_of_operation_arn: typing.Optional[builtins.str] = None,
        hours_of_operation_name: typing.Optional[builtins.str] = None,
    ) -> "IHoursOfOperation":
        '''
        :param scope: -
        :param id: -
        :param instance_arn: 
        :param hours_of_operation_arn: 
        :param hours_of_operation_name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4673e61b6dd0fc3edfdb5fb7a03ed85ccf8770a847ad587524f97b0889b5cb12)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = HoursOfOperationLookupOptions(
            instance_arn=instance_arn,
            hours_of_operation_arn=hours_of_operation_arn,
            hours_of_operation_name=hours_of_operation_name,
        )

        return typing.cast("IHoursOfOperation", jsii.sinvoke(cls, "fromLookup", [scope, id, options]))

    @builtins.property
    @jsii.member(jsii_name="hoursOfOperation")
    def hours_of_operation(self) -> "_aws_cdk_aws_connect_ceddda9d.CfnHoursOfOperation":
        '''
        :stability: experimental
        '''
        return typing.cast("_aws_cdk_aws_connect_ceddda9d.CfnHoursOfOperation", jsii.get(self, "hoursOfOperation"))

    @builtins.property
    @jsii.member(jsii_name="hoursOfOperationArn")
    def hours_of_operation_arn(self) -> builtins.str:
        '''(experimental) The ARN of the hours of operation.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "hoursOfOperationArn"))

    @builtins.property
    @jsii.member(jsii_name="instance")
    def instance(self) -> "IInstance":
        '''
        :stability: experimental
        '''
        return typing.cast("IInstance", jsii.get(self, "instance"))

    @builtins.property
    @jsii.member(jsii_name="instanceArn")
    def instance_arn(self) -> builtins.str:
        '''(experimental) The ARN of the attached instance.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceArn"))


__all__ = [
    "ContactFlow",
    "ContactFlowLookupOptions",
    "ContactFlowModule",
    "ContactFlowModuleLookupOptions",
    "ContactFlowModuleProps",
    "ContactFlowModuleState",
    "ContactFlowProps",
    "ContactFlowState",
    "ContactFlowType",
    "EmailAddress",
    "EmailAddressProps",
    "HoursOfOperation",
    "HoursOfOperationDayOfWeek",
    "HoursOfOperationDefinition",
    "HoursOfOperationLookupOptions",
    "HoursOfOperationProps",
    "IContactFlow",
    "IContactFlowModule",
    "IEmailAddress",
    "IHierarchyGroup",
    "IHoursOfOperation",
    "IInstance",
    "IPhoneNumber",
    "IQueue",
    "IQuickConnect",
    "IRoutingProfile",
    "ISecurityProfile",
    "ITrafficDistributionGroup",
    "IUser",
    "IdentityManagementType",
    "Instance",
    "InstanceLookupOptions",
    "InstanceProps",
    "OtherConfigProps",
    "PhoneNumber",
    "PhoneNumberProps",
    "PhoneNumberType",
    "PollyConfigProps",
    "Queue",
    "QueueOutboundCallerConfig",
    "QueueProps",
    "QueueStatus",
    "QuickConnect",
    "QuickConnectProps",
    "QuickConnectQueueConfig",
    "QuickConnectType",
    "QuickConnectUserConfig",
    "StorageConfig",
    "StorageConfigKinesisFirehose",
    "StorageConfigKinesisStream",
    "StorageConfigKinesisVideoStream",
    "StorageConfigS3",
    "StorageConfigType",
    "StorageEncryptionConfig",
    "StorageEncryptionType",
    "StorageResourceType",
    "TelephonyConfigProps",
    "TrafficDistributionGroup",
    "TrafficDistributionGroupProps",
    "User",
    "UserIdentityInfoProps",
    "UserLookupOptions",
    "UserPhoneConfigProps",
    "UserPhoneType",
    "UserProficiencyProps",
    "UserProps",
]

publication.publish()

def _typecheckingstub__612add7e7784dbb2fdd2d884a3166a6f11ec1ab27dcd6a16d3a3f7c4437013fb(
    *,
    contact_flow_arn: typing.Optional[builtins.str] = None,
    contact_flow_name: typing.Optional[builtins.str] = None,
    instance_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30462058666bbbe70edb9e8e93fdd0b547c930d10abd2e220810139342294c55(
    *,
    contact_flow_module_arn: typing.Optional[builtins.str] = None,
    contact_flow_module_name: typing.Optional[builtins.str] = None,
    instance_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b31e7ecb7c01891c8e66356be42d6f920eaa88baba508eeaa92678ebe46c93dc(
    *,
    content: builtins.str,
    instance: IInstance,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    state: typing.Optional[ContactFlowModuleState] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__840f428237fdaa4d433c15ac2450573484f0b9d381e51f0f5c49818f6a902552(
    *,
    content: builtins.str,
    instance: IInstance,
    name: builtins.str,
    type: ContactFlowType,
    description: typing.Optional[builtins.str] = None,
    state: typing.Optional[ContactFlowState] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab1e0b61936fc552f9cdf849545caa3f1818ce11a90da643054e86d5bbc552c8(
    *,
    email_address: builtins.str,
    instance: IInstance,
    aliases: typing.Optional[typing.Sequence[IEmailAddress]] = None,
    description: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e2a14b3b922288969469f29db5056b9c306fc5210950f68fdf4695585aac863(
    day: HoursOfOperationDayOfWeek,
    start_time: builtins.str,
    end_time: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a0d730f5d911cfdb1ca8e31ea08431cd37de560378361b10d9b6963a7493fb1(
    time: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c58bd826778475e54a81b53753c3b0be186cec7b65ba62eca6af04b12fedba3(
    *,
    instance_arn: builtins.str,
    hours_of_operation_arn: typing.Optional[builtins.str] = None,
    hours_of_operation_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebc62e22f5715fb189129a4377a59686c2ff01421d1ab7ced6b38ca63d8e8085(
    *,
    instance: IInstance,
    name: builtins.str,
    definitions: typing.Optional[typing.Sequence[HoursOfOperationDefinition]] = None,
    time_zone: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__408938508c4b72245f0fb331acf58a74b88ad5bf6e024cf2147a5a60074db772(
    config: StorageConfig,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f02b04749de22f2fbe9c10ec899e58cc0b47949c3685b89f1ea3e4deed402daf(
    func: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01bdeccf53b04c5691b183c8b4b2d4bab29fad4a4ea84063187b95d9740ea861(
    bot: _aws_cdk_interfaces_aws_lex_ceddda9d.IBotAliasRef,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d4ca1ccc95e1fd44217cf0d3d24eb076784056088d595f21c857899af7b8e28(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    identity_type: IdentityManagementType,
    telephony_config: typing.Union[TelephonyConfigProps, typing.Dict[builtins.str, typing.Any]],
    directory_id: typing.Optional[builtins.str] = None,
    instance_alias: typing.Optional[builtins.str] = None,
    other_config: typing.Optional[typing.Union[OtherConfigProps, typing.Dict[builtins.str, typing.Any]]] = None,
    polly_config: typing.Optional[typing.Union[PollyConfigProps, typing.Dict[builtins.str, typing.Any]]] = None,
    storage_configs: typing.Optional[typing.Sequence[StorageConfig]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c53d68a4360f5b158c85f6e90de7aca880c357aa4e901f4cb0d442a107c3b68d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_arn: typing.Optional[builtins.str] = None,
    instance_id: typing.Optional[builtins.str] = None,
    instance_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9843491e91dbc13a26d18eff5b8410790856145a2b9fc93614e69e34df7a3b6(
    config: StorageConfig,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88a34a45e0f2cef26c539c2a6ee3467dc330a4c2d5d14b74c98c7f6a7944481b(
    func: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a260f868e1acef3b2c069c4c84e1365d5fcafa08a7e749dc939a759c49604ea3(
    bot: _aws_cdk_interfaces_aws_lex_ceddda9d.IBotAliasRef,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c2ac0b77614759f52400f4e3b5705e02f36450ea9fb0e7a287113cf90e480c8(
    *,
    instance_arn: typing.Optional[builtins.str] = None,
    instance_id: typing.Optional[builtins.str] = None,
    instance_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24ec8441d8b3275943bb5034b7d2a90b8151b49cf837c06c930c772bbd4fbe16(
    *,
    identity_type: IdentityManagementType,
    telephony_config: typing.Union[TelephonyConfigProps, typing.Dict[builtins.str, typing.Any]],
    directory_id: typing.Optional[builtins.str] = None,
    instance_alias: typing.Optional[builtins.str] = None,
    other_config: typing.Optional[typing.Union[OtherConfigProps, typing.Dict[builtins.str, typing.Any]]] = None,
    polly_config: typing.Optional[typing.Union[PollyConfigProps, typing.Dict[builtins.str, typing.Any]]] = None,
    storage_configs: typing.Optional[typing.Sequence[StorageConfig]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84716c68401fa6516bffd90f0f78d0c162f73bb7f10d9e410378eacaab0d9a25(
    *,
    contactflow_logs: typing.Optional[builtins.bool] = None,
    contact_lens: typing.Optional[builtins.bool] = None,
    enhanced_chat_monitoring: typing.Optional[builtins.bool] = None,
    enhanced_contact_monitoring: typing.Optional[builtins.bool] = None,
    high_volume_out_bound: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a759311bb7fca42f6e295e529cee0557768c3410ed33b911e3492126a3285aa1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    target: typing.Union[IInstance, ITrafficDistributionGroup],
    country_code: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    prefix: typing.Optional[builtins.str] = None,
    source_phone_number_arn: typing.Optional[builtins.str] = None,
    type: typing.Optional[PhoneNumberType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__831f7cf9bf3db596ec7b8a8e73c054160c221bbaac018bbd0d8608a561a4566f(
    *,
    target: typing.Union[IInstance, ITrafficDistributionGroup],
    country_code: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    prefix: typing.Optional[builtins.str] = None,
    source_phone_number_arn: typing.Optional[builtins.str] = None,
    type: typing.Optional[PhoneNumberType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b263cb24cbf99c98cad20e61187924e03e8fbab6c737d87a7e25ae94e0b290(
    *,
    auto_resolve_best_voices: typing.Optional[builtins.bool] = None,
    use_custom_tts_voices: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df1bf4f0dc9b67355d036f308b6547a29fadb0873bc99de78048f206373054ce(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    hours_of_operation: IHoursOfOperation,
    instance: IInstance,
    name: builtins.str,
    quick_connects: typing.Sequence[IQuickConnect],
    description: typing.Optional[builtins.str] = None,
    max_queue_size: typing.Optional[jsii.Number] = None,
    outbound_caller_config: typing.Optional[typing.Union[QueueOutboundCallerConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    outbound_email: typing.Optional[IEmailAddress] = None,
    status: typing.Optional[QueueStatus] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a1ba3ee3d693e1124f5d1db08fea9d2abc5c1c552618878a5867e558b5d9895(
    *,
    caller_id_name: builtins.str,
    caller_id_number: IPhoneNumber,
    flow: IContactFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa519a3ad62f67876eb28ebd135dbc254f97babc66a55ddf298d17177d8ac6ef(
    *,
    hours_of_operation: IHoursOfOperation,
    instance: IInstance,
    name: builtins.str,
    quick_connects: typing.Sequence[IQuickConnect],
    description: typing.Optional[builtins.str] = None,
    max_queue_size: typing.Optional[jsii.Number] = None,
    outbound_caller_config: typing.Optional[typing.Union[QueueOutboundCallerConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    outbound_email: typing.Optional[IEmailAddress] = None,
    status: typing.Optional[QueueStatus] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4ad015cef0a9423a9d350148a4c17b3bd58f9b1d807d14e064e5221a6e840f6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance: IInstance,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    phone_number: typing.Optional[builtins.str] = None,
    queue_config: typing.Optional[typing.Union[QuickConnectQueueConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    user_config: typing.Optional[typing.Union[QuickConnectUserConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94f1fb4aaf1c08212fff677008c00287c6a869e8d0b841a0967a32c04ef17cbd(
    *,
    instance: IInstance,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    phone_number: typing.Optional[builtins.str] = None,
    queue_config: typing.Optional[typing.Union[QuickConnectQueueConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    user_config: typing.Optional[typing.Union[QuickConnectUserConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4612b1d08466e062f3e2f2f1f23b186b1064b60aec86a19fd51aa91622bce30f(
    *,
    flow: IContactFlow,
    queue: IQueue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40391ee66807d4c7da85cdf08dc043c052c8d84971387a70e1ef04106d05bd90(
    *,
    flow: IContactFlow,
    user: IUser,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96192c7bebafbf59e5c33ceee4d17690a4bce248436ba705aa655a4959a4d488(
    resource_type: StorageResourceType,
    *,
    firehose: _aws_cdk_aws_kinesisfirehose_ceddda9d.IDeliveryStream,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__573a3a4671d626227bf31bccb0ea9d955b93c94091f00b3a83949a176d4590df(
    resource_type: StorageResourceType,
    *,
    stream: _aws_cdk_aws_kinesis_ceddda9d.IStream,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06bd88047b1340ad9fdbbb62b68dbb151d90a284e6456aa45aa07d83ff153f72(
    resource_type: StorageResourceType,
    *,
    encryption_config: typing.Union[StorageEncryptionConfig, typing.Dict[builtins.str, typing.Any]],
    prefix: builtins.str,
    retention_period_hours: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b058c995809d45432a29ad56b83533d75a0d464706c3ff623f38fec215b58218(
    resource_type: StorageResourceType,
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    prefix: builtins.str,
    encryption_config: typing.Optional[typing.Union[StorageEncryptionConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b03dfc18b41f9f422f5179273c5a1998433e6ee745fe4bb1a6601ca4f51dae8c(
    instance_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ea13485e504ac921557e0160b99895f9350adfd2eb0a4b1fcbb1089c7bc13ca(
    *,
    firehose: _aws_cdk_aws_kinesisfirehose_ceddda9d.IDeliveryStream,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7dcf1d70d6cfaad8de61d1b28e5f928e580a29bc9556bd2d456cbfe5bca99ac(
    *,
    stream: _aws_cdk_aws_kinesis_ceddda9d.IStream,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b20d86be6495f57a1361ff6b0d24ef8033bb958580a458a5f4fc4dca8f0648ae(
    *,
    encryption_config: typing.Union[StorageEncryptionConfig, typing.Dict[builtins.str, typing.Any]],
    prefix: builtins.str,
    retention_period_hours: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0128197d9ef83f86e8fb494ed9b456f460f7c3bad3da43edd2db355c8fbc9ea(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    prefix: builtins.str,
    encryption_config: typing.Optional[typing.Union[StorageEncryptionConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__564ff8d21820f3b0ae50abff4c8d83da62a0d1d2b8836f923b6ddceeba2f44d1(
    *,
    encryption_key: _aws_cdk_aws_kms_ceddda9d.IKey,
    encryption_type: StorageEncryptionType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a36f508c5ab4605ae7cbcff9da972b0373f3feb5397ded6929bfa5bc83c4b47(
    *,
    inbound_calls: builtins.bool,
    outbound_calls: builtins.bool,
    early_media_enabled: typing.Optional[builtins.bool] = None,
    multi_party_chat_conference: typing.Optional[builtins.bool] = None,
    multi_party_conference: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27192f3316e42fd457fd61be44d4c1def160c2cf3ae98366858a7319e1627e14(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance: IInstance,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__862d50ab6f2cd1936b5695dec0d1a01846ad48d59993c5167dc53f780a559cc9(
    *,
    instance: IInstance,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01db7b40096e5865646ef25642423d66ddb1959f8ac41925fec407ab0b31bc5a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance: IInstance,
    phone_config: typing.Union[UserPhoneConfigProps, typing.Dict[builtins.str, typing.Any]],
    proficiencies: typing.Sequence[typing.Union[UserProficiencyProps, typing.Dict[builtins.str, typing.Any]]],
    routing_profile: IRoutingProfile,
    security_profiles: typing.Sequence[ISecurityProfile],
    username: builtins.str,
    directory_user_id: typing.Optional[builtins.str] = None,
    hierarchy_group: typing.Optional[IHierarchyGroup] = None,
    identity_info: typing.Optional[typing.Union[UserIdentityInfoProps, typing.Dict[builtins.str, typing.Any]]] = None,
    password: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__765b8268338bf771470d6b2cfd5960a852ea8c2085544fe8f8d8e478984583c1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_arn: builtins.str,
    user_arn: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d3bcff9b917338b2dd494d3fe904c9b56362e73d74165c85cc84e5872a9dbfc(
    *,
    email: typing.Optional[builtins.str] = None,
    first_name: typing.Optional[builtins.str] = None,
    last_name: typing.Optional[builtins.str] = None,
    mobile_number: typing.Optional[builtins.str] = None,
    secondary_email: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61e13a1115e14d7a58860d33076002cd49d813cedb8d05f3fa28fa7bd0cb09b8(
    *,
    instance_arn: builtins.str,
    user_arn: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9784773eb34f1a932aa156e42364cf78f1ead935624a2ba1afaf2d8b73a8d5f1(
    *,
    phone_type: UserPhoneType,
    after_contact_work_time_limit: typing.Optional[jsii.Number] = None,
    auto_accept: typing.Optional[builtins.bool] = None,
    desk_phone_number: typing.Optional[builtins.str] = None,
    persistent_connection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6cdc625fbcfa0165f0f4b9abaca8e94a97c9b7137673a973f56e1857123c1f4(
    *,
    attribute_name: builtins.str,
    attribute_value: builtins.str,
    proficiency_level: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93271760644f43e84292ddf06145230f941db89bac0eb5fdf67b4e50c6896d51(
    *,
    instance: IInstance,
    phone_config: typing.Union[UserPhoneConfigProps, typing.Dict[builtins.str, typing.Any]],
    proficiencies: typing.Sequence[typing.Union[UserProficiencyProps, typing.Dict[builtins.str, typing.Any]]],
    routing_profile: IRoutingProfile,
    security_profiles: typing.Sequence[ISecurityProfile],
    username: builtins.str,
    directory_user_id: typing.Optional[builtins.str] = None,
    hierarchy_group: typing.Optional[IHierarchyGroup] = None,
    identity_info: typing.Optional[typing.Union[UserIdentityInfoProps, typing.Dict[builtins.str, typing.Any]]] = None,
    password: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b810a02c04b50b94dbb2dd9e96be32f5539ccef31001c553172386ccb4749af(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    content: builtins.str,
    instance: IInstance,
    name: builtins.str,
    type: ContactFlowType,
    description: typing.Optional[builtins.str] = None,
    state: typing.Optional[ContactFlowState] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97b2711f59b0901eeeea703d940648e7d4f104916e2cc6eac17ce0a374c0e97c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    contact_flow_arn: typing.Optional[builtins.str] = None,
    contact_flow_name: typing.Optional[builtins.str] = None,
    instance_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__513266e9e1aef658eb757f8df85bb94a8704484ef884737119ac10fc8e3d8bcd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    content: builtins.str,
    instance: IInstance,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    state: typing.Optional[ContactFlowModuleState] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa1418c6984aae5dde375f4529b9ffd45bd47064b64e26b7d19f7d325599fff7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    contact_flow_module_arn: typing.Optional[builtins.str] = None,
    contact_flow_module_name: typing.Optional[builtins.str] = None,
    instance_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66d5a14a4fda9a3ed2cfaf518f12fef5322aa79237597a4937f0ae7b57a99337(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    email_address: builtins.str,
    instance: IInstance,
    aliases: typing.Optional[typing.Sequence[IEmailAddress]] = None,
    description: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0af1a70b2a81b4677284597a3d4bf4e662007e533dba385b2527ca3cf1373068(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance: IInstance,
    name: builtins.str,
    definitions: typing.Optional[typing.Sequence[HoursOfOperationDefinition]] = None,
    time_zone: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4673e61b6dd0fc3edfdb5fb7a03ed85ccf8770a847ad587524f97b0889b5cb12(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_arn: builtins.str,
    hours_of_operation_arn: typing.Optional[builtins.str] = None,
    hours_of_operation_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

for cls in [IContactFlow, IContactFlowModule, IEmailAddress, IHierarchyGroup, IHoursOfOperation, IInstance, IPhoneNumber, IQueue, IQuickConnect, IRoutingProfile, ISecurityProfile, ITrafficDistributionGroup, IUser]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
