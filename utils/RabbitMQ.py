import pika
import logging

class RabbitMQ:
    def __init__(self, host, exchange, queue=None):
        self._host = host
        self._exchange = exchange
        self._queue = queue
        self.connection = None
        self.channel = None

    def connect(self, queue=None):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._host))
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self._exchange, exchange_type='fanout')

            # If for subscriber - create queue and bind to it
            if self._queue is not None:
                result = self.channel.queue_declare(queue=self._queue, exclusive=True)
                self.channel.queue_bind(exchange=self._exchange, queue=self._queue)
        except:
            raise Exception("Couldn't connect to rabbitmq")

    def _publish(self, msg):
        self.channel.basic_publish(exchange=self._exchange, 
                                         routing_key='', 
                                         body=bytes(msg, encoding='utf8'))
        logging.debug('message sent: %s', msg)

    def publish(self, msg):
        """Publish msg, reconnecting if necessary."""
        try:
            self._publish(msg)
        except pika.exceptions.StreamLostError:
            logging.debug('reconnecting to queue')
            self.connect()
            self._publish(msg)

    def _subscribe(self, callback):
        self.channel.basic_consume(queue=self._queue, 
                                   on_message_callback=callback, 
                                   auto_ack=True)
        self.channel.start_consuming()

    def subscribe(self, callback):
        """Subscribe msg, reconnecting if necessary."""
        try:
            self._subscribe(callback)
        except pika.exceptions.ChannelClosed:
            logging.debug('reconnecting to queue')
            self.connect()
            self._subscribe(msg)