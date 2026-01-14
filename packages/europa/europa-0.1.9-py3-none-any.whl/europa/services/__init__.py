"""
If you are launching services using -m module command, you need to import them here like this
"""
from .sample_service import SampleService
from .sample_service_with_websocket import SampleServiceWithWebsocket
from .sample_single_queue_service import SampleSingleQueueService, SampleSinglePostgresQueueService
from .sample_service_with_hazelcast import SampleServiceWithHazelcast