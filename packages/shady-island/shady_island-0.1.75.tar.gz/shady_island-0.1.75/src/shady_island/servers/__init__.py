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

from .._jsii import *

import aws_cdk.aws_autoscaling as _aws_cdk_aws_autoscaling_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_efs as _aws_cdk_aws_efs_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8
from ..configuration import IFirewallRules as _IFirewallRules_115dd143


@jsii.data_type(
    jsii_type="shady-island.servers.CustomDomainOptions",
    jsii_struct_bases=[],
    name_mapping={"hosted_zone": "hostedZone", "subdomain": "subdomain"},
)
class CustomDomainOptions:
    def __init__(
        self,
        *,
        hosted_zone: "_aws_cdk_aws_route53_ceddda9d.IHostedZone",
        subdomain: builtins.str,
    ) -> None:
        '''Options for DNS record updates when the instance launches.

        :param hosted_zone: The Route 53 hosted zone where the record is upserted.
        :param subdomain: The subdomain for the record (e.g. ``bastion``, ``ssh``, ``jump``).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2db1d2891e6a764bd61683fbdec14a104accc85746f29662cd5bc9a4f83cfb6d)
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument subdomain", value=subdomain, expected_type=type_hints["subdomain"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hosted_zone": hosted_zone,
            "subdomain": subdomain,
        }

    @builtins.property
    def hosted_zone(self) -> "_aws_cdk_aws_route53_ceddda9d.IHostedZone":
        '''The Route 53 hosted zone where the record is upserted.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast("_aws_cdk_aws_route53_ceddda9d.IHostedZone", result)

    @builtins.property
    def subdomain(self) -> builtins.str:
        '''The subdomain for the record (e.g. ``bastion``, ``ssh``, ``jump``).'''
        result = self._values.get("subdomain")
        assert result is not None, "Required property 'subdomain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomDomainOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.servers.ElasticFileSystemMount",
    jsii_struct_bases=[],
    name_mapping={"directory": "directory", "file_system": "fileSystem"},
)
class ElasticFileSystemMount:
    def __init__(
        self,
        *,
        directory: builtins.str,
        file_system: "_aws_cdk_aws_efs_ceddda9d.IFileSystem",
    ) -> None:
        '''The details for a single EFS mount.

        :param directory: The path where the NFS volume should be mounted.
        :param file_system: The EFS filesystem to mount.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ce921d23c04ba7e05abe297fb0d1bf15a4742b2a29ae4cafa3506ed4e70afdc)
            check_type(argname="argument directory", value=directory, expected_type=type_hints["directory"])
            check_type(argname="argument file_system", value=file_system, expected_type=type_hints["file_system"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "directory": directory,
            "file_system": file_system,
        }

    @builtins.property
    def directory(self) -> builtins.str:
        '''The path where the NFS volume should be mounted.'''
        result = self._values.get("directory")
        assert result is not None, "Required property 'directory' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_system(self) -> "_aws_cdk_aws_efs_ceddda9d.IFileSystem":
        '''The EFS filesystem to mount.'''
        result = self._values.get("file_system")
        assert result is not None, "Required property 'file_system' is missing"
        return typing.cast("_aws_cdk_aws_efs_ceddda9d.IFileSystem", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticFileSystemMount(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_ec2_ceddda9d.IConnectable, _aws_cdk_aws_iam_ceddda9d.IGrantable)
class UbuntuLinuxBastion(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.servers.UbuntuLinuxBastion",
):
    '''A bastion host running Ubuntu GNU/Linux with an instance firewall.

    This construct produces an Auto-Scaling Group and corresponding launch
    template. The ASG has a minimum of zero instances and a maximum of one.
    Instances launched will be placed in a public subnet of the VPC.
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        vpc: "_aws_cdk_aws_ec2_ceddda9d.IVpc",
        apt_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        apt_repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
        architecture: typing.Optional["_aws_cdk_aws_ec2_ceddda9d.InstanceArchitecture"] = None,
        custom_domain: typing.Optional[typing.Union["CustomDomainOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        file_systems: typing.Optional[typing.Sequence[typing.Union["ElasticFileSystemMount", typing.Dict[builtins.str, typing.Any]]]] = None,
        install_aws_cli: typing.Optional[builtins.bool] = None,
        instance_type: typing.Optional["_aws_cdk_aws_ec2_ceddda9d.InstanceType"] = None,
        key_pair: typing.Optional["_aws_cdk_aws_ec2_ceddda9d.IKeyPair"] = None,
        role: typing.Optional["_aws_cdk_aws_iam_ceddda9d.IRole"] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, "_aws_cdk_aws_secretsmanager_ceddda9d.ISecret"]] = None,
        security_group: typing.Optional["_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup"] = None,
        ubuntu_version: typing.Optional[builtins.str] = None,
        volume_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''A bastion host running Ubuntu GNU/Linux.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param vpc: The VPC where the bastion will reside.
        :param apt_packages: An array of APT package names to install. If you supply any Elastic Filesystems to mount, this construct will also install the "nfs-common" package.
        :param apt_repositories: The names of repositories to enable using apt-add-repository. e.g. ppa:redislabs/redis
        :param architecture: The CPU architecture for the bastion. Default: - InstanceArchitecture.ARM_64
        :param custom_domain: The options for creating DNS records upon launch.
        :param enable_ipv6: Whether to enable IPv6. Default: - false
        :param file_systems: The Elastic Filesystems to mount.
        :param install_aws_cli: Whether to install the AWS CLI Snap package. Default: - true
        :param instance_type: The instance type for the bastion. Default: - t3.micro for X86_64, t4g.micro for ARM_64
        :param key_pair: The key pair to use for this instance. Default: - A new key pair is generated and stored in SSM Parameter Store
        :param role: The instance role (the trust policy must permit ec2.amazonaws.com). Default: - A new role is created.
        :param secrets: The secrets containing database credentials. The key of the object corresponds to the filename in ``/run/secrets``.
        :param security_group: The security group to attach to the bastion instance. Default: - A new security group is created
        :param ubuntu_version: The version of Ubuntu to use. Default: - 24.04
        :param volume_size: The size in gibibytes (GiB) of the primary disk volume. Default: - 10
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__feed70f44a62d1a377cfb6ba61d31a6adf4b75788815dea56858878124d3846a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = UbuntuLinuxBastionProps(
            vpc=vpc,
            apt_packages=apt_packages,
            apt_repositories=apt_repositories,
            architecture=architecture,
            custom_domain=custom_domain,
            enable_ipv6=enable_ipv6,
            file_systems=file_systems,
            install_aws_cli=install_aws_cli,
            instance_type=instance_type,
            key_pair=key_pair,
            role=role,
            secrets=secrets,
            security_group=security_group,
            ubuntu_version=ubuntu_version,
            volume_size=volume_size,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="allowSshAccessFrom")
    def allow_ssh_access_from(self, *peer: "_aws_cdk_aws_ec2_ceddda9d.IPeer") -> None:
        '''Allow SSH access from the given peer or peers.

        :param peer: - The peer or peers to allow.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb60136d65960d559855ffa080ecfafe6e3466eb878725d71594d5bf7eec125c)
            check_type(argname="argument peer", value=peer, expected_type=typing.Tuple[type_hints["peer"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(None, jsii.invoke(self, "allowSshAccessFrom", [*peer]))

    @builtins.property
    @jsii.member(jsii_name="autoScalingGroup")
    def auto_scaling_group(
        self,
    ) -> "_aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup":
        '''The auto-scaling group for this bastion.'''
        return typing.cast("_aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup", jsii.get(self, "autoScalingGroup"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> "_aws_cdk_aws_ec2_ceddda9d.Connections":
        '''The network connections associated with this resource.'''
        return typing.cast("_aws_cdk_aws_ec2_ceddda9d.Connections", jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="firewall")
    def firewall(self) -> "_IFirewallRules_115dd143":
        '''The instance firewall rules.'''
        return typing.cast("_IFirewallRules_115dd143", jsii.get(self, "firewall"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> "_aws_cdk_aws_iam_ceddda9d.IPrincipal":
        '''The principal to grant permissions to.'''
        return typing.cast("_aws_cdk_aws_iam_ceddda9d.IPrincipal", jsii.get(self, "grantPrincipal"))


@jsii.data_type(
    jsii_type="shady-island.servers.UbuntuLinuxBastionProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "apt_packages": "aptPackages",
        "apt_repositories": "aptRepositories",
        "architecture": "architecture",
        "custom_domain": "customDomain",
        "enable_ipv6": "enableIpv6",
        "file_systems": "fileSystems",
        "install_aws_cli": "installAwsCli",
        "instance_type": "instanceType",
        "key_pair": "keyPair",
        "role": "role",
        "secrets": "secrets",
        "security_group": "securityGroup",
        "ubuntu_version": "ubuntuVersion",
        "volume_size": "volumeSize",
    },
)
class UbuntuLinuxBastionProps:
    def __init__(
        self,
        *,
        vpc: "_aws_cdk_aws_ec2_ceddda9d.IVpc",
        apt_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        apt_repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
        architecture: typing.Optional["_aws_cdk_aws_ec2_ceddda9d.InstanceArchitecture"] = None,
        custom_domain: typing.Optional[typing.Union["CustomDomainOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        file_systems: typing.Optional[typing.Sequence[typing.Union["ElasticFileSystemMount", typing.Dict[builtins.str, typing.Any]]]] = None,
        install_aws_cli: typing.Optional[builtins.bool] = None,
        instance_type: typing.Optional["_aws_cdk_aws_ec2_ceddda9d.InstanceType"] = None,
        key_pair: typing.Optional["_aws_cdk_aws_ec2_ceddda9d.IKeyPair"] = None,
        role: typing.Optional["_aws_cdk_aws_iam_ceddda9d.IRole"] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, "_aws_cdk_aws_secretsmanager_ceddda9d.ISecret"]] = None,
        security_group: typing.Optional["_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup"] = None,
        ubuntu_version: typing.Optional[builtins.str] = None,
        volume_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Properties for the UbuntuLinuxBastion constructor.

        :param vpc: The VPC where the bastion will reside.
        :param apt_packages: An array of APT package names to install. If you supply any Elastic Filesystems to mount, this construct will also install the "nfs-common" package.
        :param apt_repositories: The names of repositories to enable using apt-add-repository. e.g. ppa:redislabs/redis
        :param architecture: The CPU architecture for the bastion. Default: - InstanceArchitecture.ARM_64
        :param custom_domain: The options for creating DNS records upon launch.
        :param enable_ipv6: Whether to enable IPv6. Default: - false
        :param file_systems: The Elastic Filesystems to mount.
        :param install_aws_cli: Whether to install the AWS CLI Snap package. Default: - true
        :param instance_type: The instance type for the bastion. Default: - t3.micro for X86_64, t4g.micro for ARM_64
        :param key_pair: The key pair to use for this instance. Default: - A new key pair is generated and stored in SSM Parameter Store
        :param role: The instance role (the trust policy must permit ec2.amazonaws.com). Default: - A new role is created.
        :param secrets: The secrets containing database credentials. The key of the object corresponds to the filename in ``/run/secrets``.
        :param security_group: The security group to attach to the bastion instance. Default: - A new security group is created
        :param ubuntu_version: The version of Ubuntu to use. Default: - 24.04
        :param volume_size: The size in gibibytes (GiB) of the primary disk volume. Default: - 10
        '''
        if isinstance(custom_domain, dict):
            custom_domain = CustomDomainOptions(**custom_domain)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__570592b2fbcf2c377a0bfdd5ce86ce59dcab8e8875fc3f36aaf9c289300b4313)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument apt_packages", value=apt_packages, expected_type=type_hints["apt_packages"])
            check_type(argname="argument apt_repositories", value=apt_repositories, expected_type=type_hints["apt_repositories"])
            check_type(argname="argument architecture", value=architecture, expected_type=type_hints["architecture"])
            check_type(argname="argument custom_domain", value=custom_domain, expected_type=type_hints["custom_domain"])
            check_type(argname="argument enable_ipv6", value=enable_ipv6, expected_type=type_hints["enable_ipv6"])
            check_type(argname="argument file_systems", value=file_systems, expected_type=type_hints["file_systems"])
            check_type(argname="argument install_aws_cli", value=install_aws_cli, expected_type=type_hints["install_aws_cli"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument key_pair", value=key_pair, expected_type=type_hints["key_pair"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument secrets", value=secrets, expected_type=type_hints["secrets"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument ubuntu_version", value=ubuntu_version, expected_type=type_hints["ubuntu_version"])
            check_type(argname="argument volume_size", value=volume_size, expected_type=type_hints["volume_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if apt_packages is not None:
            self._values["apt_packages"] = apt_packages
        if apt_repositories is not None:
            self._values["apt_repositories"] = apt_repositories
        if architecture is not None:
            self._values["architecture"] = architecture
        if custom_domain is not None:
            self._values["custom_domain"] = custom_domain
        if enable_ipv6 is not None:
            self._values["enable_ipv6"] = enable_ipv6
        if file_systems is not None:
            self._values["file_systems"] = file_systems
        if install_aws_cli is not None:
            self._values["install_aws_cli"] = install_aws_cli
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if key_pair is not None:
            self._values["key_pair"] = key_pair
        if role is not None:
            self._values["role"] = role
        if secrets is not None:
            self._values["secrets"] = secrets
        if security_group is not None:
            self._values["security_group"] = security_group
        if ubuntu_version is not None:
            self._values["ubuntu_version"] = ubuntu_version
        if volume_size is not None:
            self._values["volume_size"] = volume_size

    @builtins.property
    def vpc(self) -> "_aws_cdk_aws_ec2_ceddda9d.IVpc":
        '''The VPC where the bastion will reside.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast("_aws_cdk_aws_ec2_ceddda9d.IVpc", result)

    @builtins.property
    def apt_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An array of APT package names to install.

        If you supply any Elastic Filesystems to mount, this construct will also
        install the "nfs-common" package.
        '''
        result = self._values.get("apt_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def apt_repositories(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The names of repositories to enable using apt-add-repository.

        e.g. ppa:redislabs/redis
        '''
        result = self._values.get("apt_repositories")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def architecture(
        self,
    ) -> typing.Optional["_aws_cdk_aws_ec2_ceddda9d.InstanceArchitecture"]:
        '''The CPU architecture for the bastion.

        :default: - InstanceArchitecture.ARM_64
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional["_aws_cdk_aws_ec2_ceddda9d.InstanceArchitecture"], result)

    @builtins.property
    def custom_domain(self) -> typing.Optional["CustomDomainOptions"]:
        '''The options for creating DNS records upon launch.'''
        result = self._values.get("custom_domain")
        return typing.cast(typing.Optional["CustomDomainOptions"], result)

    @builtins.property
    def enable_ipv6(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable IPv6.

        :default: - false
        '''
        result = self._values.get("enable_ipv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def file_systems(self) -> typing.Optional[typing.List["ElasticFileSystemMount"]]:
        '''The Elastic Filesystems to mount.'''
        result = self._values.get("file_systems")
        return typing.cast(typing.Optional[typing.List["ElasticFileSystemMount"]], result)

    @builtins.property
    def install_aws_cli(self) -> typing.Optional[builtins.bool]:
        '''Whether to install the AWS CLI Snap package.

        :default: - true
        '''
        result = self._values.get("install_aws_cli")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_type(
        self,
    ) -> typing.Optional["_aws_cdk_aws_ec2_ceddda9d.InstanceType"]:
        '''The instance type for the bastion.

        :default: - t3.micro for X86_64, t4g.micro for ARM_64
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional["_aws_cdk_aws_ec2_ceddda9d.InstanceType"], result)

    @builtins.property
    def key_pair(self) -> typing.Optional["_aws_cdk_aws_ec2_ceddda9d.IKeyPair"]:
        '''The key pair to use for this instance.

        :default: - A new key pair is generated and stored in SSM Parameter Store
        '''
        result = self._values.get("key_pair")
        return typing.cast(typing.Optional["_aws_cdk_aws_ec2_ceddda9d.IKeyPair"], result)

    @builtins.property
    def role(self) -> typing.Optional["_aws_cdk_aws_iam_ceddda9d.IRole"]:
        '''The instance role (the trust policy must permit ec2.amazonaws.com).

        :default: - A new role is created.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional["_aws_cdk_aws_iam_ceddda9d.IRole"], result)

    @builtins.property
    def secrets(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "_aws_cdk_aws_secretsmanager_ceddda9d.ISecret"]]:
        '''The secrets containing database credentials.

        The key of the object corresponds to the filename in ``/run/secrets``.
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "_aws_cdk_aws_secretsmanager_ceddda9d.ISecret"]], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional["_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup"]:
        '''The security group to attach to the bastion instance.

        :default: - A new security group is created
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional["_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup"], result)

    @builtins.property
    def ubuntu_version(self) -> typing.Optional[builtins.str]:
        '''The version of Ubuntu to use.

        :default: - 24.04
        '''
        result = self._values.get("ubuntu_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''The size in gibibytes (GiB) of the primary disk volume.

        :default: - 10
        '''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UbuntuLinuxBastionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CustomDomainOptions",
    "ElasticFileSystemMount",
    "UbuntuLinuxBastion",
    "UbuntuLinuxBastionProps",
]

publication.publish()

def _typecheckingstub__2db1d2891e6a764bd61683fbdec14a104accc85746f29662cd5bc9a4f83cfb6d(
    *,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    subdomain: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ce921d23c04ba7e05abe297fb0d1bf15a4742b2a29ae4cafa3506ed4e70afdc(
    *,
    directory: builtins.str,
    file_system: _aws_cdk_aws_efs_ceddda9d.IFileSystem,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__feed70f44a62d1a377cfb6ba61d31a6adf4b75788815dea56858878124d3846a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    apt_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
    apt_repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
    architecture: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceArchitecture] = None,
    custom_domain: typing.Optional[typing.Union[CustomDomainOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_ipv6: typing.Optional[builtins.bool] = None,
    file_systems: typing.Optional[typing.Sequence[typing.Union[ElasticFileSystemMount, typing.Dict[builtins.str, typing.Any]]]] = None,
    install_aws_cli: typing.Optional[builtins.bool] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    secrets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_secretsmanager_ceddda9d.ISecret]] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    ubuntu_version: typing.Optional[builtins.str] = None,
    volume_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb60136d65960d559855ffa080ecfafe6e3466eb878725d71594d5bf7eec125c(
    *peer: _aws_cdk_aws_ec2_ceddda9d.IPeer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__570592b2fbcf2c377a0bfdd5ce86ce59dcab8e8875fc3f36aaf9c289300b4313(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    apt_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
    apt_repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
    architecture: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceArchitecture] = None,
    custom_domain: typing.Optional[typing.Union[CustomDomainOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_ipv6: typing.Optional[builtins.bool] = None,
    file_systems: typing.Optional[typing.Sequence[typing.Union[ElasticFileSystemMount, typing.Dict[builtins.str, typing.Any]]]] = None,
    install_aws_cli: typing.Optional[builtins.bool] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    secrets: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_secretsmanager_ceddda9d.ISecret]] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    ubuntu_version: typing.Optional[builtins.str] = None,
    volume_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
