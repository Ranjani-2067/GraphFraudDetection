from app.database.neo4j import get_connection
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.graph_repository import GraphRepository
from app.algorithms.graph_algorithms import GraphAnalytics
from app.algorithms.fraud_detector import FraudDetector

def conn(): return get_connection()
def account_repo(): return AccountRepository(conn())
def transaction_repo(): return TransactionRepository(conn())
def graph_repo(): return GraphRepository(conn())
def analytics(): return GraphAnalytics(conn())
def detector(): return FraudDetector(analytics(),graph_repo())
