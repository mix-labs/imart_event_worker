from datetime import datetime
from typing import List, Tuple
from common.util import new_uuid
from common.redis import redis_cli
from model.token_id import TokenId, TokenDataId
from observer.observer import Observer
from model.order.delist_event import DelistEvent, DelistEventData
from model.state import State
from model.event import Event
from common.db import prisma_client
from prisma import enums


class DelistEventObserver(Observer[DelistEvent]):

    async def process_all(self, state: State, events: List[Event[DelistEvent]]) -> State:
        return await super().process_all(state, events)

    async def process(self, state: State, event: Event[DelistEvent]) -> Tuple[State, bool]:
        new_state = state
        seqno = event.sequence_number
        data = DelistEventData(**event.data)
        token_data_id = TokenDataId(**TokenId(**data.token_id).token_data_id)

        token = await prisma_client.aptostoken.find_first(where={
            'name': token_data_id.name,
            'creator': token_data_id.creator,
            'collection': token_data_id.collection,
        })
        if token == None:
            raise Exception(
                f'[Delist Order]: Token ({token_data_id}) not found but the delist event ({data}) was existed.')

        async with prisma_client.tx(timeout=60000) as transaction:

            # order
            timestamp = datetime.fromtimestamp(
                float(data.timestamp) / 1000000)
            updated = await transaction.aptosorder.update_many(
                where={
                    'status': enums.OrderStatus.LISTING,
                    'tokenId': token.id
                },
                data={
                    'status': enums.OrderStatus.CANCELED,
                }
            )
            if updated == None:
                raise Exception(
                    f"[Delist Order]: Failed to update order status to CANCELED")

            # activity
            result = await transaction.aptosactivity.create(
                data={
                    'id': new_uuid(),
                    'orderId': "",
                    'collectionId': token.collectionId,
                    'tokenId': token.id,
                    'source': data.seller,
                    'destination': "",
                    'txHash': f'{event.version}',
                    'txType': enums.TxType.CANCEL,
                    'quantity': data.token_amount,
                    'price': "0",
                    'txTimestamp': timestamp
                }
            )
            if result == None or result.txType != enums.TxType.CANCEL:
                raise Exception(
                    f"[Token Activity]: Failed to create new activity with delist event")

            # seqno
            updated_offset = await transaction.eventoffset.update(
                where={'id': 0},
                data={
                    "delist_event_excuted_offset": int(seqno)
                }
            )
            if updated_offset == None or updated_offset.delist_event_excuted_offset != int(seqno):
                raise Exception(f"[Delist Order]: Failed to update offset")

            new_state.new_offset.delist_events_excuted_offset = updated_offset.delist_event_excuted_offset
            
            # delete cache
            redis_cli.delete(f"cache:imart:aptosOrder:id:{token.id}")
            redis_cli.delete(f"cache:imart:collectionstats:id:{token.collectionId}")
            return new_state, True
