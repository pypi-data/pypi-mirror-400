from typing import Optional

from pydantic import BaseModel, Field


class System(BaseModel):
    """A System is a specific software product. Systems may or may not belong to a company in the crossroads network."""
    name: str = Field(..., description="Name of the system")
    description: Optional[str] = Field(None, description="Details")
    is_erp: bool = Field(False, description="Does this sytem provide ERP functionality?")
    is_tms: bool = Field(False, description="Does this sytem provide TMS functionality?")
    is_active: bool = Field(True)


class Integration(BaseModel):
    """An Integration describes a runnable integration that can be used in the crossroads network."""
    name: str = Field(..., description="Name of the integration")
    description: Optional[str] = Field(None, description="Detailed description of the integration.")
    supersedes: Optional[str] = Field(None, description="ID of the integration that this integration supersedes. It is suggested to use this integration instead of the linked integration.")
    config_schema: dict = Field(default_factory=dict, description="A JSON schema for the configuration that this integration expects.")
    default_config: dict = Field(default_factory=dict, description="The default configuration values for this job.")
    is_active: bool = Field(True)


class Node(BaseModel):
    """A node is best thought of as a Company @ a System. So Caseys@Gravitate S+D, TTE@Gravitate S+D, Eagle@Telapoint are 3 nodes."""
    company_id: str = Field(..., description="Mongodb ID of the company")
    system_id: str = Field(..., description="Mongodb ID of the system")
    is_phantom: bool = Field(False, description="Should this be shown as a phantom node?")
    is_active: bool = Field(True)


class Connection(BaseModel):
    """A connection is an instance of an integration. It points between two Nodes, references an integration to run, and specifies the config for this integration."""
    name: str = Field(..., description="Name of the connection")
    description: Optional[str] = Field(None, description="Detailed description of the connection")
    origin_node_id: str = Field(..., description="ID of the origin node")
    target_node_id: str = Field(..., description="ID of the target node")
    integration_id: str = Field(..., description="ID of the integration")
    config: dict = Field(..., description="Config of this instance of the integration. This must conform to the schema defined by that integration.")
    is_active: bool = Field(True)