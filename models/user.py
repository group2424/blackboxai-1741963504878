import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import random
import string

# Initialize Firebase Admin
cred = credentials.Certificate('serviceAccountKey.json')
try:
    firebase_admin.initialize_app(cred)
except ValueError:
    # App already initialized
    pass

db = firestore.client()

class User:
    def __init__(self, phone_number, password, full_name):
        self.phone_number = phone_number
        self.password = password
        self.full_name = full_name
        self.balance = 0
        self.investments = []
        self.referrals = {'level_a': [], 'level_b': [], 'level_c': []}
        self.referral_code = self._generate_referral_code()
        self.is_blocked = False
        self.referred_by = None

    def _generate_referral_code(self):
        """Generate a unique 6-character referral code"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=6))
            # Check if code already exists
            existing = db.collection('users').where('referral_code', '==', code).get()
            if not list(existing):  # Convert to list to check if empty
                return code

    def save(self):
        """Save user data to Firestore"""
        user_data = {
            'phone_number': self.phone_number,
            'password': self.password,
            'full_name': self.full_name,
            'balance': self.balance,
            'investments': self.investments,
            'referrals': self.referrals,
            'referral_code': self.referral_code,
            'is_blocked': self.is_blocked,
            'referred_by': self.referred_by
        }
        db.collection('users').document(self.phone_number).set(user_data)

    @staticmethod
    def get_by_phone(phone_number):
        """Get user by phone number"""
        doc = db.collection('users').document(phone_number).get()
        if doc.exists:
            data = doc.to_dict()
            user = User(
                phone_number=data['phone_number'],
                password=data['password'],
                full_name=data['full_name']
            )
            user.balance = data.get('balance', 0)
            user.investments = data.get('investments', [])
            user.referrals = data.get('referrals', {'level_a': [], 'level_b': [], 'level_c': []})
            user.referral_code = data.get('referral_code')
            user.is_blocked = data.get('is_blocked', False)
            user.referred_by = data.get('referred_by')
            return user
        return None

    @staticmethod
    def get_by_referral_code(referral_code):
        """Get user by referral code"""
        docs = db.collection('users').where('referral_code', '==', referral_code).limit(1).get()
        for doc in docs:
            data = doc.to_dict()
            user = User(
                phone_number=data['phone_number'],
                password=data['password'],
                full_name=data['full_name']
            )
            user.balance = data.get('balance', 0)
            user.investments = data.get('investments', [])
            user.referrals = data.get('referrals', {'level_a': [], 'level_b': [], 'level_c': []})
            user.referral_code = data.get('referral_code')
            user.is_blocked = data.get('is_blocked', False)
            user.referred_by = data.get('referred_by')
            return user
        return None

    @staticmethod
    def get_all_users():
        """Get all users"""
        users = []
        docs = db.collection('users').stream()
        for doc in docs:
            data = doc.to_dict()
            user = User(
                phone_number=data['phone_number'],
                password=data['password'],
                full_name=data['full_name']
            )
            user.balance = data.get('balance', 0)
            user.investments = data.get('investments', [])
            user.referrals = data.get('referrals', {'level_a': [], 'level_b': [], 'level_c': []})
            user.referral_code = data.get('referral_code')
            user.is_blocked = data.get('is_blocked', False)
            user.referred_by = data.get('referred_by')
            users.append(user)
        return users

    def add_investment(self, amount):
        """Add a new investment"""
        if amount > self.balance:
            return False, "Insufficient balance"
        
        self.balance -= amount
        investment = {
            'id': str(uuid.uuid4()),
            'amount': amount,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        self.investments.append(investment)
        self.save()
        return True, "Investment added successfully"

    def add_referral(self, phone_number, level):
        """Add a referral at specified level (a, b, or c)"""
        level_key = f'level_{level}'
        if level_key in self.referrals and phone_number not in self.referrals[level_key]:
            self.referrals[level_key].append(phone_number)
            self.save()

    def get_team_size(self):
        """Get total number of referrals across all levels"""
        return (
            len(self.referrals.get('level_a', [])) +
            len(self.referrals.get('level_b', [])) +
            len(self.referrals.get('level_c', []))
        )

    def get_monthly_reward(self):
        """Calculate monthly team reward based on team size"""
        team_size = self.get_team_size()
        if team_size >= 100:
            return 100000  # 100k RWF for 100+ team members
        elif team_size >= 50:
            return 50000   # 50k RWF for 50+ team members
        elif team_size >= 20:
            return 20000   # 20k RWF for 20+ team members
        elif team_size >= 10:
            return 10000   # 10k RWF for 10+ team members
        return 0

    @staticmethod
    def calculate_daily_interest(amount):
        """Calculate daily interest based on investment amount"""
        tiers = [
            {'min': 1000, 'max': 49999, 'rate': 0.01},      # 1% daily
            {'min': 50000, 'max': 499999, 'rate': 0.015},   # 1.5% daily
            {'min': 500000, 'max': float('inf'), 'rate': 0.02}  # 2% daily
        ]
        
        for tier in tiers:
            if tier['min'] <= amount <= tier['max']:
                return amount * tier['rate']
        return 0
