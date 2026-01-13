from dataclasses import dataclass, field
from typing import Optional, Union, Mapping

@dataclass
class RequestContext:
    # Inbound metadata (lower/any case; map as-is)
    headers: Mapping[str, str] = field(default_factory=dict)
    params: Mapping[str, list[str]] = field(default_factory=dict)
    body: Optional[Union[dict, bytes]] = None          # only present for POST/AMQP
    # Hints for outbound call
    accept: Optional[str] = None                            # override outbound Accept
    content_type: Optional[str] = None 
