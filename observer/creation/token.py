from typing import List, Tuple
from observer.observer import Observer
from model.creation.create_token_event import CreateTokenEvent, CreateTokenEventData
from model.state import State
from model.event import Event
from common.db import prisma_client
from prisma import enums
from common.util import primary_key_of_token

DEFAULT_COLLECTION = "Imart Default Collection"
DEFAULT_CREATOR = "0x94961b26c3541d4be6638913335da22cf3c45aa3d44ff110d9df8890c0c1a34b"
DEFAULT_RESOURCE_ACCOUNT = "0xe59d3179e6d4598937a33beb71f811b9bad18af1c253014d6b4945e44f710590"


class CreateTokenEventObserver(Observer[CreateTokenEvent]):

    async def process_all(self, state: State, events: List[Event[CreateTokenEvent]]) -> State:
        return await super().process_all(state, events)

    async def process(self, state: State, event: Event[CreateTokenEvent]) -> Tuple[State, bool]:
        new_state = state
        seqno = event.sequence_number
        data = CreateTokenEventData(**event.data)

        collection = await prisma_client.collection.find_unique(where={
            'chain_creator_name': {
                'chain': enums.Chain.APTOS,
                'creator': DEFAULT_CREATOR,
                'name': DEFAULT_COLLECTION,
            }
        })
        if collection == None:
            raise Exception(
                f'[Create token]: collection not found, but created token event({data}) was existed')

        async with prisma_client.tx(timeout=60000) as transaction:

            result = await transaction.aptostoken.create(
                data={
                    'id': primary_key_of_token(data.user, DEFAULT_COLLECTION, data.name),
                    'collectionId': collection.id,
                    'owner': data.user,
                    'creator': DEFAULT_RESOURCE_ACCOUNT,
                    'collection': DEFAULT_COLLECTION,
                    'name': data.name,
                    'description': data.description,
                    'uri': data.uri,
                    'propertyVersion': '0',
                    'seqno': seqno
                }
            )
            if result == None:
                raise Exception(
                    f'[Create token]: Failed to create new token({data})')

            updated_offset = await transaction.eventoffset.update(
                where={'id': 0},
                data={
                    "create_token_excuted_offset": int(seqno)
                }
            )
            if updated_offset == None:
                raise Exception(f'[Create token]: Failed to update offset')

            new_state.new_offset.create_token_excuted_offset = updated_offset.create_token_excuted_offset
            return new_state, True
