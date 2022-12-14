from dataclasses import dataclass
from model.event import Event
from model.token_id import TokenId


@dataclass
class OfferCreateEventData:
    id: str
    token_id: TokenId
    source: str
    destination: str
    price: str
    gallery_id: str
    commission_feerate_numerator: str
    commission_feerate_denominator: str
    offer_start_at: str
    offer_expired_at: str
    exhibit_duration: str
    url: str
    detail: str


@dataclass
class OfferCreateEvent(Event[OfferCreateEventData]):
    pass
