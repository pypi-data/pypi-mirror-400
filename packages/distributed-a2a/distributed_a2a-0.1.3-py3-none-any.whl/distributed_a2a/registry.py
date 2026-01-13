import boto3
from langchain_core.tools import StructuredTool


class DynamoDbRegistryLookup:
    def __init__(self, agent_card_tabel: str):
        dynamo = boto3.resource("dynamodb", region_name="eu-central-1")
        self.table = dynamo.Table(agent_card_tabel)

    def get_agent_cards(self) -> list[str]:

        items = self.table.scan().get("Items", [])
        cards: list[str] = [it["card"] for it in items]
        return cards

    def as_tool(self) -> StructuredTool:
        return StructuredTool.from_function(func=lambda: self.get_agent_cards(), name="agent_card_lookup",
                                            description="Gets all available agent cards")
