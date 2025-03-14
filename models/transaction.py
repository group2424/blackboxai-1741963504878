from firebase_admin import firestore
import uuid

db = firestore.client()

class Transaction:
    def __init__(self, phone_number, amount, transaction_type, payment_method=None, transaction_id=None):
        self.id = str(uuid.uuid4())
        self.phone_number = phone_number
        self.amount = amount
        self.type = transaction_type  # 'deposit', 'withdrawal', or 'investment'
        self.status = 'pending'  # 'pending', 'approved', or 'rejected'
        self.payment_method = payment_method  # 'MTN' or 'Airtel'
        self.transaction_id = transaction_id  # Mobile money transaction ID
        self.created_at = firestore.SERVER_TIMESTAMP

    def save(self):
        """Save transaction to Firestore"""
        transaction_data = {
            'id': self.id,
            'phone_number': self.phone_number,
            'amount': self.amount,
            'type': self.type,
            'status': self.status,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at
        }
        db.collection('transactions').document(self.id).set(transaction_data)

    @staticmethod
    def get_by_id(transaction_id):
        """Get transaction by ID"""
        doc = db.collection('transactions').document(transaction_id).get()
        if doc.exists:
            data = doc.to_dict()
            transaction = Transaction(
                phone_number=data['phone_number'],
                amount=data['amount'],
                transaction_type=data['type'],
                payment_method=data.get('payment_method'),
                transaction_id=data.get('transaction_id')
            )
            transaction.id = data['id']
            transaction.status = data['status']
            transaction.created_at = data.get('created_at')
            return transaction
        return None

    @staticmethod
    def get_user_transactions(phone_number):
        """Get all transactions for a user"""
        transactions = []
        # Changed to simple query without ordering
        docs = (db.collection('transactions')
               .where('phone_number', '==', phone_number)
               .stream())
        
        for doc in docs:
            data = doc.to_dict()
            transaction = Transaction(
                phone_number=data['phone_number'],
                amount=data['amount'],
                transaction_type=data['type'],
                payment_method=data.get('payment_method'),
                transaction_id=data.get('transaction_id')
            )
            transaction.id = data['id']
            transaction.status = data['status']
            transaction.created_at = data.get('created_at')
            transactions.append(transaction)
        
        # Sort transactions in memory instead of using Firestore ordering
        transactions.sort(key=lambda x: x.created_at if x.created_at else 0, reverse=True)
        return transactions

    @staticmethod
    def get_pending_deposits():
        """Get all pending deposits"""
        transactions = []
        # Changed to simple query without ordering
        docs = (db.collection('transactions')
               .where('type', '==', 'deposit')
               .where('status', '==', 'pending')
               .stream())
        
        for doc in docs:
            data = doc.to_dict()
            transaction = Transaction(
                phone_number=data['phone_number'],
                amount=data['amount'],
                transaction_type=data['type'],
                payment_method=data.get('payment_method'),
                transaction_id=data.get('transaction_id')
            )
            transaction.id = data['id']
            transaction.status = data['status']
            transaction.created_at = data.get('created_at')
            transactions.append(transaction)
        
        # Sort transactions in memory
        transactions.sort(key=lambda x: x.created_at if x.created_at else 0, reverse=True)
        return transactions

    @staticmethod
    def get_pending_withdrawals():
        """Get all pending withdrawals"""
        transactions = []
        # Changed to simple query without ordering
        docs = (db.collection('transactions')
               .where('type', '==', 'withdrawal')
               .where('status', '==', 'pending')
               .stream())
        
        for doc in docs:
            data = doc.to_dict()
            transaction = Transaction(
                phone_number=data['phone_number'],
                amount=data['amount'],
                transaction_type=data['type'],
                payment_method=data.get('payment_method'),
                transaction_id=data.get('transaction_id')
            )
            transaction.id = data['id']
            transaction.status = data['status']
            transaction.created_at = data.get('created_at')
            transactions.append(transaction)
        
        # Sort transactions in memory
        transactions.sort(key=lambda x: x.created_at if x.created_at else 0, reverse=True)
        return transactions

    @staticmethod
    def get_all_deposits():
        """Get all deposits"""
        transactions = []
        docs = (db.collection('transactions')
               .where('type', '==', 'deposit')
               .where('status', '==', 'approved')
               .stream())
        
        for doc in docs:
            data = doc.to_dict()
            transaction = Transaction(
                phone_number=data['phone_number'],
                amount=data['amount'],
                transaction_type=data['type']
            )
            transaction.id = data['id']
            transaction.status = data['status']
            transactions.append(transaction)
        return transactions

    @staticmethod
    def get_all_withdrawals():
        """Get all withdrawals"""
        transactions = []
        docs = (db.collection('transactions')
               .where('type', '==', 'withdrawal')
               .where('status', '==', 'approved')
               .stream())
        
        for doc in docs:
            data = doc.to_dict()
            transaction = Transaction(
                phone_number=data['phone_number'],
                amount=data['amount'],
                transaction_type=data['type']
            )
            transaction.id = data['id']
            transaction.status = data['status']
            transactions.append(transaction)
        return transactions

    @staticmethod
    def get_all_investments():
        """Get all investments"""
        transactions = []
        docs = (db.collection('transactions')
               .where('type', '==', 'investment')
               .stream())
        
        for doc in docs:
            data = doc.to_dict()
            transaction = Transaction(
                phone_number=data['phone_number'],
                amount=data['amount'],
                transaction_type=data['type']
            )
            transaction.id = data['id']
            transaction.status = data['status']
            transactions.append(transaction)
        return transactions
