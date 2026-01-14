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

from ..._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.interfaces.aws_codebuild as _aws_cdk_interfaces_aws_codebuild_ceddda9d


class ProjectEvents(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents",
):
    '''(experimental) EventBridge event patterns for Project.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
        from aws_cdk.interfaces import aws_codebuild as interfaces_codebuild
        
        # project_ref: interfaces_codebuild.IProjectRef
        
        project_events = codebuild_events.ProjectEvents.from_project(project_ref)
    '''

    @jsii.member(jsii_name="fromProject")
    @builtins.classmethod
    def from_project(
        cls,
        project_ref: "_aws_cdk_interfaces_aws_codebuild_ceddda9d.IProjectRef",
    ) -> "ProjectEvents":
        '''(experimental) Create ProjectEvents from a Project reference.

        :param project_ref: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db4d32fb7791ee1d99407b942179cc160a485c3efe1a1bf3d6c836e1b2638ff0)
            check_type(argname="argument project_ref", value=project_ref, expected_type=type_hints["project_ref"])
        return typing.cast("ProjectEvents", jsii.sinvoke(cls, "fromProject", [project_ref]))

    @jsii.member(jsii_name="codeBuildBuildPhaseChangePattern")
    def code_build_build_phase_change_pattern(
        self,
        *,
        additional_information: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformation", typing.Dict[builtins.str, typing.Any]]] = None,
        build_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        completed_phase: typing.Optional[typing.Sequence[builtins.str]] = None,
        completed_phase_context: typing.Optional[typing.Sequence[builtins.str]] = None,
        completed_phase_duration_seconds: typing.Optional[typing.Sequence[builtins.str]] = None,
        completed_phase_end: typing.Optional[typing.Sequence[builtins.str]] = None,
        completed_phase_start: typing.Optional[typing.Sequence[builtins.str]] = None,
        completed_phase_status: typing.Optional[typing.Sequence[builtins.str]] = None,
        event_metadata: typing.Optional[typing.Union["_aws_cdk_ceddda9d.AWSEventMetadataProps", typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "_aws_cdk_aws_events_ceddda9d.EventPattern":
        '''(experimental) EventBridge event pattern for Project CodeBuild Build Phase Change.

        :param additional_information: (experimental) additional-information property. Specify an array of string values to match this event if the actual value of additional-information is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param build_id: (experimental) build-id property. Specify an array of string values to match this event if the actual value of build-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param completed_phase: (experimental) completed-phase property. Specify an array of string values to match this event if the actual value of completed-phase is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param completed_phase_context: (experimental) completed-phase-context property. Specify an array of string values to match this event if the actual value of completed-phase-context is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param completed_phase_duration_seconds: (experimental) completed-phase-duration-seconds property. Specify an array of string values to match this event if the actual value of completed-phase-duration-seconds is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param completed_phase_end: (experimental) completed-phase-end property. Specify an array of string values to match this event if the actual value of completed-phase-end is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param completed_phase_start: (experimental) completed-phase-start property. Specify an array of string values to match this event if the actual value of completed-phase-start is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param completed_phase_status: (experimental) completed-phase-status property. Specify an array of string values to match this event if the actual value of completed-phase-status is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param event_metadata: (experimental) EventBridge event metadata. Default: - -
        :param project_name: (experimental) project-name property. Specify an array of string values to match this event if the actual value of project-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Filter with the Project reference
        :param version: (experimental) version property. Specify an array of string values to match this event if the actual value of version is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

        :stability: experimental
        '''
        options = ProjectEvents.CodeBuildBuildPhaseChange.CodeBuildBuildPhaseChangeProps(
            additional_information=additional_information,
            build_id=build_id,
            completed_phase=completed_phase,
            completed_phase_context=completed_phase_context,
            completed_phase_duration_seconds=completed_phase_duration_seconds,
            completed_phase_end=completed_phase_end,
            completed_phase_start=completed_phase_start,
            completed_phase_status=completed_phase_status,
            event_metadata=event_metadata,
            project_name=project_name,
            version=version,
        )

        return typing.cast("_aws_cdk_aws_events_ceddda9d.EventPattern", jsii.invoke(self, "codeBuildBuildPhaseChangePattern", [options]))

    @jsii.member(jsii_name="codeBuildBuildStateChangePattern")
    def code_build_build_state_change_pattern(
        self,
        *,
        additional_information: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildStateChange.AdditionalInformation", typing.Dict[builtins.str, typing.Any]]] = None,
        build_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        build_status: typing.Optional[typing.Sequence[builtins.str]] = None,
        current_phase: typing.Optional[typing.Sequence[builtins.str]] = None,
        current_phase_context: typing.Optional[typing.Sequence[builtins.str]] = None,
        event_metadata: typing.Optional[typing.Union["_aws_cdk_ceddda9d.AWSEventMetadataProps", typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "_aws_cdk_aws_events_ceddda9d.EventPattern":
        '''(experimental) EventBridge event pattern for Project CodeBuild Build State Change.

        :param additional_information: (experimental) additional-information property. Specify an array of string values to match this event if the actual value of additional-information is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param build_id: (experimental) build-id property. Specify an array of string values to match this event if the actual value of build-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param build_status: (experimental) build-status property. Specify an array of string values to match this event if the actual value of build-status is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param current_phase: (experimental) current-phase property. Specify an array of string values to match this event if the actual value of current-phase is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param current_phase_context: (experimental) current-phase-context property. Specify an array of string values to match this event if the actual value of current-phase-context is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
        :param event_metadata: (experimental) EventBridge event metadata. Default: - -
        :param project_name: (experimental) project-name property. Specify an array of string values to match this event if the actual value of project-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Filter with the Project reference
        :param version: (experimental) version property. Specify an array of string values to match this event if the actual value of version is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

        :stability: experimental
        '''
        options = ProjectEvents.CodeBuildBuildStateChange.CodeBuildBuildStateChangeProps(
            additional_information=additional_information,
            build_id=build_id,
            build_status=build_status,
            current_phase=current_phase,
            current_phase_context=current_phase_context,
            event_metadata=event_metadata,
            project_name=project_name,
            version=version,
        )

        return typing.cast("_aws_cdk_aws_events_ceddda9d.EventPattern", jsii.invoke(self, "codeBuildBuildStateChangePattern", [options]))

    class CodeBuildBuildPhaseChange(
        metaclass=jsii.JSIIMeta,
        jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange",
    ):
        '''(experimental) aws.codebuild@CodeBuildBuildPhaseChange event types for Project.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
            
            code_build_build_phase_change = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange()
        '''

        def __init__(self) -> None:
            '''
            :stability: experimental
            '''
            jsii.create(self.__class__, self, [])

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformation",
            jsii_struct_bases=[],
            name_mapping={
                "artifact": "artifact",
                "build_complete": "buildComplete",
                "build_start_time": "buildStartTime",
                "cache": "cache",
                "environment": "environment",
                "initiator": "initiator",
                "logs": "logs",
                "network_interface": "networkInterface",
                "phases": "phases",
                "queued_timeout_in_minutes": "queuedTimeoutInMinutes",
                "source": "source",
                "source_version": "sourceVersion",
                "timeout_in_minutes": "timeoutInMinutes",
                "vpc_config": "vpcConfig",
            },
        )
        class AdditionalInformation:
            def __init__(
                self,
                *,
                artifact: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.Artifact", typing.Dict[builtins.str, typing.Any]]] = None,
                build_complete: typing.Optional[typing.Sequence[builtins.str]] = None,
                build_start_time: typing.Optional[typing.Sequence[builtins.str]] = None,
                cache: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.Cache", typing.Dict[builtins.str, typing.Any]]] = None,
                environment: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.Environment", typing.Dict[builtins.str, typing.Any]]] = None,
                initiator: typing.Optional[typing.Sequence[builtins.str]] = None,
                logs: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.Logs", typing.Dict[builtins.str, typing.Any]]] = None,
                network_interface: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.NetworkInterface", typing.Dict[builtins.str, typing.Any]]] = None,
                phases: typing.Optional[typing.Sequence[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformationItem", typing.Dict[builtins.str, typing.Any]]]] = None,
                queued_timeout_in_minutes: typing.Optional[typing.Sequence[builtins.str]] = None,
                source: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.Source", typing.Dict[builtins.str, typing.Any]]] = None,
                source_version: typing.Optional[typing.Sequence[builtins.str]] = None,
                timeout_in_minutes: typing.Optional[typing.Sequence[builtins.str]] = None,
                vpc_config: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.VpcConfig", typing.Dict[builtins.str, typing.Any]]] = None,
            ) -> None:
                '''(experimental) Type definition for Additional-information.

                :param artifact: (experimental) artifact property. Specify an array of string values to match this event if the actual value of artifact is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param build_complete: (experimental) build-complete property. Specify an array of string values to match this event if the actual value of build-complete is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param build_start_time: (experimental) build-start-time property. Specify an array of string values to match this event if the actual value of build-start-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param cache: (experimental) cache property. Specify an array of string values to match this event if the actual value of cache is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param environment: (experimental) environment property. Specify an array of string values to match this event if the actual value of environment is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param initiator: (experimental) initiator property. Specify an array of string values to match this event if the actual value of initiator is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param logs: (experimental) logs property. Specify an array of string values to match this event if the actual value of logs is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param network_interface: (experimental) network-interface property. Specify an array of string values to match this event if the actual value of network-interface is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param phases: (experimental) phases property. Specify an array of string values to match this event if the actual value of phases is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param queued_timeout_in_minutes: (experimental) queued-timeout-in-minutes property. Specify an array of string values to match this event if the actual value of queued-timeout-in-minutes is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param source: (experimental) source property. Specify an array of string values to match this event if the actual value of source is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param source_version: (experimental) source-version property. Specify an array of string values to match this event if the actual value of source-version is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param timeout_in_minutes: (experimental) timeout-in-minutes property. Specify an array of string values to match this event if the actual value of timeout-in-minutes is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param vpc_config: (experimental) vpc-config property. Specify an array of string values to match this event if the actual value of vpc-config is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    additional_information = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformation(
                        artifact=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Artifact(
                            location=["location"],
                            md5_sum=["md5Sum"],
                            sha256_sum=["sha256Sum"]
                        ),
                        build_complete=["buildComplete"],
                        build_start_time=["buildStartTime"],
                        cache=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Cache(
                            location=["location"],
                            type=["type"]
                        ),
                        environment=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Environment(
                            compute_type=["computeType"],
                            environment_variables=[codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.EnvironmentItem(
                                name=["name"],
                                type=["type"],
                                value=["value"]
                            )],
                            image=["image"],
                            image_pull_credentials_type=["imagePullCredentialsType"],
                            privileged_mode=["privilegedMode"],
                            type=["type"]
                        ),
                        initiator=["initiator"],
                        logs=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Logs(
                            deep_link=["deepLink"],
                            group_name=["groupName"],
                            stream_name=["streamName"]
                        ),
                        network_interface=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.NetworkInterface(
                            eni_id=["eniId"],
                            subnet_id=["subnetId"]
                        ),
                        phases=[codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformationItem(
                            duration_in_seconds=["durationInSeconds"],
                            end_time=["endTime"],
                            phase_context=["phaseContext"],
                            phase_status=["phaseStatus"],
                            phase_type=["phaseType"],
                            start_time=["startTime"]
                        )],
                        queued_timeout_in_minutes=["queuedTimeoutInMinutes"],
                        source=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Source(
                            auth=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Auth(
                                type=["type"]
                            ),
                            buildspec=["buildspec"],
                            location=["location"],
                            type=["type"]
                        ),
                        source_version=["sourceVersion"],
                        timeout_in_minutes=["timeoutInMinutes"],
                        vpc_config=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.VpcConfig(
                            security_group_ids=["securityGroupIds"],
                            subnets=[codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.VpcConfigItem(
                                build_fleet_az=["buildFleetAz"],
                                customer_az=["customerAz"],
                                subnet_id=["subnetId"]
                            )],
                            vpc_id=["vpcId"]
                        )
                    )
                '''
                if isinstance(artifact, dict):
                    artifact = ProjectEvents.CodeBuildBuildPhaseChange.Artifact(**artifact)
                if isinstance(cache, dict):
                    cache = ProjectEvents.CodeBuildBuildPhaseChange.Cache(**cache)
                if isinstance(environment, dict):
                    environment = ProjectEvents.CodeBuildBuildPhaseChange.Environment(**environment)
                if isinstance(logs, dict):
                    logs = ProjectEvents.CodeBuildBuildPhaseChange.Logs(**logs)
                if isinstance(network_interface, dict):
                    network_interface = ProjectEvents.CodeBuildBuildPhaseChange.NetworkInterface(**network_interface)
                if isinstance(source, dict):
                    source = ProjectEvents.CodeBuildBuildPhaseChange.Source(**source)
                if isinstance(vpc_config, dict):
                    vpc_config = ProjectEvents.CodeBuildBuildPhaseChange.VpcConfig(**vpc_config)
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__6ecb5a299d9616eeef3b9eaa22dd2371a32362c2e6e50306f5e97f7fcdb88b4a)
                    check_type(argname="argument artifact", value=artifact, expected_type=type_hints["artifact"])
                    check_type(argname="argument build_complete", value=build_complete, expected_type=type_hints["build_complete"])
                    check_type(argname="argument build_start_time", value=build_start_time, expected_type=type_hints["build_start_time"])
                    check_type(argname="argument cache", value=cache, expected_type=type_hints["cache"])
                    check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
                    check_type(argname="argument initiator", value=initiator, expected_type=type_hints["initiator"])
                    check_type(argname="argument logs", value=logs, expected_type=type_hints["logs"])
                    check_type(argname="argument network_interface", value=network_interface, expected_type=type_hints["network_interface"])
                    check_type(argname="argument phases", value=phases, expected_type=type_hints["phases"])
                    check_type(argname="argument queued_timeout_in_minutes", value=queued_timeout_in_minutes, expected_type=type_hints["queued_timeout_in_minutes"])
                    check_type(argname="argument source", value=source, expected_type=type_hints["source"])
                    check_type(argname="argument source_version", value=source_version, expected_type=type_hints["source_version"])
                    check_type(argname="argument timeout_in_minutes", value=timeout_in_minutes, expected_type=type_hints["timeout_in_minutes"])
                    check_type(argname="argument vpc_config", value=vpc_config, expected_type=type_hints["vpc_config"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if artifact is not None:
                    self._values["artifact"] = artifact
                if build_complete is not None:
                    self._values["build_complete"] = build_complete
                if build_start_time is not None:
                    self._values["build_start_time"] = build_start_time
                if cache is not None:
                    self._values["cache"] = cache
                if environment is not None:
                    self._values["environment"] = environment
                if initiator is not None:
                    self._values["initiator"] = initiator
                if logs is not None:
                    self._values["logs"] = logs
                if network_interface is not None:
                    self._values["network_interface"] = network_interface
                if phases is not None:
                    self._values["phases"] = phases
                if queued_timeout_in_minutes is not None:
                    self._values["queued_timeout_in_minutes"] = queued_timeout_in_minutes
                if source is not None:
                    self._values["source"] = source
                if source_version is not None:
                    self._values["source_version"] = source_version
                if timeout_in_minutes is not None:
                    self._values["timeout_in_minutes"] = timeout_in_minutes
                if vpc_config is not None:
                    self._values["vpc_config"] = vpc_config

            @builtins.property
            def artifact(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Artifact"]:
                '''(experimental) artifact property.

                Specify an array of string values to match this event if the actual value of artifact is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("artifact")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Artifact"], result)

            @builtins.property
            def build_complete(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) build-complete property.

                Specify an array of string values to match this event if the actual value of build-complete is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("build_complete")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def build_start_time(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) build-start-time property.

                Specify an array of string values to match this event if the actual value of build-start-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("build_start_time")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def cache(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Cache"]:
                '''(experimental) cache property.

                Specify an array of string values to match this event if the actual value of cache is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("cache")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Cache"], result)

            @builtins.property
            def environment(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Environment"]:
                '''(experimental) environment property.

                Specify an array of string values to match this event if the actual value of environment is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("environment")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Environment"], result)

            @builtins.property
            def initiator(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) initiator property.

                Specify an array of string values to match this event if the actual value of initiator is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("initiator")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def logs(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Logs"]:
                '''(experimental) logs property.

                Specify an array of string values to match this event if the actual value of logs is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("logs")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Logs"], result)

            @builtins.property
            def network_interface(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.NetworkInterface"]:
                '''(experimental) network-interface property.

                Specify an array of string values to match this event if the actual value of network-interface is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("network_interface")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.NetworkInterface"], result)

            @builtins.property
            def phases(
                self,
            ) -> typing.Optional[typing.List["ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformationItem"]]:
                '''(experimental) phases property.

                Specify an array of string values to match this event if the actual value of phases is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("phases")
                return typing.cast(typing.Optional[typing.List["ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformationItem"]], result)

            @builtins.property
            def queued_timeout_in_minutes(
                self,
            ) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) queued-timeout-in-minutes property.

                Specify an array of string values to match this event if the actual value of queued-timeout-in-minutes is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("queued_timeout_in_minutes")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def source(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Source"]:
                '''(experimental) source property.

                Specify an array of string values to match this event if the actual value of source is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("source")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Source"], result)

            @builtins.property
            def source_version(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) source-version property.

                Specify an array of string values to match this event if the actual value of source-version is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("source_version")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def timeout_in_minutes(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) timeout-in-minutes property.

                Specify an array of string values to match this event if the actual value of timeout-in-minutes is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("timeout_in_minutes")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def vpc_config(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.VpcConfig"]:
                '''(experimental) vpc-config property.

                Specify an array of string values to match this event if the actual value of vpc-config is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("vpc_config")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.VpcConfig"], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "AdditionalInformation(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformationItem",
            jsii_struct_bases=[],
            name_mapping={
                "duration_in_seconds": "durationInSeconds",
                "end_time": "endTime",
                "phase_context": "phaseContext",
                "phase_status": "phaseStatus",
                "phase_type": "phaseType",
                "start_time": "startTime",
            },
        )
        class AdditionalInformationItem:
            def __init__(
                self,
                *,
                duration_in_seconds: typing.Optional[typing.Sequence[builtins.str]] = None,
                end_time: typing.Optional[typing.Sequence[builtins.str]] = None,
                phase_context: typing.Optional[typing.Sequence[builtins.str]] = None,
                phase_status: typing.Optional[typing.Sequence[builtins.str]] = None,
                phase_type: typing.Optional[typing.Sequence[builtins.str]] = None,
                start_time: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Additional-informationItem.

                :param duration_in_seconds: (experimental) duration-in-seconds property. Specify an array of string values to match this event if the actual value of duration-in-seconds is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param end_time: (experimental) end-time property. Specify an array of string values to match this event if the actual value of end-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param phase_context: (experimental) phase-context property. Specify an array of string values to match this event if the actual value of phase-context is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param phase_status: (experimental) phase-status property. Specify an array of string values to match this event if the actual value of phase-status is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param phase_type: (experimental) phase-type property. Specify an array of string values to match this event if the actual value of phase-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param start_time: (experimental) start-time property. Specify an array of string values to match this event if the actual value of start-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    additional_information_item = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformationItem(
                        duration_in_seconds=["durationInSeconds"],
                        end_time=["endTime"],
                        phase_context=["phaseContext"],
                        phase_status=["phaseStatus"],
                        phase_type=["phaseType"],
                        start_time=["startTime"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__aad1456ad482bb9be39804b8132265a949e6d7e70e7ee21f5300ccc7b226b12d)
                    check_type(argname="argument duration_in_seconds", value=duration_in_seconds, expected_type=type_hints["duration_in_seconds"])
                    check_type(argname="argument end_time", value=end_time, expected_type=type_hints["end_time"])
                    check_type(argname="argument phase_context", value=phase_context, expected_type=type_hints["phase_context"])
                    check_type(argname="argument phase_status", value=phase_status, expected_type=type_hints["phase_status"])
                    check_type(argname="argument phase_type", value=phase_type, expected_type=type_hints["phase_type"])
                    check_type(argname="argument start_time", value=start_time, expected_type=type_hints["start_time"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if duration_in_seconds is not None:
                    self._values["duration_in_seconds"] = duration_in_seconds
                if end_time is not None:
                    self._values["end_time"] = end_time
                if phase_context is not None:
                    self._values["phase_context"] = phase_context
                if phase_status is not None:
                    self._values["phase_status"] = phase_status
                if phase_type is not None:
                    self._values["phase_type"] = phase_type
                if start_time is not None:
                    self._values["start_time"] = start_time

            @builtins.property
            def duration_in_seconds(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) duration-in-seconds property.

                Specify an array of string values to match this event if the actual value of duration-in-seconds is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("duration_in_seconds")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def end_time(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) end-time property.

                Specify an array of string values to match this event if the actual value of end-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("end_time")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def phase_context(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) phase-context property.

                Specify an array of string values to match this event if the actual value of phase-context is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("phase_context")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def phase_status(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) phase-status property.

                Specify an array of string values to match this event if the actual value of phase-status is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("phase_status")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def phase_type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) phase-type property.

                Specify an array of string values to match this event if the actual value of phase-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("phase_type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def start_time(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) start-time property.

                Specify an array of string values to match this event if the actual value of start-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("start_time")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "AdditionalInformationItem(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.Artifact",
            jsii_struct_bases=[],
            name_mapping={
                "location": "location",
                "md5_sum": "md5Sum",
                "sha256_sum": "sha256Sum",
            },
        )
        class Artifact:
            def __init__(
                self,
                *,
                location: typing.Optional[typing.Sequence[builtins.str]] = None,
                md5_sum: typing.Optional[typing.Sequence[builtins.str]] = None,
                sha256_sum: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Artifact.

                :param location: (experimental) location property. Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param md5_sum: (experimental) md5sum property. Specify an array of string values to match this event if the actual value of md5sum is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param sha256_sum: (experimental) sha256sum property. Specify an array of string values to match this event if the actual value of sha256sum is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    artifact = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Artifact(
                        location=["location"],
                        md5_sum=["md5Sum"],
                        sha256_sum=["sha256Sum"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__5a75e9dc66baf399a9bdaddc2af06109add940240a5399d6c6d62b1f67896dc6)
                    check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                    check_type(argname="argument md5_sum", value=md5_sum, expected_type=type_hints["md5_sum"])
                    check_type(argname="argument sha256_sum", value=sha256_sum, expected_type=type_hints["sha256_sum"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if location is not None:
                    self._values["location"] = location
                if md5_sum is not None:
                    self._values["md5_sum"] = md5_sum
                if sha256_sum is not None:
                    self._values["sha256_sum"] = sha256_sum

            @builtins.property
            def location(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) location property.

                Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("location")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def md5_sum(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) md5sum property.

                Specify an array of string values to match this event if the actual value of md5sum is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("md5_sum")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def sha256_sum(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) sha256sum property.

                Specify an array of string values to match this event if the actual value of sha256sum is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("sha256_sum")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Artifact(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.Auth",
            jsii_struct_bases=[],
            name_mapping={"type": "type"},
        )
        class Auth:
            def __init__(
                self,
                *,
                type: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Auth.

                :param type: (experimental) type property. Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    auth = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Auth(
                        type=["type"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__e9a5872c8a44faf787b2548fa103e5c095bdd09ae0ef8eec3afd8177a1c2814b)
                    check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if type is not None:
                    self._values["type"] = type

            @builtins.property
            def type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) type property.

                Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Auth(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.Cache",
            jsii_struct_bases=[],
            name_mapping={"location": "location", "type": "type"},
        )
        class Cache:
            def __init__(
                self,
                *,
                location: typing.Optional[typing.Sequence[builtins.str]] = None,
                type: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Cache.

                :param location: (experimental) location property. Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param type: (experimental) type property. Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    cache = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Cache(
                        location=["location"],
                        type=["type"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__edd011b0f74f6d1c9f068235c602a94953a0cd0b7737d75ac9cfd4565b239746)
                    check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                    check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if location is not None:
                    self._values["location"] = location
                if type is not None:
                    self._values["type"] = type

            @builtins.property
            def location(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) location property.

                Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("location")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) type property.

                Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Cache(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.CodeBuildBuildPhaseChangeProps",
            jsii_struct_bases=[],
            name_mapping={
                "additional_information": "additionalInformation",
                "build_id": "buildId",
                "completed_phase": "completedPhase",
                "completed_phase_context": "completedPhaseContext",
                "completed_phase_duration_seconds": "completedPhaseDurationSeconds",
                "completed_phase_end": "completedPhaseEnd",
                "completed_phase_start": "completedPhaseStart",
                "completed_phase_status": "completedPhaseStatus",
                "event_metadata": "eventMetadata",
                "project_name": "projectName",
                "version": "version",
            },
        )
        class CodeBuildBuildPhaseChangeProps:
            def __init__(
                self,
                *,
                additional_information: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformation", typing.Dict[builtins.str, typing.Any]]] = None,
                build_id: typing.Optional[typing.Sequence[builtins.str]] = None,
                completed_phase: typing.Optional[typing.Sequence[builtins.str]] = None,
                completed_phase_context: typing.Optional[typing.Sequence[builtins.str]] = None,
                completed_phase_duration_seconds: typing.Optional[typing.Sequence[builtins.str]] = None,
                completed_phase_end: typing.Optional[typing.Sequence[builtins.str]] = None,
                completed_phase_start: typing.Optional[typing.Sequence[builtins.str]] = None,
                completed_phase_status: typing.Optional[typing.Sequence[builtins.str]] = None,
                event_metadata: typing.Optional[typing.Union["_aws_cdk_ceddda9d.AWSEventMetadataProps", typing.Dict[builtins.str, typing.Any]]] = None,
                project_name: typing.Optional[typing.Sequence[builtins.str]] = None,
                version: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Props type for Project aws.codebuild@CodeBuildBuildPhaseChange event.

                :param additional_information: (experimental) additional-information property. Specify an array of string values to match this event if the actual value of additional-information is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param build_id: (experimental) build-id property. Specify an array of string values to match this event if the actual value of build-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param completed_phase: (experimental) completed-phase property. Specify an array of string values to match this event if the actual value of completed-phase is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param completed_phase_context: (experimental) completed-phase-context property. Specify an array of string values to match this event if the actual value of completed-phase-context is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param completed_phase_duration_seconds: (experimental) completed-phase-duration-seconds property. Specify an array of string values to match this event if the actual value of completed-phase-duration-seconds is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param completed_phase_end: (experimental) completed-phase-end property. Specify an array of string values to match this event if the actual value of completed-phase-end is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param completed_phase_start: (experimental) completed-phase-start property. Specify an array of string values to match this event if the actual value of completed-phase-start is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param completed_phase_status: (experimental) completed-phase-status property. Specify an array of string values to match this event if the actual value of completed-phase-status is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param event_metadata: (experimental) EventBridge event metadata. Default: - -
                :param project_name: (experimental) project-name property. Specify an array of string values to match this event if the actual value of project-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Filter with the Project reference
                :param version: (experimental) version property. Specify an array of string values to match this event if the actual value of version is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    from aws_cdk import AWSEventMetadataProps
                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    code_build_build_phase_change_props = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.CodeBuildBuildPhaseChangeProps(
                        additional_information=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformation(
                            artifact=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Artifact(
                                location=["location"],
                                md5_sum=["md5Sum"],
                                sha256_sum=["sha256Sum"]
                            ),
                            build_complete=["buildComplete"],
                            build_start_time=["buildStartTime"],
                            cache=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Cache(
                                location=["location"],
                                type=["type"]
                            ),
                            environment=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Environment(
                                compute_type=["computeType"],
                                environment_variables=[codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.EnvironmentItem(
                                    name=["name"],
                                    type=["type"],
                                    value=["value"]
                                )],
                                image=["image"],
                                image_pull_credentials_type=["imagePullCredentialsType"],
                                privileged_mode=["privilegedMode"],
                                type=["type"]
                            ),
                            initiator=["initiator"],
                            logs=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Logs(
                                deep_link=["deepLink"],
                                group_name=["groupName"],
                                stream_name=["streamName"]
                            ),
                            network_interface=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.NetworkInterface(
                                eni_id=["eniId"],
                                subnet_id=["subnetId"]
                            ),
                            phases=[codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformationItem(
                                duration_in_seconds=["durationInSeconds"],
                                end_time=["endTime"],
                                phase_context=["phaseContext"],
                                phase_status=["phaseStatus"],
                                phase_type=["phaseType"],
                                start_time=["startTime"]
                            )],
                            queued_timeout_in_minutes=["queuedTimeoutInMinutes"],
                            source=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Source(
                                auth=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Auth(
                                    type=["type"]
                                ),
                                buildspec=["buildspec"],
                                location=["location"],
                                type=["type"]
                            ),
                            source_version=["sourceVersion"],
                            timeout_in_minutes=["timeoutInMinutes"],
                            vpc_config=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.VpcConfig(
                                security_group_ids=["securityGroupIds"],
                                subnets=[codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.VpcConfigItem(
                                    build_fleet_az=["buildFleetAz"],
                                    customer_az=["customerAz"],
                                    subnet_id=["subnetId"]
                                )],
                                vpc_id=["vpcId"]
                            )
                        ),
                        build_id=["buildId"],
                        completed_phase=["completedPhase"],
                        completed_phase_context=["completedPhaseContext"],
                        completed_phase_duration_seconds=["completedPhaseDurationSeconds"],
                        completed_phase_end=["completedPhaseEnd"],
                        completed_phase_start=["completedPhaseStart"],
                        completed_phase_status=["completedPhaseStatus"],
                        event_metadata=AWSEventMetadataProps(
                            region=["region"],
                            resources=["resources"],
                            version=["version"]
                        ),
                        project_name=["projectName"],
                        version=["version"]
                    )
                '''
                if isinstance(additional_information, dict):
                    additional_information = ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformation(**additional_information)
                if isinstance(event_metadata, dict):
                    event_metadata = _aws_cdk_ceddda9d.AWSEventMetadataProps(**event_metadata)
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__0be4c0166f5a8e7480cc14c31731d7e3f8bac9b5c3bd5c27f58af645417e9ec5)
                    check_type(argname="argument additional_information", value=additional_information, expected_type=type_hints["additional_information"])
                    check_type(argname="argument build_id", value=build_id, expected_type=type_hints["build_id"])
                    check_type(argname="argument completed_phase", value=completed_phase, expected_type=type_hints["completed_phase"])
                    check_type(argname="argument completed_phase_context", value=completed_phase_context, expected_type=type_hints["completed_phase_context"])
                    check_type(argname="argument completed_phase_duration_seconds", value=completed_phase_duration_seconds, expected_type=type_hints["completed_phase_duration_seconds"])
                    check_type(argname="argument completed_phase_end", value=completed_phase_end, expected_type=type_hints["completed_phase_end"])
                    check_type(argname="argument completed_phase_start", value=completed_phase_start, expected_type=type_hints["completed_phase_start"])
                    check_type(argname="argument completed_phase_status", value=completed_phase_status, expected_type=type_hints["completed_phase_status"])
                    check_type(argname="argument event_metadata", value=event_metadata, expected_type=type_hints["event_metadata"])
                    check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
                    check_type(argname="argument version", value=version, expected_type=type_hints["version"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if additional_information is not None:
                    self._values["additional_information"] = additional_information
                if build_id is not None:
                    self._values["build_id"] = build_id
                if completed_phase is not None:
                    self._values["completed_phase"] = completed_phase
                if completed_phase_context is not None:
                    self._values["completed_phase_context"] = completed_phase_context
                if completed_phase_duration_seconds is not None:
                    self._values["completed_phase_duration_seconds"] = completed_phase_duration_seconds
                if completed_phase_end is not None:
                    self._values["completed_phase_end"] = completed_phase_end
                if completed_phase_start is not None:
                    self._values["completed_phase_start"] = completed_phase_start
                if completed_phase_status is not None:
                    self._values["completed_phase_status"] = completed_phase_status
                if event_metadata is not None:
                    self._values["event_metadata"] = event_metadata
                if project_name is not None:
                    self._values["project_name"] = project_name
                if version is not None:
                    self._values["version"] = version

            @builtins.property
            def additional_information(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformation"]:
                '''(experimental) additional-information property.

                Specify an array of string values to match this event if the actual value of additional-information is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("additional_information")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformation"], result)

            @builtins.property
            def build_id(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) build-id property.

                Specify an array of string values to match this event if the actual value of build-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("build_id")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def completed_phase(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) completed-phase property.

                Specify an array of string values to match this event if the actual value of completed-phase is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("completed_phase")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def completed_phase_context(
                self,
            ) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) completed-phase-context property.

                Specify an array of string values to match this event if the actual value of completed-phase-context is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("completed_phase_context")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def completed_phase_duration_seconds(
                self,
            ) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) completed-phase-duration-seconds property.

                Specify an array of string values to match this event if the actual value of completed-phase-duration-seconds is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("completed_phase_duration_seconds")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def completed_phase_end(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) completed-phase-end property.

                Specify an array of string values to match this event if the actual value of completed-phase-end is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("completed_phase_end")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def completed_phase_start(
                self,
            ) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) completed-phase-start property.

                Specify an array of string values to match this event if the actual value of completed-phase-start is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("completed_phase_start")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def completed_phase_status(
                self,
            ) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) completed-phase-status property.

                Specify an array of string values to match this event if the actual value of completed-phase-status is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("completed_phase_status")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def event_metadata(
                self,
            ) -> typing.Optional["_aws_cdk_ceddda9d.AWSEventMetadataProps"]:
                '''(experimental) EventBridge event metadata.

                :default:

                -
                -

                :stability: experimental
                '''
                result = self._values.get("event_metadata")
                return typing.cast(typing.Optional["_aws_cdk_ceddda9d.AWSEventMetadataProps"], result)

            @builtins.property
            def project_name(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) project-name property.

                Specify an array of string values to match this event if the actual value of project-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Filter with the Project reference

                :stability: experimental
                '''
                result = self._values.get("project_name")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def version(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) version property.

                Specify an array of string values to match this event if the actual value of version is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("version")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "CodeBuildBuildPhaseChangeProps(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.Environment",
            jsii_struct_bases=[],
            name_mapping={
                "compute_type": "computeType",
                "environment_variables": "environmentVariables",
                "image": "image",
                "image_pull_credentials_type": "imagePullCredentialsType",
                "privileged_mode": "privilegedMode",
                "type": "type",
            },
        )
        class Environment:
            def __init__(
                self,
                *,
                compute_type: typing.Optional[typing.Sequence[builtins.str]] = None,
                environment_variables: typing.Optional[typing.Sequence[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.EnvironmentItem", typing.Dict[builtins.str, typing.Any]]]] = None,
                image: typing.Optional[typing.Sequence[builtins.str]] = None,
                image_pull_credentials_type: typing.Optional[typing.Sequence[builtins.str]] = None,
                privileged_mode: typing.Optional[typing.Sequence[builtins.str]] = None,
                type: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Environment.

                :param compute_type: (experimental) compute-type property. Specify an array of string values to match this event if the actual value of compute-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param environment_variables: (experimental) environment-variables property. Specify an array of string values to match this event if the actual value of environment-variables is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param image: (experimental) image property. Specify an array of string values to match this event if the actual value of image is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param image_pull_credentials_type: (experimental) image-pull-credentials-type property. Specify an array of string values to match this event if the actual value of image-pull-credentials-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param privileged_mode: (experimental) privileged-mode property. Specify an array of string values to match this event if the actual value of privileged-mode is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param type: (experimental) type property. Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    environment = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Environment(
                        compute_type=["computeType"],
                        environment_variables=[codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.EnvironmentItem(
                            name=["name"],
                            type=["type"],
                            value=["value"]
                        )],
                        image=["image"],
                        image_pull_credentials_type=["imagePullCredentialsType"],
                        privileged_mode=["privilegedMode"],
                        type=["type"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__661f7b330060a5f5491c6b18da12b16b74199b20c59c8309b8f1a7fc023fa0eb)
                    check_type(argname="argument compute_type", value=compute_type, expected_type=type_hints["compute_type"])
                    check_type(argname="argument environment_variables", value=environment_variables, expected_type=type_hints["environment_variables"])
                    check_type(argname="argument image", value=image, expected_type=type_hints["image"])
                    check_type(argname="argument image_pull_credentials_type", value=image_pull_credentials_type, expected_type=type_hints["image_pull_credentials_type"])
                    check_type(argname="argument privileged_mode", value=privileged_mode, expected_type=type_hints["privileged_mode"])
                    check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if compute_type is not None:
                    self._values["compute_type"] = compute_type
                if environment_variables is not None:
                    self._values["environment_variables"] = environment_variables
                if image is not None:
                    self._values["image"] = image
                if image_pull_credentials_type is not None:
                    self._values["image_pull_credentials_type"] = image_pull_credentials_type
                if privileged_mode is not None:
                    self._values["privileged_mode"] = privileged_mode
                if type is not None:
                    self._values["type"] = type

            @builtins.property
            def compute_type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) compute-type property.

                Specify an array of string values to match this event if the actual value of compute-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("compute_type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def environment_variables(
                self,
            ) -> typing.Optional[typing.List["ProjectEvents.CodeBuildBuildPhaseChange.EnvironmentItem"]]:
                '''(experimental) environment-variables property.

                Specify an array of string values to match this event if the actual value of environment-variables is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("environment_variables")
                return typing.cast(typing.Optional[typing.List["ProjectEvents.CodeBuildBuildPhaseChange.EnvironmentItem"]], result)

            @builtins.property
            def image(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) image property.

                Specify an array of string values to match this event if the actual value of image is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("image")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def image_pull_credentials_type(
                self,
            ) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) image-pull-credentials-type property.

                Specify an array of string values to match this event if the actual value of image-pull-credentials-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("image_pull_credentials_type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def privileged_mode(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) privileged-mode property.

                Specify an array of string values to match this event if the actual value of privileged-mode is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("privileged_mode")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) type property.

                Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Environment(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.EnvironmentItem",
            jsii_struct_bases=[],
            name_mapping={"name": "name", "type": "type", "value": "value"},
        )
        class EnvironmentItem:
            def __init__(
                self,
                *,
                name: typing.Optional[typing.Sequence[builtins.str]] = None,
                type: typing.Optional[typing.Sequence[builtins.str]] = None,
                value: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for EnvironmentItem.

                :param name: (experimental) name property. Specify an array of string values to match this event if the actual value of name is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param type: (experimental) type property. Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param value: (experimental) value property. Specify an array of string values to match this event if the actual value of value is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    environment_item = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.EnvironmentItem(
                        name=["name"],
                        type=["type"],
                        value=["value"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__4affad4f0be42ee8abd9903e532782b6b6d15e11aea3f8c4700ba7267b41ca84)
                    check_type(argname="argument name", value=name, expected_type=type_hints["name"])
                    check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                    check_type(argname="argument value", value=value, expected_type=type_hints["value"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if name is not None:
                    self._values["name"] = name
                if type is not None:
                    self._values["type"] = type
                if value is not None:
                    self._values["value"] = value

            @builtins.property
            def name(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) name property.

                Specify an array of string values to match this event if the actual value of name is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("name")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) type property.

                Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def value(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) value property.

                Specify an array of string values to match this event if the actual value of value is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("value")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "EnvironmentItem(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.Logs",
            jsii_struct_bases=[],
            name_mapping={
                "deep_link": "deepLink",
                "group_name": "groupName",
                "stream_name": "streamName",
            },
        )
        class Logs:
            def __init__(
                self,
                *,
                deep_link: typing.Optional[typing.Sequence[builtins.str]] = None,
                group_name: typing.Optional[typing.Sequence[builtins.str]] = None,
                stream_name: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Logs.

                :param deep_link: (experimental) deep-link property. Specify an array of string values to match this event if the actual value of deep-link is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param group_name: (experimental) group-name property. Specify an array of string values to match this event if the actual value of group-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param stream_name: (experimental) stream-name property. Specify an array of string values to match this event if the actual value of stream-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    logs = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Logs(
                        deep_link=["deepLink"],
                        group_name=["groupName"],
                        stream_name=["streamName"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__427a5300004c5dd1bc08d0af2ab5a4639ac3bf31b7aaa5a67395d9f2e6cc4e09)
                    check_type(argname="argument deep_link", value=deep_link, expected_type=type_hints["deep_link"])
                    check_type(argname="argument group_name", value=group_name, expected_type=type_hints["group_name"])
                    check_type(argname="argument stream_name", value=stream_name, expected_type=type_hints["stream_name"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if deep_link is not None:
                    self._values["deep_link"] = deep_link
                if group_name is not None:
                    self._values["group_name"] = group_name
                if stream_name is not None:
                    self._values["stream_name"] = stream_name

            @builtins.property
            def deep_link(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) deep-link property.

                Specify an array of string values to match this event if the actual value of deep-link is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("deep_link")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def group_name(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) group-name property.

                Specify an array of string values to match this event if the actual value of group-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("group_name")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def stream_name(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) stream-name property.

                Specify an array of string values to match this event if the actual value of stream-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("stream_name")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Logs(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.NetworkInterface",
            jsii_struct_bases=[],
            name_mapping={"eni_id": "eniId", "subnet_id": "subnetId"},
        )
        class NetworkInterface:
            def __init__(
                self,
                *,
                eni_id: typing.Optional[typing.Sequence[builtins.str]] = None,
                subnet_id: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Network-interface.

                :param eni_id: (experimental) eni-id property. Specify an array of string values to match this event if the actual value of eni-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param subnet_id: (experimental) subnet-id property. Specify an array of string values to match this event if the actual value of subnet-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    network_interface = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.NetworkInterface(
                        eni_id=["eniId"],
                        subnet_id=["subnetId"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__ec7f1a0d9c52c67921ca04d0ec0848af5174afc13ae9a201f3cb24e00634e4c7)
                    check_type(argname="argument eni_id", value=eni_id, expected_type=type_hints["eni_id"])
                    check_type(argname="argument subnet_id", value=subnet_id, expected_type=type_hints["subnet_id"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if eni_id is not None:
                    self._values["eni_id"] = eni_id
                if subnet_id is not None:
                    self._values["subnet_id"] = subnet_id

            @builtins.property
            def eni_id(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) eni-id property.

                Specify an array of string values to match this event if the actual value of eni-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("eni_id")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def subnet_id(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) subnet-id property.

                Specify an array of string values to match this event if the actual value of subnet-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("subnet_id")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "NetworkInterface(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.Source",
            jsii_struct_bases=[],
            name_mapping={
                "auth": "auth",
                "buildspec": "buildspec",
                "location": "location",
                "type": "type",
            },
        )
        class Source:
            def __init__(
                self,
                *,
                auth: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.Auth", typing.Dict[builtins.str, typing.Any]]] = None,
                buildspec: typing.Optional[typing.Sequence[builtins.str]] = None,
                location: typing.Optional[typing.Sequence[builtins.str]] = None,
                type: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Source.

                :param auth: (experimental) auth property. Specify an array of string values to match this event if the actual value of auth is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param buildspec: (experimental) buildspec property. Specify an array of string values to match this event if the actual value of buildspec is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param location: (experimental) location property. Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param type: (experimental) type property. Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    source = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Source(
                        auth=codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.Auth(
                            type=["type"]
                        ),
                        buildspec=["buildspec"],
                        location=["location"],
                        type=["type"]
                    )
                '''
                if isinstance(auth, dict):
                    auth = ProjectEvents.CodeBuildBuildPhaseChange.Auth(**auth)
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__fdfc0f08296e1346494b513fdd0ba3d8c688ec94319ba51132ce9e718efddec2)
                    check_type(argname="argument auth", value=auth, expected_type=type_hints["auth"])
                    check_type(argname="argument buildspec", value=buildspec, expected_type=type_hints["buildspec"])
                    check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                    check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if auth is not None:
                    self._values["auth"] = auth
                if buildspec is not None:
                    self._values["buildspec"] = buildspec
                if location is not None:
                    self._values["location"] = location
                if type is not None:
                    self._values["type"] = type

            @builtins.property
            def auth(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Auth"]:
                '''(experimental) auth property.

                Specify an array of string values to match this event if the actual value of auth is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("auth")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildPhaseChange.Auth"], result)

            @builtins.property
            def buildspec(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) buildspec property.

                Specify an array of string values to match this event if the actual value of buildspec is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("buildspec")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def location(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) location property.

                Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("location")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) type property.

                Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Source(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.VpcConfig",
            jsii_struct_bases=[],
            name_mapping={
                "security_group_ids": "securityGroupIds",
                "subnets": "subnets",
                "vpc_id": "vpcId",
            },
        )
        class VpcConfig:
            def __init__(
                self,
                *,
                security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
                subnets: typing.Optional[typing.Sequence[typing.Union["ProjectEvents.CodeBuildBuildPhaseChange.VpcConfigItem", typing.Dict[builtins.str, typing.Any]]]] = None,
                vpc_id: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Vpc-config.

                :param security_group_ids: (experimental) security-group-ids property. Specify an array of string values to match this event if the actual value of security-group-ids is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param subnets: (experimental) subnets property. Specify an array of string values to match this event if the actual value of subnets is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param vpc_id: (experimental) vpc-id property. Specify an array of string values to match this event if the actual value of vpc-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    vpc_config = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.VpcConfig(
                        security_group_ids=["securityGroupIds"],
                        subnets=[codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.VpcConfigItem(
                            build_fleet_az=["buildFleetAz"],
                            customer_az=["customerAz"],
                            subnet_id=["subnetId"]
                        )],
                        vpc_id=["vpcId"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__9f387b20e7fea012a85a28d32ecb34e1305da44355482f38fc5ae589b5741035)
                    check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
                    check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
                    check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if security_group_ids is not None:
                    self._values["security_group_ids"] = security_group_ids
                if subnets is not None:
                    self._values["subnets"] = subnets
                if vpc_id is not None:
                    self._values["vpc_id"] = vpc_id

            @builtins.property
            def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) security-group-ids property.

                Specify an array of string values to match this event if the actual value of security-group-ids is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("security_group_ids")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def subnets(
                self,
            ) -> typing.Optional[typing.List["ProjectEvents.CodeBuildBuildPhaseChange.VpcConfigItem"]]:
                '''(experimental) subnets property.

                Specify an array of string values to match this event if the actual value of subnets is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("subnets")
                return typing.cast(typing.Optional[typing.List["ProjectEvents.CodeBuildBuildPhaseChange.VpcConfigItem"]], result)

            @builtins.property
            def vpc_id(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) vpc-id property.

                Specify an array of string values to match this event if the actual value of vpc-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("vpc_id")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "VpcConfig(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildPhaseChange.VpcConfigItem",
            jsii_struct_bases=[],
            name_mapping={
                "build_fleet_az": "buildFleetAz",
                "customer_az": "customerAz",
                "subnet_id": "subnetId",
            },
        )
        class VpcConfigItem:
            def __init__(
                self,
                *,
                build_fleet_az: typing.Optional[typing.Sequence[builtins.str]] = None,
                customer_az: typing.Optional[typing.Sequence[builtins.str]] = None,
                subnet_id: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Vpc-configItem.

                :param build_fleet_az: (experimental) build-fleet-az property. Specify an array of string values to match this event if the actual value of build-fleet-az is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param customer_az: (experimental) customer-az property. Specify an array of string values to match this event if the actual value of customer-az is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param subnet_id: (experimental) subnet-id property. Specify an array of string values to match this event if the actual value of subnet-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    vpc_config_item = codebuild_events.ProjectEvents.CodeBuildBuildPhaseChange.VpcConfigItem(
                        build_fleet_az=["buildFleetAz"],
                        customer_az=["customerAz"],
                        subnet_id=["subnetId"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__c5f261f587d90625d84cad373e5267184cc6ac47a8ede001352e7864756712ba)
                    check_type(argname="argument build_fleet_az", value=build_fleet_az, expected_type=type_hints["build_fleet_az"])
                    check_type(argname="argument customer_az", value=customer_az, expected_type=type_hints["customer_az"])
                    check_type(argname="argument subnet_id", value=subnet_id, expected_type=type_hints["subnet_id"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if build_fleet_az is not None:
                    self._values["build_fleet_az"] = build_fleet_az
                if customer_az is not None:
                    self._values["customer_az"] = customer_az
                if subnet_id is not None:
                    self._values["subnet_id"] = subnet_id

            @builtins.property
            def build_fleet_az(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) build-fleet-az property.

                Specify an array of string values to match this event if the actual value of build-fleet-az is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("build_fleet_az")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def customer_az(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) customer-az property.

                Specify an array of string values to match this event if the actual value of customer-az is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("customer_az")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def subnet_id(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) subnet-id property.

                Specify an array of string values to match this event if the actual value of subnet-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("subnet_id")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "VpcConfigItem(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

    class CodeBuildBuildStateChange(
        metaclass=jsii.JSIIMeta,
        jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange",
    ):
        '''(experimental) aws.codebuild@CodeBuildBuildStateChange event types for Project.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
            
            code_build_build_state_change = codebuild_events.ProjectEvents.CodeBuildBuildStateChange()
        '''

        def __init__(self) -> None:
            '''
            :stability: experimental
            '''
            jsii.create(self.__class__, self, [])

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.AdditionalInformation",
            jsii_struct_bases=[],
            name_mapping={
                "artifact": "artifact",
                "build_complete": "buildComplete",
                "build_start_time": "buildStartTime",
                "cache": "cache",
                "environment": "environment",
                "initiator": "initiator",
                "logs": "logs",
                "network_interface": "networkInterface",
                "phases": "phases",
                "queued_timeout_in_minutes": "queuedTimeoutInMinutes",
                "source": "source",
                "source_version": "sourceVersion",
                "timeout_in_minutes": "timeoutInMinutes",
                "vpc_config": "vpcConfig",
            },
        )
        class AdditionalInformation:
            def __init__(
                self,
                *,
                artifact: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildStateChange.Artifact", typing.Dict[builtins.str, typing.Any]]] = None,
                build_complete: typing.Optional[typing.Sequence[builtins.str]] = None,
                build_start_time: typing.Optional[typing.Sequence[builtins.str]] = None,
                cache: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildStateChange.Cache", typing.Dict[builtins.str, typing.Any]]] = None,
                environment: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildStateChange.Environment", typing.Dict[builtins.str, typing.Any]]] = None,
                initiator: typing.Optional[typing.Sequence[builtins.str]] = None,
                logs: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildStateChange.Logs", typing.Dict[builtins.str, typing.Any]]] = None,
                network_interface: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildStateChange.NetworkInterface", typing.Dict[builtins.str, typing.Any]]] = None,
                phases: typing.Optional[typing.Sequence[typing.Union["ProjectEvents.CodeBuildBuildStateChange.AdditionalInformationItem", typing.Dict[builtins.str, typing.Any]]]] = None,
                queued_timeout_in_minutes: typing.Optional[typing.Sequence[builtins.str]] = None,
                source: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildStateChange.Source", typing.Dict[builtins.str, typing.Any]]] = None,
                source_version: typing.Optional[typing.Sequence[builtins.str]] = None,
                timeout_in_minutes: typing.Optional[typing.Sequence[builtins.str]] = None,
                vpc_config: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildStateChange.VpcConfig", typing.Dict[builtins.str, typing.Any]]] = None,
            ) -> None:
                '''(experimental) Type definition for Additional-information.

                :param artifact: (experimental) artifact property. Specify an array of string values to match this event if the actual value of artifact is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param build_complete: (experimental) build-complete property. Specify an array of string values to match this event if the actual value of build-complete is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param build_start_time: (experimental) build-start-time property. Specify an array of string values to match this event if the actual value of build-start-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param cache: (experimental) cache property. Specify an array of string values to match this event if the actual value of cache is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param environment: (experimental) environment property. Specify an array of string values to match this event if the actual value of environment is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param initiator: (experimental) initiator property. Specify an array of string values to match this event if the actual value of initiator is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param logs: (experimental) logs property. Specify an array of string values to match this event if the actual value of logs is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param network_interface: (experimental) network-interface property. Specify an array of string values to match this event if the actual value of network-interface is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param phases: (experimental) phases property. Specify an array of string values to match this event if the actual value of phases is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param queued_timeout_in_minutes: (experimental) queued-timeout-in-minutes property. Specify an array of string values to match this event if the actual value of queued-timeout-in-minutes is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param source: (experimental) source property. Specify an array of string values to match this event if the actual value of source is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param source_version: (experimental) source-version property. Specify an array of string values to match this event if the actual value of source-version is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param timeout_in_minutes: (experimental) timeout-in-minutes property. Specify an array of string values to match this event if the actual value of timeout-in-minutes is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param vpc_config: (experimental) vpc-config property. Specify an array of string values to match this event if the actual value of vpc-config is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    additional_information = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.AdditionalInformation(
                        artifact=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Artifact(
                            location=["location"],
                            md5_sum=["md5Sum"],
                            sha256_sum=["sha256Sum"]
                        ),
                        build_complete=["buildComplete"],
                        build_start_time=["buildStartTime"],
                        cache=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Cache(
                            location=["location"],
                            type=["type"]
                        ),
                        environment=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Environment(
                            compute_type=["computeType"],
                            environment_variables=[codebuild_events.ProjectEvents.CodeBuildBuildStateChange.EnvironmentItem(
                                name=["name"],
                                type=["type"],
                                value=["value"]
                            )],
                            image=["image"],
                            image_pull_credentials_type=["imagePullCredentialsType"],
                            privileged_mode=["privilegedMode"],
                            type=["type"]
                        ),
                        initiator=["initiator"],
                        logs=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Logs(
                            deep_link=["deepLink"],
                            group_name=["groupName"],
                            stream_name=["streamName"]
                        ),
                        network_interface=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.NetworkInterface(
                            eni_id=["eniId"],
                            subnet_id=["subnetId"]
                        ),
                        phases=[codebuild_events.ProjectEvents.CodeBuildBuildStateChange.AdditionalInformationItem(
                            duration_in_seconds=["durationInSeconds"],
                            end_time=["endTime"],
                            phase_context=["phaseContext"],
                            phase_status=["phaseStatus"],
                            phase_type=["phaseType"],
                            start_time=["startTime"]
                        )],
                        queued_timeout_in_minutes=["queuedTimeoutInMinutes"],
                        source=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Source(
                            auth=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Auth(
                                resource=["resource"],
                                type=["type"]
                            ),
                            buildspec=["buildspec"],
                            location=["location"],
                            type=["type"]
                        ),
                        source_version=["sourceVersion"],
                        timeout_in_minutes=["timeoutInMinutes"],
                        vpc_config=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.VpcConfig(
                            security_group_ids=["securityGroupIds"],
                            subnets=[codebuild_events.ProjectEvents.CodeBuildBuildStateChange.VpcConfigItem(
                                build_fleet_az=["buildFleetAz"],
                                customer_az=["customerAz"],
                                subnet_id=["subnetId"]
                            )],
                            vpc_id=["vpcId"]
                        )
                    )
                '''
                if isinstance(artifact, dict):
                    artifact = ProjectEvents.CodeBuildBuildStateChange.Artifact(**artifact)
                if isinstance(cache, dict):
                    cache = ProjectEvents.CodeBuildBuildStateChange.Cache(**cache)
                if isinstance(environment, dict):
                    environment = ProjectEvents.CodeBuildBuildStateChange.Environment(**environment)
                if isinstance(logs, dict):
                    logs = ProjectEvents.CodeBuildBuildStateChange.Logs(**logs)
                if isinstance(network_interface, dict):
                    network_interface = ProjectEvents.CodeBuildBuildStateChange.NetworkInterface(**network_interface)
                if isinstance(source, dict):
                    source = ProjectEvents.CodeBuildBuildStateChange.Source(**source)
                if isinstance(vpc_config, dict):
                    vpc_config = ProjectEvents.CodeBuildBuildStateChange.VpcConfig(**vpc_config)
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__ea31abe53a3a6d671652c648f9b0f506466da591288b846bf94f2e82b6301f36)
                    check_type(argname="argument artifact", value=artifact, expected_type=type_hints["artifact"])
                    check_type(argname="argument build_complete", value=build_complete, expected_type=type_hints["build_complete"])
                    check_type(argname="argument build_start_time", value=build_start_time, expected_type=type_hints["build_start_time"])
                    check_type(argname="argument cache", value=cache, expected_type=type_hints["cache"])
                    check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
                    check_type(argname="argument initiator", value=initiator, expected_type=type_hints["initiator"])
                    check_type(argname="argument logs", value=logs, expected_type=type_hints["logs"])
                    check_type(argname="argument network_interface", value=network_interface, expected_type=type_hints["network_interface"])
                    check_type(argname="argument phases", value=phases, expected_type=type_hints["phases"])
                    check_type(argname="argument queued_timeout_in_minutes", value=queued_timeout_in_minutes, expected_type=type_hints["queued_timeout_in_minutes"])
                    check_type(argname="argument source", value=source, expected_type=type_hints["source"])
                    check_type(argname="argument source_version", value=source_version, expected_type=type_hints["source_version"])
                    check_type(argname="argument timeout_in_minutes", value=timeout_in_minutes, expected_type=type_hints["timeout_in_minutes"])
                    check_type(argname="argument vpc_config", value=vpc_config, expected_type=type_hints["vpc_config"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if artifact is not None:
                    self._values["artifact"] = artifact
                if build_complete is not None:
                    self._values["build_complete"] = build_complete
                if build_start_time is not None:
                    self._values["build_start_time"] = build_start_time
                if cache is not None:
                    self._values["cache"] = cache
                if environment is not None:
                    self._values["environment"] = environment
                if initiator is not None:
                    self._values["initiator"] = initiator
                if logs is not None:
                    self._values["logs"] = logs
                if network_interface is not None:
                    self._values["network_interface"] = network_interface
                if phases is not None:
                    self._values["phases"] = phases
                if queued_timeout_in_minutes is not None:
                    self._values["queued_timeout_in_minutes"] = queued_timeout_in_minutes
                if source is not None:
                    self._values["source"] = source
                if source_version is not None:
                    self._values["source_version"] = source_version
                if timeout_in_minutes is not None:
                    self._values["timeout_in_minutes"] = timeout_in_minutes
                if vpc_config is not None:
                    self._values["vpc_config"] = vpc_config

            @builtins.property
            def artifact(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Artifact"]:
                '''(experimental) artifact property.

                Specify an array of string values to match this event if the actual value of artifact is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("artifact")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Artifact"], result)

            @builtins.property
            def build_complete(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) build-complete property.

                Specify an array of string values to match this event if the actual value of build-complete is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("build_complete")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def build_start_time(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) build-start-time property.

                Specify an array of string values to match this event if the actual value of build-start-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("build_start_time")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def cache(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Cache"]:
                '''(experimental) cache property.

                Specify an array of string values to match this event if the actual value of cache is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("cache")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Cache"], result)

            @builtins.property
            def environment(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Environment"]:
                '''(experimental) environment property.

                Specify an array of string values to match this event if the actual value of environment is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("environment")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Environment"], result)

            @builtins.property
            def initiator(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) initiator property.

                Specify an array of string values to match this event if the actual value of initiator is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("initiator")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def logs(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Logs"]:
                '''(experimental) logs property.

                Specify an array of string values to match this event if the actual value of logs is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("logs")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Logs"], result)

            @builtins.property
            def network_interface(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildStateChange.NetworkInterface"]:
                '''(experimental) network-interface property.

                Specify an array of string values to match this event if the actual value of network-interface is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("network_interface")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildStateChange.NetworkInterface"], result)

            @builtins.property
            def phases(
                self,
            ) -> typing.Optional[typing.List["ProjectEvents.CodeBuildBuildStateChange.AdditionalInformationItem"]]:
                '''(experimental) phases property.

                Specify an array of string values to match this event if the actual value of phases is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("phases")
                return typing.cast(typing.Optional[typing.List["ProjectEvents.CodeBuildBuildStateChange.AdditionalInformationItem"]], result)

            @builtins.property
            def queued_timeout_in_minutes(
                self,
            ) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) queued-timeout-in-minutes property.

                Specify an array of string values to match this event if the actual value of queued-timeout-in-minutes is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("queued_timeout_in_minutes")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def source(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Source"]:
                '''(experimental) source property.

                Specify an array of string values to match this event if the actual value of source is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("source")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Source"], result)

            @builtins.property
            def source_version(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) source-version property.

                Specify an array of string values to match this event if the actual value of source-version is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("source_version")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def timeout_in_minutes(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) timeout-in-minutes property.

                Specify an array of string values to match this event if the actual value of timeout-in-minutes is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("timeout_in_minutes")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def vpc_config(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildStateChange.VpcConfig"]:
                '''(experimental) vpc-config property.

                Specify an array of string values to match this event if the actual value of vpc-config is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("vpc_config")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildStateChange.VpcConfig"], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "AdditionalInformation(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.AdditionalInformationItem",
            jsii_struct_bases=[],
            name_mapping={
                "duration_in_seconds": "durationInSeconds",
                "end_time": "endTime",
                "phase_context": "phaseContext",
                "phase_status": "phaseStatus",
                "phase_type": "phaseType",
                "start_time": "startTime",
            },
        )
        class AdditionalInformationItem:
            def __init__(
                self,
                *,
                duration_in_seconds: typing.Optional[typing.Sequence[builtins.str]] = None,
                end_time: typing.Optional[typing.Sequence[builtins.str]] = None,
                phase_context: typing.Optional[typing.Sequence[builtins.str]] = None,
                phase_status: typing.Optional[typing.Sequence[builtins.str]] = None,
                phase_type: typing.Optional[typing.Sequence[builtins.str]] = None,
                start_time: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Additional-informationItem.

                :param duration_in_seconds: (experimental) duration-in-seconds property. Specify an array of string values to match this event if the actual value of duration-in-seconds is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param end_time: (experimental) end-time property. Specify an array of string values to match this event if the actual value of end-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param phase_context: (experimental) phase-context property. Specify an array of string values to match this event if the actual value of phase-context is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param phase_status: (experimental) phase-status property. Specify an array of string values to match this event if the actual value of phase-status is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param phase_type: (experimental) phase-type property. Specify an array of string values to match this event if the actual value of phase-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param start_time: (experimental) start-time property. Specify an array of string values to match this event if the actual value of start-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    additional_information_item = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.AdditionalInformationItem(
                        duration_in_seconds=["durationInSeconds"],
                        end_time=["endTime"],
                        phase_context=["phaseContext"],
                        phase_status=["phaseStatus"],
                        phase_type=["phaseType"],
                        start_time=["startTime"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__0c24187fccd4878b05d791132a7a8beda27a0ab227d5110f7fbb187b85c3dbb6)
                    check_type(argname="argument duration_in_seconds", value=duration_in_seconds, expected_type=type_hints["duration_in_seconds"])
                    check_type(argname="argument end_time", value=end_time, expected_type=type_hints["end_time"])
                    check_type(argname="argument phase_context", value=phase_context, expected_type=type_hints["phase_context"])
                    check_type(argname="argument phase_status", value=phase_status, expected_type=type_hints["phase_status"])
                    check_type(argname="argument phase_type", value=phase_type, expected_type=type_hints["phase_type"])
                    check_type(argname="argument start_time", value=start_time, expected_type=type_hints["start_time"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if duration_in_seconds is not None:
                    self._values["duration_in_seconds"] = duration_in_seconds
                if end_time is not None:
                    self._values["end_time"] = end_time
                if phase_context is not None:
                    self._values["phase_context"] = phase_context
                if phase_status is not None:
                    self._values["phase_status"] = phase_status
                if phase_type is not None:
                    self._values["phase_type"] = phase_type
                if start_time is not None:
                    self._values["start_time"] = start_time

            @builtins.property
            def duration_in_seconds(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) duration-in-seconds property.

                Specify an array of string values to match this event if the actual value of duration-in-seconds is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("duration_in_seconds")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def end_time(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) end-time property.

                Specify an array of string values to match this event if the actual value of end-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("end_time")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def phase_context(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) phase-context property.

                Specify an array of string values to match this event if the actual value of phase-context is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("phase_context")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def phase_status(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) phase-status property.

                Specify an array of string values to match this event if the actual value of phase-status is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("phase_status")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def phase_type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) phase-type property.

                Specify an array of string values to match this event if the actual value of phase-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("phase_type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def start_time(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) start-time property.

                Specify an array of string values to match this event if the actual value of start-time is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("start_time")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "AdditionalInformationItem(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.Artifact",
            jsii_struct_bases=[],
            name_mapping={
                "location": "location",
                "md5_sum": "md5Sum",
                "sha256_sum": "sha256Sum",
            },
        )
        class Artifact:
            def __init__(
                self,
                *,
                location: typing.Optional[typing.Sequence[builtins.str]] = None,
                md5_sum: typing.Optional[typing.Sequence[builtins.str]] = None,
                sha256_sum: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Artifact.

                :param location: (experimental) location property. Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param md5_sum: (experimental) md5sum property. Specify an array of string values to match this event if the actual value of md5sum is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param sha256_sum: (experimental) sha256sum property. Specify an array of string values to match this event if the actual value of sha256sum is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    artifact = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Artifact(
                        location=["location"],
                        md5_sum=["md5Sum"],
                        sha256_sum=["sha256Sum"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__46ef149d6a08f0b5ad7ff9610e288b2825d957b6a93b38981180b46b16339a4e)
                    check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                    check_type(argname="argument md5_sum", value=md5_sum, expected_type=type_hints["md5_sum"])
                    check_type(argname="argument sha256_sum", value=sha256_sum, expected_type=type_hints["sha256_sum"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if location is not None:
                    self._values["location"] = location
                if md5_sum is not None:
                    self._values["md5_sum"] = md5_sum
                if sha256_sum is not None:
                    self._values["sha256_sum"] = sha256_sum

            @builtins.property
            def location(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) location property.

                Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("location")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def md5_sum(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) md5sum property.

                Specify an array of string values to match this event if the actual value of md5sum is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("md5_sum")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def sha256_sum(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) sha256sum property.

                Specify an array of string values to match this event if the actual value of sha256sum is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("sha256_sum")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Artifact(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.Auth",
            jsii_struct_bases=[],
            name_mapping={"resource": "resource", "type": "type"},
        )
        class Auth:
            def __init__(
                self,
                *,
                resource: typing.Optional[typing.Sequence[builtins.str]] = None,
                type: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Auth.

                :param resource: (experimental) resource property. Specify an array of string values to match this event if the actual value of resource is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param type: (experimental) type property. Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    auth = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Auth(
                        resource=["resource"],
                        type=["type"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__ca1a3b1db63fd08cd6deeb6743fcdfa5bd0b306601c0b30ba97f4ba25e2631ea)
                    check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
                    check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if resource is not None:
                    self._values["resource"] = resource
                if type is not None:
                    self._values["type"] = type

            @builtins.property
            def resource(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) resource property.

                Specify an array of string values to match this event if the actual value of resource is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("resource")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) type property.

                Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Auth(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.Cache",
            jsii_struct_bases=[],
            name_mapping={"location": "location", "type": "type"},
        )
        class Cache:
            def __init__(
                self,
                *,
                location: typing.Optional[typing.Sequence[builtins.str]] = None,
                type: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Cache.

                :param location: (experimental) location property. Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param type: (experimental) type property. Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    cache = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Cache(
                        location=["location"],
                        type=["type"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__28d13ce9e3be3f458ec5c805da74cb9145da217b709929d5da37bccff982d5fd)
                    check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                    check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if location is not None:
                    self._values["location"] = location
                if type is not None:
                    self._values["type"] = type

            @builtins.property
            def location(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) location property.

                Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("location")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) type property.

                Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Cache(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.CodeBuildBuildStateChangeProps",
            jsii_struct_bases=[],
            name_mapping={
                "additional_information": "additionalInformation",
                "build_id": "buildId",
                "build_status": "buildStatus",
                "current_phase": "currentPhase",
                "current_phase_context": "currentPhaseContext",
                "event_metadata": "eventMetadata",
                "project_name": "projectName",
                "version": "version",
            },
        )
        class CodeBuildBuildStateChangeProps:
            def __init__(
                self,
                *,
                additional_information: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildStateChange.AdditionalInformation", typing.Dict[builtins.str, typing.Any]]] = None,
                build_id: typing.Optional[typing.Sequence[builtins.str]] = None,
                build_status: typing.Optional[typing.Sequence[builtins.str]] = None,
                current_phase: typing.Optional[typing.Sequence[builtins.str]] = None,
                current_phase_context: typing.Optional[typing.Sequence[builtins.str]] = None,
                event_metadata: typing.Optional[typing.Union["_aws_cdk_ceddda9d.AWSEventMetadataProps", typing.Dict[builtins.str, typing.Any]]] = None,
                project_name: typing.Optional[typing.Sequence[builtins.str]] = None,
                version: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Props type for Project aws.codebuild@CodeBuildBuildStateChange event.

                :param additional_information: (experimental) additional-information property. Specify an array of string values to match this event if the actual value of additional-information is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param build_id: (experimental) build-id property. Specify an array of string values to match this event if the actual value of build-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param build_status: (experimental) build-status property. Specify an array of string values to match this event if the actual value of build-status is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param current_phase: (experimental) current-phase property. Specify an array of string values to match this event if the actual value of current-phase is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param current_phase_context: (experimental) current-phase-context property. Specify an array of string values to match this event if the actual value of current-phase-context is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param event_metadata: (experimental) EventBridge event metadata. Default: - -
                :param project_name: (experimental) project-name property. Specify an array of string values to match this event if the actual value of project-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Filter with the Project reference
                :param version: (experimental) version property. Specify an array of string values to match this event if the actual value of version is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    from aws_cdk import AWSEventMetadataProps
                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    code_build_build_state_change_props = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.CodeBuildBuildStateChangeProps(
                        additional_information=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.AdditionalInformation(
                            artifact=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Artifact(
                                location=["location"],
                                md5_sum=["md5Sum"],
                                sha256_sum=["sha256Sum"]
                            ),
                            build_complete=["buildComplete"],
                            build_start_time=["buildStartTime"],
                            cache=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Cache(
                                location=["location"],
                                type=["type"]
                            ),
                            environment=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Environment(
                                compute_type=["computeType"],
                                environment_variables=[codebuild_events.ProjectEvents.CodeBuildBuildStateChange.EnvironmentItem(
                                    name=["name"],
                                    type=["type"],
                                    value=["value"]
                                )],
                                image=["image"],
                                image_pull_credentials_type=["imagePullCredentialsType"],
                                privileged_mode=["privilegedMode"],
                                type=["type"]
                            ),
                            initiator=["initiator"],
                            logs=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Logs(
                                deep_link=["deepLink"],
                                group_name=["groupName"],
                                stream_name=["streamName"]
                            ),
                            network_interface=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.NetworkInterface(
                                eni_id=["eniId"],
                                subnet_id=["subnetId"]
                            ),
                            phases=[codebuild_events.ProjectEvents.CodeBuildBuildStateChange.AdditionalInformationItem(
                                duration_in_seconds=["durationInSeconds"],
                                end_time=["endTime"],
                                phase_context=["phaseContext"],
                                phase_status=["phaseStatus"],
                                phase_type=["phaseType"],
                                start_time=["startTime"]
                            )],
                            queued_timeout_in_minutes=["queuedTimeoutInMinutes"],
                            source=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Source(
                                auth=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Auth(
                                    resource=["resource"],
                                    type=["type"]
                                ),
                                buildspec=["buildspec"],
                                location=["location"],
                                type=["type"]
                            ),
                            source_version=["sourceVersion"],
                            timeout_in_minutes=["timeoutInMinutes"],
                            vpc_config=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.VpcConfig(
                                security_group_ids=["securityGroupIds"],
                                subnets=[codebuild_events.ProjectEvents.CodeBuildBuildStateChange.VpcConfigItem(
                                    build_fleet_az=["buildFleetAz"],
                                    customer_az=["customerAz"],
                                    subnet_id=["subnetId"]
                                )],
                                vpc_id=["vpcId"]
                            )
                        ),
                        build_id=["buildId"],
                        build_status=["buildStatus"],
                        current_phase=["currentPhase"],
                        current_phase_context=["currentPhaseContext"],
                        event_metadata=AWSEventMetadataProps(
                            region=["region"],
                            resources=["resources"],
                            version=["version"]
                        ),
                        project_name=["projectName"],
                        version=["version"]
                    )
                '''
                if isinstance(additional_information, dict):
                    additional_information = ProjectEvents.CodeBuildBuildStateChange.AdditionalInformation(**additional_information)
                if isinstance(event_metadata, dict):
                    event_metadata = _aws_cdk_ceddda9d.AWSEventMetadataProps(**event_metadata)
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__247f87e2ef8ff9c682d2d3e8d9f448f4bd5a6bf4b27696ad5c4184325e8e39be)
                    check_type(argname="argument additional_information", value=additional_information, expected_type=type_hints["additional_information"])
                    check_type(argname="argument build_id", value=build_id, expected_type=type_hints["build_id"])
                    check_type(argname="argument build_status", value=build_status, expected_type=type_hints["build_status"])
                    check_type(argname="argument current_phase", value=current_phase, expected_type=type_hints["current_phase"])
                    check_type(argname="argument current_phase_context", value=current_phase_context, expected_type=type_hints["current_phase_context"])
                    check_type(argname="argument event_metadata", value=event_metadata, expected_type=type_hints["event_metadata"])
                    check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
                    check_type(argname="argument version", value=version, expected_type=type_hints["version"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if additional_information is not None:
                    self._values["additional_information"] = additional_information
                if build_id is not None:
                    self._values["build_id"] = build_id
                if build_status is not None:
                    self._values["build_status"] = build_status
                if current_phase is not None:
                    self._values["current_phase"] = current_phase
                if current_phase_context is not None:
                    self._values["current_phase_context"] = current_phase_context
                if event_metadata is not None:
                    self._values["event_metadata"] = event_metadata
                if project_name is not None:
                    self._values["project_name"] = project_name
                if version is not None:
                    self._values["version"] = version

            @builtins.property
            def additional_information(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildStateChange.AdditionalInformation"]:
                '''(experimental) additional-information property.

                Specify an array of string values to match this event if the actual value of additional-information is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("additional_information")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildStateChange.AdditionalInformation"], result)

            @builtins.property
            def build_id(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) build-id property.

                Specify an array of string values to match this event if the actual value of build-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("build_id")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def build_status(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) build-status property.

                Specify an array of string values to match this event if the actual value of build-status is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("build_status")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def current_phase(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) current-phase property.

                Specify an array of string values to match this event if the actual value of current-phase is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("current_phase")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def current_phase_context(
                self,
            ) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) current-phase-context property.

                Specify an array of string values to match this event if the actual value of current-phase-context is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("current_phase_context")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def event_metadata(
                self,
            ) -> typing.Optional["_aws_cdk_ceddda9d.AWSEventMetadataProps"]:
                '''(experimental) EventBridge event metadata.

                :default:

                -
                -

                :stability: experimental
                '''
                result = self._values.get("event_metadata")
                return typing.cast(typing.Optional["_aws_cdk_ceddda9d.AWSEventMetadataProps"], result)

            @builtins.property
            def project_name(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) project-name property.

                Specify an array of string values to match this event if the actual value of project-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Filter with the Project reference

                :stability: experimental
                '''
                result = self._values.get("project_name")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def version(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) version property.

                Specify an array of string values to match this event if the actual value of version is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("version")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "CodeBuildBuildStateChangeProps(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.Environment",
            jsii_struct_bases=[],
            name_mapping={
                "compute_type": "computeType",
                "environment_variables": "environmentVariables",
                "image": "image",
                "image_pull_credentials_type": "imagePullCredentialsType",
                "privileged_mode": "privilegedMode",
                "type": "type",
            },
        )
        class Environment:
            def __init__(
                self,
                *,
                compute_type: typing.Optional[typing.Sequence[builtins.str]] = None,
                environment_variables: typing.Optional[typing.Sequence[typing.Union["ProjectEvents.CodeBuildBuildStateChange.EnvironmentItem", typing.Dict[builtins.str, typing.Any]]]] = None,
                image: typing.Optional[typing.Sequence[builtins.str]] = None,
                image_pull_credentials_type: typing.Optional[typing.Sequence[builtins.str]] = None,
                privileged_mode: typing.Optional[typing.Sequence[builtins.str]] = None,
                type: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Environment.

                :param compute_type: (experimental) compute-type property. Specify an array of string values to match this event if the actual value of compute-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param environment_variables: (experimental) environment-variables property. Specify an array of string values to match this event if the actual value of environment-variables is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param image: (experimental) image property. Specify an array of string values to match this event if the actual value of image is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param image_pull_credentials_type: (experimental) image-pull-credentials-type property. Specify an array of string values to match this event if the actual value of image-pull-credentials-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param privileged_mode: (experimental) privileged-mode property. Specify an array of string values to match this event if the actual value of privileged-mode is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param type: (experimental) type property. Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    environment = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Environment(
                        compute_type=["computeType"],
                        environment_variables=[codebuild_events.ProjectEvents.CodeBuildBuildStateChange.EnvironmentItem(
                            name=["name"],
                            type=["type"],
                            value=["value"]
                        )],
                        image=["image"],
                        image_pull_credentials_type=["imagePullCredentialsType"],
                        privileged_mode=["privilegedMode"],
                        type=["type"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__d9a7a3e59a3a9d0182c405e644501762c95f7e0b3d68602141b4415685150d1f)
                    check_type(argname="argument compute_type", value=compute_type, expected_type=type_hints["compute_type"])
                    check_type(argname="argument environment_variables", value=environment_variables, expected_type=type_hints["environment_variables"])
                    check_type(argname="argument image", value=image, expected_type=type_hints["image"])
                    check_type(argname="argument image_pull_credentials_type", value=image_pull_credentials_type, expected_type=type_hints["image_pull_credentials_type"])
                    check_type(argname="argument privileged_mode", value=privileged_mode, expected_type=type_hints["privileged_mode"])
                    check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if compute_type is not None:
                    self._values["compute_type"] = compute_type
                if environment_variables is not None:
                    self._values["environment_variables"] = environment_variables
                if image is not None:
                    self._values["image"] = image
                if image_pull_credentials_type is not None:
                    self._values["image_pull_credentials_type"] = image_pull_credentials_type
                if privileged_mode is not None:
                    self._values["privileged_mode"] = privileged_mode
                if type is not None:
                    self._values["type"] = type

            @builtins.property
            def compute_type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) compute-type property.

                Specify an array of string values to match this event if the actual value of compute-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("compute_type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def environment_variables(
                self,
            ) -> typing.Optional[typing.List["ProjectEvents.CodeBuildBuildStateChange.EnvironmentItem"]]:
                '''(experimental) environment-variables property.

                Specify an array of string values to match this event if the actual value of environment-variables is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("environment_variables")
                return typing.cast(typing.Optional[typing.List["ProjectEvents.CodeBuildBuildStateChange.EnvironmentItem"]], result)

            @builtins.property
            def image(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) image property.

                Specify an array of string values to match this event if the actual value of image is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("image")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def image_pull_credentials_type(
                self,
            ) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) image-pull-credentials-type property.

                Specify an array of string values to match this event if the actual value of image-pull-credentials-type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("image_pull_credentials_type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def privileged_mode(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) privileged-mode property.

                Specify an array of string values to match this event if the actual value of privileged-mode is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("privileged_mode")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) type property.

                Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Environment(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.EnvironmentItem",
            jsii_struct_bases=[],
            name_mapping={"name": "name", "type": "type", "value": "value"},
        )
        class EnvironmentItem:
            def __init__(
                self,
                *,
                name: typing.Optional[typing.Sequence[builtins.str]] = None,
                type: typing.Optional[typing.Sequence[builtins.str]] = None,
                value: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for EnvironmentItem.

                :param name: (experimental) name property. Specify an array of string values to match this event if the actual value of name is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param type: (experimental) type property. Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param value: (experimental) value property. Specify an array of string values to match this event if the actual value of value is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    environment_item = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.EnvironmentItem(
                        name=["name"],
                        type=["type"],
                        value=["value"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__e8ca5ce61a55477cd686d88af984e8012aad27eac29be39943eb937077a03b3a)
                    check_type(argname="argument name", value=name, expected_type=type_hints["name"])
                    check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                    check_type(argname="argument value", value=value, expected_type=type_hints["value"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if name is not None:
                    self._values["name"] = name
                if type is not None:
                    self._values["type"] = type
                if value is not None:
                    self._values["value"] = value

            @builtins.property
            def name(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) name property.

                Specify an array of string values to match this event if the actual value of name is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("name")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) type property.

                Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def value(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) value property.

                Specify an array of string values to match this event if the actual value of value is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("value")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "EnvironmentItem(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.Logs",
            jsii_struct_bases=[],
            name_mapping={
                "deep_link": "deepLink",
                "group_name": "groupName",
                "stream_name": "streamName",
            },
        )
        class Logs:
            def __init__(
                self,
                *,
                deep_link: typing.Optional[typing.Sequence[builtins.str]] = None,
                group_name: typing.Optional[typing.Sequence[builtins.str]] = None,
                stream_name: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Logs.

                :param deep_link: (experimental) deep-link property. Specify an array of string values to match this event if the actual value of deep-link is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param group_name: (experimental) group-name property. Specify an array of string values to match this event if the actual value of group-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param stream_name: (experimental) stream-name property. Specify an array of string values to match this event if the actual value of stream-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    logs = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Logs(
                        deep_link=["deepLink"],
                        group_name=["groupName"],
                        stream_name=["streamName"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__f2b98380917106d1e25035b3876a898f582d99440aebbe2ae8e31a9c8b2ffd90)
                    check_type(argname="argument deep_link", value=deep_link, expected_type=type_hints["deep_link"])
                    check_type(argname="argument group_name", value=group_name, expected_type=type_hints["group_name"])
                    check_type(argname="argument stream_name", value=stream_name, expected_type=type_hints["stream_name"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if deep_link is not None:
                    self._values["deep_link"] = deep_link
                if group_name is not None:
                    self._values["group_name"] = group_name
                if stream_name is not None:
                    self._values["stream_name"] = stream_name

            @builtins.property
            def deep_link(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) deep-link property.

                Specify an array of string values to match this event if the actual value of deep-link is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("deep_link")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def group_name(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) group-name property.

                Specify an array of string values to match this event if the actual value of group-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("group_name")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def stream_name(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) stream-name property.

                Specify an array of string values to match this event if the actual value of stream-name is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("stream_name")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Logs(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.NetworkInterface",
            jsii_struct_bases=[],
            name_mapping={"eni_id": "eniId", "subnet_id": "subnetId"},
        )
        class NetworkInterface:
            def __init__(
                self,
                *,
                eni_id: typing.Optional[typing.Sequence[builtins.str]] = None,
                subnet_id: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Network-interface.

                :param eni_id: (experimental) eni-id property. Specify an array of string values to match this event if the actual value of eni-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param subnet_id: (experimental) subnet-id property. Specify an array of string values to match this event if the actual value of subnet-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    network_interface = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.NetworkInterface(
                        eni_id=["eniId"],
                        subnet_id=["subnetId"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__1cbf229245e57dc3be76f03394e2e397a5a4d736300cca765e0e0d49c20117fe)
                    check_type(argname="argument eni_id", value=eni_id, expected_type=type_hints["eni_id"])
                    check_type(argname="argument subnet_id", value=subnet_id, expected_type=type_hints["subnet_id"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if eni_id is not None:
                    self._values["eni_id"] = eni_id
                if subnet_id is not None:
                    self._values["subnet_id"] = subnet_id

            @builtins.property
            def eni_id(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) eni-id property.

                Specify an array of string values to match this event if the actual value of eni-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("eni_id")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def subnet_id(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) subnet-id property.

                Specify an array of string values to match this event if the actual value of subnet-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("subnet_id")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "NetworkInterface(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.Source",
            jsii_struct_bases=[],
            name_mapping={
                "auth": "auth",
                "buildspec": "buildspec",
                "location": "location",
                "type": "type",
            },
        )
        class Source:
            def __init__(
                self,
                *,
                auth: typing.Optional[typing.Union["ProjectEvents.CodeBuildBuildStateChange.Auth", typing.Dict[builtins.str, typing.Any]]] = None,
                buildspec: typing.Optional[typing.Sequence[builtins.str]] = None,
                location: typing.Optional[typing.Sequence[builtins.str]] = None,
                type: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Source.

                :param auth: (experimental) auth property. Specify an array of string values to match this event if the actual value of auth is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param buildspec: (experimental) buildspec property. Specify an array of string values to match this event if the actual value of buildspec is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param location: (experimental) location property. Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param type: (experimental) type property. Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    source = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Source(
                        auth=codebuild_events.ProjectEvents.CodeBuildBuildStateChange.Auth(
                            resource=["resource"],
                            type=["type"]
                        ),
                        buildspec=["buildspec"],
                        location=["location"],
                        type=["type"]
                    )
                '''
                if isinstance(auth, dict):
                    auth = ProjectEvents.CodeBuildBuildStateChange.Auth(**auth)
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__54fd7619baff800de1819390ce75793500ad97c7d3b3c39ca9ccf61bbd5f2181)
                    check_type(argname="argument auth", value=auth, expected_type=type_hints["auth"])
                    check_type(argname="argument buildspec", value=buildspec, expected_type=type_hints["buildspec"])
                    check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                    check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if auth is not None:
                    self._values["auth"] = auth
                if buildspec is not None:
                    self._values["buildspec"] = buildspec
                if location is not None:
                    self._values["location"] = location
                if type is not None:
                    self._values["type"] = type

            @builtins.property
            def auth(
                self,
            ) -> typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Auth"]:
                '''(experimental) auth property.

                Specify an array of string values to match this event if the actual value of auth is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("auth")
                return typing.cast(typing.Optional["ProjectEvents.CodeBuildBuildStateChange.Auth"], result)

            @builtins.property
            def buildspec(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) buildspec property.

                Specify an array of string values to match this event if the actual value of buildspec is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("buildspec")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def location(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) location property.

                Specify an array of string values to match this event if the actual value of location is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("location")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def type(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) type property.

                Specify an array of string values to match this event if the actual value of type is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("type")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "Source(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.VpcConfig",
            jsii_struct_bases=[],
            name_mapping={
                "security_group_ids": "securityGroupIds",
                "subnets": "subnets",
                "vpc_id": "vpcId",
            },
        )
        class VpcConfig:
            def __init__(
                self,
                *,
                security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
                subnets: typing.Optional[typing.Sequence[typing.Union["ProjectEvents.CodeBuildBuildStateChange.VpcConfigItem", typing.Dict[builtins.str, typing.Any]]]] = None,
                vpc_id: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Vpc-config.

                :param security_group_ids: (experimental) security-group-ids property. Specify an array of string values to match this event if the actual value of security-group-ids is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param subnets: (experimental) subnets property. Specify an array of string values to match this event if the actual value of subnets is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param vpc_id: (experimental) vpc-id property. Specify an array of string values to match this event if the actual value of vpc-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    vpc_config = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.VpcConfig(
                        security_group_ids=["securityGroupIds"],
                        subnets=[codebuild_events.ProjectEvents.CodeBuildBuildStateChange.VpcConfigItem(
                            build_fleet_az=["buildFleetAz"],
                            customer_az=["customerAz"],
                            subnet_id=["subnetId"]
                        )],
                        vpc_id=["vpcId"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__9a9acc660327cfdc8a3b28c741c4a9f7be8bdde5db61a83b6d8d332c9e6dbab0)
                    check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
                    check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
                    check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if security_group_ids is not None:
                    self._values["security_group_ids"] = security_group_ids
                if subnets is not None:
                    self._values["subnets"] = subnets
                if vpc_id is not None:
                    self._values["vpc_id"] = vpc_id

            @builtins.property
            def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) security-group-ids property.

                Specify an array of string values to match this event if the actual value of security-group-ids is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("security_group_ids")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def subnets(
                self,
            ) -> typing.Optional[typing.List["ProjectEvents.CodeBuildBuildStateChange.VpcConfigItem"]]:
                '''(experimental) subnets property.

                Specify an array of string values to match this event if the actual value of subnets is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("subnets")
                return typing.cast(typing.Optional[typing.List["ProjectEvents.CodeBuildBuildStateChange.VpcConfigItem"]], result)

            @builtins.property
            def vpc_id(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) vpc-id property.

                Specify an array of string values to match this event if the actual value of vpc-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("vpc_id")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "VpcConfig(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )

        @jsii.data_type(
            jsii_type="@aws-cdk/mixins-preview.aws_codebuild.events.ProjectEvents.CodeBuildBuildStateChange.VpcConfigItem",
            jsii_struct_bases=[],
            name_mapping={
                "build_fleet_az": "buildFleetAz",
                "customer_az": "customerAz",
                "subnet_id": "subnetId",
            },
        )
        class VpcConfigItem:
            def __init__(
                self,
                *,
                build_fleet_az: typing.Optional[typing.Sequence[builtins.str]] = None,
                customer_az: typing.Optional[typing.Sequence[builtins.str]] = None,
                subnet_id: typing.Optional[typing.Sequence[builtins.str]] = None,
            ) -> None:
                '''(experimental) Type definition for Vpc-configItem.

                :param build_fleet_az: (experimental) build-fleet-az property. Specify an array of string values to match this event if the actual value of build-fleet-az is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param customer_az: (experimental) customer-az property. Specify an array of string values to match this event if the actual value of customer-az is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field
                :param subnet_id: (experimental) subnet-id property. Specify an array of string values to match this event if the actual value of subnet-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match`` for more advanced matching options. Default: - Do not filter on this field

                :stability: experimental
                :exampleMetadata: fixture=_generated

                Example::

                    # The code below shows an example of how to instantiate this type.
                    # The values are placeholders you should change.
                    from aws_cdk.mixins_preview.aws_codebuild import events as codebuild_events
                    
                    vpc_config_item = codebuild_events.ProjectEvents.CodeBuildBuildStateChange.VpcConfigItem(
                        build_fleet_az=["buildFleetAz"],
                        customer_az=["customerAz"],
                        subnet_id=["subnetId"]
                    )
                '''
                if __debug__:
                    type_hints = typing.get_type_hints(_typecheckingstub__2803432195ab033e61166bde8a9619c696a997cc118f7d0eb7b4738b2af0339b)
                    check_type(argname="argument build_fleet_az", value=build_fleet_az, expected_type=type_hints["build_fleet_az"])
                    check_type(argname="argument customer_az", value=customer_az, expected_type=type_hints["customer_az"])
                    check_type(argname="argument subnet_id", value=subnet_id, expected_type=type_hints["subnet_id"])
                self._values: typing.Dict[builtins.str, typing.Any] = {}
                if build_fleet_az is not None:
                    self._values["build_fleet_az"] = build_fleet_az
                if customer_az is not None:
                    self._values["customer_az"] = customer_az
                if subnet_id is not None:
                    self._values["subnet_id"] = subnet_id

            @builtins.property
            def build_fleet_az(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) build-fleet-az property.

                Specify an array of string values to match this event if the actual value of build-fleet-az is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("build_fleet_az")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def customer_az(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) customer-az property.

                Specify an array of string values to match this event if the actual value of customer-az is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("customer_az")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            @builtins.property
            def subnet_id(self) -> typing.Optional[typing.List[builtins.str]]:
                '''(experimental) subnet-id property.

                Specify an array of string values to match this event if the actual value of subnet-id is one of the values in the array. Use one of the constructors on the ``aws_events.Match``  for more advanced matching options.

                :default: - Do not filter on this field

                :stability: experimental
                '''
                result = self._values.get("subnet_id")
                return typing.cast(typing.Optional[typing.List[builtins.str]], result)

            def __eq__(self, rhs: typing.Any) -> builtins.bool:
                return isinstance(rhs, self.__class__) and rhs._values == self._values

            def __ne__(self, rhs: typing.Any) -> builtins.bool:
                return not (rhs == self)

            def __repr__(self) -> str:
                return "VpcConfigItem(%s)" % ", ".join(
                    k + "=" + repr(v) for k, v in self._values.items()
                )


__all__ = [
    "ProjectEvents",
]

publication.publish()

def _typecheckingstub__db4d32fb7791ee1d99407b942179cc160a485c3efe1a1bf3d6c836e1b2638ff0(
    project_ref: _aws_cdk_interfaces_aws_codebuild_ceddda9d.IProjectRef,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ecb5a299d9616eeef3b9eaa22dd2371a32362c2e6e50306f5e97f7fcdb88b4a(
    *,
    artifact: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.Artifact, typing.Dict[builtins.str, typing.Any]]] = None,
    build_complete: typing.Optional[typing.Sequence[builtins.str]] = None,
    build_start_time: typing.Optional[typing.Sequence[builtins.str]] = None,
    cache: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.Cache, typing.Dict[builtins.str, typing.Any]]] = None,
    environment: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    initiator: typing.Optional[typing.Sequence[builtins.str]] = None,
    logs: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.Logs, typing.Dict[builtins.str, typing.Any]]] = None,
    network_interface: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.NetworkInterface, typing.Dict[builtins.str, typing.Any]]] = None,
    phases: typing.Optional[typing.Sequence[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformationItem, typing.Dict[builtins.str, typing.Any]]]] = None,
    queued_timeout_in_minutes: typing.Optional[typing.Sequence[builtins.str]] = None,
    source: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.Source, typing.Dict[builtins.str, typing.Any]]] = None,
    source_version: typing.Optional[typing.Sequence[builtins.str]] = None,
    timeout_in_minutes: typing.Optional[typing.Sequence[builtins.str]] = None,
    vpc_config: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.VpcConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aad1456ad482bb9be39804b8132265a949e6d7e70e7ee21f5300ccc7b226b12d(
    *,
    duration_in_seconds: typing.Optional[typing.Sequence[builtins.str]] = None,
    end_time: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase_context: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase_status: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase_type: typing.Optional[typing.Sequence[builtins.str]] = None,
    start_time: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a75e9dc66baf399a9bdaddc2af06109add940240a5399d6c6d62b1f67896dc6(
    *,
    location: typing.Optional[typing.Sequence[builtins.str]] = None,
    md5_sum: typing.Optional[typing.Sequence[builtins.str]] = None,
    sha256_sum: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9a5872c8a44faf787b2548fa103e5c095bdd09ae0ef8eec3afd8177a1c2814b(
    *,
    type: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edd011b0f74f6d1c9f068235c602a94953a0cd0b7737d75ac9cfd4565b239746(
    *,
    location: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0be4c0166f5a8e7480cc14c31731d7e3f8bac9b5c3bd5c27f58af645417e9ec5(
    *,
    additional_information: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.AdditionalInformation, typing.Dict[builtins.str, typing.Any]]] = None,
    build_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    completed_phase: typing.Optional[typing.Sequence[builtins.str]] = None,
    completed_phase_context: typing.Optional[typing.Sequence[builtins.str]] = None,
    completed_phase_duration_seconds: typing.Optional[typing.Sequence[builtins.str]] = None,
    completed_phase_end: typing.Optional[typing.Sequence[builtins.str]] = None,
    completed_phase_start: typing.Optional[typing.Sequence[builtins.str]] = None,
    completed_phase_status: typing.Optional[typing.Sequence[builtins.str]] = None,
    event_metadata: typing.Optional[typing.Union[_aws_cdk_ceddda9d.AWSEventMetadataProps, typing.Dict[builtins.str, typing.Any]]] = None,
    project_name: typing.Optional[typing.Sequence[builtins.str]] = None,
    version: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__661f7b330060a5f5491c6b18da12b16b74199b20c59c8309b8f1a7fc023fa0eb(
    *,
    compute_type: typing.Optional[typing.Sequence[builtins.str]] = None,
    environment_variables: typing.Optional[typing.Sequence[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.EnvironmentItem, typing.Dict[builtins.str, typing.Any]]]] = None,
    image: typing.Optional[typing.Sequence[builtins.str]] = None,
    image_pull_credentials_type: typing.Optional[typing.Sequence[builtins.str]] = None,
    privileged_mode: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4affad4f0be42ee8abd9903e532782b6b6d15e11aea3f8c4700ba7267b41ca84(
    *,
    name: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[typing.Sequence[builtins.str]] = None,
    value: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__427a5300004c5dd1bc08d0af2ab5a4639ac3bf31b7aaa5a67395d9f2e6cc4e09(
    *,
    deep_link: typing.Optional[typing.Sequence[builtins.str]] = None,
    group_name: typing.Optional[typing.Sequence[builtins.str]] = None,
    stream_name: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec7f1a0d9c52c67921ca04d0ec0848af5174afc13ae9a201f3cb24e00634e4c7(
    *,
    eni_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnet_id: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdfc0f08296e1346494b513fdd0ba3d8c688ec94319ba51132ce9e718efddec2(
    *,
    auth: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.Auth, typing.Dict[builtins.str, typing.Any]]] = None,
    buildspec: typing.Optional[typing.Sequence[builtins.str]] = None,
    location: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f387b20e7fea012a85a28d32ecb34e1305da44355482f38fc5ae589b5741035(
    *,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnets: typing.Optional[typing.Sequence[typing.Union[ProjectEvents.CodeBuildBuildPhaseChange.VpcConfigItem, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpc_id: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5f261f587d90625d84cad373e5267184cc6ac47a8ede001352e7864756712ba(
    *,
    build_fleet_az: typing.Optional[typing.Sequence[builtins.str]] = None,
    customer_az: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnet_id: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea31abe53a3a6d671652c648f9b0f506466da591288b846bf94f2e82b6301f36(
    *,
    artifact: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildStateChange.Artifact, typing.Dict[builtins.str, typing.Any]]] = None,
    build_complete: typing.Optional[typing.Sequence[builtins.str]] = None,
    build_start_time: typing.Optional[typing.Sequence[builtins.str]] = None,
    cache: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildStateChange.Cache, typing.Dict[builtins.str, typing.Any]]] = None,
    environment: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildStateChange.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    initiator: typing.Optional[typing.Sequence[builtins.str]] = None,
    logs: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildStateChange.Logs, typing.Dict[builtins.str, typing.Any]]] = None,
    network_interface: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildStateChange.NetworkInterface, typing.Dict[builtins.str, typing.Any]]] = None,
    phases: typing.Optional[typing.Sequence[typing.Union[ProjectEvents.CodeBuildBuildStateChange.AdditionalInformationItem, typing.Dict[builtins.str, typing.Any]]]] = None,
    queued_timeout_in_minutes: typing.Optional[typing.Sequence[builtins.str]] = None,
    source: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildStateChange.Source, typing.Dict[builtins.str, typing.Any]]] = None,
    source_version: typing.Optional[typing.Sequence[builtins.str]] = None,
    timeout_in_minutes: typing.Optional[typing.Sequence[builtins.str]] = None,
    vpc_config: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildStateChange.VpcConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c24187fccd4878b05d791132a7a8beda27a0ab227d5110f7fbb187b85c3dbb6(
    *,
    duration_in_seconds: typing.Optional[typing.Sequence[builtins.str]] = None,
    end_time: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase_context: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase_status: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase_type: typing.Optional[typing.Sequence[builtins.str]] = None,
    start_time: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46ef149d6a08f0b5ad7ff9610e288b2825d957b6a93b38981180b46b16339a4e(
    *,
    location: typing.Optional[typing.Sequence[builtins.str]] = None,
    md5_sum: typing.Optional[typing.Sequence[builtins.str]] = None,
    sha256_sum: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca1a3b1db63fd08cd6deeb6743fcdfa5bd0b306601c0b30ba97f4ba25e2631ea(
    *,
    resource: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28d13ce9e3be3f458ec5c805da74cb9145da217b709929d5da37bccff982d5fd(
    *,
    location: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__247f87e2ef8ff9c682d2d3e8d9f448f4bd5a6bf4b27696ad5c4184325e8e39be(
    *,
    additional_information: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildStateChange.AdditionalInformation, typing.Dict[builtins.str, typing.Any]]] = None,
    build_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    build_status: typing.Optional[typing.Sequence[builtins.str]] = None,
    current_phase: typing.Optional[typing.Sequence[builtins.str]] = None,
    current_phase_context: typing.Optional[typing.Sequence[builtins.str]] = None,
    event_metadata: typing.Optional[typing.Union[_aws_cdk_ceddda9d.AWSEventMetadataProps, typing.Dict[builtins.str, typing.Any]]] = None,
    project_name: typing.Optional[typing.Sequence[builtins.str]] = None,
    version: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9a7a3e59a3a9d0182c405e644501762c95f7e0b3d68602141b4415685150d1f(
    *,
    compute_type: typing.Optional[typing.Sequence[builtins.str]] = None,
    environment_variables: typing.Optional[typing.Sequence[typing.Union[ProjectEvents.CodeBuildBuildStateChange.EnvironmentItem, typing.Dict[builtins.str, typing.Any]]]] = None,
    image: typing.Optional[typing.Sequence[builtins.str]] = None,
    image_pull_credentials_type: typing.Optional[typing.Sequence[builtins.str]] = None,
    privileged_mode: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8ca5ce61a55477cd686d88af984e8012aad27eac29be39943eb937077a03b3a(
    *,
    name: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[typing.Sequence[builtins.str]] = None,
    value: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2b98380917106d1e25035b3876a898f582d99440aebbe2ae8e31a9c8b2ffd90(
    *,
    deep_link: typing.Optional[typing.Sequence[builtins.str]] = None,
    group_name: typing.Optional[typing.Sequence[builtins.str]] = None,
    stream_name: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cbf229245e57dc3be76f03394e2e397a5a4d736300cca765e0e0d49c20117fe(
    *,
    eni_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnet_id: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54fd7619baff800de1819390ce75793500ad97c7d3b3c39ca9ccf61bbd5f2181(
    *,
    auth: typing.Optional[typing.Union[ProjectEvents.CodeBuildBuildStateChange.Auth, typing.Dict[builtins.str, typing.Any]]] = None,
    buildspec: typing.Optional[typing.Sequence[builtins.str]] = None,
    location: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a9acc660327cfdc8a3b28c741c4a9f7be8bdde5db61a83b6d8d332c9e6dbab0(
    *,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnets: typing.Optional[typing.Sequence[typing.Union[ProjectEvents.CodeBuildBuildStateChange.VpcConfigItem, typing.Dict[builtins.str, typing.Any]]]] = None,
    vpc_id: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2803432195ab033e61166bde8a9619c696a997cc118f7d0eb7b4738b2af0339b(
    *,
    build_fleet_az: typing.Optional[typing.Sequence[builtins.str]] = None,
    customer_az: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnet_id: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
