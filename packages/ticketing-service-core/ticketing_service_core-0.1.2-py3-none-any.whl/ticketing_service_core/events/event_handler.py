"""
event_handler Module
"""

import os
import time
import importlib
import json
import yaml
import pika
import jsonschema
from loguru import logger
from ticketing_service_core.orm import SQLAdministrator
from .consumer_exception import ConsumerException

class EventHandler:
    """
    The EventHandler sets up queue bindings and routes message handling to the
    relevant callback
    """

    def __init__(self, service: str):
        self.__rabbitmq = None
        self.__routing_map = {}
        self.__sql = SQLAdministrator()

        # Load events configuration
        with open(
            os.environ["EVENTS_CONFIG"], "r",
            encoding="utf-8"
        ) as events_file:
            config = yaml.safe_load(events_file)
            self.__events = config["events"]
            self.__message_queue = f"{service}.service.queue"


    def run(self):
        """
        Setup queue bindings and start message consumption
        """

        # Open a RabbitMQ connection if one does not exists
        while not self.__rabbitmq:
            logger.info("Attempting connection to RabbitMQ")
            try:
                self.__connect_to_rabbitmq()
                logger.info("Connection to RabbitMQ successful!")
            except pika.exceptions.AMQPConnectionError as e:
                logger.info(f"Failed to connect to RabbitMQ: {e}. Retrying.")
                time.sleep(1)

        channel = self.__rabbitmq.channel()

        # Ensure a consumer only receives a single message at a time
        channel.basic_qos(prefetch_count=1)

        # Setup Queue Bindings
        bindings = []
        for event in self.__events:
            # Initialise routing key
            action = (f".{event['action']}" if ("action" in event) else "")
            routing_key = f"{event['resource']}{action}"

            # If the service queue has already been bound to the target exchange
            # with this routing key
            if f"{event["exchange"]}:{routing_key}" in bindings:
                continue

            # Bind microservice queue to the indicated exchange
            logger.info(
                f"Binding {self.__message_queue} to {event['exchange']} exchange"
                f" with '{routing_key}' routing key"
            )

            try:
                channel.queue_bind(
                    exchange=event["exchange"],
                    queue=self.__message_queue,
                    routing_key=routing_key
                )

                bindings.append(f"{event["exchange"]}:{routing_key}")
            except pika.exceptions.ChannelClosedByBroker as e:
                logger.warning(
                    f"Could not bind service queue to {event["exchange"]} exchange: {e}"
                )

                channel = self.__rabbitmq.channel()

                # Ensure a consumer only receives a single message at a time
                channel.basic_qos(prefetch_count=1)


        # Start message consumption
        for event in self.__events:
            # Initialise routing key
            action = (f".{event['action']}" if ("action" in event) else "")
            routing_key = f"{event['resource']}{action}"

            # Add routing map entry
            if f"{event["exchange"]}:{routing_key}" not in self.__routing_map:
                self.__routing_map[f"{event["exchange"]}:{routing_key}"] = []

            # Dynamically import consumer module and instantiate consumer class
            consumer = getattr(
                importlib.import_module(os.environ["CONSUMER_MODULE"]),
                event["consumer"]
            )

            # Dynamically import excepted message schema
            request_schema = getattr(
                importlib.import_module("ticketing_service_core.schema"),
                event["schema"]
            )

            self.__routing_map[f"{event["exchange"]}:{routing_key}"].append({
                "handler": consumer(),
                "schema": request_schema
            })

        # Setup message consumption
        channel.basic_consume(
            queue=self.__message_queue,
            on_message_callback=self.__route_event,
            auto_ack=False
        )

        # Start consumption loop
        logger.info(
            f"Listening for nessages to {self.__message_queue}"
        )

        try:
            channel.start_consuming()
            channel.close()

            self.__rabbitmq = None
        except pika.exceptions.ConnectionClosedByBroker as e:
            logger.info("RabbitMQ went away. Attempting to reconnext")

            self.__rabbitmq = None
            self.run()


    def stop(self):
        """
        Close RabbitMQ connection, cleaning up queues if necessary
        """

        # Close the open RabbitMQ connection if one exists
        if self.__rabbitmq:
            self.__rabbitmq.close()

    def __connect_to_rabbitmq(self):
        # Setup blocking connection to RabbitMQ
        self.__rabbitmq = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.environ["MQ_HOSTNAME"],
                port=os.environ["MQ_PORT"],
                credentials=pika.PlainCredentials(
                    os.environ["MQ_USERNAME"],
                    os.environ["MQ_PASSWORD"]
                )
            )
        )

    def __route_event(self, channel, method, properties, body):
        for consumer in self.__routing_map[f"{method.exchange}:{method.routing_key}"]:
            processing_error = None
            response = None
            message = {}

            try:
                # Validate message body
                message = json.loads(body)
                jsonschema.validate(instance=message, schema=consumer["schema"])

                self.__sql.connect()

                # Process message
                response = consumer["handler"].consume(
                    channel=channel,
                    body=message,
                    sql=self.__sql
                )
            except (ValueError, jsonschema.ValidationError) as e:
                logger.warning(f"Parsing message body failed: {e}")
                response = {
                    "processing_error":
                    "The message body did not match the excepted schema."
                }
            except ConsumerException as e:
                processing_error = f"Comsumer threw an exception: {e}"
                response = {
                    "processing_error":
                    "The consumer encountered an error while processing this message."
                }

            # Send response to message when called in an RPC context
            try:
                if "reply_to" in message:
                    if "correlation_id" in message:
                        # Add correlation id to response
                        response["correlation_id"] = message["correlation_id"]

                    channel.basic_publish(
                        exchange="",
                        routing_key=message["reply_to"],
                        body=json.dumps(response)
                    )
            except TypeError as e:
                processing_error = f"Consumer responded with invalid data: {e}"
                response = {
                    "processing_error":
                    "The consumer encountered an error while processing this message."
                }

        # Handle any processing errors
        if processing_error:
            self.__sql.rollback()

            logger.error(
                f"Can't process message to '{method.exchange}' exchange "
                f"with routing key {method.routing_key}. "
                f"{processing_error}"
            )

            #Thottle redelivery to prevent flooding service
            time.sleep(1)

            # Send NACK to broker if message could not be processed
            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=True
            )

            logger.info("NACKed message. Waiting for redelivery.")
        else:
            self.__sql.commit()

            # Send ACK to broker upon successful processing
            channel.basic_ack(delivery_tag=method.delivery_tag)

        self.__sql.close()
