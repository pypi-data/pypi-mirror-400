from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_deployment_response_200_deployments_item_decision_definition import (
        CreateDeploymentResponse200DeploymentsItemDecisionDefinition,
    )
    from ..models.create_deployment_response_200_deployments_item_decision_requirements import (
        CreateDeploymentResponse200DeploymentsItemDecisionRequirements,
    )
    from ..models.create_deployment_response_200_deployments_item_form import (
        CreateDeploymentResponse200DeploymentsItemForm,
    )
    from ..models.create_deployment_response_200_deployments_item_process_definition import (
        CreateDeploymentResponse200DeploymentsItemProcessDefinition,
    )
    from ..models.create_deployment_response_200_deployments_item_resource import (
        CreateDeploymentResponse200DeploymentsItemResource,
    )


T = TypeVar("T", bound="CreateDeploymentResponse200DeploymentsItem")


@_attrs_define
class CreateDeploymentResponse200DeploymentsItem:
    """
    Attributes:
        process_definition (CreateDeploymentResponse200DeploymentsItemProcessDefinition | Unset): A deployed process.
        decision_definition (CreateDeploymentResponse200DeploymentsItemDecisionDefinition | Unset): A deployed decision.
        decision_requirements (CreateDeploymentResponse200DeploymentsItemDecisionRequirements | Unset): Deployed
            decision requirements.
        form (CreateDeploymentResponse200DeploymentsItemForm | Unset): A deployed form.
        resource (CreateDeploymentResponse200DeploymentsItemResource | Unset): A deployed Resource.
    """

    process_definition: (
        CreateDeploymentResponse200DeploymentsItemProcessDefinition | Unset
    ) = UNSET
    decision_definition: (
        CreateDeploymentResponse200DeploymentsItemDecisionDefinition | Unset
    ) = UNSET
    decision_requirements: (
        CreateDeploymentResponse200DeploymentsItemDecisionRequirements | Unset
    ) = UNSET
    form: CreateDeploymentResponse200DeploymentsItemForm | Unset = UNSET
    resource: CreateDeploymentResponse200DeploymentsItemResource | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition: dict[str, Any] | Unset = UNSET
        if not isinstance(self.process_definition, Unset):
            process_definition = self.process_definition.to_dict()

        decision_definition: dict[str, Any] | Unset = UNSET
        if not isinstance(self.decision_definition, Unset):
            decision_definition = self.decision_definition.to_dict()

        decision_requirements: dict[str, Any] | Unset = UNSET
        if not isinstance(self.decision_requirements, Unset):
            decision_requirements = self.decision_requirements.to_dict()

        form: dict[str, Any] | Unset = UNSET
        if not isinstance(self.form, Unset):
            form = self.form.to_dict()

        resource: dict[str, Any] | Unset = UNSET
        if not isinstance(self.resource, Unset):
            resource = self.resource.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if process_definition is not UNSET:
            field_dict["processDefinition"] = process_definition
        if decision_definition is not UNSET:
            field_dict["decisionDefinition"] = decision_definition
        if decision_requirements is not UNSET:
            field_dict["decisionRequirements"] = decision_requirements
        if form is not UNSET:
            field_dict["form"] = form
        if resource is not UNSET:
            field_dict["resource"] = resource

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_deployment_response_200_deployments_item_decision_definition import (
            CreateDeploymentResponse200DeploymentsItemDecisionDefinition,
        )
        from ..models.create_deployment_response_200_deployments_item_decision_requirements import (
            CreateDeploymentResponse200DeploymentsItemDecisionRequirements,
        )
        from ..models.create_deployment_response_200_deployments_item_form import (
            CreateDeploymentResponse200DeploymentsItemForm,
        )
        from ..models.create_deployment_response_200_deployments_item_process_definition import (
            CreateDeploymentResponse200DeploymentsItemProcessDefinition,
        )
        from ..models.create_deployment_response_200_deployments_item_resource import (
            CreateDeploymentResponse200DeploymentsItemResource,
        )

        d = dict(src_dict)
        _process_definition = d.pop("processDefinition", UNSET)
        process_definition: (
            CreateDeploymentResponse200DeploymentsItemProcessDefinition | Unset
        )
        if isinstance(_process_definition, Unset):
            process_definition = UNSET
        else:
            process_definition = (
                CreateDeploymentResponse200DeploymentsItemProcessDefinition.from_dict(
                    _process_definition
                )
            )

        _decision_definition = d.pop("decisionDefinition", UNSET)
        decision_definition: (
            CreateDeploymentResponse200DeploymentsItemDecisionDefinition | Unset
        )
        if isinstance(_decision_definition, Unset):
            decision_definition = UNSET
        else:
            decision_definition = (
                CreateDeploymentResponse200DeploymentsItemDecisionDefinition.from_dict(
                    _decision_definition
                )
            )

        _decision_requirements = d.pop("decisionRequirements", UNSET)
        decision_requirements: (
            CreateDeploymentResponse200DeploymentsItemDecisionRequirements | Unset
        )
        if isinstance(_decision_requirements, Unset):
            decision_requirements = UNSET
        else:
            decision_requirements = CreateDeploymentResponse200DeploymentsItemDecisionRequirements.from_dict(
                _decision_requirements
            )

        _form = d.pop("form", UNSET)
        form: CreateDeploymentResponse200DeploymentsItemForm | Unset
        if isinstance(_form, Unset):
            form = UNSET
        else:
            form = CreateDeploymentResponse200DeploymentsItemForm.from_dict(_form)

        _resource = d.pop("resource", UNSET)
        resource: CreateDeploymentResponse200DeploymentsItemResource | Unset
        if isinstance(_resource, Unset):
            resource = UNSET
        else:
            resource = CreateDeploymentResponse200DeploymentsItemResource.from_dict(
                _resource
            )

        create_deployment_response_200_deployments_item = cls(
            process_definition=process_definition,
            decision_definition=decision_definition,
            decision_requirements=decision_requirements,
            form=form,
            resource=resource,
        )

        create_deployment_response_200_deployments_item.additional_properties = d
        return create_deployment_response_200_deployments_item

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
