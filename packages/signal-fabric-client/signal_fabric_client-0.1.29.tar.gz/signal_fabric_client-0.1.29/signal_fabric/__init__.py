"""
Signal Fabric Client Library
gRPC client for interacting with Signal Fabric server
"""

from .grpc_client import GrpcClient, SignalOutcome, BacktestMetadata, BacktestCandle

__version__ = "0.1.29"

__all__ = ['GrpcClient', 'SignalOutcome', 'BacktestMetadata', 'BacktestCandle', '__version__']
