from typing import List, Tuple
from observer.observer import Observer
from model.curation.offer_reject_event import OfferRejectEvent, OfferRejectEventData
from model.state import State
from model.event import Event
from common.db import prisma_client
from prisma import enums
from config import config


class OfferRejectEventObserver(Observer[OfferRejectEvent]):

    async def process_all(self, state: State, events: List[Event[OfferRejectEvent]]) -> State:
        return await super().process_all(state, events)

    async def process(self, state: State, event: Event[OfferRejectEvent]) -> Tuple[State, bool]:
        new_state = state
        seqno = event.sequence_number
        data = OfferRejectEventData(**event.data)
        index = int(data.id)
        async with prisma_client.tx(timeout=60000) as transaction:
            result = await transaction.curationoffer.update(
                where={
                    'index_root': {
                        'index': index,
                        'root': config.curation.address()
                    }
                },
                data={
                    'status':  enums.CurationOfferStatus.rejected
                }
            )
            if result == None or result.status != enums.CurationOfferStatus.rejected:
                raise Exception(
                    f'[Curator reject offer]: Failed to reject curation offer({data})')

            updated_offset = await transaction.eventoffset.update(
                where={'id': 0},
                data={
                    "curation_offer_reject_excuted_offset": int(seqno)
                }
            )
            if updated_offset == None:
                raise Exception(
                    f'[Curation reject Offer]: Failed to update offset')

            new_state.new_offset.curation_offer_reject_excuted_offset = updated_offset.curation_offer_reject_excuted_offset
            return new_state, True
