"""
EDC-related exceptions.
"""

from typing import List, Dict


class NegotiationRequired(Exception):
    """
    Exception raised when contract negotiation is required.

    Contains information to guide the consumer's connector to initiate negotiation.
    """
    def __init__(self, asset_id: str, participant_id: str, suggested_policies: List[Dict]):
        self.asset_id = asset_id
        self.participant_id = participant_id
        self.suggested_policies = suggested_policies
        self.status_code = 449  # Retry With (custom status for negotiation needed)
        super().__init__(f"Contract negotiation required for asset {asset_id}")
