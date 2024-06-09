import json
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from carpark.asgi import application

class WebsocketTests(TestCase):
    async def async_test_parking_lot_update_consumer(self):
        communicator = WebsocketCommunicator(application, "/ws/parking_lot_updates/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Simulate a message being sent to the group
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "parking_lot_updates",
            {
                "type": "send_parking_lot_update",
                "data": {"update": "Parking lot full"},
            },
        )

        response = await communicator.receive_json_from()
        self.assertEqual(response, {"update": "Parking lot full"})

        # Close the connection
        await communicator.disconnect()

    async def async_test_parking_spot_update_consumer(self):
        communicator = WebsocketCommunicator(application, "/ws/parking_spot_updates/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Simulate a message being sent to the group
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "parking_spot_updates",
            {
                "type": "send_parking_spot_update",
                "data": {"update": "Parking spot taken"},
            },
        )

        response = await communicator.receive_json_from()
        self.assertEqual(response, {"update": "Parking spot taken"})

        # Close the connection
        await communicator.disconnect()

    async def async_test_camera_update_consumer(self):
        communicator = WebsocketCommunicator(application, "/ws/camera_updates/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Test sending and processing frame data
        frame_data = {
            "type": "frame_data",
            "camera_address": "camera_1",
            "destination_type": "entry",
            "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAAAD/4QBiRXhpZgAATU0AKgAAAAgABwESAAMAAAABAAEAAAEaAAUAAAABAAAAYgEbAAUAAAABAAAAagEoAAMAAAABAAIAAAExAAIAAAAGAAAAbgEyAAIAAAAUAAAAYodpAAQAAAABAAAAcgAAAAAAAABIAAAAAQAAAEgAAAABAAKgAgAEAAAAAQAAACqgAwAEAAAAAQAAACAAAAAB/9sAQwADAgICAgMCAgIDAwMDBAYEBAQEBQcFBQQECAgICAgICAgICAgICAwMDAwMDAwMDBQQFBQUFBQUEBAQFBQUGBgYGBgcGBgYGBv/xAAaAAACAwEBAAAAAAAAAAAAAAAABQIDBAYB/8QAMxAAAQMDAQYEBwEAAAAAAAABAgMEBREABhIhMRMiQVFhcYEHMkKBkaGxFCNC8P/EABQBAQAAAAAAAAAAAAAAAAAAAAD/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwD8RqELtFRnAfbQ9r91G4kmMlnWwEXE3Tb66yfY0Wb25tOlz5RDLsAB5P2fvU4M11WsNlXVp0h7ThZVsASNgWv66nt4nT15M3WHEyjcXKoEItDSUqTQLKWVxuVXaz2DbvPceOxGvPTN7HhItItpqTwkhmZtLO5NmCdo68DjJPnVT6hxmhR+PhXKYztLEdSuwLWwJOt5/QD1O/uDvV8sM9yzTR2HcFJ0kFMUtEsNa4IwJQPLg6hWpW8kjYOPfvx5Hq2k5+zuFg3YixEbVwSz5RkMPCrxL5OB2ST5drZOSOfmloy2oOVjE5LuMNj9RUZlxZgsp0k9q5XAkTBMjqF8tlBG7AN3MWXq2guM8fFOsAdKwdrMD4wOQfY/rAOrq4K2gDAbDszxYAmAIySx4ACtBdA2CMtEjqA7DrX7z8vU8/9k="
        }
        await communicator.send_json_to(frame_data)
        response = await communicator.receive_json_from()
        self.assertEqual(response["message"], "Received frame from camera: camera_1, license plate: [extracted_license_plate], destination: entry")

        # Close the connection
        await communicator.disconnect()

    def test_parking_lot_update_consumer(self):
        import asyncio
        asyncio.run(self.async_test_parking_lot_update_consumer())

    def test_parking_spot_update_consumer(self):
        import asyncio
        asyncio.run(self.async_test_parking_spot_update_consumer())

    # def test_camera_update_consumer(self):
    #     import asyncio
    #     asyncio.run(self.async_test_camera_update_consumer())
