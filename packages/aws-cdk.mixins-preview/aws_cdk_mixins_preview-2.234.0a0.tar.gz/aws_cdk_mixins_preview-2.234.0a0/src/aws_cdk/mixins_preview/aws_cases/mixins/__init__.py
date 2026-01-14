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
import constructs as _constructs_77d1e7e8
from ...core import IMixin as _IMixin_11e4b965, Mixin as _Mixin_a69446c0
from ...mixins import (
    CfnPropertyMixinOptions as _CfnPropertyMixinOptions_9cbff649,
    PropertyMergeStrategy as _PropertyMergeStrategy_49c157e8,
)


@jsii.data_type(
    jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnCaseRuleMixinProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "domain_id": "domainId",
        "name": "name",
        "rule": "rule",
        "tags": "tags",
    },
)
class CfnCaseRuleMixinProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        domain_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        rule: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnCaseRulePropsMixin.CaseRuleDetailsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["_aws_cdk_ceddda9d.CfnTag", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for CfnCaseRulePropsMixin.

        :param description: Description of a case rule.
        :param domain_id: Unique identifier of a Cases domain.
        :param name: Name of the case rule.
        :param rule: Represents what rule type should take place, under what conditions.
        :param tags: An array of key-value pairs to apply to this resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-caserule.html
        :exampleMetadata: fixture=_generated

        Example::

            from aws_cdk import CfnTag
            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
            
            # empty_value: Any
            
            cfn_case_rule_mixin_props = cases_mixins.CfnCaseRuleMixinProps(
                description="description",
                domain_id="domainId",
                name="name",
                rule=cases_mixins.CfnCaseRulePropsMixin.CaseRuleDetailsProperty(
                    hidden=cases_mixins.CfnCaseRulePropsMixin.HiddenCaseRuleProperty(
                        conditions=[cases_mixins.CfnCaseRulePropsMixin.BooleanConditionProperty(
                            equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                                operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                    field_id="fieldId"
                                ),
                                operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                    boolean_value=False,
                                    double_value=123,
                                    empty_value=empty_value,
                                    string_value="stringValue"
                                ),
                                result=False
                            ),
                            not_equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                                operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                    field_id="fieldId"
                                ),
                                operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                    boolean_value=False,
                                    double_value=123,
                                    empty_value=empty_value,
                                    string_value="stringValue"
                                ),
                                result=False
                            )
                        )],
                        default_value=False
                    ),
                    required=cases_mixins.CfnCaseRulePropsMixin.RequiredCaseRuleProperty(
                        conditions=[cases_mixins.CfnCaseRulePropsMixin.BooleanConditionProperty(
                            equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                                operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                    field_id="fieldId"
                                ),
                                operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                    boolean_value=False,
                                    double_value=123,
                                    empty_value=empty_value,
                                    string_value="stringValue"
                                ),
                                result=False
                            ),
                            not_equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                                operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                    field_id="fieldId"
                                ),
                                operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                    boolean_value=False,
                                    double_value=123,
                                    empty_value=empty_value,
                                    string_value="stringValue"
                                ),
                                result=False
                            )
                        )],
                        default_value=False
                    )
                ),
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cdb9e56fe45438927dc663e67a2af5c6f774a9c75ece463d6bc817c3333525d)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument domain_id", value=domain_id, expected_type=type_hints["domain_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument rule", value=rule, expected_type=type_hints["rule"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if domain_id is not None:
            self._values["domain_id"] = domain_id
        if name is not None:
            self._values["name"] = name
        if rule is not None:
            self._values["rule"] = rule
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of a case rule.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-caserule.html#cfn-cases-caserule-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_id(self) -> typing.Optional[builtins.str]:
        '''Unique identifier of a Cases domain.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-caserule.html#cfn-cases-caserule-domainid
        '''
        result = self._values.get("domain_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the case rule.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-caserule.html#cfn-cases-caserule-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rule(
        self,
    ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.CaseRuleDetailsProperty"]]:
        '''Represents what rule type should take place, under what conditions.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-caserule.html#cfn-cases-caserule-rule
        '''
        result = self._values.get("rule")
        return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.CaseRuleDetailsProperty"]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List["_aws_cdk_ceddda9d.CfnTag"]]:
        '''An array of key-value pairs to apply to this resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-caserule.html#cfn-cases-caserule-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List["_aws_cdk_ceddda9d.CfnTag"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCaseRuleMixinProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IMixin_11e4b965)
class CfnCaseRulePropsMixin(
    _Mixin_a69446c0,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnCaseRulePropsMixin",
):
    '''Creates a new case rule.

    In the Amazon Connect admin website, case rules are known as *case field conditions* . For more information about case field conditions, see `Add case field conditions to a case template <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ .

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-caserule.html
    :cloudformationResource: AWS::Cases::CaseRule
    :mixin: true
    :exampleMetadata: fixture=_generated

    Example::

        from aws_cdk import CfnTag
        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk.mixins_preview import mixins
        from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
        
        # empty_value: Any
        
        cfn_case_rule_props_mixin = cases_mixins.CfnCaseRulePropsMixin(cases_mixins.CfnCaseRuleMixinProps(
            description="description",
            domain_id="domainId",
            name="name",
            rule=cases_mixins.CfnCaseRulePropsMixin.CaseRuleDetailsProperty(
                hidden=cases_mixins.CfnCaseRulePropsMixin.HiddenCaseRuleProperty(
                    conditions=[cases_mixins.CfnCaseRulePropsMixin.BooleanConditionProperty(
                        equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                            operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                field_id="fieldId"
                            ),
                            operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                boolean_value=False,
                                double_value=123,
                                empty_value=empty_value,
                                string_value="stringValue"
                            ),
                            result=False
                        ),
                        not_equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                            operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                field_id="fieldId"
                            ),
                            operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                boolean_value=False,
                                double_value=123,
                                empty_value=empty_value,
                                string_value="stringValue"
                            ),
                            result=False
                        )
                    )],
                    default_value=False
                ),
                required=cases_mixins.CfnCaseRulePropsMixin.RequiredCaseRuleProperty(
                    conditions=[cases_mixins.CfnCaseRulePropsMixin.BooleanConditionProperty(
                        equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                            operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                field_id="fieldId"
                            ),
                            operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                boolean_value=False,
                                double_value=123,
                                empty_value=empty_value,
                                string_value="stringValue"
                            ),
                            result=False
                        ),
                        not_equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                            operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                field_id="fieldId"
                            ),
                            operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                boolean_value=False,
                                double_value=123,
                                empty_value=empty_value,
                                string_value="stringValue"
                            ),
                            result=False
                        )
                    )],
                    default_value=False
                )
            ),
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        ),
            strategy=mixins.PropertyMergeStrategy.OVERRIDE
        )
    '''

    def __init__(
        self,
        props: typing.Union["CfnCaseRuleMixinProps", typing.Dict[builtins.str, typing.Any]],
        *,
        strategy: typing.Optional["_PropertyMergeStrategy_49c157e8"] = None,
    ) -> None:
        '''Create a mixin to apply properties to ``AWS::Cases::CaseRule``.

        :param props: L1 properties to apply.
        :param strategy: (experimental) Strategy for merging nested properties. Default: - PropertyMergeStrategy.MERGE
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25e9fb0da31a933f2de5298f74d7baa511041ca1a071ec66ae08e2af618be95d)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        options = _CfnPropertyMixinOptions_9cbff649(strategy=strategy)

        jsii.create(self.__class__, self, [props, options])

    @jsii.member(jsii_name="applyTo")
    def apply_to(
        self,
        construct: "_constructs_77d1e7e8.IConstruct",
    ) -> "_constructs_77d1e7e8.IConstruct":
        '''Apply the mixin properties to the construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c27a52a301511321043a24392cbaee63fc9b55f6a2633568b7ea5618bbd462fb)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast("_constructs_77d1e7e8.IConstruct", jsii.invoke(self, "applyTo", [construct]))

    @jsii.member(jsii_name="supports")
    def supports(self, construct: "_constructs_77d1e7e8.IConstruct") -> builtins.bool:
        '''Check if this mixin supports the given construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2cac2b7ad2d9db325b33cb264607deebcce8b793ef296d4e876f577a886dd40)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(builtins.bool, jsii.invoke(self, "supports", [construct]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_PROPERTY_KEYS")
    def CFN_PROPERTY_KEYS(cls) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.sget(cls, "CFN_PROPERTY_KEYS"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def _props(self) -> "CfnCaseRuleMixinProps":
        return typing.cast("CfnCaseRuleMixinProps", jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def _strategy(self) -> "_PropertyMergeStrategy_49c157e8":
        return typing.cast("_PropertyMergeStrategy_49c157e8", jsii.get(self, "strategy"))

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnCaseRulePropsMixin.BooleanConditionProperty",
        jsii_struct_bases=[],
        name_mapping={"equal_to": "equalTo", "not_equal_to": "notEqualTo"},
    )
    class BooleanConditionProperty:
        def __init__(
            self,
            *,
            equal_to: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnCaseRulePropsMixin.BooleanOperandsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            not_equal_to: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnCaseRulePropsMixin.BooleanOperandsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''Boolean condition for a rule.

            In the Amazon Connect admin website, case rules are known as *case field conditions* . For more information about case field conditions, see `Add case field conditions to a case template <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ .

            :param equal_to: Tests that operandOne is equal to operandTwo.
            :param not_equal_to: Tests that operandOne is not equal to operandTwo.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-booleancondition.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                # empty_value: Any
                
                boolean_condition_property = cases_mixins.CfnCaseRulePropsMixin.BooleanConditionProperty(
                    equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                        operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                            field_id="fieldId"
                        ),
                        operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                            boolean_value=False,
                            double_value=123,
                            empty_value=empty_value,
                            string_value="stringValue"
                        ),
                        result=False
                    ),
                    not_equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                        operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                            field_id="fieldId"
                        ),
                        operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                            boolean_value=False,
                            double_value=123,
                            empty_value=empty_value,
                            string_value="stringValue"
                        ),
                        result=False
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__05c32b941460f3eefc8d4e4a58993a3f4387fa0cd80eac0e9d72a3a1c434bf4c)
                check_type(argname="argument equal_to", value=equal_to, expected_type=type_hints["equal_to"])
                check_type(argname="argument not_equal_to", value=not_equal_to, expected_type=type_hints["not_equal_to"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if equal_to is not None:
                self._values["equal_to"] = equal_to
            if not_equal_to is not None:
                self._values["not_equal_to"] = not_equal_to

        @builtins.property
        def equal_to(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.BooleanOperandsProperty"]]:
            '''Tests that operandOne is equal to operandTwo.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-booleancondition.html#cfn-cases-caserule-booleancondition-equalto
            '''
            result = self._values.get("equal_to")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.BooleanOperandsProperty"]], result)

        @builtins.property
        def not_equal_to(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.BooleanOperandsProperty"]]:
            '''Tests that operandOne is not equal to operandTwo.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-booleancondition.html#cfn-cases-caserule-booleancondition-notequalto
            '''
            result = self._values.get("not_equal_to")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.BooleanOperandsProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BooleanConditionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "operand_one": "operandOne",
            "operand_two": "operandTwo",
            "result": "result",
        },
    )
    class BooleanOperandsProperty:
        def __init__(
            self,
            *,
            operand_one: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnCaseRulePropsMixin.OperandOneProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            operand_two: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnCaseRulePropsMixin.OperandTwoProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            result: typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]] = None,
        ) -> None:
            '''Boolean operands for a condition.

            In the Amazon Connect admin website, case rules are known as *case field conditions* . For more information about case field conditions, see `Add case field conditions to a case template <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ .

            :param operand_one: Represents the left hand operand in the condition.
            :param operand_two: Represents the right hand operand in the condition.
            :param result: The value of the outer rule if the condition evaluates to true.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-booleanoperands.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                # empty_value: Any
                
                boolean_operands_property = cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                    operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                        field_id="fieldId"
                    ),
                    operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                        boolean_value=False,
                        double_value=123,
                        empty_value=empty_value,
                        string_value="stringValue"
                    ),
                    result=False
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__2a2608a5095da0024b04268724b1573d49106807886f82060df90a9174da139e)
                check_type(argname="argument operand_one", value=operand_one, expected_type=type_hints["operand_one"])
                check_type(argname="argument operand_two", value=operand_two, expected_type=type_hints["operand_two"])
                check_type(argname="argument result", value=result, expected_type=type_hints["result"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if operand_one is not None:
                self._values["operand_one"] = operand_one
            if operand_two is not None:
                self._values["operand_two"] = operand_two
            if result is not None:
                self._values["result"] = result

        @builtins.property
        def operand_one(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.OperandOneProperty"]]:
            '''Represents the left hand operand in the condition.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-booleanoperands.html#cfn-cases-caserule-booleanoperands-operandone
            '''
            result = self._values.get("operand_one")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.OperandOneProperty"]], result)

        @builtins.property
        def operand_two(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.OperandTwoProperty"]]:
            '''Represents the right hand operand in the condition.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-booleanoperands.html#cfn-cases-caserule-booleanoperands-operandtwo
            '''
            result = self._values.get("operand_two")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.OperandTwoProperty"]], result)

        @builtins.property
        def result(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]]:
            '''The value of the outer rule if the condition evaluates to true.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-booleanoperands.html#cfn-cases-caserule-booleanoperands-result
            '''
            result = self._values.get("result")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BooleanOperandsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnCaseRulePropsMixin.CaseRuleDetailsProperty",
        jsii_struct_bases=[],
        name_mapping={"hidden": "hidden", "required": "required"},
    )
    class CaseRuleDetailsProperty:
        def __init__(
            self,
            *,
            hidden: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnCaseRulePropsMixin.HiddenCaseRuleProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            required: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnCaseRulePropsMixin.RequiredCaseRuleProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''Represents what rule type should take place, under what conditions.

            In the Amazon Connect admin website, case rules are known as *case field conditions* . For more information about case field conditions, see `Add case field conditions to a case template <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ .

            :param hidden: Whether a field is visible, based on values in other fields.
            :param required: Required rule type, used to indicate whether a field is required.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-caseruledetails.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                # empty_value: Any
                
                case_rule_details_property = cases_mixins.CfnCaseRulePropsMixin.CaseRuleDetailsProperty(
                    hidden=cases_mixins.CfnCaseRulePropsMixin.HiddenCaseRuleProperty(
                        conditions=[cases_mixins.CfnCaseRulePropsMixin.BooleanConditionProperty(
                            equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                                operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                    field_id="fieldId"
                                ),
                                operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                    boolean_value=False,
                                    double_value=123,
                                    empty_value=empty_value,
                                    string_value="stringValue"
                                ),
                                result=False
                            ),
                            not_equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                                operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                    field_id="fieldId"
                                ),
                                operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                    boolean_value=False,
                                    double_value=123,
                                    empty_value=empty_value,
                                    string_value="stringValue"
                                ),
                                result=False
                            )
                        )],
                        default_value=False
                    ),
                    required=cases_mixins.CfnCaseRulePropsMixin.RequiredCaseRuleProperty(
                        conditions=[cases_mixins.CfnCaseRulePropsMixin.BooleanConditionProperty(
                            equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                                operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                    field_id="fieldId"
                                ),
                                operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                    boolean_value=False,
                                    double_value=123,
                                    empty_value=empty_value,
                                    string_value="stringValue"
                                ),
                                result=False
                            ),
                            not_equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                                operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                    field_id="fieldId"
                                ),
                                operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                    boolean_value=False,
                                    double_value=123,
                                    empty_value=empty_value,
                                    string_value="stringValue"
                                ),
                                result=False
                            )
                        )],
                        default_value=False
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__a6a60a35ed4bb50f762dc39354a5b2eeb9e178a528bc07a55f2d89b83392295b)
                check_type(argname="argument hidden", value=hidden, expected_type=type_hints["hidden"])
                check_type(argname="argument required", value=required, expected_type=type_hints["required"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if hidden is not None:
                self._values["hidden"] = hidden
            if required is not None:
                self._values["required"] = required

        @builtins.property
        def hidden(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.HiddenCaseRuleProperty"]]:
            '''Whether a field is visible, based on values in other fields.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-caseruledetails.html#cfn-cases-caserule-caseruledetails-hidden
            '''
            result = self._values.get("hidden")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.HiddenCaseRuleProperty"]], result)

        @builtins.property
        def required(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.RequiredCaseRuleProperty"]]:
            '''Required rule type, used to indicate whether a field is required.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-caseruledetails.html#cfn-cases-caserule-caseruledetails-required
            '''
            result = self._values.get("required")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.RequiredCaseRuleProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CaseRuleDetailsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnCaseRulePropsMixin.HiddenCaseRuleProperty",
        jsii_struct_bases=[],
        name_mapping={"conditions": "conditions", "default_value": "defaultValue"},
    )
    class HiddenCaseRuleProperty:
        def __init__(
            self,
            *,
            conditions: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Sequence[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnCaseRulePropsMixin.BooleanConditionProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
            default_value: typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]] = None,
        ) -> None:
            '''A rule that controls field visibility based on conditions.

            Fields can be shown or hidden dynamically based on values in other fields.

            :param conditions: A list of conditions that determine field visibility.
            :param default_value: Whether the field is hidden when no conditions match.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-hiddencaserule.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                # empty_value: Any
                
                hidden_case_rule_property = cases_mixins.CfnCaseRulePropsMixin.HiddenCaseRuleProperty(
                    conditions=[cases_mixins.CfnCaseRulePropsMixin.BooleanConditionProperty(
                        equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                            operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                field_id="fieldId"
                            ),
                            operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                boolean_value=False,
                                double_value=123,
                                empty_value=empty_value,
                                string_value="stringValue"
                            ),
                            result=False
                        ),
                        not_equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                            operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                field_id="fieldId"
                            ),
                            operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                boolean_value=False,
                                double_value=123,
                                empty_value=empty_value,
                                string_value="stringValue"
                            ),
                            result=False
                        )
                    )],
                    default_value=False
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__d324d5b44428687762657b1184ee223050c88f39c4bb3303bf21cf3025ea64e7)
                check_type(argname="argument conditions", value=conditions, expected_type=type_hints["conditions"])
                check_type(argname="argument default_value", value=default_value, expected_type=type_hints["default_value"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if conditions is not None:
                self._values["conditions"] = conditions
            if default_value is not None:
                self._values["default_value"] = default_value

        @builtins.property
        def conditions(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.BooleanConditionProperty"]]]]:
            '''A list of conditions that determine field visibility.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-hiddencaserule.html#cfn-cases-caserule-hiddencaserule-conditions
            '''
            result = self._values.get("conditions")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.BooleanConditionProperty"]]]], result)

        @builtins.property
        def default_value(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]]:
            '''Whether the field is hidden when no conditions match.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-hiddencaserule.html#cfn-cases-caserule-hiddencaserule-defaultvalue
            '''
            result = self._values.get("default_value")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HiddenCaseRuleProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnCaseRulePropsMixin.OperandOneProperty",
        jsii_struct_bases=[],
        name_mapping={"field_id": "fieldId"},
    )
    class OperandOneProperty:
        def __init__(self, *, field_id: typing.Optional[builtins.str] = None) -> None:
            '''Represents the left hand operand in the condition.

            In the Amazon Connect admin website, case rules are known as *case field conditions* . For more information about case field conditions, see `Add case field conditions to a case template <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ .

            :param field_id: The field ID that this operand should take the value of.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-operandone.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                operand_one_property = cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                    field_id="fieldId"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__1ceea2c438a1ec9bde8b7eefb4c83868fc6d6c6196a3037ea8b783dafb52e369)
                check_type(argname="argument field_id", value=field_id, expected_type=type_hints["field_id"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if field_id is not None:
                self._values["field_id"] = field_id

        @builtins.property
        def field_id(self) -> typing.Optional[builtins.str]:
            '''The field ID that this operand should take the value of.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-operandone.html#cfn-cases-caserule-operandone-fieldid
            '''
            result = self._values.get("field_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OperandOneProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnCaseRulePropsMixin.OperandTwoProperty",
        jsii_struct_bases=[],
        name_mapping={
            "boolean_value": "booleanValue",
            "double_value": "doubleValue",
            "empty_value": "emptyValue",
            "string_value": "stringValue",
        },
    )
    class OperandTwoProperty:
        def __init__(
            self,
            *,
            boolean_value: typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]] = None,
            double_value: typing.Optional[jsii.Number] = None,
            empty_value: typing.Any = None,
            string_value: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Represents the right hand operand in the condition.

            In the Amazon Connect admin website, case rules are known as *case field conditions* . For more information about case field conditions, see `Add case field conditions to a case template <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ .

            :param boolean_value: Boolean value type.
            :param double_value: Double value type.
            :param empty_value: Represents an empty operand value. In the Amazon Connect admin website, case rules are known as *case field conditions* . For more information about case field conditions, see `Add case field conditions to a case template <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ .
            :param string_value: String value type.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-operandtwo.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                # empty_value: Any
                
                operand_two_property = cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                    boolean_value=False,
                    double_value=123,
                    empty_value=empty_value,
                    string_value="stringValue"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__37e6113170581cfb1c8aacd5dd8105fe481902c40d708eba14ccbe4f7bfe3d61)
                check_type(argname="argument boolean_value", value=boolean_value, expected_type=type_hints["boolean_value"])
                check_type(argname="argument double_value", value=double_value, expected_type=type_hints["double_value"])
                check_type(argname="argument empty_value", value=empty_value, expected_type=type_hints["empty_value"])
                check_type(argname="argument string_value", value=string_value, expected_type=type_hints["string_value"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if boolean_value is not None:
                self._values["boolean_value"] = boolean_value
            if double_value is not None:
                self._values["double_value"] = double_value
            if empty_value is not None:
                self._values["empty_value"] = empty_value
            if string_value is not None:
                self._values["string_value"] = string_value

        @builtins.property
        def boolean_value(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]]:
            '''Boolean value type.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-operandtwo.html#cfn-cases-caserule-operandtwo-booleanvalue
            '''
            result = self._values.get("boolean_value")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]], result)

        @builtins.property
        def double_value(self) -> typing.Optional[jsii.Number]:
            '''Double value type.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-operandtwo.html#cfn-cases-caserule-operandtwo-doublevalue
            '''
            result = self._values.get("double_value")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def empty_value(self) -> typing.Any:
            '''Represents an empty operand value.

            In the Amazon Connect admin website, case rules are known as *case field conditions* . For more information about case field conditions, see `Add case field conditions to a case template <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ .

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-operandtwo.html#cfn-cases-caserule-operandtwo-emptyvalue
            '''
            result = self._values.get("empty_value")
            return typing.cast(typing.Any, result)

        @builtins.property
        def string_value(self) -> typing.Optional[builtins.str]:
            '''String value type.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-operandtwo.html#cfn-cases-caserule-operandtwo-stringvalue
            '''
            result = self._values.get("string_value")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OperandTwoProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnCaseRulePropsMixin.RequiredCaseRuleProperty",
        jsii_struct_bases=[],
        name_mapping={"conditions": "conditions", "default_value": "defaultValue"},
    )
    class RequiredCaseRuleProperty:
        def __init__(
            self,
            *,
            conditions: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Sequence[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnCaseRulePropsMixin.BooleanConditionProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
            default_value: typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]] = None,
        ) -> None:
            '''Required rule type, used to indicate whether a field is required.

            In the Amazon Connect admin website, case rules are known as *case field conditions* . For more information about case field conditions, see `Add case field conditions to a case template <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ .

            :param conditions: List of conditions for the required rule; the first condition to evaluate to true dictates the value of the rule.
            :param default_value: The value of the rule (that is, whether the field is required) should none of the conditions evaluate to true.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-requiredcaserule.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                # empty_value: Any
                
                required_case_rule_property = cases_mixins.CfnCaseRulePropsMixin.RequiredCaseRuleProperty(
                    conditions=[cases_mixins.CfnCaseRulePropsMixin.BooleanConditionProperty(
                        equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                            operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                field_id="fieldId"
                            ),
                            operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                boolean_value=False,
                                double_value=123,
                                empty_value=empty_value,
                                string_value="stringValue"
                            ),
                            result=False
                        ),
                        not_equal_to=cases_mixins.CfnCaseRulePropsMixin.BooleanOperandsProperty(
                            operand_one=cases_mixins.CfnCaseRulePropsMixin.OperandOneProperty(
                                field_id="fieldId"
                            ),
                            operand_two=cases_mixins.CfnCaseRulePropsMixin.OperandTwoProperty(
                                boolean_value=False,
                                double_value=123,
                                empty_value=empty_value,
                                string_value="stringValue"
                            ),
                            result=False
                        )
                    )],
                    default_value=False
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__7f6bf31661ac5d4d46aff3efe7884368bd5df0cb5215daf460c019a9611ee111)
                check_type(argname="argument conditions", value=conditions, expected_type=type_hints["conditions"])
                check_type(argname="argument default_value", value=default_value, expected_type=type_hints["default_value"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if conditions is not None:
                self._values["conditions"] = conditions
            if default_value is not None:
                self._values["default_value"] = default_value

        @builtins.property
        def conditions(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.BooleanConditionProperty"]]]]:
            '''List of conditions for the required rule;

            the first condition to evaluate to true dictates the value of the rule.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-requiredcaserule.html#cfn-cases-caserule-requiredcaserule-conditions
            '''
            result = self._values.get("conditions")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnCaseRulePropsMixin.BooleanConditionProperty"]]]], result)

        @builtins.property
        def default_value(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]]:
            '''The value of the rule (that is, whether the field is required) should none of the conditions evaluate to true.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-caserule-requiredcaserule.html#cfn-cases-caserule-requiredcaserule-defaultvalue
            '''
            result = self._values.get("default_value")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, "_aws_cdk_ceddda9d.IResolvable"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RequiredCaseRuleProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnDomainMixinProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "tags": "tags"},
)
class CfnDomainMixinProps:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["_aws_cdk_ceddda9d.CfnTag", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for CfnDomainPropsMixin.

        :param name: The name of the domain.
        :param tags: An array of key-value pairs to apply to this resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-domain.html
        :exampleMetadata: fixture=_generated

        Example::

            from aws_cdk import CfnTag
            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
            
            cfn_domain_mixin_props = cases_mixins.CfnDomainMixinProps(
                name="name",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d50dd451ae33d8d77bc434cc5c398f125da9c02ed304209779e4616673b45434)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the domain.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-domain.html#cfn-cases-domain-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List["_aws_cdk_ceddda9d.CfnTag"]]:
        '''An array of key-value pairs to apply to this resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-domain.html#cfn-cases-domain-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List["_aws_cdk_ceddda9d.CfnTag"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDomainMixinProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IMixin_11e4b965)
class CfnDomainPropsMixin(
    _Mixin_a69446c0,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnDomainPropsMixin",
):
    '''Creates a domain, which is a container for all case data, such as cases, fields, templates and layouts.

    Each Amazon Connect instance can be associated with only one Cases domain.
    .. epigraph::

       This will not associate your connect instance to Cases domain. Instead, use the Amazon Connect `CreateIntegrationAssociation <https://docs.aws.amazon.com/connect/latest/APIReference/API_CreateIntegrationAssociation.html>`_ API. You need specific IAM permissions to successfully associate the Cases domain. For more information, see `Onboard to Cases <https://docs.aws.amazon.com/connect/latest/adminguide/required-permissions-iam-cases.html#onboard-cases-iam>`_ .

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-domain.html
    :cloudformationResource: AWS::Cases::Domain
    :mixin: true
    :exampleMetadata: fixture=_generated

    Example::

        from aws_cdk import CfnTag
        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk.mixins_preview import mixins
        from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
        
        cfn_domain_props_mixin = cases_mixins.CfnDomainPropsMixin(cases_mixins.CfnDomainMixinProps(
            name="name",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        ),
            strategy=mixins.PropertyMergeStrategy.OVERRIDE
        )
    '''

    def __init__(
        self,
        props: typing.Union["CfnDomainMixinProps", typing.Dict[builtins.str, typing.Any]],
        *,
        strategy: typing.Optional["_PropertyMergeStrategy_49c157e8"] = None,
    ) -> None:
        '''Create a mixin to apply properties to ``AWS::Cases::Domain``.

        :param props: L1 properties to apply.
        :param strategy: (experimental) Strategy for merging nested properties. Default: - PropertyMergeStrategy.MERGE
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ace6eeb6fa32549753339c1a477269a7111d65e08cbd7c309644d67cf20fb013)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        options = _CfnPropertyMixinOptions_9cbff649(strategy=strategy)

        jsii.create(self.__class__, self, [props, options])

    @jsii.member(jsii_name="applyTo")
    def apply_to(
        self,
        construct: "_constructs_77d1e7e8.IConstruct",
    ) -> "_constructs_77d1e7e8.IConstruct":
        '''Apply the mixin properties to the construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00071e8fb45022a0210fe09444f4f9754bfa9113dc1057c94e6a8570c2aca9af)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast("_constructs_77d1e7e8.IConstruct", jsii.invoke(self, "applyTo", [construct]))

    @jsii.member(jsii_name="supports")
    def supports(self, construct: "_constructs_77d1e7e8.IConstruct") -> builtins.bool:
        '''Check if this mixin supports the given construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bcad20f316ac2ed813b2d409c690515fc01426cb7227d975304402694c2aae9)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(builtins.bool, jsii.invoke(self, "supports", [construct]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_PROPERTY_KEYS")
    def CFN_PROPERTY_KEYS(cls) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.sget(cls, "CFN_PROPERTY_KEYS"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def _props(self) -> "CfnDomainMixinProps":
        return typing.cast("CfnDomainMixinProps", jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def _strategy(self) -> "_PropertyMergeStrategy_49c157e8":
        return typing.cast("_PropertyMergeStrategy_49c157e8", jsii.get(self, "strategy"))


@jsii.data_type(
    jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnFieldMixinProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "domain_id": "domainId",
        "name": "name",
        "tags": "tags",
        "type": "type",
    },
)
class CfnFieldMixinProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        domain_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["_aws_cdk_ceddda9d.CfnTag", typing.Dict[builtins.str, typing.Any]]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for CfnFieldPropsMixin.

        :param description: Description of the field.
        :param domain_id: The unique identifier of the Cases domain.
        :param name: Name of the field.
        :param tags: An array of key-value pairs to apply to this resource.
        :param type: Type of the field.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-field.html
        :exampleMetadata: fixture=_generated

        Example::

            from aws_cdk import CfnTag
            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
            
            cfn_field_mixin_props = cases_mixins.CfnFieldMixinProps(
                description="description",
                domain_id="domainId",
                name="name",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                type="type"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a40e34007d29686b88e731ff5f1e469f14bed061ff6f4d6c537e0f92cd932e52)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument domain_id", value=domain_id, expected_type=type_hints["domain_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if domain_id is not None:
            self._values["domain_id"] = domain_id
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the field.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-field.html#cfn-cases-field-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_id(self) -> typing.Optional[builtins.str]:
        '''The unique identifier of the Cases domain.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-field.html#cfn-cases-field-domainid
        '''
        result = self._values.get("domain_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the field.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-field.html#cfn-cases-field-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List["_aws_cdk_ceddda9d.CfnTag"]]:
        '''An array of key-value pairs to apply to this resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-field.html#cfn-cases-field-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List["_aws_cdk_ceddda9d.CfnTag"]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Type of the field.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-field.html#cfn-cases-field-type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnFieldMixinProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IMixin_11e4b965)
class CfnFieldPropsMixin(
    _Mixin_a69446c0,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnFieldPropsMixin",
):
    '''Creates a field in the Cases domain.

    This field is used to define the case object model (that is, defines what data can be captured on cases) in a Cases domain.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-field.html
    :cloudformationResource: AWS::Cases::Field
    :mixin: true
    :exampleMetadata: fixture=_generated

    Example::

        from aws_cdk import CfnTag
        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk.mixins_preview import mixins
        from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
        
        cfn_field_props_mixin = cases_mixins.CfnFieldPropsMixin(cases_mixins.CfnFieldMixinProps(
            description="description",
            domain_id="domainId",
            name="name",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            type="type"
        ),
            strategy=mixins.PropertyMergeStrategy.OVERRIDE
        )
    '''

    def __init__(
        self,
        props: typing.Union["CfnFieldMixinProps", typing.Dict[builtins.str, typing.Any]],
        *,
        strategy: typing.Optional["_PropertyMergeStrategy_49c157e8"] = None,
    ) -> None:
        '''Create a mixin to apply properties to ``AWS::Cases::Field``.

        :param props: L1 properties to apply.
        :param strategy: (experimental) Strategy for merging nested properties. Default: - PropertyMergeStrategy.MERGE
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__381885005b899f2c9b7e0915f94b9f764902ddae4b124ebce1161a6af0341045)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        options = _CfnPropertyMixinOptions_9cbff649(strategy=strategy)

        jsii.create(self.__class__, self, [props, options])

    @jsii.member(jsii_name="applyTo")
    def apply_to(
        self,
        construct: "_constructs_77d1e7e8.IConstruct",
    ) -> "_constructs_77d1e7e8.IConstruct":
        '''Apply the mixin properties to the construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2e20e1461bde1b7a72a202d5156cd26526e7960d11d5e3c762fff33c1096649)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast("_constructs_77d1e7e8.IConstruct", jsii.invoke(self, "applyTo", [construct]))

    @jsii.member(jsii_name="supports")
    def supports(self, construct: "_constructs_77d1e7e8.IConstruct") -> builtins.bool:
        '''Check if this mixin supports the given construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0f3e73bedd8c99b3e3a7d56a4a55fcdf4de7f936312e38c555262962c01b96c)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(builtins.bool, jsii.invoke(self, "supports", [construct]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_PROPERTY_KEYS")
    def CFN_PROPERTY_KEYS(cls) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.sget(cls, "CFN_PROPERTY_KEYS"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def _props(self) -> "CfnFieldMixinProps":
        return typing.cast("CfnFieldMixinProps", jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def _strategy(self) -> "_PropertyMergeStrategy_49c157e8":
        return typing.cast("_PropertyMergeStrategy_49c157e8", jsii.get(self, "strategy"))


@jsii.data_type(
    jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnLayoutMixinProps",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "domain_id": "domainId",
        "name": "name",
        "tags": "tags",
    },
)
class CfnLayoutMixinProps:
    def __init__(
        self,
        *,
        content: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnLayoutPropsMixin.LayoutContentProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        domain_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["_aws_cdk_ceddda9d.CfnTag", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for CfnLayoutPropsMixin.

        :param content: Object to store union of different versions of layout content.
        :param domain_id: The unique identifier of the Cases domain.
        :param name: The name of the layout.
        :param tags: An array of key-value pairs to apply to this resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-layout.html
        :exampleMetadata: fixture=_generated

        Example::

            from aws_cdk import CfnTag
            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
            
            cfn_layout_mixin_props = cases_mixins.CfnLayoutMixinProps(
                content=cases_mixins.CfnLayoutPropsMixin.LayoutContentProperty(
                    basic=cases_mixins.CfnLayoutPropsMixin.BasicLayoutProperty(
                        more_info=cases_mixins.CfnLayoutPropsMixin.LayoutSectionsProperty(
                            sections=[cases_mixins.CfnLayoutPropsMixin.SectionProperty(
                                field_group=cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                                    fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                                        id="id"
                                    )],
                                    name="name"
                                )
                            )]
                        ),
                        top_panel=cases_mixins.CfnLayoutPropsMixin.LayoutSectionsProperty(
                            sections=[cases_mixins.CfnLayoutPropsMixin.SectionProperty(
                                field_group=cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                                    fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                                        id="id"
                                    )],
                                    name="name"
                                )
                            )]
                        )
                    )
                ),
                domain_id="domainId",
                name="name",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f03cd116dea8f5f8221df12230d50b2f0eb3ccc2d3406d0ca206bba32da88cc)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument domain_id", value=domain_id, expected_type=type_hints["domain_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if content is not None:
            self._values["content"] = content
        if domain_id is not None:
            self._values["domain_id"] = domain_id
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def content(
        self,
    ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.LayoutContentProperty"]]:
        '''Object to store union of different versions of layout content.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-layout.html#cfn-cases-layout-content
        '''
        result = self._values.get("content")
        return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.LayoutContentProperty"]], result)

    @builtins.property
    def domain_id(self) -> typing.Optional[builtins.str]:
        '''The unique identifier of the Cases domain.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-layout.html#cfn-cases-layout-domainid
        '''
        result = self._values.get("domain_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the layout.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-layout.html#cfn-cases-layout-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List["_aws_cdk_ceddda9d.CfnTag"]]:
        '''An array of key-value pairs to apply to this resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-layout.html#cfn-cases-layout-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List["_aws_cdk_ceddda9d.CfnTag"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnLayoutMixinProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IMixin_11e4b965)
class CfnLayoutPropsMixin(
    _Mixin_a69446c0,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnLayoutPropsMixin",
):
    '''Creates a layout in the Cases domain.

    Layouts define the following configuration in the top section and More Info tab of the Cases user interface:

    - Fields to display to the users
    - Field ordering

    .. epigraph::

       Title and Status fields cannot be part of layouts since they are not configurable.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-layout.html
    :cloudformationResource: AWS::Cases::Layout
    :mixin: true
    :exampleMetadata: fixture=_generated

    Example::

        from aws_cdk import CfnTag
        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk.mixins_preview import mixins
        from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
        
        cfn_layout_props_mixin = cases_mixins.CfnLayoutPropsMixin(cases_mixins.CfnLayoutMixinProps(
            content=cases_mixins.CfnLayoutPropsMixin.LayoutContentProperty(
                basic=cases_mixins.CfnLayoutPropsMixin.BasicLayoutProperty(
                    more_info=cases_mixins.CfnLayoutPropsMixin.LayoutSectionsProperty(
                        sections=[cases_mixins.CfnLayoutPropsMixin.SectionProperty(
                            field_group=cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                                fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                                    id="id"
                                )],
                                name="name"
                            )
                        )]
                    ),
                    top_panel=cases_mixins.CfnLayoutPropsMixin.LayoutSectionsProperty(
                        sections=[cases_mixins.CfnLayoutPropsMixin.SectionProperty(
                            field_group=cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                                fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                                    id="id"
                                )],
                                name="name"
                            )
                        )]
                    )
                )
            ),
            domain_id="domainId",
            name="name",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        ),
            strategy=mixins.PropertyMergeStrategy.OVERRIDE
        )
    '''

    def __init__(
        self,
        props: typing.Union["CfnLayoutMixinProps", typing.Dict[builtins.str, typing.Any]],
        *,
        strategy: typing.Optional["_PropertyMergeStrategy_49c157e8"] = None,
    ) -> None:
        '''Create a mixin to apply properties to ``AWS::Cases::Layout``.

        :param props: L1 properties to apply.
        :param strategy: (experimental) Strategy for merging nested properties. Default: - PropertyMergeStrategy.MERGE
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__121b0562c03e4a034293f6a29e757ab0d4e6050624b9c8ef08f74668aa83f8a9)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        options = _CfnPropertyMixinOptions_9cbff649(strategy=strategy)

        jsii.create(self.__class__, self, [props, options])

    @jsii.member(jsii_name="applyTo")
    def apply_to(
        self,
        construct: "_constructs_77d1e7e8.IConstruct",
    ) -> "_constructs_77d1e7e8.IConstruct":
        '''Apply the mixin properties to the construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc3dc83319dba7d8f0f443db05833f3f870ea5c6ba1c8ec316b767c32186a0dc)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast("_constructs_77d1e7e8.IConstruct", jsii.invoke(self, "applyTo", [construct]))

    @jsii.member(jsii_name="supports")
    def supports(self, construct: "_constructs_77d1e7e8.IConstruct") -> builtins.bool:
        '''Check if this mixin supports the given construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cf847c84097050b99a76e5c3e8f93ba1f4b315a213dbe3c10a2810dbfc41a89)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(builtins.bool, jsii.invoke(self, "supports", [construct]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_PROPERTY_KEYS")
    def CFN_PROPERTY_KEYS(cls) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.sget(cls, "CFN_PROPERTY_KEYS"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def _props(self) -> "CfnLayoutMixinProps":
        return typing.cast("CfnLayoutMixinProps", jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def _strategy(self) -> "_PropertyMergeStrategy_49c157e8":
        return typing.cast("_PropertyMergeStrategy_49c157e8", jsii.get(self, "strategy"))

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnLayoutPropsMixin.BasicLayoutProperty",
        jsii_struct_bases=[],
        name_mapping={"more_info": "moreInfo", "top_panel": "topPanel"},
    )
    class BasicLayoutProperty:
        def __init__(
            self,
            *,
            more_info: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnLayoutPropsMixin.LayoutSectionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            top_panel: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnLayoutPropsMixin.LayoutSectionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''Content specific to ``BasicLayout`` type.

            It configures fields in the top panel and More Info tab of agent application.

            :param more_info: This represents sections in a tab of the page layout.
            :param top_panel: This represents sections in a panel of the page layout.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-basiclayout.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                basic_layout_property = cases_mixins.CfnLayoutPropsMixin.BasicLayoutProperty(
                    more_info=cases_mixins.CfnLayoutPropsMixin.LayoutSectionsProperty(
                        sections=[cases_mixins.CfnLayoutPropsMixin.SectionProperty(
                            field_group=cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                                fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                                    id="id"
                                )],
                                name="name"
                            )
                        )]
                    ),
                    top_panel=cases_mixins.CfnLayoutPropsMixin.LayoutSectionsProperty(
                        sections=[cases_mixins.CfnLayoutPropsMixin.SectionProperty(
                            field_group=cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                                fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                                    id="id"
                                )],
                                name="name"
                            )
                        )]
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__6224d8b2856d82f13c7e212494c9f8caafa07299f98a1e6979a66abab44008a2)
                check_type(argname="argument more_info", value=more_info, expected_type=type_hints["more_info"])
                check_type(argname="argument top_panel", value=top_panel, expected_type=type_hints["top_panel"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if more_info is not None:
                self._values["more_info"] = more_info
            if top_panel is not None:
                self._values["top_panel"] = top_panel

        @builtins.property
        def more_info(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.LayoutSectionsProperty"]]:
            '''This represents sections in a tab of the page layout.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-basiclayout.html#cfn-cases-layout-basiclayout-moreinfo
            '''
            result = self._values.get("more_info")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.LayoutSectionsProperty"]], result)

        @builtins.property
        def top_panel(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.LayoutSectionsProperty"]]:
            '''This represents sections in a panel of the page layout.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-basiclayout.html#cfn-cases-layout-basiclayout-toppanel
            '''
            result = self._values.get("top_panel")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.LayoutSectionsProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BasicLayoutProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnLayoutPropsMixin.FieldGroupProperty",
        jsii_struct_bases=[],
        name_mapping={"fields": "fields", "name": "name"},
    )
    class FieldGroupProperty:
        def __init__(
            self,
            *,
            fields: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Sequence[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnLayoutPropsMixin.FieldItemProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
            name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Object for a group of fields and associated properties.

            :param fields: Represents an ordered list containing field related information.
            :param name: Name of the field group.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-fieldgroup.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                field_group_property = cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                    fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                        id="id"
                    )],
                    name="name"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__34ffb749da95d2cc2dd2533486990c6760f8593fdd61b327d9103ee05fe23e14)
                check_type(argname="argument fields", value=fields, expected_type=type_hints["fields"])
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if fields is not None:
                self._values["fields"] = fields
            if name is not None:
                self._values["name"] = name

        @builtins.property
        def fields(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.FieldItemProperty"]]]]:
            '''Represents an ordered list containing field related information.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-fieldgroup.html#cfn-cases-layout-fieldgroup-fields
            '''
            result = self._values.get("fields")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.FieldItemProperty"]]]], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''Name of the field group.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-fieldgroup.html#cfn-cases-layout-fieldgroup-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FieldGroupProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnLayoutPropsMixin.FieldItemProperty",
        jsii_struct_bases=[],
        name_mapping={"id": "id"},
    )
    class FieldItemProperty:
        def __init__(self, *, id: typing.Optional[builtins.str] = None) -> None:
            '''Object for field related information.

            :param id: Unique identifier of a field.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-fielditem.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                field_item_property = cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                    id="id"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__428637e1466dfd21157fda5c8b6dd1b10b6ed2cb481d6ee5ccdff4fad28e95a2)
                check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if id is not None:
                self._values["id"] = id

        @builtins.property
        def id(self) -> typing.Optional[builtins.str]:
            '''Unique identifier of a field.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-fielditem.html#cfn-cases-layout-fielditem-id
            '''
            result = self._values.get("id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FieldItemProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnLayoutPropsMixin.LayoutContentProperty",
        jsii_struct_bases=[],
        name_mapping={"basic": "basic"},
    )
    class LayoutContentProperty:
        def __init__(
            self,
            *,
            basic: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnLayoutPropsMixin.BasicLayoutProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''Object to store union of different versions of layout content.

            :param basic: Content specific to ``BasicLayout`` type. It configures fields in the top panel and More Info tab of agent application.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-layoutcontent.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                layout_content_property = cases_mixins.CfnLayoutPropsMixin.LayoutContentProperty(
                    basic=cases_mixins.CfnLayoutPropsMixin.BasicLayoutProperty(
                        more_info=cases_mixins.CfnLayoutPropsMixin.LayoutSectionsProperty(
                            sections=[cases_mixins.CfnLayoutPropsMixin.SectionProperty(
                                field_group=cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                                    fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                                        id="id"
                                    )],
                                    name="name"
                                )
                            )]
                        ),
                        top_panel=cases_mixins.CfnLayoutPropsMixin.LayoutSectionsProperty(
                            sections=[cases_mixins.CfnLayoutPropsMixin.SectionProperty(
                                field_group=cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                                    fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                                        id="id"
                                    )],
                                    name="name"
                                )
                            )]
                        )
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__9ea7278228a6228332174324628106a88a3fb7b6e3752ae3f9bb060405f9848c)
                check_type(argname="argument basic", value=basic, expected_type=type_hints["basic"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if basic is not None:
                self._values["basic"] = basic

        @builtins.property
        def basic(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.BasicLayoutProperty"]]:
            '''Content specific to ``BasicLayout`` type.

            It configures fields in the top panel and More Info tab of agent application.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-layoutcontent.html#cfn-cases-layout-layoutcontent-basic
            '''
            result = self._values.get("basic")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.BasicLayoutProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LayoutContentProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnLayoutPropsMixin.LayoutSectionsProperty",
        jsii_struct_bases=[],
        name_mapping={"sections": "sections"},
    )
    class LayoutSectionsProperty:
        def __init__(
            self,
            *,
            sections: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Sequence[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnLayoutPropsMixin.SectionProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        ) -> None:
            '''Ordered list containing different kinds of sections that can be added.

            A LayoutSections object can only contain one section.

            :param sections: Ordered list containing different kinds of sections that can be added. A LayoutSections object can only contain one section.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-layoutsections.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                layout_sections_property = cases_mixins.CfnLayoutPropsMixin.LayoutSectionsProperty(
                    sections=[cases_mixins.CfnLayoutPropsMixin.SectionProperty(
                        field_group=cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                            fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                                id="id"
                            )],
                            name="name"
                        )
                    )]
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__583c27c9aa2777ef2d63f8876dac5fca0bec024a335356329baa6e772f9286db)
                check_type(argname="argument sections", value=sections, expected_type=type_hints["sections"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if sections is not None:
                self._values["sections"] = sections

        @builtins.property
        def sections(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.SectionProperty"]]]]:
            '''Ordered list containing different kinds of sections that can be added.

            A LayoutSections object can only contain one section.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-layoutsections.html#cfn-cases-layout-layoutsections-sections
            '''
            result = self._values.get("sections")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.SectionProperty"]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LayoutSectionsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnLayoutPropsMixin.SectionProperty",
        jsii_struct_bases=[],
        name_mapping={"field_group": "fieldGroup"},
    )
    class SectionProperty:
        def __init__(
            self,
            *,
            field_group: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnLayoutPropsMixin.FieldGroupProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''This represents a sections within a panel or tab of the page layout.

            :param field_group: Consists of a group of fields and associated properties.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-section.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                section_property = cases_mixins.CfnLayoutPropsMixin.SectionProperty(
                    field_group=cases_mixins.CfnLayoutPropsMixin.FieldGroupProperty(
                        fields=[cases_mixins.CfnLayoutPropsMixin.FieldItemProperty(
                            id="id"
                        )],
                        name="name"
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__6a0d64e6c5aff46993069e065f1c53d2cb02042932bac80998586e6bf8765fcf)
                check_type(argname="argument field_group", value=field_group, expected_type=type_hints["field_group"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if field_group is not None:
                self._values["field_group"] = field_group

        @builtins.property
        def field_group(
            self,
        ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.FieldGroupProperty"]]:
            '''Consists of a group of fields and associated properties.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-layout-section.html#cfn-cases-layout-section-fieldgroup
            '''
            result = self._values.get("field_group")
            return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnLayoutPropsMixin.FieldGroupProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SectionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnTemplateMixinProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "domain_id": "domainId",
        "layout_configuration": "layoutConfiguration",
        "name": "name",
        "required_fields": "requiredFields",
        "rules": "rules",
        "status": "status",
        "tags": "tags",
    },
)
class CfnTemplateMixinProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        domain_id: typing.Optional[builtins.str] = None,
        layout_configuration: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnTemplatePropsMixin.LayoutConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        name: typing.Optional[builtins.str] = None,
        required_fields: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Sequence[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnTemplatePropsMixin.RequiredFieldProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        rules: typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Sequence[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.Union["CfnTemplatePropsMixin.TemplateRuleProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        status: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["_aws_cdk_ceddda9d.CfnTag", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for CfnTemplatePropsMixin.

        :param description: A brief description of the template.
        :param domain_id: The unique identifier of the Cases domain.
        :param layout_configuration: Object to store configuration of layouts associated to the template.
        :param name: The template name.
        :param required_fields: A list of fields that must contain a value for a case to be successfully created with this template.
        :param rules: A list of case rules (also known as `case field conditions <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ ) on a template.
        :param status: The status of the template.
        :param tags: An array of key-value pairs to apply to this resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-template.html
        :exampleMetadata: fixture=_generated

        Example::

            from aws_cdk import CfnTag
            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
            
            cfn_template_mixin_props = cases_mixins.CfnTemplateMixinProps(
                description="description",
                domain_id="domainId",
                layout_configuration=cases_mixins.CfnTemplatePropsMixin.LayoutConfigurationProperty(
                    default_layout="defaultLayout"
                ),
                name="name",
                required_fields=[cases_mixins.CfnTemplatePropsMixin.RequiredFieldProperty(
                    field_id="fieldId"
                )],
                rules=[cases_mixins.CfnTemplatePropsMixin.TemplateRuleProperty(
                    case_rule_id="caseRuleId",
                    field_id="fieldId"
                )],
                status="status",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33f4ce50897ae6a6fbaf04b92cb708f86e58d9a97f18051ec25fb4b44f946eb3)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument domain_id", value=domain_id, expected_type=type_hints["domain_id"])
            check_type(argname="argument layout_configuration", value=layout_configuration, expected_type=type_hints["layout_configuration"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument required_fields", value=required_fields, expected_type=type_hints["required_fields"])
            check_type(argname="argument rules", value=rules, expected_type=type_hints["rules"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if domain_id is not None:
            self._values["domain_id"] = domain_id
        if layout_configuration is not None:
            self._values["layout_configuration"] = layout_configuration
        if name is not None:
            self._values["name"] = name
        if required_fields is not None:
            self._values["required_fields"] = required_fields
        if rules is not None:
            self._values["rules"] = rules
        if status is not None:
            self._values["status"] = status
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A brief description of the template.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-template.html#cfn-cases-template-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_id(self) -> typing.Optional[builtins.str]:
        '''The unique identifier of the Cases domain.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-template.html#cfn-cases-template-domainid
        '''
        result = self._values.get("domain_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def layout_configuration(
        self,
    ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnTemplatePropsMixin.LayoutConfigurationProperty"]]:
        '''Object to store configuration of layouts associated to the template.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-template.html#cfn-cases-template-layoutconfiguration
        '''
        result = self._values.get("layout_configuration")
        return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnTemplatePropsMixin.LayoutConfigurationProperty"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The template name.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-template.html#cfn-cases-template-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def required_fields(
        self,
    ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnTemplatePropsMixin.RequiredFieldProperty"]]]]:
        '''A list of fields that must contain a value for a case to be successfully created with this template.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-template.html#cfn-cases-template-requiredfields
        '''
        result = self._values.get("required_fields")
        return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnTemplatePropsMixin.RequiredFieldProperty"]]]], result)

    @builtins.property
    def rules(
        self,
    ) -> typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnTemplatePropsMixin.TemplateRuleProperty"]]]]:
        '''A list of case rules (also known as `case field conditions <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ ) on a template.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-template.html#cfn-cases-template-rules
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.Union["_aws_cdk_ceddda9d.IResolvable", typing.List[typing.Union["_aws_cdk_ceddda9d.IResolvable", "CfnTemplatePropsMixin.TemplateRuleProperty"]]]], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''The status of the template.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-template.html#cfn-cases-template-status
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List["_aws_cdk_ceddda9d.CfnTag"]]:
        '''An array of key-value pairs to apply to this resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-template.html#cfn-cases-template-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List["_aws_cdk_ceddda9d.CfnTag"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnTemplateMixinProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IMixin_11e4b965)
class CfnTemplatePropsMixin(
    _Mixin_a69446c0,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnTemplatePropsMixin",
):
    '''Creates a template in the Cases domain.

    This template is used to define the case object model (that is, to define what data can be captured on cases) in a Cases domain. A template must have a unique name within a domain, and it must reference existing field IDs and layout IDs. Additionally, multiple fields with same IDs are not allowed within the same Template. A template can be either Active or Inactive, as indicated by its status. Inactive templates cannot be used to create cases.

    Other template APIs are:

    - `DeleteTemplate <https://docs.aws.amazon.com/connect/latest/APIReference/API_connect-cases_DeleteTemplate.html>`_
    - `GetTemplate <https://docs.aws.amazon.com/connect/latest/APIReference/API_connect-cases_GetTemplate.html>`_
    - `ListTemplates <https://docs.aws.amazon.com/connect/latest/APIReference/API_connect-cases_ListTemplates.html>`_
    - `UpdateTemplate <https://docs.aws.amazon.com/connect/latest/APIReference/API_connect-cases_UpdateTemplate.html>`_

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cases-template.html
    :cloudformationResource: AWS::Cases::Template
    :mixin: true
    :exampleMetadata: fixture=_generated

    Example::

        from aws_cdk import CfnTag
        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk.mixins_preview import mixins
        from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
        
        cfn_template_props_mixin = cases_mixins.CfnTemplatePropsMixin(cases_mixins.CfnTemplateMixinProps(
            description="description",
            domain_id="domainId",
            layout_configuration=cases_mixins.CfnTemplatePropsMixin.LayoutConfigurationProperty(
                default_layout="defaultLayout"
            ),
            name="name",
            required_fields=[cases_mixins.CfnTemplatePropsMixin.RequiredFieldProperty(
                field_id="fieldId"
            )],
            rules=[cases_mixins.CfnTemplatePropsMixin.TemplateRuleProperty(
                case_rule_id="caseRuleId",
                field_id="fieldId"
            )],
            status="status",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        ),
            strategy=mixins.PropertyMergeStrategy.OVERRIDE
        )
    '''

    def __init__(
        self,
        props: typing.Union["CfnTemplateMixinProps", typing.Dict[builtins.str, typing.Any]],
        *,
        strategy: typing.Optional["_PropertyMergeStrategy_49c157e8"] = None,
    ) -> None:
        '''Create a mixin to apply properties to ``AWS::Cases::Template``.

        :param props: L1 properties to apply.
        :param strategy: (experimental) Strategy for merging nested properties. Default: - PropertyMergeStrategy.MERGE
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8644df0d83a24f33215047919767abb7cc0602a4c15b8d703fd332bf095ee817)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        options = _CfnPropertyMixinOptions_9cbff649(strategy=strategy)

        jsii.create(self.__class__, self, [props, options])

    @jsii.member(jsii_name="applyTo")
    def apply_to(
        self,
        construct: "_constructs_77d1e7e8.IConstruct",
    ) -> "_constructs_77d1e7e8.IConstruct":
        '''Apply the mixin properties to the construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d06d0987dc7a04b72232339e06efa07362a44e88bbabf72f4792f3fd3b3b984a)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast("_constructs_77d1e7e8.IConstruct", jsii.invoke(self, "applyTo", [construct]))

    @jsii.member(jsii_name="supports")
    def supports(self, construct: "_constructs_77d1e7e8.IConstruct") -> builtins.bool:
        '''Check if this mixin supports the given construct.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__572c2fc3157d687e41bcc78461285a32ec88d83f8a9e87f95d4d62aa9bbcd9b2)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(builtins.bool, jsii.invoke(self, "supports", [construct]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_PROPERTY_KEYS")
    def CFN_PROPERTY_KEYS(cls) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.sget(cls, "CFN_PROPERTY_KEYS"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def _props(self) -> "CfnTemplateMixinProps":
        return typing.cast("CfnTemplateMixinProps", jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def _strategy(self) -> "_PropertyMergeStrategy_49c157e8":
        return typing.cast("_PropertyMergeStrategy_49c157e8", jsii.get(self, "strategy"))

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnTemplatePropsMixin.LayoutConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"default_layout": "defaultLayout"},
    )
    class LayoutConfigurationProperty:
        def __init__(
            self,
            *,
            default_layout: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Object to store configuration of layouts associated to the template.

            :param default_layout: Unique identifier of a layout.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-template-layoutconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                layout_configuration_property = cases_mixins.CfnTemplatePropsMixin.LayoutConfigurationProperty(
                    default_layout="defaultLayout"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__f9ae1b342461933e517d9d9b731de07fc99a9c1abbc81f4f8b7603347376ef82)
                check_type(argname="argument default_layout", value=default_layout, expected_type=type_hints["default_layout"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if default_layout is not None:
                self._values["default_layout"] = default_layout

        @builtins.property
        def default_layout(self) -> typing.Optional[builtins.str]:
            '''Unique identifier of a layout.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-template-layoutconfiguration.html#cfn-cases-template-layoutconfiguration-defaultlayout
            '''
            result = self._values.get("default_layout")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LayoutConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnTemplatePropsMixin.RequiredFieldProperty",
        jsii_struct_bases=[],
        name_mapping={"field_id": "fieldId"},
    )
    class RequiredFieldProperty:
        def __init__(self, *, field_id: typing.Optional[builtins.str] = None) -> None:
            '''List of fields that must have a value provided to create a case.

            :param field_id: Unique identifier of a field.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-template-requiredfield.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                required_field_property = cases_mixins.CfnTemplatePropsMixin.RequiredFieldProperty(
                    field_id="fieldId"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__8c0a0904a11852af933a4d39346af31fc4f9c2a4377e6c1034a803d5901a0033)
                check_type(argname="argument field_id", value=field_id, expected_type=type_hints["field_id"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if field_id is not None:
                self._values["field_id"] = field_id

        @builtins.property
        def field_id(self) -> typing.Optional[builtins.str]:
            '''Unique identifier of a field.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-template-requiredfield.html#cfn-cases-template-requiredfield-fieldid
            '''
            result = self._values.get("field_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RequiredFieldProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/mixins-preview.aws_cases.mixins.CfnTemplatePropsMixin.TemplateRuleProperty",
        jsii_struct_bases=[],
        name_mapping={"case_rule_id": "caseRuleId", "field_id": "fieldId"},
    )
    class TemplateRuleProperty:
        def __init__(
            self,
            *,
            case_rule_id: typing.Optional[builtins.str] = None,
            field_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''An association representing a case rule acting upon a field.

            In the Amazon Connect admin website, case rules are known as *case field conditions* . For more information about case field conditions, see `Add case field conditions to a case template <https://docs.aws.amazon.com/connect/latest/adminguide/case-field-conditions.html>`_ .

            :param case_rule_id: Unique identifier of a case rule.
            :param field_id: Unique identifier of a field.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-template-templaterule.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk.mixins_preview.aws_cases import mixins as cases_mixins
                
                template_rule_property = cases_mixins.CfnTemplatePropsMixin.TemplateRuleProperty(
                    case_rule_id="caseRuleId",
                    field_id="fieldId"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__7192892b4b55ec1c3d03bf55a2f848e9ac74e4d56ffae2c91df52710e161ed39)
                check_type(argname="argument case_rule_id", value=case_rule_id, expected_type=type_hints["case_rule_id"])
                check_type(argname="argument field_id", value=field_id, expected_type=type_hints["field_id"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if case_rule_id is not None:
                self._values["case_rule_id"] = case_rule_id
            if field_id is not None:
                self._values["field_id"] = field_id

        @builtins.property
        def case_rule_id(self) -> typing.Optional[builtins.str]:
            '''Unique identifier of a case rule.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-template-templaterule.html#cfn-cases-template-templaterule-caseruleid
            '''
            result = self._values.get("case_rule_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def field_id(self) -> typing.Optional[builtins.str]:
            '''Unique identifier of a field.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cases-template-templaterule.html#cfn-cases-template-templaterule-fieldid
            '''
            result = self._values.get("field_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TemplateRuleProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


__all__ = [
    "CfnCaseRuleMixinProps",
    "CfnCaseRulePropsMixin",
    "CfnDomainMixinProps",
    "CfnDomainPropsMixin",
    "CfnFieldMixinProps",
    "CfnFieldPropsMixin",
    "CfnLayoutMixinProps",
    "CfnLayoutPropsMixin",
    "CfnTemplateMixinProps",
    "CfnTemplatePropsMixin",
]

publication.publish()

def _typecheckingstub__1cdb9e56fe45438927dc663e67a2af5c6f774a9c75ece463d6bc817c3333525d(
    *,
    description: typing.Optional[builtins.str] = None,
    domain_id: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    rule: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnCaseRulePropsMixin.CaseRuleDetailsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25e9fb0da31a933f2de5298f74d7baa511041ca1a071ec66ae08e2af618be95d(
    props: typing.Union[CfnCaseRuleMixinProps, typing.Dict[builtins.str, typing.Any]],
    *,
    strategy: typing.Optional[_PropertyMergeStrategy_49c157e8] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c27a52a301511321043a24392cbaee63fc9b55f6a2633568b7ea5618bbd462fb(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2cac2b7ad2d9db325b33cb264607deebcce8b793ef296d4e876f577a886dd40(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05c32b941460f3eefc8d4e4a58993a3f4387fa0cd80eac0e9d72a3a1c434bf4c(
    *,
    equal_to: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnCaseRulePropsMixin.BooleanOperandsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    not_equal_to: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnCaseRulePropsMixin.BooleanOperandsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a2608a5095da0024b04268724b1573d49106807886f82060df90a9174da139e(
    *,
    operand_one: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnCaseRulePropsMixin.OperandOneProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    operand_two: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnCaseRulePropsMixin.OperandTwoProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    result: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6a60a35ed4bb50f762dc39354a5b2eeb9e178a528bc07a55f2d89b83392295b(
    *,
    hidden: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnCaseRulePropsMixin.HiddenCaseRuleProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    required: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnCaseRulePropsMixin.RequiredCaseRuleProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d324d5b44428687762657b1184ee223050c88f39c4bb3303bf21cf3025ea64e7(
    *,
    conditions: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnCaseRulePropsMixin.BooleanConditionProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    default_value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ceea2c438a1ec9bde8b7eefb4c83868fc6d6c6196a3037ea8b783dafb52e369(
    *,
    field_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37e6113170581cfb1c8aacd5dd8105fe481902c40d708eba14ccbe4f7bfe3d61(
    *,
    boolean_value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    double_value: typing.Optional[jsii.Number] = None,
    empty_value: typing.Any = None,
    string_value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f6bf31661ac5d4d46aff3efe7884368bd5df0cb5215daf460c019a9611ee111(
    *,
    conditions: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnCaseRulePropsMixin.BooleanConditionProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    default_value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d50dd451ae33d8d77bc434cc5c398f125da9c02ed304209779e4616673b45434(
    *,
    name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ace6eeb6fa32549753339c1a477269a7111d65e08cbd7c309644d67cf20fb013(
    props: typing.Union[CfnDomainMixinProps, typing.Dict[builtins.str, typing.Any]],
    *,
    strategy: typing.Optional[_PropertyMergeStrategy_49c157e8] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00071e8fb45022a0210fe09444f4f9754bfa9113dc1057c94e6a8570c2aca9af(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bcad20f316ac2ed813b2d409c690515fc01426cb7227d975304402694c2aae9(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a40e34007d29686b88e731ff5f1e469f14bed061ff6f4d6c537e0f92cd932e52(
    *,
    description: typing.Optional[builtins.str] = None,
    domain_id: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__381885005b899f2c9b7e0915f94b9f764902ddae4b124ebce1161a6af0341045(
    props: typing.Union[CfnFieldMixinProps, typing.Dict[builtins.str, typing.Any]],
    *,
    strategy: typing.Optional[_PropertyMergeStrategy_49c157e8] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e20e1461bde1b7a72a202d5156cd26526e7960d11d5e3c762fff33c1096649(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0f3e73bedd8c99b3e3a7d56a4a55fcdf4de7f936312e38c555262962c01b96c(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f03cd116dea8f5f8221df12230d50b2f0eb3ccc2d3406d0ca206bba32da88cc(
    *,
    content: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnLayoutPropsMixin.LayoutContentProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    domain_id: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__121b0562c03e4a034293f6a29e757ab0d4e6050624b9c8ef08f74668aa83f8a9(
    props: typing.Union[CfnLayoutMixinProps, typing.Dict[builtins.str, typing.Any]],
    *,
    strategy: typing.Optional[_PropertyMergeStrategy_49c157e8] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc3dc83319dba7d8f0f443db05833f3f870ea5c6ba1c8ec316b767c32186a0dc(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cf847c84097050b99a76e5c3e8f93ba1f4b315a213dbe3c10a2810dbfc41a89(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6224d8b2856d82f13c7e212494c9f8caafa07299f98a1e6979a66abab44008a2(
    *,
    more_info: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnLayoutPropsMixin.LayoutSectionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    top_panel: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnLayoutPropsMixin.LayoutSectionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34ffb749da95d2cc2dd2533486990c6760f8593fdd61b327d9103ee05fe23e14(
    *,
    fields: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnLayoutPropsMixin.FieldItemProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__428637e1466dfd21157fda5c8b6dd1b10b6ed2cb481d6ee5ccdff4fad28e95a2(
    *,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ea7278228a6228332174324628106a88a3fb7b6e3752ae3f9bb060405f9848c(
    *,
    basic: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnLayoutPropsMixin.BasicLayoutProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__583c27c9aa2777ef2d63f8876dac5fca0bec024a335356329baa6e772f9286db(
    *,
    sections: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnLayoutPropsMixin.SectionProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a0d64e6c5aff46993069e065f1c53d2cb02042932bac80998586e6bf8765fcf(
    *,
    field_group: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnLayoutPropsMixin.FieldGroupProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33f4ce50897ae6a6fbaf04b92cb708f86e58d9a97f18051ec25fb4b44f946eb3(
    *,
    description: typing.Optional[builtins.str] = None,
    domain_id: typing.Optional[builtins.str] = None,
    layout_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnTemplatePropsMixin.LayoutConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    name: typing.Optional[builtins.str] = None,
    required_fields: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnTemplatePropsMixin.RequiredFieldProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    rules: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[CfnTemplatePropsMixin.TemplateRuleProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    status: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8644df0d83a24f33215047919767abb7cc0602a4c15b8d703fd332bf095ee817(
    props: typing.Union[CfnTemplateMixinProps, typing.Dict[builtins.str, typing.Any]],
    *,
    strategy: typing.Optional[_PropertyMergeStrategy_49c157e8] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d06d0987dc7a04b72232339e06efa07362a44e88bbabf72f4792f3fd3b3b984a(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__572c2fc3157d687e41bcc78461285a32ec88d83f8a9e87f95d4d62aa9bbcd9b2(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9ae1b342461933e517d9d9b731de07fc99a9c1abbc81f4f8b7603347376ef82(
    *,
    default_layout: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c0a0904a11852af933a4d39346af31fc4f9c2a4377e6c1034a803d5901a0033(
    *,
    field_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7192892b4b55ec1c3d03bf55a2f848e9ac74e4d56ffae2c91df52710e161ed39(
    *,
    case_rule_id: typing.Optional[builtins.str] = None,
    field_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
