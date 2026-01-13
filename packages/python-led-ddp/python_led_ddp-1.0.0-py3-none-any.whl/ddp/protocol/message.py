"""JSON message types for DDP control, config, and status."""

from typing import Optional, Any, Dict, List, Union
from dataclasses import dataclass
import json
from ddp.protocol.id import ID
from ddp.error import ParseError


@dataclass
class Status:
    """Device status information."""
    update: Optional[str] = None
    state: Optional[str] = None
    man: Optional[str] = None  # manufacturer
    model: Optional[str] = None  # renamed from 'mod' in JSON
    ver: Optional[str] = None
    mac: Optional[str] = None
    push: Optional[bool] = None
    ntp: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {}
        if self.update is not None:
            result['update'] = self.update
        if self.state is not None:
            result['state'] = self.state
        if self.man is not None:
            result['man'] = self.man
        if self.model is not None:
            result['mod'] = self.model  # Use 'mod' in JSON
        if self.ver is not None:
            result['ver'] = self.ver
        if self.mac is not None:
            result['mac'] = self.mac
        if self.push is not None:
            result['push'] = self.push
        if self.ntp is not None:
            result['ntp'] = self.ntp
        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Status':
        """Parse from dictionary."""
        return Status(
            update=data.get('update'),
            state=data.get('state'),
            man=data.get('man'),
            model=data.get('mod'),  # Map 'mod' to 'model'
            ver=data.get('ver'),
            mac=data.get('mac'),
            push=data.get('push'),
            ntp=data.get('ntp'),
        )


@dataclass
class StatusRoot:
    """Root object for status messages."""
    status: Status

    def to_dict(self) -> Dict[str, Any]:
        return {'status': self.status.to_dict()}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StatusRoot':
        return StatusRoot(status=Status.from_dict(data['status']))


@dataclass
class Port:
    """Output port configuration."""
    port: int
    ts: int  # number of T's
    l: int  # number of lights
    ss: int  # starting slot

    def to_dict(self) -> Dict[str, Any]:
        return {'port': self.port, 'ts': self.ts, 'l': self.l, 'ss': self.ss}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Port':
        return Port(
            port=data['port'],
            ts=data['ts'],
            l=data['l'],
            ss=data['ss'],
        )


@dataclass
class Config:
    """Device configuration."""
    ip: Optional[str] = None
    nm: Optional[str] = None  # netmask
    gw: Optional[str] = None  # gateway
    ports: List[Port] = None

    def __post_init__(self):
        if self.ports is None:
            self.ports = []

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.ip is not None:
            result['ip'] = self.ip
        if self.nm is not None:
            result['nm'] = self.nm
        if self.gw is not None:
            result['gw'] = self.gw
        if self.ports:
            result['ports'] = [p.to_dict() for p in self.ports]
        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Config':
        ports_data = data.get('ports', [])
        ports = [Port.from_dict(p) for p in ports_data]
        return Config(
            ip=data.get('ip'),
            nm=data.get('nm'),
            gw=data.get('gw'),
            ports=ports,
        )


@dataclass
class ConfigRoot:
    """Root object for config messages."""
    config: Config

    def to_dict(self) -> Dict[str, Any]:
        return {'config': self.config.to_dict()}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ConfigRoot':
        return ConfigRoot(config=Config.from_dict(data['config']))


@dataclass
class Color:
    """RGB color value."""
    r: int
    g: int
    b: int

    def to_dict(self) -> Dict[str, int]:
        return {'r': self.r, 'g': self.g, 'b': self.b}

    @staticmethod
    def from_dict(data: Dict[str, int]) -> 'Color':
        return Color(r=data['r'], g=data['g'], b=data['b'])


@dataclass
class Control:
    """Device control settings."""
    fx: Optional[str] = None  # effect name
    int: Optional[int] = None  # intensity
    spd: Optional[int] = None  # speed
    dir: Optional[int] = None  # direction
    colors: Optional[List[Color]] = None
    save: Optional[int] = None
    power: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.fx is not None:
            result['fx'] = self.fx
        if self.int is not None:
            result['int'] = self.int
        if self.spd is not None:
            result['spd'] = self.spd
        if self.dir is not None:
            result['dir'] = self.dir
        if self.colors is not None:
            result['colors'] = [c.to_dict() for c in self.colors]
        if self.save is not None:
            result['save'] = self.save
        if self.power is not None:
            result['power'] = self.power
        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Control':
        colors_data = data.get('colors')
        colors = [Color.from_dict(c) for c in colors_data] if colors_data else None
        return Control(
            fx=data.get('fx'),
            int=data.get('int'),
            spd=data.get('spd'),
            dir=data.get('dir'),
            colors=colors,
            save=data.get('save'),
            power=data.get('power'),
        )


@dataclass
class ControlRoot:
    """Root object for control messages."""
    control: Control

    def to_dict(self) -> Dict[str, Any]:
        return {'control': self.control.to_dict()}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ControlRoot':
        return ControlRoot(control=Control.from_dict(data['control']))


# Union type for different message types
Message = Union[
    ControlRoot,
    StatusRoot,
    ConfigRoot,
    tuple[ID, Dict[str, Any]],  # Parsed but untyped
    tuple[ID, str],  # Unparsed string
]


def message_to_bytes(msg: Message) -> bytes:
    """Convert a message to bytes for transmission."""
    try:
        if isinstance(msg, (ControlRoot, StatusRoot, ConfigRoot)):
            return json.dumps(msg.to_dict()).encode('utf-8')
        elif isinstance(msg, tuple) and len(msg) == 2:
            _, content = msg
            if isinstance(content, dict):
                return json.dumps(content).encode('utf-8')
            elif isinstance(content, str):
                return content.encode('utf-8')
        raise ParseError("Unknown message type")
    except Exception as e:
        raise ParseError(f"Failed to serialize message: {e}")


def message_get_id(msg: Message) -> ID:
    """Get the ID from a message."""
    if isinstance(msg, ControlRoot):
        return ID.CONTROL
    elif isinstance(msg, StatusRoot):
        return ID.STATUS
    elif isinstance(msg, ConfigRoot):
        return ID.CONFIG
    elif isinstance(msg, tuple) and len(msg) == 2:
        return msg[0]
    else:
        return ID.DEFAULT
