import json
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logger.warning("paho-mqtt not installed. MQTT functionality disabled.")


# Alert thresholds for different sensor types
ALERT_THRESHOLDS = {
    "vibration": {"warning": 5.0, "critical": 8.0, "unit": "mm/s"},
    "gas": {"warning": 50.0, "critical": 100.0, "unit": "ppm"},
    "sound": {"warning": 70.0, "critical": 90.0, "unit": "dB"},
    "temperature": {"warning": 45.0, "critical": 60.0, "unit": "C"},
    "life_detector": {"warning": 0.5, "critical": 0.8, "unit": "probability"},
}


class MQTTHandler:
    """MQTT handler for IoT sensor communication."""

    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        client_id: str = "earthquake-rescue-api",
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.client: Optional[object] = None
        self.connected = False
        self.on_alert_callback: Optional[Callable] = None
        self.on_data_callback: Optional[Callable] = None

        if MQTT_AVAILABLE:
            self.client = mqtt.Client(client_id=client_id)
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            # Subscribe to all sensor topics
            self.client.subscribe("sensors/#")
            self.client.subscribe("devices/#")
            self.client.subscribe("alerts/#")
            logger.info("Subscribed to sensor topics: sensors/#, devices/#, alerts/#")
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnect (rc={rc}). Attempting reconnect...")

    def _on_message(self, client, userdata, msg):
        """Process incoming sensor messages."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode("utf-8"))
            logger.debug(f"MQTT message on '{topic}': {payload}")

            device_id = payload.get("device_id")
            sensor_type = payload.get("type", "unknown")
            value = payload.get("value")
            unit = payload.get("unit", "")

            if value is not None:
                # Check thresholds and trigger alerts
                self._check_thresholds(device_id, sensor_type, value, unit, payload)

                # Forward data to callback
                if self.on_data_callback:
                    self.on_data_callback(device_id, sensor_type, value, unit, payload)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON on topic '{msg.topic}': {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _check_thresholds(
        self,
        device_id: Optional[int],
        sensor_type: str,
        value: float,
        unit: str,
        raw_payload: dict,
    ):
        """Check sensor value against defined thresholds and trigger alerts."""
        thresholds = ALERT_THRESHOLDS.get(sensor_type)
        if not thresholds:
            return

        alert_level = None
        if value >= thresholds["critical"]:
            alert_level = "CRITICAL"
        elif value >= thresholds["warning"]:
            alert_level = "WARNING"

        if alert_level:
            alert_data = {
                "level": alert_level,
                "device_id": device_id,
                "sensor_type": sensor_type,
                "value": value,
                "unit": unit,
                "threshold": thresholds[alert_level.lower()] if alert_level.lower() in thresholds else None,
                "raw": raw_payload,
            }
            logger.warning(
                f"[ALERT][{alert_level}] Device {device_id}: "
                f"{sensor_type} = {value} {unit}"
            )

            if self.on_alert_callback:
                self.on_alert_callback(alert_data)

            # Publish alert to alerts topic
            if self.connected and self.client:
                self.client.publish(
                    f"alerts/{sensor_type}/{device_id}",
                    json.dumps(alert_data),
                )

    def connect(self):
        """Connect to the MQTT broker."""
        if not MQTT_AVAILABLE:
            logger.warning("Cannot connect: paho-mqtt not installed")
            return False
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        if self.client and self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")

    def publish(self, topic: str, data: dict) -> bool:
        """Publish data to an MQTT topic."""
        if not self.connected or not self.client:
            logger.warning("Cannot publish: not connected to MQTT broker")
            return False
        try:
            payload = json.dumps(data)
            self.client.publish(topic, payload)
            return True
        except Exception as e:
            logger.error(f"Failed to publish to '{topic}': {e}")
            return False

    def set_alert_callback(self, callback: Callable):
        """Set callback function for alert events."""
        self.on_alert_callback = callback

    def set_data_callback(self, callback: Callable):
        """Set callback function for incoming sensor data."""
        self.on_data_callback = callback
