from google.cloud.pubsub_v1 import publisher
from google.cloud.pubsub_v1.subscriber.message import Message
import logging.config

# Setup logging
logger = logging.getLogger()


class Publisher:
    """Utility class to set up connection to PubSub and publish message to Topic"""

    def __init__(self, project_id: str, topic_id: str):
        self.project_id = project_id
        self.topic_id = topic_id

    def publish(self, message: Message, **custom_attributes) -> str:
        """Publishes a message with custom attributes if applied"""

        pubsub_client = publisher.client.Client()
        topic_path = pubsub_client.topic_path(self.project_id, self.topic_id)
        attributes = {}
        result: str
        try:
            if custom_attributes:
                for k, v in custom_attributes.items():
                    attributes[str(k)] = str(v)
                result = pubsub_client.publish(
                    topic_path, bytes(str(message.data), "utf-8"), **attributes
                ).result(timeout=10)
                logger.info(
                    f'Posted message with custom attributes {attributes} to topic "{topic_path}" with id: {result}'
                )
            else:
                result = pubsub_client.publish(
                    topic_path,
                    bytes(str(message.data), "utf-8"),
                ).result(timeout=10)
                logger.info(f'Posted message to topic "{topic_path}" with id: {result}')
            return result
        except Exception as e:
            logger.error(f"Exception encountered on publish: {e}")
            raise e

    def publish_string_content(self, message: str, **custom_attributes) -> str:
        """Publishes string content with custom attributes if applied"""

        pubsub_client = publisher.client.Client()
        topic_path = pubsub_client.topic_path(self.project_id, self.topic_id)
        attributes = {}
        result: str
        try:
            if custom_attributes:
                for k, v in custom_attributes.items():
                    attributes[str(k)] = str(v)
                result = pubsub_client.publish(
                    topic_path,
                    bytes(message, "utf-8"),
                    **attributes,
                ).result(timeout=10)
                logging.info(
                    f'Posted message with custom attributes {attributes} to topic "{topic_path}" with id: {result}'
                )
            else:
                result = pubsub_client.publish(
                    topic_path,
                    bytes(message, "utf-8"),
                ).result(timeout=10)
                logging.info(
                    f'Posted message to topic "{topic_path}" with id: {result}'
                )
            return result

        except Exception as e:
            logger.error(f"Exception encountered on publish: {e}")
            raise e
